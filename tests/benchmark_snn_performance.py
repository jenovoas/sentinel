# tests/benchmark_snn_performance.py
import sys
import os
import time
import statistics

# Adjust path to find src module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.sentinel_core.brain.snn_core import AkashicLIFNeuron

def benchmark_interaction():
    print("🚀 [Bench] Starting Akashic SNN Benchmark...")
    
    # Initialize Neuron
    neuron = AkashicLIFNeuron(neuron_id="BENCH_01", tau=8.0, threshold=1.2)
    
    iterations = 1_000_000
    start_time = time.perf_counter()
    
    for _ in range(iterations):
        # Simulate a low-threat stimulus (LEAK scenario)
        neuron.step(input_current=0.1, genetic_bias=0.0)
        
    end_time = time.perf_counter()
    duration = end_time - start_time
    ops_per_sec = iterations / duration
    latency_ns = (duration / iterations) * 1e9
    
    print(f"📊 [Result] Processed {iterations:,} stimuli in {duration:.4f}s")
    print(f"   -> Throughput: {ops_per_sec:,.2f} ops/sec")
    print(f"   -> Latency: {latency_ns:.2f} ns/op")
    
    # Validation against budget
    print("-" * 40)
    print("Checking against Ring 0 budget (10,000 ns/op)...")
    if latency_ns < 10000:
        print("✅ PASS: Performance is suitable for high-frequency kernel loops.")
    else:
        print("❌ FAIL: Too slow for kernel integration.")

if __name__ == "__main__":
    benchmark_interaction()
