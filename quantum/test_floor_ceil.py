#!/usr/bin/env python3
"""
🧪 TEST: floor() y ceil()
=========================
Valida las funciones de redondeo.
"""

from quantum.yatra_core import S60
from quantum.yatra_math import S60Math

def test_floor():
    """Test floor() - redondeo hacia abajo."""
    print("\n📐 TEST: floor()")
    print("=" * 60)
    
    test_cases = [
        (S60(3, 14, 15), 3),      # π → 3
        (S60(5, 59, 59), 5),      # 5.999... → 5
        (S60(-2, 30, 0), -3),     # -2.5 → -3
        (S60(-5, 0, 0), -5),      # -5.0 → -5
        (S60(0, 0, 1), 0),        # 0.00...01 → 0
        (S60(7, 0, 0), 7),        # 7.0 → 7
    ]
    
    passed = 0
    for x, expected in test_cases:
        result = S60Math.floor(x)
        result_val = result.to_base_units() // S60.SCALE_0
        
        status = "✅" if result_val == expected else "❌"
        print(f"{status} floor({x}) = {result_val} (esperado: {expected})")
        
        if result_val == expected:
            passed += 1
    
    print(f"\n📊 Resultado: {passed}/{len(test_cases)} tests pasados")
    return passed == len(test_cases)

def test_ceil():
    """Test ceil() - redondeo hacia arriba."""
    print("\n📐 TEST: ceil()")
    print("=" * 60)
    
    test_cases = [
        (S60(3, 14, 15), 4),      # π → 4
        (S60(5, 0, 1), 6),        # 5.00...01 → 6
        (S60(-2, 30, 0), -2),     # -2.5 → -2
        (S60(-5, 0, 0), -5),      # -5.0 → -5
        (S60(0, 0, 1), 1),        # 0.00...01 → 1
        (S60(7, 0, 0), 7),        # 7.0 → 7
    ]
    
    passed = 0
    for x, expected in test_cases:
        result = S60Math.ceil(x)
        result_val = result.to_base_units() // S60.SCALE_0
        
        status = "✅" if result_val == expected else "❌"
        print(f"{status} ceil({x}) = {result_val} (esperado: {expected})")
        
        if result_val == expected:
            passed += 1
    
    print(f"\n📊 Resultado: {passed}/{len(test_cases)} tests pasados")
    return passed == len(test_cases)

def main():
    """Ejecuta todos los tests."""
    print("\n🛡️ TESTS: Funciones de Redondeo")
    print("=" * 60)
    
    results = {
        "floor()": test_floor(),
        "ceil()": test_ceil(),
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
    else:
        print("⚠️  ALGUNOS TESTS FALLARON")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
