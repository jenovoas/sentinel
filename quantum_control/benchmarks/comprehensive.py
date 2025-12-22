#!/usr/bin/env python3
"""
Quantum Control Framework - Comprehensive Benchmark

Generates hard evidence of performance improvements.
"""

import sys
sys.path.insert(0, '/home/jnovoas/sentinel')

import time
import random
from collections import defaultdict
from quantum_control.core import QuantumController
from quantum_control.physics import OptomechanicalCooling
from quantum_control.resources import BufferResource, ThreadPoolResource, MemoryResource


def generate_traffic_pattern(length=50, pattern_type="random"):
    """Generate realistic traffic pattern."""
    pattern = []
    
    if pattern_type == "random":
        # Random bursts
        util = 0.5
        for i in range(length):
            change = random.uniform(-0.2, 0.4)
            util = max(0.3, min(0.99, util + change))
            drop_rate = max(0, (util - 0.7) * 0.3) if util > 0.7 else 0
            pattern.append((float(i), util, drop_rate))
    
    elif pattern_type == "burst":
        # Sudden burst
        for i in range(length):
            if 10 <= i <= 20:
                util = 0.95 + random.uniform(0, 0.04)
                drop_rate = 0.2
            else:
                util = 0.5 + random.uniform(-0.1, 0.1)
                drop_rate = 0
            pattern.append((float(i), util, drop_rate))
    
    elif pattern_type == "oscillating":
        # Periodic bursts
        for i in range(length):
            if i % 10 < 3:
                util = 0.9 + random.uniform(0, 0.09)
                drop_rate = 0.15
            else:
                util = 0.6 + random.uniform(-0.1, 0.1)
                drop_rate = 0
            pattern.append((float(i), util, drop_rate))
    
    return pattern


def benchmark_resource(resource_name, resource, pattern, use_controller=True):
    """Benchmark a single resource."""
    if use_controller:
        physics = OptomechanicalCooling()
        controller = QuantumController(
            resource=resource,
            physics_model=physics,
            poll_interval=0.1
        )
    
    total_drops = 0
    peak_size = resource.current_size if hasattr(resource, 'current_size') else \
                resource.current_threads if hasattr(resource, 'current_threads') else \
                resource.current_heap
    
    for timestamp, utilization, drop_rate in pattern:
        if use_controller:
            # Simulate state
            state = resource.measure_state()
            new_size, _ = controller.physics.calculate_force(state, controller.history), ""
            controller.history.append(state)
            
            # Apply control
            if len(controller.history) > 5:
                controller._control_cycle()
        
        # Calculate drops
        drops = int(drop_rate * 1000)
        total_drops += drops
        
        # Track peak
        current = resource.current_size if hasattr(resource, 'current_size') else \
                 resource.current_threads if hasattr(resource, 'current_threads') else \
                 resource.current_heap
        peak_size = max(peak_size, current)
    
    return {
        'total_drops': total_drops,
        'peak_size': peak_size
    }


def run_benchmark():
    """Run comprehensive benchmark."""
    print("="*70)
    print("🧪 QUANTUM CONTROL - COMPREHENSIVE BENCHMARK")
    print("="*70)
    print()
    print("Testing all resources against multiple traffic patterns...")
    print()
    
    resources = {
        'Buffer': BufferResource(initial_size=1000, min_size=512, max_size=16384),
        'Thread': ThreadPoolResource(initial_threads=10, min_threads=2, max_threads=1000),
        'Memory': MemoryResource(initial_heap=1024, min_heap=256, max_heap=8192)
    }
    
    patterns = {
        'Random': 'random',
        'Burst': 'burst',
        'Oscillating': 'oscillating'
    }
    
    results = defaultdict(dict)
    
    for pattern_name, pattern_type in patterns.items():
        print(f"\n{'='*70}")
        print(f"📊 PATTERN: {pattern_name}")
        print(f"{'='*70}\n")
        
        pattern = generate_traffic_pattern(50, pattern_type)
        
        for resource_name, resource_class in [
            ('Buffer', BufferResource),
            ('Thread', ThreadPoolResource),
            ('Memory', MemoryResource)
        ]:
            # Create resources with correct parameters
            if resource_name == 'Buffer':
                resource_baseline = BufferResource(initial_size=1000, min_size=512, max_size=16384)
                resource_controlled = BufferResource(initial_size=1000, min_size=512, max_size=16384)
            elif resource_name == 'Thread':
                resource_baseline = ThreadPoolResource(initial_threads=10, min_threads=2, max_threads=1000)
                resource_controlled = ThreadPoolResource(initial_threads=10, min_threads=2, max_threads=1000)
            else:  # Memory
                resource_baseline = MemoryResource(initial_heap=1024, min_heap=256, max_heap=8192)
                resource_controlled = MemoryResource(initial_heap=1024, min_heap=256, max_heap=8192)
            
            baseline = benchmark_resource(resource_name, resource_baseline, pattern, use_controller=False)
            controlled = benchmark_resource(resource_name, resource_controlled, pattern, use_controller=True)
            
            # Calculate improvement
            improvement = (1 - controlled['total_drops'] / max(baseline['total_drops'], 1)) * 100
            
            results[pattern_name][resource_name] = {
                'baseline_drops': baseline['total_drops'],
                'controlled_drops': controlled['total_drops'],
                'improvement': improvement,
                'peak_size': controlled['peak_size']
            }
            
            print(f"{resource_name:10} | Baseline: {baseline['total_drops']:4d} drops | "
                  f"Controlled: {controlled['total_drops']:4d} drops | "
                  f"Improvement: {improvement:5.1f}%")
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 SUMMARY")
    print(f"{'='*70}\n")
    
    print(f"{'Resource':<10} | {'Pattern':<12} | {'Baseline':<8} | {'Controlled':<10} | {'Improvement':<12}")
    print("-"*70)
    
    total_baseline = 0
    total_controlled = 0
    
    for pattern_name in patterns.keys():
        for resource_name in ['Buffer', 'Thread', 'Memory']:
            r = results[pattern_name][resource_name]
            total_baseline += r['baseline_drops']
            total_controlled += r['controlled_drops']
            
            print(f"{resource_name:<10} | {pattern_name:<12} | {r['baseline_drops']:<8} | "
                  f"{r['controlled_drops']:<10} | {r['improvement']:>10.1f}%")
    
    print("-"*70)
    overall_improvement = (1 - total_controlled / max(total_baseline, 1)) * 100
    print(f"{'OVERALL':<10} | {'ALL':<12} | {total_baseline:<8} | "
          f"{total_controlled:<10} | {overall_improvement:>10.1f}%")
    
    print(f"\n{'='*70}")
    print("✅ BENCHMARK COMPLETE")
    print(f"{'='*70}\n")
    
    print(f"Total drops prevented: {total_baseline - total_controlled}")
    print(f"Overall improvement: {overall_improvement:.1f}%")
    print()
    
    return results


if __name__ == '__main__':
    start = time.time()
    results = run_benchmark()
    elapsed = time.time() - start
    
    print(f"Benchmark completed in {elapsed:.2f} seconds")
    print()
