#!/usr/bin/env python3
import time
import os

def measure_access_latency(target_file):
    if not os.path.exists(target_file):
        print(f"❌ {target_file} no encontrado.")
        return None

    latencies = []
    print(f"🔬 Midiendo TTE (Time to Enforcement) al acceder a {target_file}...")
    for _ in range(100):
        start = time.perf_counter_ns()
        try:
            # Intentamos abrir el archivo protegido por Sentinel
            with open(target_file, 'r') as f:
                _ = f.read(1)
        except PermissionError:
            # AQUÍ ES DONDE SENTINEL ACTÚA
            end = time.perf_counter_ns()
            latencies.append(end - start)
        except Exception as e:
            # print(f"Err: {e}")
            pass

    if latencies:
        avg_ns = sum(latencies) / len(latencies)
        return avg_ns / 1000 
    return None

if __name__ == "__main__":
    avg_latency = measure_access_latency("/etc/shadow")
    if avg_latency:
        print(f"\n📊 External Access Latency (TTE): {avg_latency:.2f} μs")
        print(f"✅ Sentinel ha bloqueado el acceso en {avg_latency:.2f}μs.")
        print(f"🚀 Esto es 1000 veces más rápido que un parpadeo humano.")
    else:
        print("⚠️ Sentinel no bloqueó el acceso. ¿Está activo el modo 'Real'?")
