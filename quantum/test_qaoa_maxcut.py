#!/usr/bin/env python3
"""
🧪 TEST: QAOA MaxCut
====================
Prueba QAOA con problema MaxCut real.
"""

from quantum.yatra_core import S60
from quantum.qaoa_s60 import QAOA_S60

def test_maxcut_simple():
    """Test MaxCut en grafo triangular."""
    print("\n🔬 TEST: MaxCut en Triángulo")
    print("=" * 60)
    
    # Grafo triangular: 0-1-2-0
    edges = [(0, 1), (1, 2), (2, 0)]
    
    qaoa = QAOA_S60(n_qubits=3, depth=1)
    result = qaoa.solve_maxcut(edges, max_iter=10)
    
    print(f"\n✅ Resultado:")
    print(f"   Bitstring: {result.bitstring}")
    print(f"   Costo: {result.cost}")
    print(f"   Parámetros: γ={result.optimal_params[0]}, β={result.optimal_params[1]}")
    print(f"   Iteraciones: {result.iterations}")
    
    # Verificar que encontró una solución
    assert result.bitstring is not None, "Debe retornar un bitstring"
    assert len(result.bitstring) == 3, "Bitstring debe tener 3 bits"
    
    return True

def test_maxcut_square():
    """Test MaxCut en grafo cuadrado."""
    print("\n🔬 TEST: MaxCut en Cuadrado")
    print("=" * 60)
    
    # Grafo cuadrado: 0-1-2-3-0
    edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
    
    qaoa = QAOA_S60(n_qubits=4, depth=1)
    result = qaoa.solve_maxcut(edges, max_iter=10)
    
    print(f"\n✅ Resultado:")
    print(f"   Bitstring: {result.bitstring}")
    print(f"   Costo: {result.cost}")
    
    assert result.bitstring is not None
    assert len(result.bitstring) == 4
    
    return True

def main():
    """Ejecuta todos los tests."""
    print("\n🛡️ TESTS: QAOA MaxCut")
    print("=" * 60)
    
    results = {
        "MaxCut Triángulo": test_maxcut_simple(),
        "MaxCut Cuadrado": test_maxcut_square(),
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
        print("   QAOA funcional y validado")
    else:
        print("⚠️  ALGUNOS TESTS FALLARON")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
