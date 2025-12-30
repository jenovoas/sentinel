import asyncio
import aiohttp
import time
import statistics

URL = "http://localhost:8001/verify"
CONCURRENT_REQUESTS = 50
TOTAL_REQUESTS = 1000

TEST_PAYLOAD = {
    "text": "The unemployment rate is 3.5% according to the Bureau of Labor Statistics. The sky is blue. I think it is nice."
}

async def send_request(session):
    start = time.perf_counter()
    async with session.post(URL, json=TEST_PAYLOAD) as response:
        result = await response.json()
        latency = (time.perf_counter() - start) * 1000 # ms
        return latency, result["cache_hit"]

async def main():
    print(f"🚀 Starting TruthSync Load Test...")
    print(f"Target: {URL}")
    print(f"Requests: {TOTAL_REQUESTS}, Concurrency: {CONCURRENT_REQUESTS}")

    latencies = []
    cache_hits = 0

    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(TOTAL_REQUESTS):
            tasks.append(send_request(session))
            if len(tasks) >= CONCURRENT_REQUESTS:
                results = await asyncio.gather(*tasks)
                for latency, hit in results:
                    latencies.append(latency)
                    if hit:
                        cache_hits += 1
                tasks = []
        
        if tasks:
            results = await asyncio.gather(*tasks)
            for latency, hit in results:
                latencies.append(latency)
                if hit:
                    cache_hits += 1

    avg_latency = statistics.mean(latencies)
    p99_latency = statistics.quantiles(latencies, n=100)[98]
    tps = TOTAL_REQUESTS / (sum(latencies) / 1000 / CONCURRENT_REQUESTS) # Rough estimation

    print("\n--- Results ---")
    print(f"Total Requests: {TOTAL_REQUESTS}")
    print(f"Cache Hit Rate: {(cache_hits/TOTAL_REQUESTS)*100:.1f}%")
    print(f"Avg Latency: {avg_latency:.2f} ms")
    print(f"P99 Latency: {p99_latency:.2f} ms")
    # print(f"Est. Throughput: {TOTAL_REQUESTS / (max(latencies)/1000):.2f} req/s")

if __name__ == "__main__":
    asyncio.run(main())
