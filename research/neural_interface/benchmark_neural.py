#!/usr/bin/env python3
"""
Neural Control - Benchmark Suite

Validates neural entropy control performance.
"""

import sys
sys.path.insert(0, '/home/jnovoas/sentinel')

import time
import random
from research.neural_interface.neural_control import NeuralEntropyController


def generate_neural_pattern(length=100, pattern_type="noisy"):
    """Generate realistic neural spike pattern."""
    pattern = []
    
    if pattern_type == "noisy":
        # Random noise around baseline
        rate = 50.0
        for i in range(length):
            rate += random.uniform(-10, 10)
            rate = max(10.0, min(100.0, rate))
            pattern.append(rate)
    
    elif pattern_type == "burst":
        # Sudden burst of activity
        for i in range(length):
            if 30 <= i <= 50:
                rate = 90.0 + random.uniform(0, 10)
            else:
                rate = 40.0 + random.uniform(-5, 5)
            pattern.append(rate)
    
    elif pattern_type == "oscillating":
        # Periodic oscillations
        for i in range(length):
            rate = 50.0 + 30.0 * (i % 20 - 10) / 10.0
            rate += random.uniform(-5, 5)
            pattern.append(max(10.0, min(100.0, rate)))
    
    return pattern


def benchmark_convergence():
    """Benchmark convergence speed."""
    print("="*70)
    print("BENCHMARK 1: Convergence Speed")
    print("="*70)
    print()
    
    controller = NeuralEntropyController()
    pattern = generate_neural_pattern(100, "noisy")
    
    entropies = []
    
    for t, spike_rate in enumerate(pattern):
        intensity, action = controller.update(spike_rate, float(t))
        
        if len(controller.history) > 0:
            entropies.append(controller.history[-1].entropy)
    
    # Calculate convergence time
    converged = False
    convergence_time = None
    
    for t, entropy in enumerate(entropies):
        if t > 20 and entropy < 0.2:  # Converged threshold
            if not converged:
                convergence_time = t
                converged = True
    
    print(f"Initial entropy: {entropies[0]:.3f}")
    print(f"Final entropy: {entropies[-1]:.3f}")
    print(f"Convergence time: {convergence_time} steps")
    print(f"Reduction: {(1 - entropies[-1]/entropies[0])*100:.1f}%")
    print()


def benchmark_stability():
    """Benchmark stability across patterns."""
    print("="*70)
    print("BENCHMARK 2: Stability Across Patterns")
    print("="*70)
    print()
    
    patterns = {
        'Noisy': 'noisy',
        'Burst': 'burst',
        'Oscillating': 'oscillating'
    }
    
    print(f"{'Pattern':<15} | {'Initial':<8} | {'Final':<8} | {'Reduction':<10}")
    print("-"*70)
    
    for name, pattern_type in patterns.items():
        controller = NeuralEntropyController()
        pattern = generate_neural_pattern(100, pattern_type)
        
        for t, spike_rate in enumerate(pattern):
            controller.update(spike_rate, float(t))
        
        initial = controller.history[0].entropy
        final = controller.history[-1].entropy
        reduction = (1 - final/initial) * 100
        
        print(f"{name:<15} | {initial:8.3f} | {final:8.3f} | {reduction:9.1f}%")
    
    print()


def benchmark_performance():
    """Benchmark execution speed."""
    print("="*70)
    print("BENCHMARK 3: Execution Speed")
    print("="*70)
    print()
    
    controller = NeuralEntropyController()
    pattern = generate_neural_pattern(1000, "noisy")
    
    start = time.time()
    
    for t, spike_rate in enumerate(pattern):
        controller.update(spike_rate, float(t))
    
    elapsed = time.time() - start
    
    print(f"Total steps: 1000")
    print(f"Total time: {elapsed:.3f}s")
    print(f"Time per step: {elapsed/1000*1000:.3f}ms")
    print(f"Throughput: {1000/elapsed:.0f} steps/second")
    print()


def benchmark_statistical():
    """Statistical validation (n=1000)."""
    print("="*70)
    print("BENCHMARK 4: Statistical Validation (n=1000)")
    print("="*70)
    print()
    
    print("Running 1000 random scenarios...")
    print()
    
    reductions = []
    
    start = time.time()
    
    for i in range(1000):
        if (i + 1) % 100 == 0:
            print(f"Progress: {i+1}/1000")
        
        controller = NeuralEntropyController()
        pattern = generate_neural_pattern(50, "noisy")
        
        for t, spike_rate in enumerate(pattern):
            controller.update(spike_rate, float(t))
        
        if len(controller.history) > 1:
            initial = controller.history[0].entropy
            final = controller.history[-1].entropy
            reduction = (1 - final/initial) * 100
            reductions.append(reduction)
    
    elapsed = time.time() - start
    
    # Calculate statistics
    avg_reduction = sum(reductions) / len(reductions)
    min_reduction = min(reductions)
    max_reduction = max(reductions)
    
    print()
    print("="*70)
    print("RESULTS")
    print("="*70)
    print()
    print(f"Execution time: {elapsed:.1f}s")
    print()
    print("ENTROPY REDUCTION:")
    print(f"  Average: {avg_reduction:.2f}%")
    print(f"  Min: {min_reduction:.2f}%")
    print(f"  Max: {max_reduction:.2f}%")
    print()
    print(f"Throughput: {1000/elapsed:.0f} scenarios/second")
    print()


def main():
    """Run all benchmarks."""
    print()
    print("="*70)
    print("🧪 NEURAL ENTROPY CONTROL - BENCHMARK SUITE")
    print("="*70)
    print()
    
    benchmark_convergence()
    benchmark_stability()
    benchmark_performance()
    benchmark_statistical()
    
    print("="*70)
    print("✅ ALL BENCHMARKS COMPLETE")
    print("="*70)
    print()


if __name__ == '__main__':
    main()
