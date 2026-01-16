"""
Ollama GPU Benchmark Suite
Comprehensive performance testing for GPU-accelerated inference
"""

import asyncio
import time
import json
import subprocess
from dataclasses import dataclass, asdict
from typing import List, Dict
from pathlib import Path
import httpx
import statistics


@dataclass
class BenchmarkResult:
    """Single benchmark result"""
    model: str
    prompt_tokens: int
    latency_p50: float
    latency_p95: float
    latency_p99: float
    vram_usage_mb: int
    throughput_tokens_per_sec: float
    concurrent_requests: int


def get_vram_usage() -> int:
    """Get current VRAM usage in MB"""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            check=True
        )
        return int(result.stdout.strip())
    except:
        return 0


async def bench_single_request(model: str, prompt: str) -> float:
    """Benchmark a single request, return latency in seconds"""
    start = time.time()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Request failed: {response.status_code}")
    
    return time.time() - start


async def bench_model(
    model: str,
    prompt_size: int,
    n_requests: int = 10,
    concurrent: int = 1
) -> BenchmarkResult:
    """Benchmark a model with specific prompt size"""
    
    # Generate prompt of specific size (approx)
    prompt = "Count: " + " ".join(str(i) for i in range(prompt_size // 2))
    
    print(f"\n📊 Benchmarking {model} (prompt_size={prompt_size}, concurrent={concurrent})")
    
    latencies = []
    
    # Run requests
    for batch in range(0, n_requests, concurrent):
        batch_size = min(concurrent, n_requests - batch)
        tasks = [bench_single_request(model, prompt) for _ in range(batch_size)]
        batch_latencies = await asyncio.gather(*tasks)
        latencies.extend(batch_latencies)
        
        print(f"  Progress: {len(latencies)}/{n_requests} requests")
    
    # Calculate statistics
    latencies.sort()
    p50 = statistics.median(latencies)
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    
    # Estimate throughput
    total_time = sum(latencies)
    throughput = (n_requests * prompt_size) / total_time if total_time > 0 else 0
    
    # Get VRAM usage
    vram = get_vram_usage()
    
    result = BenchmarkResult(
        model=model,
        prompt_tokens=prompt_size,
        latency_p50=p50,
        latency_p95=p95,
        latency_p99=p99,
        vram_usage_mb=vram,
        throughput_tokens_per_sec=throughput,
        concurrent_requests=concurrent
    )
    
    print(f"  ✅ p50={p50:.2f}s, p95={p95:.2f}s, VRAM={vram}MB")
    
    return result


async def bench_cpu_vs_gpu():
    """Compare CPU vs GPU performance"""
    print("\n" + "="*60)
    print("CPU vs GPU Comparison")
    print("="*60)
    
    # Note: This requires stopping Ollama and restarting without GPU
    # For now, we'll just document GPU performance
    print("⚠️  CPU benchmark requires manual Ollama restart without GPU")
    print("    Current results are GPU-only")
    
    return await bench_model("llama3.2:3b", prompt_size=50, n_requests=5)


async def bench_models():
    """Compare different models"""
    print("\n" + "="*60)
    print("Model Comparison")
    print("="*60)
    
    models = ["llama3.2:1b", "llama3.2:3b"]
    results = []
    
    for model in models:
        try:
            result = await bench_model(model, prompt_size=50, n_requests=5)
            results.append(result)
        except Exception as e:
            print(f"  ❌ {model} failed: {e}")
    
    return results


async def bench_prompt_sizes():
    """Test different prompt sizes"""
    print("\n" + "="*60)
    print("Prompt Size Scaling")
    print("="*60)
    
    sizes = [10, 50, 100, 200]
    results = []
    
    for size in sizes:
        result = await bench_model("llama3.2:3b", prompt_size=size, n_requests=5)
        results.append(result)
    
    return results


async def bench_concurrency():
    """Test concurrent requests"""
    print("\n" + "="*60)
    print("Concurrency Test")
    print("="*60)
    
    concurrency_levels = [1, 2, 5, 10]
    results = []
    
    for concurrent in concurrency_levels:
        result = await bench_model(
            "llama3.2:3b",
            prompt_size=50,
            n_requests=10,
            concurrent=concurrent
        )
        results.append(result)
    
    return results


async def run_all_benchmarks():
    """Run complete benchmark suite"""
    print("\n🚀 Starting Ollama GPU Benchmark Suite")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = {
        "timestamp": time.time(),
        "gpu_info": {},
        "benchmarks": {}
    }
    
    # Get GPU info
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            check=True
        )
        gpu_name, vram_total, driver = result.stdout.strip().split(", ")
        all_results["gpu_info"] = {
            "name": gpu_name,
            "vram_total_mb": vram_total,
            "driver": driver
        }
        print(f"\n🎮 GPU: {gpu_name} ({vram_total})")
    except:
        print("\n⚠️  Could not detect GPU")
    
    # Run benchmarks
    all_results["benchmarks"]["cpu_vs_gpu"] = asdict(await bench_cpu_vs_gpu())
    all_results["benchmarks"]["models"] = [asdict(r) for r in await bench_models()]
    all_results["benchmarks"]["prompt_sizes"] = [asdict(r) for r in await bench_prompt_sizes()]
    all_results["benchmarks"]["concurrency"] = [asdict(r) for r in await bench_concurrency()]
    
    return all_results


def save_results(results: Dict, output_file: str = "benchmark_results.json"):
    """Save results to JSON file"""
    output_path = Path(output_file)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to: {output_path.absolute()}")


def print_summary(results: Dict):
    """Print summary of results"""
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    
    if "gpu_info" in results:
        gpu = results["gpu_info"]
        print(f"\n🎮 GPU: {gpu.get('name', 'Unknown')}")
        print(f"   VRAM: {gpu.get('vram_total_mb', 'Unknown')}")
        print(f"   Driver: {gpu.get('driver', 'Unknown')}")
    
    # Model comparison
    if "models" in results["benchmarks"]:
        print("\n📊 Model Comparison (50 tokens):")
        for result in results["benchmarks"]["models"]:
            print(f"   {result['model']:15} p50={result['latency_p50']:.2f}s  VRAM={result['vram_usage_mb']}MB")
    
    # Concurrency
    if "concurrency" in results["benchmarks"]:
        print("\n⚡ Concurrency Performance:")
        for result in results["benchmarks"]["concurrency"]:
            print(f"   {result['concurrent_requests']:2}x concurrent: p50={result['latency_p50']:.2f}s")
    
    print("\n" + "="*60)


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ollama GPU Benchmark Suite")
    parser.add_argument("--output", default="benchmark_results.json", help="Output JSON file")
    parser.add_argument("--quick", action="store_true", help="Quick benchmark (fewer requests)")
    args = parser.parse_args()
    
    try:
        results = await run_all_benchmarks()
        save_results(results, args.output)
        print_summary(results)
        
        print("\n✅ Benchmark complete!")
        print(f"\n📈 To visualize results:")
        print(f"   python -m json.tool {args.output}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Benchmark failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
