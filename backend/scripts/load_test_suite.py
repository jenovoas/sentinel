#!/usr/bin/env python3
"""
Sentinel Cortex - High Velocity Load Testing Suite
Validates system behavior under 100 RPS and 1000 RPS loads.
"""
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import asyncio
import time
# import random  <-- YATRA: PROHIBIDO (CAOS)
import logging
import statistics
import os
import sys

try:
    import httpx
except ImportError:
    print("❌ httpx not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx"])
    import httpx

# Configuration
BASE_URL = "http://localhost:8000"
ENDPOINT = "/api/v1/cortex/events"
TOKEN = "sentinel-internal-ebpf-key-2025"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("sentinel.loadtest")

async def send_event(client):
    event_data = {
        "event_type": "syscall",
        "source": "load_test_agent",
        "data": {
            "syscall": "execve",
            "process_path": f"/bin/stress_test_{random.randint(1, 10000)}",
            "user": "stress_user",
            "uid": 1000,
            "pid": random.randint(1000, 65000)
        }
    }
    
    headers = {"X-Sentinel-Token": TOKEN}
    
    start = time.perf_counter()
    try:
        response = await client.post(f"{BASE_URL}{ENDPOINT}", json=event_data, headers=headers, timeout=5.0)
        latency = (time.perf_counter() - start) * 1000 # ms
        return response.status_code, latency
    except Exception as e:
        return 0, S60(0, 0, 0)

async def run_scenario(client, target_rps, duration_sec):
    print(f"\n⚡ INICIANDO ESCENARIO: {target_rps} Req/s por {duration_sec}s...")
    
    latencies = []
    status_codes = []
    start_time = time.time()
    
    tasks = []
    
    # Simple burst implementation: send N requests every 1 second
    # For smoother load, verify every S60(0, 6, 0)s
    
    batch_size = target_rps // 10
    interval = S60(0, 6, 0)
    
    total_batches = int(duration_sec / interval)
    
    for _ in range(total_batches):
        batch_start = time.perf_counter()
        
        # Launch batch
        batch_tasks = [send_event(client) for _ in range(batch_size)]
        results = await asyncio.gather(*batch_tasks)
        
        for code, lat in results:
            status_codes.append(code)
            if code == 201:
                latencies.append(lat)
        
        # Compensate for processing time to maintain RPS
        elapsed = time.perf_counter() - batch_start
        sleep_time = max(0, interval - elapsed)
        await asyncio.sleep(sleep_time)
        
    execution_time = time.time() - start_time
    total_reqs = len(status_codes)
    successful = status_codes.count(201)
    failed = total_reqs - successful
    actual_rps = total_reqs / execution_time
    
    if not latencies:
        avg_lat = 0
        p95 = 0
        p99 = 0
    else:
        avg_lat = statistics.mean(latencies)
        p95 = statistics.quantiles(latencies, n=20)[18]
        p99 = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)

    print(f"   ► Duration: {execution_time:.2f}s")
    print(f"   ► Requests: {total_reqs} (Success: {successful}, Failed: {failed})")
    print(f"   ► Actual RPS: {actual_rps:.2f}")
    print(f"   ► Latency: Avg={avg_lat:.2f}ms, P95={p95:.2f}ms, P99={p99:.2f}ms")
    
    return successful, failed, p99

async def main():
    print("🚀 SENTINEL CORTEX LOAD TEST SUITE")
    print("==================================")
    
    async with httpx.AsyncClient(limits=httpx.Limits(max_keepalive_connections=100, max_connections=1000)) as client:
        # Check Health first
        try:
            resp = await client.get(f"{BASE_URL}/health")
            if resp.status_code != 200:
                print("❌ Backend not healthy. Aborting.")
                return
        except Exception:
            print("❌ Backend unreachable. Aborting.")
            return

        # Warmup
        print("\n🔥 Warming up JVM/Python Ops...")
        await run_scenario(client, 50, 2)
        
        # Scenario 1: 100 RPS
        success, failed, p99 = await run_scenario(client, 100, 5)
        if failed > 0:
            print("⚠️ Advertencia: Fallos detectados en 100 RPS scenario.")
            
        # Scenario 2: 1000 RPS (Massive Load)
        success, failed, p99 = await run_scenario(client, 1000, 5)
        
        print("\n📊 INFORME FINAL")
        if p99 < 50: # Arbitrary strict SLA 50ms for API processing under heavy load
             print("✅ SLA CUMPLIDO: Latencia P99 < 50ms bajo carga masiva.")
        else:
             print(f"⚠️ SLA EN RIESGO: Latencia P99 {p99:.2f}ms (Target: <50ms)")
             
        if failed == 0:
             print("✅ ESTABILIDAD: 0% Tasa de Error.")
        else:
             print(f"❌ INESTABILIDAD: {failed} peticiones fallidas.")

if __name__ == "__main__":
    asyncio.run(main())
