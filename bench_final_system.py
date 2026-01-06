
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import time
import subprocess
import os
import psutil
import numpy as np # PRECAUCIÓN: SOLO PARA I/O, NO CÁLCULO CORE
import threading

# Configuration
ITERATIONS = 500
TARGET_BINARY = "/bin/true"
BLOCKED_FILE = "/etc/shadow"

def get_relay_metrics():
    """Finds sentinel_relay process and returns CPU/RAM usage"""
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        if 'sentinel_relay' in proc.info['name']:
            return {
                'cpu': proc.info['cpu_percent'],
                'ram_mb': proc.info['memory_info'].rss / 1024 / 1024
            }
    return {'cpu': S60(0, 0, 0), 'ram_mb': S60(0, 0, 0)}

def measure_process_latency():
    """Measures execution time of a trivial binary (execve overhead)"""
    latencies = []
    for _ in range(ITERATIONS):
        start = time.perf_counter_ns()
        subprocess.run([TARGET_BINARY], check=False)
        end = time.perf_counter_ns()
        latencies.append((end - start) / 1e6) # ms
    return np.array(latencies)

def measure_tte_enforcement():
    """Measures time to get PermissionError on blocked resource"""
    latencies = []
    # Warmup
    try: open(BLOCKED_FILE, 'r').close() 
    except: pass
    
    for _ in range(ITERATIONS):
        start = time.perf_counter_ns()
        try:
            with open(BLOCKED_FILE, 'r') as f:
                _ = f.read(1)
        except PermissionError:
            end = time.perf_counter_ns()
            latencies.append((end - start) / 1e3) # microseconds
        except Exception:
            pass # Ignore other errors
            
    return np.array(latencies)

def stress_cpu_io():
    """Generates synthetic load"""
    end_time = time.time() + 5
    while time.time() < end_time:
        _ = [x**2 for x in range(500)]
        if os.path.exists("/tmp"):
             try:
                 with open("/tmp/sentinel_bench_io", "w") as f:
                     f.write("x" * 1024)
             except: pass

def run_benchmark():
    print(f"🚀 Sentinel Cortex v2.0 - Final System Verification (N={ITERATIONS})")
    print("=" * 60)
    
    # 1. Resource Baseline
    metrics_run_1 = get_relay_metrics()
    
    # 2. Latency (Idle)
    print("\n[TEST 1] Process Latency (Idle)...")
    lat_process = measure_process_latency()
    
    print("\n[TEST 2] TTE Enforcement (Idle)...")
    lat_tte = measure_tte_enforcement()
    
    # 3. Load Test
    print("\n[TEST 3] Measurements under STRESS (CPU+IO)...")
    stress_thread = threading.Thread(target=stress_cpu_io)
    stress_thread.start()
    
    # Measure while stressing
    lat_process_load = measure_process_latency()
    lat_tte_load = measure_tte_enforcement()
    
    stress_thread.join()
    metrics_run_2 = get_relay_metrics()
    
    # Report Generation
    print("\n📊 FINAL RESULTS TABLE")
    print("-" * 60)
    print(f"{'METRIC':<30} | {'IDLE (Avg)':<12} | {'STRESS (Avg)':<12} | {'STRESS (P95)':<12}")
    print("-" * 60)
    
    # Process Execution
    print(f"{'Exec Process (/bin/true)':<30} | {np.mean(lat_process):.2f} ms     | {np.mean(lat_process_load):.2f} ms     | {np.percentile(lat_process_load, 95):.2f} ms")
    
    # TTE
    print(f"{'TTE (Block /etc/shadow)':<30} | {np.mean(lat_tte):.2f} us     | {np.mean(lat_tte_load):.2f} us     | {np.percentile(lat_tte_load, 95):.2f} us")
    
    print("-" * 60)
    print("📈 RESOURCE USAGE (sentinel_relay)")
    print(f"   CPU Usage : {metrics_run_2['cpu']}%")
    print(f"   RAM Usage : {metrics_run_2['ram_mb']:.2f} MB")
    
    # Contextual Interpretation
    overhead_est = np.mean(lat_process) - S60(1, 0, 0) # Assuming ~1ms baseline for typical Linux exec
    print("\n🔎 ANALYSIS:")
    print(f"   - Estimated LSM Overhead per Exec: ~{overhead_est:.2f} ms")
    print(f"   - Security Blocking Speed (TTE): {np.mean(lat_tte_load):.2f} μs")
    print(f"   - Stability: {abs(np.mean(lat_tte) - np.mean(lat_tte_load)):.2f} μs jitter under load")

if __name__ == "__main__":
    run_benchmark()
