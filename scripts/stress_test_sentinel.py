#!/usr/bin/env python3
"""
Batería de Pruebas de Estrés y Carga Concurrente para Sentinel Cortex (S60)
========================================================================
Puntos de Prueba:
  1. POST /api/v1/truth_claim (Verificación de Invariant / TruthSync)
  2. GET  /metrics (Exporter de Prometheus & Capa PAI-Neural SNN)
  3. POST /api/v1/truth_claim (AIOpsShield Interception under High Load)

Métricas Calculadas:
  - Latencia P50, P95, P99
  - Requests / segundo (Throughput RPS)
  - Tasa de Error / Rechazo
"""

import time
import json
import argparse
import urllib.request
import urllib.error
import concurrent.futures

TARGET_URL = "http://10.88.0.1:8000"

def send_truth_claim_req(engine_id, payload):
    url = f"{TARGET_URL}/api/v1/truth_claim"
    body = json.dumps({
        "engine": f"stress_worker_{engine_id}",
        "claim_payload": payload,
        "trust_threshold": 0.85
    }).encode("utf-8")
    
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"}
    )
    
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            status = resp.status
            data = resp.read()
            dt_us = (time.perf_counter() - t0) * 1_000_000
            return status == 200, dt_us, len(data)
    except Exception as e:
        dt_us = (time.perf_counter() - t0) * 1_000_000
        return False, dt_us, 0

def run_stress_suite(concurrency=50, total_requests=1000):
    print(f"🚀 Iniciando Batería de Estrés Sentinel Cortex ({total_requests} reqs | Concurrencia: {concurrency})...")
    
    payloads = [
        "Plimpton 322 sexagesimal constant ratio verification test",
        "LiquidLattice 3x3 fluid diffusion step check",
        "rm -rf /sys/fs/bpf/cortex_events", # Trigger AIOpsShield Interception
        "Normal AI claim payload verification"
    ]
    
    latencies = []
    successes = 0
    failures = 0
    
    t_start = time.perf_counter()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = []
        for i in range(total_requests):
            payload = payloads[i % len(payloads)]
            futures.append(executor.submit(send_truth_claim_req, i % concurrency, payload))
            
        for f in concurrent.futures.as_completed(futures):
            ok, latency_us, _ = f.result()
            latencies.append(latency_us)
            if ok:
                successes += 1
            else:
                failures += 1
                
    total_time_s = time.perf_counter() - t_start
    rps = total_requests / total_time_s
    
    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.50)] / 1000.0
    p95 = latencies[int(len(latencies) * 0.95)] / 1000.0
    p99 = latencies[int(len(latencies) * 0.99)] / 1000.0
    
    print("\n=======================================================")
    print("📊 RESULTADOS DE LA PRUEBA DE ESTRÉS SENTINEL S60")
    print("=======================================================")
    print(f"⏱️  Tiempo Total Ejecución: {total_time_s:.3f} s")
    print(f"⚡ Throughput Obtenido:    {rps:.2f} req/s")
    print(f"✅ Exitosas (HTTP 200):     {successes} ({successes/total_requests*100:.1f}%)")
    print(f"❌ Fallidas / Rehusadas:    {failures}")
    print(f"📈 Latencia P50 (Mediana):  {p50:.2f} ms")
    print(f"📈 Latencia P95:            {p95:.2f} ms")
    print(f"📈 Latencia P99:            {p99:.2f} ms")
    print("=======================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sentinel Stress Test Suite")
    parser.add_argument("-c", "--concurrency", type=int, default=50, help="Número de hilos concurrentes")
    parser.add_argument("-n", "--requests", type=int, default=1000, help="Total de peticiones a realizar")
    args = parser.parse_args()
    
    run_stress_suite(concurrency=args.concurrency, total_requests=args.requests)
