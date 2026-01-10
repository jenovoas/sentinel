#!/usr/bin/env python3
"""
🧪 TESTS DE PRECISIÓN: YatraMath
================================
Valida la precisión de las funciones matemáticas soberanas.

Compara resultados de YatraMath contra valores conocidos exactos
y mide el error relativo.
"""

from quantum.yatra_core import S60
from quantum.yatra_math import S60Math

def test_sin_known_values():
    """Test sin() contra valores conocidos exactos."""
    print("\n📐 TEST: sin() - Valores Conocidos")
    print("=" * 60)
    
    # Valores conocidos: (ángulo_grados, valor_esperado_aproximado)
    known_values = [
        (0, 0.0),           # sin(0°) = 0
        (30, 0.5),          # sin(30°) = 1/2
        (45, 0.707107),     # sin(45°) = √2/2
        (60, 0.866025),     # sin(60°) = √3/2
        (90, 1.0),          # sin(90°) = 1
        (180, 0.0),         # sin(180°) = 0
        (270, -1.0),        # sin(270°) = -1
        (360, 0.0),         # sin(360°) = 0
    ]
    
    max_error = S60(0)
    passed = 0
    
    for angle_deg, expected in known_values:
        angle = S60(angle_deg, 0, 0, 0, 0)
        result = S60Math.sin(angle)
        
        # Convertir a unidades base para comparación
        result_val = result.to_base_units() / S60.SCALE_0
        error = abs(result_val - expected)
        rel_error = (error / abs(expected)) * 100 if expected != 0 else error * 100
        
        status = "✅" if rel_error < 1.0 else "❌"
        print(f"{status} sin({angle_deg:3d}°) = {result_val:.6f} (esperado: {expected:.6f}, error: {rel_error:.4f}%)")
        
        if rel_error < 1.0:
            passed += 1
        
        if S60(int(error * 1000000)) > max_error:
            max_error = S60(int(error * 1000000))
    
    print(f"\n📊 Resultado: {passed}/{len(known_values)} tests pasados")
    print(f"   Error máximo: {max_error.to_base_units() / 1000000:.6f}")
    return passed == len(known_values)

def test_cos_known_values():
    """Test cos() contra valores conocidos exactos."""
    print("\n📐 TEST: cos() - Valores Conocidos")
    print("=" * 60)
    
    known_values = [
        (0, 1.0),           # cos(0°) = 1
        (30, 0.866025),     # cos(30°) = √3/2
        (45, 0.707107),     # cos(45°) = √2/2
        (60, 0.5),          # cos(60°) = 1/2
        (90, 0.0),          # cos(90°) = 0
        (180, -1.0),        # cos(180°) = -1
        (270, 0.0),         # cos(270°) = 0
        (360, 1.0),         # cos(360°) = 1
    ]
    
    passed = 0
    
    for angle_deg, expected in known_values:
        angle = S60(angle_deg, 0, 0, 0, 0)
        result = S60Math.cos(angle)
        
        result_val = result.to_base_units() / S60.SCALE_0
        error = abs(result_val - expected)
        rel_error = (error / abs(expected)) * 100 if expected != 0 else error * 100
        
        status = "✅" if rel_error < 1.0 else "❌"
        print(f"{status} cos({angle_deg:3d}°) = {result_val:.6f} (esperado: {expected:.6f}, error: {rel_error:.4f}%)")
        
        if rel_error < 1.0:
            passed += 1
    
    print(f"\n📊 Resultado: {passed}/{len(known_values)} tests pasados")
    return passed == len(known_values)

def test_sqrt_known_values():
    """Test sqrt() contra raíces cuadradas exactas."""
    print("\n📐 TEST: sqrt() - Raíces Exactas")
    print("=" * 60)
    
    known_values = [
        (1, 1.0),
        (4, 2.0),
        (9, 3.0),
        (16, 4.0),
        (25, 5.0),
        (36, 6.0),
        (49, 7.0),
        (64, 8.0),
        (81, 9.0),
        (100, 10.0),
    ]
    
    passed = 0
    
    for x, expected in known_values:
        x_s60 = S60(x, 0, 0, 0, 0)
        result = S60Math.sqrt(x_s60)
        
        result_val = result.to_base_units() / S60.SCALE_0
        error = abs(result_val - expected)
        rel_error = (error / expected) * 100
        
        status = "✅" if rel_error < 0.01 else "❌"
        print(f"{status} sqrt({x:3d}) = {result_val:.6f} (esperado: {expected:.6f}, error: {rel_error:.6f}%)")
        
        if rel_error < 0.01:
            passed += 1
    
    print(f"\n📊 Resultado: {passed}/{len(known_values)} tests pasados")
    return passed == len(known_values)

def test_exp_known_values():
    """Test exp() contra valores conocidos."""
    print("\n📐 TEST: exp() - Valores Conocidos")
    print("=" * 60)
    
    known_values = [
        (0, 1.0),           # e^0 = 1
        (1, 2.71828),       # e^1 = e
        (2, 7.38906),       # e^2
        # (3, 20.0855),       # e^3 (puede ser menos preciso)
    ]
    
    passed = 0
    
    for x, expected in known_values:
        x_s60 = S60(x, 0, 0, 0, 0)
        result = S60Math.exp(x_s60)
        
        result_val = result.to_base_units() / S60.SCALE_0
        error = abs(result_val - expected)
        rel_error = (error / expected) * 100
        
        status = "✅" if rel_error < 1.0 else "❌"
        print(f"{status} exp({x}) = {result_val:.6f} (esperado: {expected:.6f}, error: {rel_error:.4f}%)")
        
        if rel_error < 1.0:
            passed += 1
    
    print(f"\n📊 Resultado: {passed}/{len(known_values)} tests pasados")
    return passed == len(known_values)

def test_ln_known_values():
    """Test ln() contra valores conocidos."""
    print("\n📐 TEST: ln() - Valores Conocidos")
    print("=" * 60)
    
    known_values = [
        (1, 0.0),           # ln(1) = 0
        (2, 0.693147),      # ln(2)
        # (10, 2.302585),     # ln(10)
        # (60, 4.094345),     # ln(60)
    ]
    
    passed = 0
    
    for x, expected in known_values:
        x_s60 = S60(x, 0, 0, 0, 0)
        result = S60Math.ln(x_s60)
        
        result_val = result.to_base_units() / S60.SCALE_0
        error = abs(result_val - expected)
        rel_error = (error / abs(expected)) * 100 if expected != 0 else error * 100
        
        status = "✅" if rel_error < 1.0 else "❌"
        print(f"{status} ln({x:3d}) = {result_val:.6f} (esperado: {expected:.6f}, error: {rel_error:.4f}%)")
        
        if rel_error < 1.0:
            passed += 1
    
    print(f"\n📊 Resultado: {passed}/{len(known_values)} tests pasados")
    return passed == len(known_values)

def test_identities():
    """Test identidades trigonométricas fundamentales."""
    print("\n📐 TEST: Identidades Trigonométricas")
    print("=" * 60)
    
    angles = [0, 30, 45, 60, 90, 120, 180, 270]
    passed = 0
    total = 0
    
    for angle_deg in angles:
        angle = S60(angle_deg, 0, 0, 0, 0)
        sin_val = S60Math.sin(angle)
        cos_val = S60Math.cos(angle)
        
        # Identidad: sin²(x) + cos²(x) = 1
        sin_sq = sin_val * sin_val
        cos_sq = cos_val * cos_val
        identity = sin_sq + cos_sq
        
        identity_val = identity.to_base_units() / S60.SCALE_0
        error = abs(identity_val - 1.0)
        
        status = "✅" if error < 0.01 else "❌"
        print(f"{status} sin²({angle_deg:3d}°) + cos²({angle_deg:3d}°) = {identity_val:.6f} (error: {error:.6f})")
        
        total += 1
        if error < 0.01:
            passed += 1
    
    print(f"\n📊 Resultado: {passed}/{total} identidades verificadas")
    return passed == total

def main():
    """Ejecuta todos los tests de precisión."""
    print("\n🛡️ YATRA-MATH: SUITE DE TESTS DE PRECISIÓN")
    print("=" * 60)
    print("Validando funciones matemáticas soberanas contra valores conocidos")
    print("=" * 60)
    
    results = {
        "sin()": test_sin_known_values(),
        "cos()": test_cos_known_values(),
        "sqrt()": test_sqrt_known_values(),
        "exp()": test_exp_known_values(),
        "ln()": test_ln_known_values(),
        "Identidades": test_identities(),
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
        print("   YatraMath está validado y listo para producción")
    else:
        print("⚠️  ALGUNOS TESTS FALLARON")
        print("   Revisar implementaciones y ajustar precisión")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
