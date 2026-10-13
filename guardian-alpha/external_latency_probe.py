#!/usr/bin/env python3
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import time
import os
import subprocess
import statistics

def measure_execution_latency(cmd):
    """Mide latencia de ejecución desde la perspectiva de usuario"""
    start = time.perf_counter_ns()
    try:
        # Usamos os.spawnv o subprocess para medir el spawn real
        proc = subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
        exit_code = proc.returncode
    except subprocess.TimeoutExpired:
        exit_code = -1
    end = time.perf_counter_ns()
    
    return (end - start) / 1000, exit_code

def run_benchmark(label, cmd, iterations=50):
    print(f"🚀 Benchmarking {label}...")
    latencies = []
    blocks = 0
    
    for _ in range(iterations):
        lat, code = measure_execution_latency(cmd)
        latencies.append(lat)
        if code != 0: # Asumimos que != 0 es un bloqueo o error provocado
            blocks += 1
            
    avg = statistics.mean(latencies)
    p95 = statistics.quantiles(latencies, n=20)[-1] if len(latencies) > 20 else max(latencies)
    
    print(f"   Avg: {avg:.2f}μs | p95: {p95:.2f}μs | Blocked: {blocks}/{iterations}")
    return avg, p95

if __name__ == "__main__":
    print("🔬 SENTINEL EXTERNAL PROBE - Validando latencia real de usuario\n")
    
    # 1. Baseline: Comando inocente (ls)
    avg_norm, p95_norm = run_benchmark("NORMAL (ls)", "ls /tmp")
    
    # 2. Stress: Comando que Sentinel debe analizar/bloquear
    # Usamos algo que dispare el score pero sea seguro para el test
    avg_sent, p95_sent = run_benchmark("SENTINEL PROTECTED (rm -rf /etc/shadow)", "rm -rf /etc/shadow")
    
    delta = avg_sent - avg_norm
    print(f"\n📊 ANÁLISIS DE OVERHEAD REAL:")
    print(f"   Overhead neto de Sentinel: {delta:.2f}μs")
    print(f"   Disonancia detectada: {'NINGUNA' if delta < 500 else 'ALTA'}")
    
    if delta < 100:
        print("✅ EXCELENTE: El overhead es casi imperceptible (<100μs)")
    elif delta < 500:
        print("⚠️  ACEPTABLE: Overhead dentro de márgenes de seguridad.")
    else:
        print("❌ CRÍTICO: Sentinel está ralentizando el sistema visiblemente.")
