#!/usr/bin/env python3
"""
🧪 TEST: VQE para H2 y Cristales Resonantes
============================================
Valida VQE con sistemas reales.
"""

from quantum.yatra_core import S60
from quantum.vqe_s60 import VQE_S60

def test_h2_molecule():
    """Test VQE con molécula H2."""
    print("\n🔬 TEST: Molécula H2")
    print("=" * 60)
    
    # Longitud de enlace típica de H2: 0.74 Å
    bond_length = S60(0, 44, 24)  # 0.74 en S60
    
    vqe = VQE_S60(n_qubits=2, depth=1)
    result = vqe.solve_H2(bond_length, max_iter=20)
    
    print(f"\n✅ Resultado:")
    print(f"   Energía: {result.energy}")
    print(f"   Iteraciones: {result.iterations}")
    print(f"   Convergió: {result.converged}")
    
    # Verificar que encontró una energía
    assert result.energy is not None, "Debe retornar una energía"
    assert result.converged, "Debe converger"
    
    return True

def test_crystal_resonance():
    """Test VQE con cristal resonante."""
    print("\n💎 TEST: Cristal Resonante")
    print("=" * 60)
    
    # Acoplamiento entre sitios
    coupling = S60(1, 0, 0)  # J = 1
    
    vqe = VQE_S60(n_qubits=4, depth=1)
    result = vqe.solve_crystal_resonance(coupling, n_sites=4, max_iter=20)
    
    print(f"\n✅ Resultado:")
    print(f"   Energía de resonancia: {result.energy}")
    print(f"   Iteraciones: {result.iterations}")
    
    assert result.energy is not None
    assert result.converged
    
    return True

def test_crystal_different_couplings():
    """Test cristal con diferentes acoplamientos."""
    print("\n💎 TEST: Cristal con Diferentes Acoplamientos")
    print("=" * 60)
    
    couplings = [S60(0, 30, 0), S60(1, 0, 0), S60(2, 0, 0)]
    
    vqe = VQE_S60(n_qubits=3, depth=1)
    
    for coupling in couplings:
        result = vqe.solve_crystal_resonance(coupling, n_sites=3, max_iter=15)
        print(f"   J={coupling} → E={result.energy}")
    
    print("  ✅ Diferentes acoplamientos calculados")
    
    return True

def main():
    """Ejecuta todos los tests."""
    print("\n🛡️ TESTS: VQE - Moléculas y Cristales")
    print("=" * 60)
    
    results = {
        "Molécula H2": test_h2_molecule(),
        "Cristal Resonante": test_crystal_resonance(),
        "Diferentes Acoplamientos": test_crystal_different_couplings(),
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
        print("   VQE funcional para cristales resonantes")
    else:
        print("⚠️  ALGUNOS TESTS FALLARON")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
