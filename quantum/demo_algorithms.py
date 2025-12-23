#!/usr/bin/env python3
"""
Sentinel Quantum Algorithms - Advanced Demo
Demonstrates QAOA and VQE on laptop-safe configurations
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from sentinel_quantum_core import (
    SentinelQuantumCore, 
    SentinelQAOA, 
    SentinelVQE,
    SentinelConfig
)
import time

def demo_qaoa():
    """
    QAOA - Quantum Approximate Optimization Algorithm
    Finds optimal solutions to combinatorial problems
    """
    print("=" * 60)
    print("QAOA - QUANTUM APPROXIMATE OPTIMIZATION ALGORITHM")
    print("=" * 60)
    print()
    
    # Laptop-safe configuration
    print("🔧 Configuration:")
    config = SentinelConfig(N_membranes=3, N_levels=5)
    print(f"   Membranes: {config.N_membranes}")
    print(f"   Levels: {config.N_levels}")
    print(f"   Hilbert dimension: {config.N_levels ** config.N_membranes}")
    print()
    
    # Initialize
    print("🚀 Initializing Sentinel Quantum Core...")
    core = SentinelQuantumCore(config)
    qaoa = SentinelQAOA(core)
    print("   ✅ Core initialized")
    print()
    
    # Run QAOA with different depths
    print("🔬 Running QAOA optimization...")
    results = []
    depths = [1, 2, 3]
    
    for p in depths:
        print(f"\n   Depth p={p}:")
        start = time.time()
        result = qaoa.optimize(p=p, maxiter=30)
        elapsed = time.time() - start
        
        print(f"      Energy: {result['optimal_energy']:.6f}")
        print(f"      Success: {result['success']}")
        print(f"      Time: {elapsed:.2f}s")
        
        results.append({
            'depth': p,
            'energy': result['optimal_energy'],
            'time': elapsed,
            'success': result['success']
        })
    
    print()
    print("=" * 60)
    print("QAOA RESULTS SUMMARY")
    print("=" * 60)
    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"p={r['depth']}: E={r['energy']:.6f}, t={r['time']:.2f}s {status}")
    
    return results


def demo_vqe():
    """
    VQE - Variational Quantum Eigensolver
    Finds ground state energy of quantum systems
    """
    print("\n\n")
    print("=" * 60)
    print("VQE - VARIATIONAL QUANTUM EIGENSOLVER")
    print("=" * 60)
    print()
    
    # Laptop-safe configuration
    print("🔧 Configuration:")
    config = SentinelConfig(N_membranes=3, N_levels=4)
    print(f"   Membranes: {config.N_membranes}")
    print(f"   Levels: {config.N_levels}")
    print(f"   Hilbert dimension: {config.N_levels ** config.N_membranes}")
    print()
    
    # Initialize
    print("🚀 Initializing Sentinel Quantum Core...")
    core = SentinelQuantumCore(config)
    vqe = SentinelVQE(core)
    print("   ✅ Core initialized")
    print()
    
    # Run VQE
    print("🔬 Running VQE ground state search...")
    start = time.time()
    result = vqe.optimize(maxiter=50)
    elapsed = time.time() - start
    
    print(f"\n   Ground state energy (VQE): {result['vqe_energy']:.6f}")
    print(f"   Exact ground energy: {result['exact_energy']:.6f}")
    print(f"   Error: {result['error']:.6e}")
    print(f"   Time: {elapsed:.2f}s")
    
    print()
    print("=" * 60)
    print("VQE RESULTS SUMMARY")
    print("=" * 60)
    print(f"Ground Energy (VQE):   {result['vqe_energy']:.6f}")
    print(f"Ground Energy (Exact): {result['exact_energy']:.6f}")
    print(f"Accuracy: {(1 - result['error'] / abs(result['exact_energy'])) * 100:.2f}%")
    
    return result


def visualize_results(qaoa_results, vqe_result):
    """Create visualization of algorithm performance"""
    print("\n\n")
    print("📊 Generating visualization...")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # QAOA: Energy vs Depth
    ax1 = axes[0]
    depths = [r['depth'] for r in qaoa_results]
    energies = [r['energy'] for r in qaoa_results]
    times = [r['time'] for r in qaoa_results]
    
    color = 'tab:blue'
    ax1.set_xlabel('QAOA Depth (p)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Optimal Energy', color=color, fontsize=12, fontweight='bold')
    ax1.plot(depths, energies, 'o-', color=color, linewidth=2, markersize=8, label='Energy')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, alpha=0.3)
    ax1.set_title('QAOA: Energy Optimization', fontsize=14, fontweight='bold')
    
    # Add time on secondary axis
    ax1_twin = ax1.twinx()
    color = 'tab:orange'
    ax1_twin.set_ylabel('Computation Time (s)', color=color, fontsize=12, fontweight='bold')
    ax1_twin.plot(depths, times, 's--', color=color, linewidth=2, markersize=8, label='Time')
    ax1_twin.tick_params(axis='y', labelcolor=color)
    
    # VQE: Convergence comparison
    ax2 = axes[1]
    categories = ['VQE Result', 'Exact Ground']
    values = [vqe_result['vqe_energy'], vqe_result['exact_energy']]
    colors = ['tab:green', 'tab:red']
    
    bars = ax2.bar(categories, values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax2.set_ylabel('Ground State Energy', fontsize=12, fontweight='bold')
    ax2.set_title('VQE: Ground State Accuracy', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.6f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    
    # Save
    output_path = '/home/jnovoas/sentinel/quantum/algorithm_comparison.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"   ✅ Saved: {output_path}")
    
    # plt.show()  # Commented for non-interactive execution


def compare_algorithms():
    """Compare QAOA vs VQE performance"""
    print("\n\n")
    print("=" * 60)
    print("ALGORITHM COMPARISON")
    print("=" * 60)
    print()
    
    print("┌─────────────┬──────────────┬──────────────┬─────────────┐")
    print("│ Algorithm   │ Use Case     │ Strength     │ Complexity  │")
    print("├─────────────┼──────────────┼──────────────┼─────────────┤")
    print("│ QAOA        │ Optimization │ Combinatorial│ O(p × n²)   │")
    print("│             │ Problems     │ Search       │             │")
    print("├─────────────┼──────────────┼──────────────┼─────────────┤")
    print("│ VQE         │ Ground State │ Chemistry,   │ O(iter × n²)│")
    print("│             │ Finding      │ Materials    │             │")
    print("└─────────────┴──────────────┴──────────────┴─────────────┘")
    print()
    
    print("🎯 Key Insights:")
    print("   • QAOA: Better for discrete optimization (scheduling, routing)")
    print("   • VQE: Better for continuous problems (molecular energy)")
    print("   • Both: Hybrid quantum-classical algorithms")
    print("   • Scalability: Limited by qubit count and coherence time")
    print()


def main():
    """Run complete algorithm demonstration"""
    print("\n")
    print("🌟" * 30)
    print("   SENTINEL QUANTUM ALGORITHMS - ADVANCED DEMO")
    print("🌟" * 30)
    print()
    
    # Run QAOA
    qaoa_results = demo_qaoa()
    
    # Run VQE
    vqe_result = demo_vqe()
    
    # Compare
    compare_algorithms()
    
    # Visualize
    visualize_results(qaoa_results, vqe_result)
    
    print("\n")
    print("=" * 60)
    print("✅ DEMO COMPLETE!")
    print("=" * 60)
    print()
    print("📚 Next steps:")
    print("   1. Explore custom Hamiltonians")
    print("   2. Scale to larger systems (with more RAM)")
    print("   3. Integrate with Sentinel Cortex™ for real-world problems")
    print("   4. Benchmark against classical algorithms")
    print()


if __name__ == "__main__":
    main()
