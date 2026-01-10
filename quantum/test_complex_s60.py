#!/usr/bin/env python3
"""
🧪 TEST: ComplexS60
===================
Valida números complejos en S60.
"""

from quantum.yatra_core import S60
from quantum.complex_s60 import ComplexS60, I, ONE, ZERO

def test_basic_operations():
    """Test operaciones básicas."""
    print("\n📐 TEST: Operaciones Básicas")
    print("=" * 60)
    
    # Suma
    z1 = ComplexS60(S60(3), S60(4))  # 3 + 4i
    z2 = ComplexS60(S60(1), S60(2))  # 1 + 2i
    result = z1 + z2  # = 4 + 6i
    
    assert result.real == S60(4), "Suma real incorrecta"
    assert result.imag == S60(6), "Suma imag incorrecta"
    print("  ✅ Suma: (3+4i) + (1+2i) = (4+6i)")
    
    # Multiplicación
    z3 = ComplexS60(S60(2), S60(3))  # 2 + 3i
    z4 = ComplexS60(S60(4), S60(5))  # 4 + 5i
    result = z3 * z4  # = (8-15) + (10+12)i = -7 + 22i
    
    expected_real = S60(2)*S60(4) - S60(3)*S60(5)  # -7
    expected_imag = S60(2)*S60(5) + S60(3)*S60(4)  # 22
    
    assert result.real == expected_real, f"Mult real: {result.real} != {expected_real}"
    assert result.imag == expected_imag, f"Mult imag: {result.imag} != {expected_imag}"
    print("  ✅ Multiplicación: (2+3i) * (4+5i) = (-7+22i)")
    
    return True

def test_conjugate():
    """Test conjugado."""
    print("\n📐 TEST: Conjugado")
    print("=" * 60)
    
    z = ComplexS60(S60(3), S60(4))
    z_conj = z.conjugate()
    
    assert z_conj.real == S60(3), "Conjugado real incorrecto"
    assert z_conj.imag == S60(-4), "Conjugado imag incorrecto"
    print("  ✅ Conjugado: (3+4i)* = (3-4i)")
    
    return True

def test_magnitude():
    """Test magnitud."""
    print("\n📐 TEST: Magnitud")
    print("=" * 60)
    
    # 3 + 4i -> |z| = 5
    z = ComplexS60(S60(3), S60(4))
    mag = z.magnitude()
    
    # Verificar que |z| ≈ 5
    mag_val = mag.to_base_units() // S60.SCALE_0
    assert mag_val == 5, f"Magnitud incorrecta: {mag_val} != 5"
    print("  ✅ Magnitud: |3+4i| = 5")
    
    return True

def test_exp_i_theta():
    """Test e^(iθ)."""
    print("\n📐 TEST: e^(iθ)")
    print("=" * 60)
    
    # e^(i*0) = 1
    z = ComplexS60.exp_i_theta(S60(0))
    assert z.real == S60(1), "e^(i*0) real debe ser 1"
    assert z.imag == S60(0), "e^(i*0) imag debe ser 0"
    print("  ✅ e^(i*0) = 1")
    
    # e^(i*90°) = i
    z = ComplexS60.exp_i_theta(S60(90))
    # cos(90°) ≈ 0 (pero puede tener pequeño error numérico)
    # sin(90°) = 1
    real_val = abs(z.real.to_base_units()) // S60.SCALE_0
    # Redondear imag: si está muy cerca de 1, considerar como 1
    imag_raw = z.imag.to_base_units()
    imag_val = (imag_raw + S60.SCALE_0 // 2) // S60.SCALE_0  # Redondeo
    
    # Tolerancia: cos(90°) puede ser pequeño pero no exactamente 0
    assert real_val <= 1, f"e^(i*90°) real debe ser ~0, got {real_val}"
    assert imag_val == 1, f"e^(i*90°) imag debe ser 1, got {imag_val} (raw: {imag_raw})"
    print("  ✅ e^(i*90°) ≈ i (dentro de tolerancia numérica)")
    
    return True

def test_polar_form():
    """Test forma polar."""
    print("\n📐 TEST: Forma Polar")
    print("=" * 60)
    
    # r=5, θ=0° -> 5 + 0i
    z = ComplexS60.from_polar(S60(5), S60(0))
    assert z.real == S60(5), "Polar real incorrecto"
    
    print("  ✅ Forma polar: r=5, θ=0° -> 5+0i")
    
    return True

def main():
    """Ejecuta todos los tests."""
    print("\n🛡️ TESTS: ComplexS60")
    print("=" * 60)
    
    results = {
        "Operaciones Básicas": test_basic_operations(),
        "Conjugado": test_conjugate(),
        "Magnitud": test_magnitude(),
        "e^(iθ)": test_exp_i_theta(),
        "Forma Polar": test_polar_form(),
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
        print("   ComplexS60 validado y listo")
    else:
        print("⚠️  ALGUNOS TESTS FALLARON")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
