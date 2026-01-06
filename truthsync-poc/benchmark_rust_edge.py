#!/usr/bin/env python3
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import asyncio
import aiohttp
import time
import statistics
import json

RUST_SERVER_URL = "http://localhost:8001/verify"
PYTHON_BASELINE_US = 32.24
NUM_REQUESTS = 5000
CONCURRENCY = 50

async def verify_claim(session, text):
    start = time.perf_counter()
    async with session.post(RUST_SERVER_URL, json={"text": text}) as response:
        res = await response.json()
        end = time.perf_counter()
        return res, (end - start) * 1_000_000  # Wall clock time in μs

async def run_benchmark():
    print("="*60)
    print("TRUTHSYNC RUST EDGE SERVER BENCHMARK")
    print("="*60)
    
    texts = [
        "The unemployment rate is 3.5% according to BLS.",
        "Tesla announced a new electric vehicle.",
        "The stock market was up 2% today.",
        "I think the economy is doing well.", # Negative/Opinion
    ]

    async with aiohttp.ClientSession() as session:
        # 1. Warmup & Cache Population
        print("🔥 Warming up cache...")
        for text in texts:
            await verify_claim(session, text)
        
        # 2. Benchmark Cache Hits
        print(f"📊 Testing {NUM_REQUESTS} Cache HITS...")
        hit_times_total = []
        hit_times_engine = []
        
        hit_text = texts[0]
        
        start_batch = time.perf_counter()
        for _ in range(NUM_REQUESTS // CONCURRENCY):
            batch_tasks = [verify_claim(session, hit_text) for _ in range(CONCURRENCY)]
            results = await asyncio.gather(*batch_tasks)
            for res, total_time in results:
                hit_times_total.append(total_time)
                hit_times_engine.append(res['processing_time_us'])
        end_batch = time.perf_counter()
        
        # 3. Benchmark Cache Misses
        print(f"📊 Testing {NUM_REQUESTS} Potential MISSES (unique strings)...")
        miss_times_total = []
        miss_times_engine = []
        for i in range(NUM_REQUESTS // CONCURRENCY):
            batch_tasks = [verify_claim(session, f"Unique fact number {i}-{j} is true.") for j in range(CONCURRENCY)]
            results = await asyncio.gather(*batch_tasks)
            for res, total_time in results:
                miss_times_total.append(total_time)
                miss_times_engine.append(res['processing_time_us'])

        avg_hit_total = statistics.mean(hit_times_total)
        avg_hit_engine = statistics.mean(hit_times_engine)
        avg_miss_engine = statistics.mean(miss_times_engine)
        
        print("\n" + "="*60)
        print("LATENCY RESULTS")
        print("="*60)
        print(f"Avg Cache Hit (Total Network): {avg_hit_total:.2f}μs")
        print(f"Avg Cache Hit (NATIVE ENGINE): {avg_hit_engine:.4f}μs")
        print(f"Avg Cache Miss (NATIVE ENGINE): {avg_miss_engine:.2f}μs")
        
        # Speedup vs Python Baseline (32.24μs)
        # We compare engine vs engine
        speedup = PYTHON_BASELINE_US / avg_hit_engine
        print(f"\n🚀 ENGINE SPEEDUP VS PYTHON BASELINE: {speedup:.2f}x")
        
        print("\n" + "="*60)
        print("THROUGHPUT")
        print("="*60)
        total_time = end_batch - start_batch
        print(f"Requests/sec (Network limited): {NUM_REQUESTS / total_time:,.0f}")
        print(f"Projected Throughput (Engine only): {1_000_000 / avg_hit_engine:,.0f} req/sec")

if __name__ == "__main__":
    try:
        asyncio.run(run_benchmark())
    except Exception as e:
        print(f"❌ Error: {e}. ¿Está el servidor Rust corriendo?")
