#!/usr/bin/env python3
"""
🧪 SUITE COMPLETA DE TESTS - Sentinel Quantum
==============================================
Ejecuta todos los tests de validación en secuencia.
"""

import sys
import subprocess

def run_test(test_name, description):
    """Ejecuta un test y retorna el resultado."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', f'quantum.{test_name}'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"❌ TIMEOUT: {test_name} tomó más de 30 segundos")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Ejecuta todos los tests."""
    print("\n🛡️ SENTINEL QUANTUM - SUITE COMPLETA DE TESTS")
    print("="*60)
    print("Ejecutando todos los tests de validación...")
    print("="*60)
    
    tests = [
        ("test_yatra_math_precision", "Tests de Precisión Matemática (sin, cos, sqrt, exp, ln)"),
        ("test_trig_additional", "Tests de Funciones Trigonométricas Adicionales"),
        ("test_tensor_product", "Tests de Producto de Kronecker"),
        ("test_qaoa_s60", "Tests de Optimización QAOA"),
        ("test_quantum_lattice_engine", "Tests del Motor de Red Cuántica"),
    ]
    
    results = {}
    
    for test_name, description in tests:
        passed = run_test(test_name, description)
        results[description] = passed
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE TESTS")
    print("="*60)
    
    for name, passed in results.items():
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"{status}: {name}")
    
    all_passed = all(results.values())
    passed_count = sum(results.values())
    total_count = len(results)
    
    print("\n" + "="*60)
    if all_passed:
        print(f"🏆 TODOS LOS TESTS PASARON ({passed_count}/{total_count})")
        print("   Sentinel Quantum está validado y listo para producción")
    else:
        print(f"⚠️  ALGUNOS TESTS FALLARON ({passed_count}/{total_count} pasaron)")
        print("   Revisar errores arriba")
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
