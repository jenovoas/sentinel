
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import time
import subprocess
import numpy as np # PRECAUCIÓN: SOLO PARA I/O, NO CÁLCULO CORE
import threading
import os
import psutil

# Configuration
ITERATIONS = 20  # Keep low for LLM testing
LOAD_DURATION = 10

def cpu_stress():
    t_end = time.time() + LOAD_DURATION
    while time.time() < t_end:
        [x**2 for x in range(1000)]

def io_stress():
    t_end = time.time() + LOAD_DURATION
    while time.time() < t_end:
        with open("/tmp/sentinel_stress", "w") as f:
            f.write("x" * 1024 * 1024)

def measure_native_cmd():
    latencies = []
    for _ in range(ITERATIONS):
        start = time.perf_counter()
        subprocess.run(["ls", "-l", "/etc"], capture_output=True)
        end = time.perf_counter()
        latencies.append((end - start) * 1000) # ms
    return latencies

def measure_semantic_cmd():
    # Calling sem_shell non-interactively might require modification or using the exposed class
    # We will import the class directly for accurate "Internal Overhead" measurement
    from sem_shell import SentinelShell
    sem = SentinelShell()
    
    latencies = []
    query = "listar archivos en /etc"
    
    for _ in range(ITERATIONS):
        start = time.perf_counter()
        # Full cognitive loop: Intent -> Validate -> Execute
        cmd = sem.contextual_intent(query)
        _ = sem.safe_execute(cmd)
        end = time.perf_counter()
        latencies.append((end - start) * 1000) # ms
    return latencies

def print_stats(name, data):
    p95 = np.percentile(data, 95)
    mean = np.mean(data)
    print(f"🔹 {name:20} | Avg: {mean:6.2f} ms | P95: {p95:6.2f} ms")
    return mean, p95

def run_bench():
    print(f"🚀 Sentinel Cortex v2.0 - Performance Benchmark (N={ITERATIONS})")
    print("=" * 60)
    
    # 1. Idle Baseline
    print("\n[PHASE 1] IDLE STATE")
    native_idle = measure_native_cmd()
    print_stats("Native (Bash)", native_idle)
    
    try:
        sentinel_idle = measure_semantic_cmd()
        print_stats("Sentinel (SemSH)", sentinel_idle)
        overhead = np.mean(sentinel_idle) - np.mean(native_idle)
        print(f"   👉 Cognitive Overhead: +{overhead:.2f} ms")
    except Exception as e:
        print(f"   ⚠️ Sentinel Error: {e}")
        sentinel_idle = []

    # 2. Under Load
    print("\n[PHASE 2] HEAVY LOAD (CPU + I/O)")
    print("   🔥 Stressing generators started...")
    
    # Start stressors
    t1 = threading.Thread(target=cpu_stress)
    t2 = threading.Thread(target=io_stress)
    t1.start()
    t2.start()
    
    # Wait a bit for load to stabilize
    time.sleep(2)
    
    native_load = measure_native_cmd()
    print_stats("Native (Bash)", native_load)
    
    if sentinel_idle:
        sentinel_load = measure_semantic_cmd()
        print_stats("Sentinel (SemSH)", sentinel_load)
        overhead_load = np.mean(sentinel_load) - np.mean(native_load)
        print(f"   👉 Cognitive Overhead: +{overhead_load:.2f} ms")
    
    t1.join()
    t2.join()
    
    print("\n✅ Benchmark Complete.")

if __name__ == "__main__":
    run_bench()
