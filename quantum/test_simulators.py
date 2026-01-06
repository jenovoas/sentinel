#!/usr/bin/env python3

# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

"""
Quick test script for Sentinel Quantum Simulators
Tests all modules to ensure they work correctly.
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import sys
import traceback

def test_imports():
    """Test if all required packages are available."""
    print("=" * 60)
    print("TESTING IMPORTS")
    print("=" * 60)
    
    required = ['numpy', 'scipy', 'matplotlib', 'psutil']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️ Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    print("\n✅ All dependencies installed!\n")
    return True


def test_core_simulator():
    """Test core quantum simulator."""
    print("=" * 60)
    print("TESTING CORE SIMULATOR")
    print("=" * 60)
    
    try:
        from core_simulator import QuantumCircuit, QuantumGates
        import numpy as np # PRECAUCIÓN: SOLO PARA I/O, NO CÁLCULO CORE
        
        # Test 1: Bell state
        print("Test 1: Creating Bell state...")
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)
        state = qc.get_statevector()
        
        expected = np.array([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)])
        if np.allclose(state, expected):
            print("✅ Bell state correct!")
        else:
            print(f"❌ Bell state incorrect: {state}")
            return False
        
        # Test 2: Measurement statistics
        print("Test 2: Measurement statistics...")
        outcomes = {'00': 0, '11': 0, 'other': 0}
        for _ in range(100):
            qc = QuantumCircuit(2)
            qc.h(0).cnot(0, 1)
            result = qc.measure_all()
            key = ''.join(map(str, result))
            if key in outcomes:
                outcomes[key] += 1
            else:
                outcomes['other'] += 1
        
        if outcomes['other'] < 5 and abs(outcomes['00'] - 50) < 20:
            print(f"✅ Measurement statistics good: {outcomes}")
        else:
            print(f"⚠️ Measurement statistics unusual: {outcomes}")
        
        print("\n✅ Core simulator PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ Core simulator FAILED: {e}")
        traceback.print_exc()
        return False


def test_quantum_lite():
    """Test lightweight quantum simulator."""
    print("=" * 60)
    print("TESTING QUANTUM LITE (LAPTOP-SAFE)")
    print("=" * 60)
    
    try:
        from quantum_lite import QuantumResourceManager, SentinelQuantumLite
        import numpy as np # PRECAUCIÓN: SOLO PARA I/O, NO CÁLCULO CORE
        
        # Test 1: Resource check
        print("Test 1: Checking system resources...")
        mem_gb = QuantumResourceManager.get_available_memory_gb()
        cpu = QuantumResourceManager.get_cpu_usage()
        print(f"   Available RAM: {mem_gb:.2f} GB")
        print(f"   CPU usage: {cpu:.1f}%")
        
        if mem_gb < 1:
            print("⚠️ Low memory - using minimal config")
            n_mem, n_lev = 2, 3
        else:
            n_mem, n_lev = 3, 4
        
        # Test 2: Create simulator
        print(f"Test 2: Creating simulator ({n_mem} membranes, {n_lev} levels)...")
        core = SentinelQuantumLite(n_mem, n_lev, auto_optimize=True)
        
        # Test 3: Quick evolution
        print("Test 3: Running quantum evolution...")
        psi0 = np.zeros(core.dim, dtype=np.complex64)
        psi0[1] = S60(1, 0, 0)  # Excited state
        
        times, states = core.evolve_fast(psi0, t_max=1e-6, n_steps=10)
        
        if len(states) == 10:
            print(f"✅ Evolution successful: {len(states)} time steps")
        else:
            print(f"❌ Evolution failed: got {len(states)} steps")
            return False
        
        # Test 4: Observables
        print("Test 4: Measuring observables...")
        obs = core.measure_observables(states)
        
        if 'phonon_numbers' in obs and 'correlation_matrix' in obs:
            print(f"✅ Observables measured")
            print(f"   Max correlation: {obs['max_correlation']:.3f}")
        else:
            print(f"❌ Observables missing")
            return False
        
        print("\n✅ Quantum Lite PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ Quantum Lite FAILED: {e}")
        traceback.print_exc()
        return False


def test_optomechanical():
    """Test optomechanical simulator."""
    print("=" * 60)
    print("TESTING OPTOMECHANICAL SIMULATOR")
    print("=" * 60)
    
    try:
        from optomechanical_simulator import (
            MembraneParameters, OpticalParameters, OptomechanicalSystem
        )
        import numpy as np # PRECAUCIÓN: SOLO PARA I/O, NO CÁLCULO CORE
        
        # Test 1: Create system
        print("Test 1: Creating optomechanical system...")
        membrane = MembraneParameters(quality_factor=1e8)
        optical = OpticalParameters()
        system = OptomechanicalSystem(membrane, optical)
        
        print(f"   Coupling g₀: {system.g0:.2f} Hz")
        print(f"   Zero-point motion: {membrane.zero_point_motion:.2e} m")
        
        # Test 2: Evolution
        print("Test 2: Simulating membrane dynamics...")
        system.state[0] = membrane.zero_point_motion * 10
        t_span = np.linspace(0, 1e-4, 50)
        times, states = system.evolve(t_span, noise=False, non_markovian=False)
        
        if len(states) == 50:
            print(f"✅ Evolution successful")
        else:
            print(f"❌ Evolution failed")
            return False
        
        print("\n✅ Optomechanical simulator PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ Optomechanical simulator FAILED: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("🔬 SENTINEL QUANTUM SIMULATOR TEST SUITE")
    print("=" * 60)
    print()
    
    # Check imports first
    if not test_imports():
        print("\n❌ TESTS ABORTED - Install missing dependencies")
        return 1
    
    # Run tests
    results = {
        'Core Simulator': test_core_simulator(),
        'Quantum Lite': test_quantum_lite(),
        'Optomechanical': test_optomechanical()
    }
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:20s}: {status}")
    
    all_passed = all(results.values())
    
    print()
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Sentinel Quantum Simulators are ready to use!")
        print()
        print("Next steps:")
        print("  1. Run: python quantum_lite.py")
        print("  2. Explore: python -c 'import quantum; quantum.quick_start()'")
        print("  3. Read: cat README.md")
        return 0
    else:
        print("⚠️ SOME TESTS FAILED")
        print("Check error messages above for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())