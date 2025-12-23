#!/usr/bin/env python3
"""
Guardian-Alpha LSM - Advanced Performance Analysis
Measures syscall interception overhead with statistical analysis
"""

import subprocess
import time
import statistics
import json
from pathlib import Path

ITERATIONS = 1000
TEST_BINARY = "/bin/true"

def run_benchmark(iterations: int) -> list[float]:
    """Run benchmark and return list of execution times in nanoseconds"""
    times = []
    
    # Warm up
    for _ in range(10):
        subprocess.run([TEST_BINARY], capture_output=True)
    
    # Actual benchmark
    for _ in range(iterations):
        start = time.perf_counter_ns()
        subprocess.run([TEST_BINARY], capture_output=True)
        end = time.perf_counter_ns()
        times.append(end - start)
    
    return times

def check_lsm_loaded() -> bool:
    """Check if Guardian-Alpha LSM is loaded"""
    try:
        result = subprocess.run(
            ["sudo", "bpftool", "prog", "show"],
            capture_output=True,
            text=True
        )
        return "guardian" in result.stdout.lower()
    except:
        return False

def get_kernel_events() -> int:
    """Count Guardian-Alpha events in kernel log"""
    try:
        result = subprocess.run(
            ["sudo", "dmesg"],
            capture_output=True,
            text=True
        )
        return result.stdout.lower().count("guardian-alpha")
    except:
        return 0

def main():
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║  Guardian-Alpha LSM - Advanced Performance Analysis      ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()
    
    lsm_loaded = check_lsm_loaded()
    
    if lsm_loaded:
        print("✅ Guardian-Alpha LSM is loaded")
    else:
        print("⚠️  Guardian-Alpha LSM is NOT loaded")
        print("   Run: sudo ./load.sh")
        return
    
    print(f"\nConfiguration:")
    print(f"  Iterations: {ITERATIONS}")
    print(f"  Test binary: {TEST_BINARY}")
    print()
    
    print("Running benchmark...")
    times = run_benchmark(ITERATIONS)
    
    # Convert to microseconds for readability
    times_us = [t / 1000 for t in times]
    
    # Statistical analysis
    mean = statistics.mean(times_us)
    median = statistics.median(times_us)
    stdev = statistics.stdev(times_us)
    min_time = min(times_us)
    max_time = max(times_us)
    
    # Percentiles
    p50 = statistics.median(times_us)
    p95 = statistics.quantiles(times_us, n=20)[18]  # 95th percentile
    p99 = statistics.quantiles(times_us, n=100)[98]  # 99th percentile
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print()
    print(f"Executions: {ITERATIONS}")
    print()
    print(f"Mean:       {mean:.2f} μs")
    print(f"Median:     {median:.2f} μs")
    print(f"Std Dev:    {stdev:.2f} μs")
    print(f"Min:        {min_time:.2f} μs")
    print(f"Max:        {max_time:.2f} μs")
    print()
    print(f"P50:        {p50:.2f} μs")
    print(f"P95:        {p95:.2f} μs")
    print(f"P99:        {p99:.2f} μs")
    print()
    
    # Overhead estimation (typical baseline ~75μs)
    typical_baseline = 75.0
    overhead = mean - typical_baseline
    overhead_pct = (overhead / typical_baseline) * 100
    
    print(f"Estimated overhead: {overhead:.2f} μs ({overhead_pct:.1f}%)")
    
    if overhead < 10:
        print("✅ Excellent: < 10μs overhead")
    elif overhead < 100:
        print("✅ Good: < 100μs overhead")
    elif overhead < 1000:
        print("⚠️  Moderate: < 1ms overhead")
    else:
        print("⚠️  High: > 1ms overhead")
    
    # Kernel events
    events = get_kernel_events()
    print(f"\nKernel events logged: {events}")
    
    # Save results
    results = {
        "timestamp": time.time(),
        "iterations": ITERATIONS,
        "lsm_loaded": lsm_loaded,
        "statistics": {
            "mean_us": mean,
            "median_us": median,
            "stdev_us": stdev,
            "min_us": min_time,
            "max_us": max_time,
            "p50_us": p50,
            "p95_us": p95,
            "p99_us": p99
        },
        "overhead": {
            "estimated_us": overhead,
            "estimated_pct": overhead_pct
        },
        "kernel_events": events
    }
    
    output_file = Path("benchmark_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_file}")

if __name__ == "__main__":
    main()
