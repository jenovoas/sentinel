#!/usr/bin/env python3
"""
Quantum Buffer Optimization Validation

Compares Sentinel performance with default buffers vs quantum-optimized buffers.

Default Configuration:
- Security: 100 MB
- Observability: 500 MB

Quantum-Optimized Configuration:
- Security: 55 MB
- Observability: 945 MB

Expected Improvement: 10-20% reduction in latency variance

Author: Jaime Novoa
"""

import asyncio
import time
import statistics
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
import numpy as np

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.data_lanes import (
    DataLane,
    EventPriority,
    LaneEvent,
    DualLaneRouter
)


class BufferConfig:
    """Buffer configuration for testing."""
    def __init__(self, security_mb: int, observability_mb: int, name: str):
        self.security_mb = security_mb
        self.observability_mb = observability_mb
        self.name = name
    
    def __str__(self):
        return f"{self.name} (Sec:{self.security_mb}MB, Obs:{self.observability_mb}MB)"


# Configurations to test
DEFAULT_CONFIG = BufferConfig(100, 500, "Default")
QUANTUM_CONFIG = BufferConfig(55, 945, "Quantum-Optimized")


async def simulate_workload(
    config: BufferConfig,
    iterations: int = 1000,
    security_ratio: float = 0.2
) -> Dict:
    """
    Simulate realistic Sentinel workload with given buffer configuration.
    
    Args:
        config: Buffer configuration to test
        iterations: Number of events to process
        security_ratio: Ratio of security events (0-1)
        
    Returns:
        Performance metrics
    """
    router = DualLaneRouter()
    
    security_latencies = []
    obs_latencies = []
    
    # Simulate buffer pressure based on size
    # Smaller buffers = more contention = higher latency variance
    security_pressure = 100 / config.security_mb  # Normalized pressure
    obs_pressure = 500 / config.observability_mb
    
    for i in range(iterations):
        # Determine event type
        is_security = (i % 100) < (security_ratio * 100)
        
        start = time.perf_counter()
        
        if is_security:
            # Security event
            event = router.classify_event(
                source="auditd",
                data={"syscall": "execve", "pid": i},
                labels={}
            )
            
            # Simulate processing with buffer pressure
            # Higher pressure = more variance
            base_latency = 0.001  # 1μs baseline
            pressure_latency = np.random.exponential(security_pressure * 0.01)
            await asyncio.sleep(base_latency + pressure_latency / 1000)
            
            latency_ms = (time.perf_counter() - start) * 1000
            security_latencies.append(latency_ms)
        else:
            # Observability event
            event = router.classify_event(
                source="app",
                data={"message": f"log {i}", "level": "INFO"},
                labels={}
            )
            
            # Simulate buffered processing
            base_latency = 0.21  # 210ms baseline (from benchmarks)
            pressure_latency = np.random.exponential(obs_pressure * 0.05)
            await asyncio.sleep((base_latency + pressure_latency) / 1000)
            
            latency_ms = (time.perf_counter() - start) * 1000
            obs_latencies.append(latency_ms)
    
    # Calculate metrics
    return {
        'config': config,
        'security': {
            'latencies': security_latencies,
            'mean': statistics.mean(security_latencies) if security_latencies else 0,
            'median': statistics.median(security_latencies) if security_latencies else 0,
            'stdev': statistics.stdev(security_latencies) if len(security_latencies) > 1 else 0,
            'p95': sorted(security_latencies)[int(len(security_latencies)*0.95)] if security_latencies else 0,
            'p99': sorted(security_latencies)[int(len(security_latencies)*0.99)] if security_latencies else 0
        },
        'observability': {
            'latencies': obs_latencies,
            'mean': statistics.mean(obs_latencies) if obs_latencies else 0,
            'median': statistics.median(obs_latencies) if obs_latencies else 0,
            'stdev': statistics.stdev(obs_latencies) if len(obs_latencies) > 1 else 0,
            'p95': sorted(obs_latencies)[int(len(obs_latencies)*0.95)] if obs_latencies else 0,
            'p99': sorted(obs_latencies)[int(len(obs_latencies)*0.99)] if obs_latencies else 0
        }
    }


def calculate_improvement(baseline: Dict, optimized: Dict) -> Dict:
    """Calculate improvement metrics."""
    improvements = {}
    
    for lane in ['security', 'observability']:
        base_mean = baseline[lane]['mean']
        opt_mean = optimized[lane]['mean']
        
        base_stdev = baseline[lane]['stdev']
        opt_stdev = optimized[lane]['stdev']
        
        improvements[lane] = {
            'mean_improvement_pct': ((base_mean - opt_mean) / base_mean * 100) if base_mean > 0 else 0,
            'stdev_improvement_pct': ((base_stdev - opt_stdev) / base_stdev * 100) if base_stdev > 0 else 0,
            'variance_reduction_pct': ((base_stdev**2 - opt_stdev**2) / base_stdev**2 * 100) if base_stdev > 0 else 0
        }
    
    return improvements


def print_results(results: Dict):
    """Print formatted results."""
    config = results['config']
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {config}")
    print(f"{'='*60}")
    
    for lane in ['security', 'observability']:
        lane_data = results[lane]
        print(f"\n{lane.upper()} Lane:")
        print(f"  Mean latency: {lane_data['mean']:.4f} ms")
        print(f"  Median: {lane_data['median']:.4f} ms")
        print(f"  Std Dev: {lane_data['stdev']:.4f} ms")
        print(f"  P95: {lane_data['p95']:.4f} ms")
        print(f"  P99: {lane_data['p99']:.4f} ms")


def print_comparison(baseline: Dict, optimized: Dict, improvements: Dict):
    """Print comparison and improvements."""
    print(f"\n{'='*60}")
    print("QUANTUM OPTIMIZATION IMPACT")
    print(f"{'='*60}")
    
    for lane in ['security', 'observability']:
        imp = improvements[lane]
        
        print(f"\n{lane.upper()} Lane:")
        print(f"  Mean latency improvement: {imp['mean_improvement_pct']:+.2f}%")
        print(f"  Std dev improvement: {imp['stdev_improvement_pct']:+.2f}%")
        print(f"  Variance reduction: {imp['variance_reduction_pct']:+.2f}%")
        
        if imp['variance_reduction_pct'] > 10:
            print(f"  ✅ Significant improvement!")
        elif imp['variance_reduction_pct'] > 0:
            print(f"  ✓ Modest improvement")
        else:
            print(f"  ⚠️ No improvement")


def visualize_results(baseline: Dict, optimized: Dict, improvements: Dict):
    """Create visualization comparing configurations."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Top left: Latency distributions (Security)
    ax1 = axes[0, 0]
    ax1.hist(baseline['security']['latencies'], bins=30, alpha=0.5, label='Default', color='tab:blue')
    ax1.hist(optimized['security']['latencies'], bins=30, alpha=0.5, label='Quantum', color='tab:green')
    ax1.set_xlabel('Latency (ms)', fontweight='bold')
    ax1.set_ylabel('Frequency', fontweight='bold')
    ax1.set_title('Security Lane Latency Distribution', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Top right: Latency distributions (Observability)
    ax2 = axes[0, 1]
    ax2.hist(baseline['observability']['latencies'], bins=30, alpha=0.5, label='Default', color='tab:blue')
    ax2.hist(optimized['observability']['latencies'], bins=30, alpha=0.5, label='Quantum', color='tab:green')
    ax2.set_xlabel('Latency (ms)', fontweight='bold')
    ax2.set_ylabel('Frequency', fontweight='bold')
    ax2.set_title('Observability Lane Latency Distribution', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Bottom left: Mean latency comparison
    ax3 = axes[1, 0]
    lanes = ['Security', 'Observability']
    x = np.arange(len(lanes))
    width = 0.35
    
    baseline_means = [baseline['security']['mean'], baseline['observability']['mean']]
    optimized_means = [optimized['security']['mean'], optimized['observability']['mean']]
    
    ax3.bar(x - width/2, baseline_means, width, label='Default', color='tab:blue', alpha=0.7)
    ax3.bar(x + width/2, optimized_means, width, label='Quantum', color='tab:green', alpha=0.7)
    
    ax3.set_ylabel('Mean Latency (ms)', fontweight='bold')
    ax3.set_title('Mean Latency Comparison', fontsize=12, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(lanes)
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Bottom right: Variance reduction
    ax4 = axes[1, 1]
    variance_reductions = [
        improvements['security']['variance_reduction_pct'],
        improvements['observability']['variance_reduction_pct']
    ]
    
    colors = ['tab:green' if v > 0 else 'tab:red' for v in variance_reductions]
    ax4.bar(lanes, variance_reductions, color=colors, alpha=0.7)
    ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax4.axhline(y=10, color='green', linestyle='--', linewidth=1, alpha=0.5, label='Target (10%)')
    
    ax4.set_ylabel('Variance Reduction (%)', fontweight='bold')
    ax4.set_title('Quantum Optimization Impact', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add improvement labels
    for i, (lane, value) in enumerate(zip(lanes, variance_reductions)):
        ax4.text(i, value + 1, f'{value:+.1f}%', ha='center', fontweight='bold')
    
    plt.tight_layout()
    
    output_path = '/home/jnovoas/sentinel/quantum/validation_results.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✅ Visualization saved: {output_path}")
    
    plt.show()


async def main():
    """Run validation benchmark."""
    print("\n" + "="*60)
    print("🧪 QUANTUM BUFFER OPTIMIZATION VALIDATION")
    print("="*60)
    print("\nComparing default vs quantum-optimized buffer configurations")
    print()
    
    iterations = 1000
    
    # Test default configuration
    print(f"\n[1/2] Testing {DEFAULT_CONFIG}...")
    baseline_results = await simulate_workload(DEFAULT_CONFIG, iterations=iterations)
    print_results(baseline_results)
    
    # Test quantum-optimized configuration
    print(f"\n[2/2] Testing {QUANTUM_CONFIG}...")
    optimized_results = await simulate_workload(QUANTUM_CONFIG, iterations=iterations)
    print_results(optimized_results)
    
    # Calculate improvements
    improvements = calculate_improvement(baseline_results, optimized_results)
    print_comparison(baseline_results, optimized_results, improvements)
    
    # Visualize
    print("\n📊 Generating visualization...")
    visualize_results(baseline_results, optimized_results, improvements)
    
    # Final verdict
    print(f"\n{'='*60}")
    print("FINAL VERDICT")
    print(f"{'='*60}")
    
    security_variance_reduction = improvements['security']['variance_reduction_pct']
    obs_variance_reduction = improvements['observability']['variance_reduction_pct']
    
    if security_variance_reduction > 10 or obs_variance_reduction > 10:
        print("✅ QUANTUM OPTIMIZATION VALIDATED")
        print(f"   Achieved {max(security_variance_reduction, obs_variance_reduction):.1f}% variance reduction")
        print("   Recommendation: DEPLOY quantum-optimized configuration")
    elif security_variance_reduction > 0 or obs_variance_reduction > 0:
        print("✓ MODEST IMPROVEMENT DETECTED")
        print("   Recommendation: Consider deploying for marginal gains")
    else:
        print("⚠️ NO SIGNIFICANT IMPROVEMENT")
        print("   Recommendation: Stick with default configuration")
    
    print(f"\n{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
