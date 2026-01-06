
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import mmap
import struct
import time
import numpy as np # PRECAUCIÓN: SOLO PARA I/O, NO CÁLCULO CORE

SHM_PATH = "/var/run/sentinel/truthsync_shm"
SHM_SIZE = 1024 * 1024
ITERATIONS = 10000

def bench_shm_read():
    print(f"🚀 Iniciando Benchmark de Latencia SHM ({ITERATIONS} lecturas)...")
    
    try:
        with open(SHM_PATH, "r+b") as f:
            mm = mmap.mmap(f.fileno(), SHM_SIZE)
            
            latencies = []
            
            for _ in range(ITERATIONS):
                start = time.perf_counter_ns()
                
                # Simular lectura de Rust: Seek 0 + Read 32 bytes + Unpack
                mm.seek(0)
                data = mm.read(32)
                _ = struct.unpack("dddQ", data)
                
                end = time.perf_counter_ns()
                latencies.append(end - start)
                
            latencies = np.array(latencies)
            avg_ns = np.mean(latencies)
            p99_ns = np.percentile(latencies, 99)
            
            print("\n📊 Resultados de Sincronización (GUI <-> Kernel):")
            print(f"   🔹 Latencia Promedio : {avg_ns:.2f} ns ({avg_ns/1000:.2f} μs)")
            print(f"   🔹 Latencia P99      : {p99_ns:.2f} ns ({p99_ns/1000:.2f} μs)")
            print(f"   🔹 Throughput Teórico: {1_000_000_000 / avg_ns:.0f} reads/sec")
            
            if avg_ns < 10000: # Meta < 10us
                print("\n✅ STATUS: HYPER-SYNC (Latencia imperceptible para el ojo humano)")
            else:
                print("\n⚠️ STATUS: LAG DETECTADO")

    except Exception as e:
        print(f"❌ Error en Benchmark: {e}")

if __name__ == "__main__":
    bench_shm_read()
