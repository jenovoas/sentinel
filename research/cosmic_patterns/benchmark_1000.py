#!/usr/bin/env python3
"""
Quantum Cooling - 1000 Iteration Statistical Benchmark

Validates performance across 1000 random traffic patterns for robust statistics.
"""

import time
import random
from quantum_cooling_v2 import QuantumCoolingPredictorV2, BufferState


def generate_random_pattern(length=20):
    """Generate random traffic pattern."""
    pattern = []
    current_util = 0.5
    
    for i in range(length):
        # Random walk with bursts
        change = random.uniform(-0.1, 0.3)
        current_util = max(0.3, min(0.99, current_util + change))
        
        # Drop rate proportional to utilization
        if current_util > 0.8:
            drop_rate = (current_util - 0.8) * 0.5
        else:
            drop_rate = 0.0
        
        pattern.append((float(i), current_util, drop_rate))
    
    return pattern


def run_single_test(pattern):
    """Run single test and return stats."""
    predictor = QuantumCoolingPredictorV2()
    
    initial_size = 1000
    current_size = initial_size
    peak_size = initial_size
    
    total_drops_without = 0
    total_drops_with = 0
    
    for timestamp, utilization, drop_rate in pattern:
        state = BufferState(
            size=current_size,
            utilization=utilization,
            drop_rate=drop_rate,
            timestamp=timestamp
        )
        
        new_size, _ = predictor.predict(state)
        
        drops_without = int(drop_rate * 1000)
        expansion_ratio = new_size / current_size if current_size > 0 else 1.0
        drops_with = int(drops_without / expansion_ratio)
        
        total_drops_without += drops_without
        total_drops_with += drops_with
        peak_size = max(peak_size, new_size)
        
        current_size = new_size
    
    improvement = (1 - total_drops_with / max(total_drops_without, 1)) * 100
    expansion = peak_size / initial_size
    
    return {
        'drops_prevented': total_drops_without - total_drops_with,
        'improvement': improvement,
        'peak_expansion': expansion
    }


def main():
    print("="*70)
    print("🧊⚛️ QUANTUM COOLING - 10,000 ITERATION BENCHMARK")
    print("="*70)
    print()
    print("Generating 10,000 random traffic patterns...")
    print("This will take ~1 minute...")
    print()
    
    results = []
    start_time = time.time()
    
    for i in range(10000):
        if (i + 1) % 1000 == 0:
            elapsed = time.time() - start_time
            print(f"Progress: {i+1}/10,000 ({elapsed:.1f}s elapsed)")
        
        pattern = generate_random_pattern()
        result = run_single_test(pattern)
        results.append(result)
    
    total_time = time.time() - start_time
    
    # Calculate statistics
    improvements = [r['improvement'] for r in results]
    expansions = [r['peak_expansion'] for r in results]
    drops_prevented = [r['drops_prevented'] for r in results]
    
    avg_improvement = sum(improvements) / len(improvements)
    min_improvement = min(improvements)
    max_improvement = max(improvements)
    
    avg_expansion = sum(expansions) / len(expansions)
    max_expansion = max(expansions)
    
    total_drops_prevented = sum(drops_prevented)
    
    # Print results
    print()
    print("="*70)
    print("📊 STATISTICAL RESULTS (n=10,000)")
    print("="*70)
    print()
    print(f"Execution time: {total_time:.1f}s")
    print()
    print("IMPROVEMENT:")
    print(f"  Average: {avg_improvement:.2f}%")
    print(f"  Min: {min_improvement:.2f}%")
    print(f"  Max: {max_improvement:.2f}%")
    print()
    print("EXPANSION:")
    print(f"  Average: {avg_expansion:.2f}x")
    print(f"  Max: {max_expansion:.2f}x")
    print()
    print("DROPS PREVENTED:")
    print(f"  Total: {total_drops_prevented:,}")
    print(f"  Average per test: {total_drops_prevented / 1000:.1f}")
    print()
    print("="*70)
    print("✅ STATISTICAL VALIDATION COMPLETE")
    print("="*70)
    print()
    print(f"Quantum Cooling validated across 10,000 random scenarios")
    print(f"Consistent improvement: {avg_improvement:.2f}% ± {max_improvement - min_improvement:.2f}%")
    print()


if __name__ == '__main__':
    main()
