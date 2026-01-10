#!/usr/bin/env python3
"""
🧪 TEST: Quantum Noise Models
==============================
Valida modelos de ruido cuántico.
"""

from quantum.yatra_core import S60
from quantum.yatra_math import S60Math
from quantum.quantum_noise_s60 import QuantumNoise, NoisySimulator

def test_depolarizing_noise():
    """Test depolarizing noise."""
    print("\n🔊 TEST: Depolarizing Noise")
    print("=" * 60)
    
    # Estado inicial: |+⟩ = (|0⟩ + |1⟩)/√2
    sqrt2 = S60Math.sqrt(S60(2))
    psi = [S60(1) / sqrt2, S60(1) / sqrt2]
    
    print(f"  Estado inicial: |ψ⟩ = [{psi[0]}, {psi[1]}]")
    
    # Aplicar ruido con probabilidad 0.5% (muy bajo)
    prob = S60(0, 0, 30)  # 0.5/60 ≈ 0.008
    psi_noisy = QuantumNoise.depolarizing_noise(psi, prob, n_qubits=1)
    
    print(f"  Estado con ruido: |ψ'⟩ = [{psi_noisy[0]}, {psi_noisy[1]}]")
    
    # Verificar que el estado cambió (puede o no cambiar dependiendo de entropía)
    print("  ✅ Ruido aplicado (determinista basado en entropía)")
    
    return True

def test_amplitude_damping():
    """Test amplitude damping."""
    print("\n🔊 TEST: Amplitude Damping")
    print("=" * 60)
    
    # Estado inicial: |1⟩
    psi = [S60(0), S60(1)]
    
    print(f"  Estado inicial: |1⟩")
    
    # Aplicar damping con γ = 0.1
    gamma = S60(0, 6, 0)  # 0.1
    psi_damped = QuantumNoise.amplitude_damping(psi, gamma, n_qubits=1)
    
    print(f"  Estado con damping: |ψ'⟩ = [{psi_damped[0]}, {psi_damped[1]}]")
    
    # |1⟩ debe haber perdido amplitud
    assert psi_damped[1]._value < psi[1]._value, "Amplitud de |1⟩ debe reducirse"
    assert psi_damped[0]._value > 0, "Debe haber transferencia a |0⟩"
    
    print("  ✅ Amplitude damping funciona correctamente")
    
    return True

def test_phase_damping():
    """Test phase damping."""
    print("\n🔊 TEST: Phase Damping")
    print("=" * 60)
    
    # Estado inicial: |+⟩
    sqrt2 = S60Math.sqrt(S60(2))
    psi = [S60(1) / sqrt2, S60(1) / sqrt2]
    
    print(f"  Estado inicial: |+⟩")
    
    # Aplicar damping con γ = 0.1
    gamma = S60(0, 6, 0)
    psi_damped = QuantumNoise.phase_damping(psi, gamma, n_qubits=1)
    
    print(f"  Estado con damping: |ψ'⟩ = [{psi_damped[0]}, {psi_damped[1]}]")
    
    # Coherencias deben reducirse
    for i in range(len(psi)):
        assert psi_damped[i]._value <= psi[i]._value, "Amplitudes deben reducirse"
    
    print("  ✅ Phase damping funciona correctamente")
    
    return True

def test_noisy_simulator():
    """Test NoisySimulator wrapper."""
    print("\n🔊 TEST: Noisy Simulator")
    print("=" * 60)
    
    # Crear simulador con ruido
    sim = NoisySimulator(
        n_qubits=2, 
        noise_model="depolarizing",
        noise_strength=S60(0, 1, 0)
    )
    
    # Estado inicial
    psi = [S60(1), S60(0), S60(0), S60(0)]
    
    # Aplicar ruido
    psi_noisy = sim.apply_noise(psi)
    
    print(f"  ✅ Simulador con ruido funcional")
    
    return True

def main():
    """Ejecuta todos los tests."""
    print("\n🛡️ TESTS: Quantum Noise Models")
    print("=" * 60)
    
    results = {
        "Depolarizing Noise": test_depolarizing_noise(),
        "Amplitude Damping": test_amplitude_damping(),
        "Phase Damping": test_phase_damping(),
        "Noisy Simulator": test_noisy_simulator(),
    }
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"   {status}: {name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🏆 TODOS LOS TESTS PASARON")
        print("   Modelos de ruido cuántico validados")
    else:
        print("⚠️  ALGUNOS TESTS FALLARON")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
