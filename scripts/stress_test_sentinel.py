#!/usr/bin/env python3
"""
Batería de Pruebas de Estrés y Carga Concurrente para Sentinel Cortex (S60)
========================================================================
Puntos de Prueba:
  1. POST /api/v1/truth_claim (Verificación de Invariante / TruthSync)
  2. POST /api/v1/truth_claim (Intercepción AIOpsShield bajo alta carga)
  3. GET  /metrics (Monitoreo de LiquidLattice retention_score y energía)

Métricas Calculadas:
  - Latencia P50, P95, P99
  - Requests / segundo (Throughput RPS)
  - Tasa de Verificación Benigna vs Bloqueo AIOpsShield vs Errores
  - LiquidLattice retention_score antes y después de la carga
"""

import argparse
import concurrent.futures
import json
import os
import re
import time
import urllib.error
import urllib.request

TARGET_URL = os.environ.get("CORTEX_URL", "http://127.0.0.1:8000")
AUTH_TOKEN = os.environ.get("CORTEX_AUTH_TOKEN", "")


def fetch_liquid_lattice_metrics():
    """Lee métricas de LiquidLattice desde /metrics"""
    try:
        url = f"{TARGET_URL}/metrics"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3) as resp:
            text = resp.read().decode("utf-8")
            retention_match = re.search(r"sentinel_liquid_lattice_retention_score\s+([0-9.]+)", text)
            energy_match = re.search(r"sentinel_lattice_total_energy\s+([0-9.]+)", text)
            retention = float(retention_match.group(1)) if retention_match else None
            energy = float(energy_match.group(1)) if energy_match else None
            return retention, energy
    except Exception as e:
        return None, None


def send_truth_claim_req(engine_id, payload, token=None):
    url = f"{TARGET_URL}/api/v1/truth_claim"
    body = json.dumps({
        "engine": f"stress_worker_{engine_id}",
        "claim_payload": payload,
        "trust_threshold": 0.85
    }).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    bearer = token or AUTH_TOKEN
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"

    req = urllib.request.Request(url, data=body, headers=headers)

    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            dt_us = (time.perf_counter() - t0) * 1_000_000
            return ("allowed", dt_us, resp.status)
    except urllib.error.HTTPError as e:
        dt_us = (time.perf_counter() - t0) * 1_000_000
        if e.code == 403:
            return ("blocked", dt_us, 403)
        return ("error", dt_us, e.code)
    except Exception as e:
        dt_us = (time.perf_counter() - t0) * 1_000_000
        return ("error", dt_us, 500)


def run_stress_suite(concurrency=50, total_requests=1000, token=None):
    print(f"🚀 Iniciando Batería de Carga Concurrente Sentinel Cortex ({total_requests} reqs | Concurrencia: {concurrency})...")

    ret_initial, energy_initial = fetch_liquid_lattice_metrics()
    print(f"💧 LiquidLattice Estado Inicial: retention_score = {ret_initial}, energía = {energy_initial}")

    payloads = [
        "Plimpton 322 sexagesimal constant ratio verification test",
        "LiquidLattice 3x3 fluid diffusion step check",
        "rm -rf /sys/fs/bpf/cortex_events",  # Trigger AIOpsShield Interception
        "Normal AI claim payload verification",
        "DROP TABLE audit_logs; --",        # Trigger SQL injection defense
    ]

    latencies = []
    allowed_count = 0
    blocked_count = 0
    error_count = 0

    t_start = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = []
        for i in range(total_requests):
            payload = payloads[i % len(payloads)]
            futures.append(executor.submit(send_truth_claim_req, i % concurrency, payload, token))

        for f in concurrent.futures.as_completed(futures):
            outcome, latency_us, status = f.result()
            latencies.append(latency_us)
            if outcome == "allowed":
                allowed_count += 1
            elif outcome == "blocked":
                blocked_count += 1
            else:
                error_count += 1

    total_time_s = time.perf_counter() - t_start
    rps = total_requests / total_time_s

    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.50)] / 1000.0
    p95 = latencies[int(len(latencies) * 0.95)] / 1000.0
    p99 = latencies[int(len(latencies) * 0.99)] / 1000.0

    ret_final, energy_final = fetch_liquid_lattice_metrics()

    print("\n=======================================================")
    print("📊 RESULTADOS DE LA BATERÍA DE CARGA SENTINEL S60")
    print("=======================================================")
    print(f"⏱️  Tiempo Total Ejecución    : {total_time_s:.3f} s")
    print(f"⚡ Throughput Obtenido       : {rps:.2f} req/s")
    print(f"✅ Reclamaciones Permitidas  : {allowed_count} ({allowed_count/total_requests*100:.1f}%)")
    print(f"🛡️  Ataques Bloqueados (403) : {blocked_count} ({blocked_count/total_requests*100:.1f}%)")
    print(f"❌ Errores Inesperados (5xx) : {error_count}")
    print(f"📈 Latencia P50 (Mediana)    : {p50:.2f} ms")
    print(f"📈 Latencia P95              : {p95:.2f} ms")
    print(f"📈 Latencia P99              : {p99:.2f} ms")
    print("───────────────────────────────────────────────────────")
    print(f"💧 LiquidLattice retention_score Final : {ret_final} (Meta >= 0.72)")
    print(f"⚡ LiquidLattice Energía Final         : {energy_final}")
    print("=======================================================\n")

    if ret_final is not None and ret_final >= 0.72 and error_count == 0:
        print("🎉 CRITERIO CUMPLIDO: retention_score >= 0.72 bajo carga concurrente sin fallos.")
    else:
        print("⚠️ Verificar métricas o estabilidad de LiquidLattice.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sentinel Stress Test Suite")
    parser.add_argument("-c", "--concurrency", type=int, default=50, help="Número de hilos concurrentes")
    parser.add_argument("-n", "--requests", type=int, default=1000, help="Total de peticiones a realizar")
    parser.add_argument("-t", "--token", type=str, default=None, help="Token JWT Bearer si es requerido")
    args = parser.parse_args()

    run_stress_suite(concurrency=args.concurrency, total_requests=args.requests, token=args.token)
