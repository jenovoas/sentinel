#!/usr/bin/env python3
"""
🧪 TESTS: Funciones Trigonométricas Adicionales
===============================================
Valida tan, atan, asin, acos, atan2
"""

from quantum.yatra_core import S60
from quantum.yatra_math import S60Math

def test_tan():
    """Test tan() contra valores conocidos."""
    print("\n📐 TEST: tan() - Valores Conocidos")
    print("=" * 60)
    
    test_cases = [
        (0, 0.0),
        (30, 0.577350),  # tan(30°) = 1/√3
        (45, 1.0),       # tan(45°) = 1
        (60, 1.732051),  # tan(60°) = √3
    ]
    
    passed = 0
    for angle_deg, expected in test_cases:
        try:
            angle = S60(angle_deg)
            result = S60Math.tan(angle)
            result_val = result.to_base_units() / S60.SCALE_0
            error = abs(result_val - expected)
            rel_error = (error / abs(expected)) * 100 if expected != 0 else error * 100
            
            status = "✅" if rel_error < 1.0 else "❌"
            print(f"{status} tan({angle_deg:3d}°) = {result_val:.6f} (esperado: {expected:.6f}, error: {rel_error:.4f}%)")
            
            if rel_error < 1.0:
                passed += 1
        except Exception as e:
            print(f"❌ tan({angle_deg}°) - Error: {e}")
    
    print(f"\n📊 Resultado: {passed}/{len(test_cases)} tests pasados")
    return passed == len(test_cases)

def test_atan():
    """Test atan() contra valores conocidos."""
    print("\n📐 TEST: atan() - Valores Conocidos")
    print("=" * 60)
    
    test_cases = [
        (0.0, 0.0),
        (0.577350, 30.0),  # atan(1/√3) = 30°
        (1.0, 45.0),       # atan(1) = 45°
        (1.732051, 60.0),  # atan(√3) = 60°
    ]
    
    passed = 0
    for x_val, expected_deg in test_cases:
        try:
            # Convertir x_val a S60
            x_int = int(x_val * S60.SCALE_0)
            x = S60._from_raw(x_int)
            
            result = S60Math.atan(x)
            result_val = result.to_base_units() / S60.SCALE_0
            error = abs(result_val - expected_deg)
            rel_error = (error / abs(expected_deg)) * 100 if expected_deg != 0 else error
            
            status = "✅" if rel_error < 5.0 else "❌"  # Más tolerante
            print(f"{status} atan({x_val:.4f}) = {result_val:.2f}° (esperado: {expected_deg:.2f}°, error: {rel_error:.4f}%)")
            
            if rel_error < 5.0:
                passed += 1
        except Exception as e:
            print(f"❌ atan({x_val}) - Error: {e}")
    
    print(f"\n📊 Resultado: {passed}/{len(test_cases)} tests pasados")
    return passed == len(test_cases)

def test_asin():
    """Test asin() contra valores conocidos."""
    print("\n📐 TEST: asin() - Valores Conocidos")
    print("=" * 60)
    
    test_cases = [
        (0.0, 0.0),
        (0.5, 30.0),       # asin(1/2) = 30°
        (0.707107, 45.0),  # asin(√2/2) = 45°
        (0.866025, 60.0),  # asin(√3/2) = 60°
        (1.0, 90.0),       # asin(1) = 90°
    ]
    
    passed = 0
    for x_val, expected_deg in test_cases:
        try:
            x_int = int(x_val * S60.SCALE_0)
            x = S60._from_raw(x_int)
            
            result = S60Math.asin(x)
            result_val = result.to_base_units() / S60.SCALE_0
            error = abs(result_val - expected_deg)
            rel_error = (error / abs(expected_deg)) * 100 if expected_deg != 0 else error
            
            status = "✅" if rel_error < 5.0 else "❌"
            print(f"{status} asin({x_val:.4f}) = {result_val:.2f}° (esperado: {expected_deg:.2f}°, error: {rel_error:.4f}%)")
            
            if rel_error < 5.0:
                passed += 1
        except Exception as e:
            print(f"❌ asin({x_val}) - Error: {e}")
    
    print(f"\n📊 Resultado: {passed}/{len(test_cases)} tests pasados")
    return passed == len(test_cases)

def test_acos():
    """Test acos() contra valores conocidos."""
    print("\n📐 TEST: acos() - Valores Conocidos")
    print("=" * 60)
    
    test_cases = [
        (1.0, 0.0),        # acos(1) = 0°
        (0.866025, 30.0),  # acos(√3/2) = 30°
        (0.707107, 45.0),  # acos(√2/2) = 45°
        (0.5, 60.0),       # acos(1/2) = 60°
        (0.0, 90.0),       # acos(0) = 90°
    ]
    
    passed = 0
    for x_val, expected_deg in test_cases:
        try:
            x_int = int(x_val * S60.SCALE_0)
            x = S60._from_raw(x_int)
            
            result = S60Math.acos(x)
            result_val = result.to_base_units() / S60.SCALE_0
            error = abs(result_val - expected_deg)
            rel_error = (error / abs(expected_deg)) * 100 if expected_deg != 0 else error
            
            status = "✅" if rel_error < 5.0 else "❌"
            print(f"{status} acos({x_val:.4f}) = {result_val:.2f}° (esperado: {expected_deg:.2f}°, error: {rel_error:.4f}%)")
            
            if rel_error < 5.0:
                passed += 1
        except Exception as e:
            print(f"❌ acos({x_val}) - Error: {e}")
    
    print(f"\n📊 Resultado: {passed}/{len(test_cases)} tests pasados")
    return passed == len(test_cases)

def test_atan2():
    """Test atan2() para conversión de coordenadas."""
    print("\n📐 TEST: atan2() - Cuadrantes")
    print("=" * 60)
    
    test_cases = [
        (1, 1, 45),      # Cuadrante I
        (1, -1, 135),    # Cuadrante II
        (-1, -1, -135),  # Cuadrante III
        (-1, 1, -45),    # Cuadrante IV
        (1, 0, 90),      # Eje Y positivo
        (0, 1, 0),       # Eje X positivo
    ]
    
    passed = 0
    for y, x, expected_deg in test_cases:
        try:
            y_s60 = S60(y)
            x_s60 = S60(x)
            
            result = S60Math.atan2(y_s60, x_s60)
            result_val = result.to_base_units() / S60.SCALE_0
            error = abs(result_val - expected_deg)
            
            status = "✅" if error < 10 else "❌"  # Tolerancia de 10°
            print(f"{status} atan2({y}, {x}) = {result_val:.2f}° (esperado: {expected_deg}°, error: {error:.2f}°)")
            
            if error < 10:
                passed += 1
        except Exception as e:
            print(f"❌ atan2({y}, {x}) - Error: {e}")
    
    print(f"\n📊 Resultado: {passed}/{len(test_cases)} tests pasados")
    return passed == len(test_cases)

def main():
    """Ejecuta todos los tests de funciones adicionales."""
    print("\n🛡️ TESTS: Funciones Trigonométricas Adicionales")
    print("=" * 60)
    
    results = {
        "tan()": test_tan(),
        "atan()": test_atan(),
        "asin()": test_asin(),
        "acos()": test_acos(),
        "atan2()": test_atan2(),
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
        print("⚠️  ALGUNOS TESTS FALLARON (puede requerir ajustes)")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
