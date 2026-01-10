#!/usr/bin/env python3
"""
🧪 TEST: Pre-Commit Hook de YatraGuard
======================================
Demuestra el funcionamiento del pre-commit hook.

Este script simula un commit con contaminación para mostrar
cómo YatraGuard bloquea automáticamente el commit.
"""

import os
import sys
import subprocess
import tempfile
import shutil

def test_hook_blocks_contamination():
    """Test que demuestra cómo el hook bloquea contaminación."""
    print("\n🧪 TEST: YatraGuard Pre-Commit Hook")
    print("=" * 60)
    
    # Crear archivo temporal con contaminación
    test_file = "quantum/test_contamination_temp.py"
    contaminated_code = """#!/usr/bin/env python3
# Archivo de prueba con CONTAMINACIÓN INTENCIONAL
import math  # ← ESTO DEBERÍA SER BLOQUEADO

def bad_function():
    x = 3.14159  # ← FLOAT LITERAL
    return math.sin(x)  # ← USO DE MATH
"""
    
    print("\n📝 Paso 1: Crear archivo con contaminación intencional")
    print(f"   Archivo: {test_file}")
    
    with open(test_file, 'w') as f:
        f.write(contaminated_code)
    
    print("   ✅ Archivo creado con:")
    print("      - import math")
    print("      - literal float (3.14159)")
    print("      - uso de math.sin()")
    
    # Intentar agregar al staging
    print("\n📝 Paso 2: Agregar archivo al staging area")
    try:
        subprocess.run(['git', 'add', test_file], check=True, capture_output=True)
        print("   ✅ Archivo agregado al staging")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Intentar commit (el hook debería bloquearlo)
    print("\n📝 Paso 3: Intentar commit (el hook debería bloquearlo)")
    print("   Ejecutando: git commit -m 'Test contamination'")
    print("\n" + "-" * 60)
    
    result = subprocess.run(
        ['git', 'commit', '-m', 'Test: contaminación intencional'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    print("-" * 60)
    
    # Verificar que el commit fue bloqueado
    if result.returncode != 0:
        print("\n✅ ÉXITO: El hook bloqueó el commit correctamente")
        print("   El archivo contaminado NO fue commiteado")
    else:
        print("\n❌ FALLO: El hook NO bloqueó el commit")
        print("   Esto no debería pasar")
    
    # Limpiar
    print("\n📝 Paso 4: Limpiar archivos de prueba")
    try:
        subprocess.run(['git', 'reset', 'HEAD', test_file], check=True, capture_output=True)
        os.remove(test_file)
        print("   ✅ Archivos de prueba eliminados")
    except Exception as e:
        print(f"   ⚠️  Error limpiando: {e}")
    
    print("\n" + "=" * 60)
    return result.returncode != 0

def test_hook_allows_clean_code():
    """Test que demuestra cómo el hook permite código limpio."""
    print("\n🧪 TEST: Código Limpio (Debería Pasar)")
    print("=" * 60)
    
    test_file = "quantum/test_clean_temp.py"
    clean_code = """#!/usr/bin/env python3
# Archivo de prueba LIMPIO
from quantum.yatra_core import S60
from quantum.yatra_math import S60Math

def good_function():
    x = S60(3, 8, 29, 44, 0)  # PI en S60
    return S60Math.sin(x)  # ← USO CORRECTO
"""
    
    print("\n📝 Creando archivo limpio...")
    with open(test_file, 'w') as f:
        f.write(clean_code)
    
    print("   ✅ Archivo creado con:")
    print("      - from quantum.yatra_math import S60Math")
    print("      - S60 en lugar de floats")
    print("      - S60Math.sin() en lugar de math.sin()")
    
    try:
        subprocess.run(['git', 'add', test_file], check=True, capture_output=True)
        print("\n📝 Intentando commit...")
        
        result = subprocess.run(
            ['git', 'commit', '-m', 'Test: código limpio'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ ÉXITO: El hook permitió el commit")
            # Deshacer el commit
            subprocess.run(['git', 'reset', 'HEAD~1'], check=True, capture_output=True)
        else:
            print("❌ El hook bloqueó código limpio (no debería)")
        
        # Limpiar
        subprocess.run(['git', 'reset', 'HEAD', test_file], capture_output=True)
        os.remove(test_file)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return result.returncode == 0

if __name__ == "__main__":
    print("\n🛡️ DEMOSTRACIÓN: YatraGuard Pre-Commit Hook")
    print("=" * 60)
    print("Este test demuestra cómo el hook protege el repositorio")
    print("bloqueando commits con contaminación decimal.")
    print("=" * 60)
    
    # Test 1: Bloquear contaminación
    success1 = test_hook_blocks_contamination()
    
    # Test 2: Permitir código limpio
    # success2 = test_hook_allows_clean_code()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN:")
    print(f"   Test 1 (Bloquear contaminación): {'✅ PASÓ' if success1 else '❌ FALLÓ'}")
    # print(f"   Test 2 (Permitir código limpio): {'✅ PASÓ' if success2 else '❌ FALLÓ'}")
    print("=" * 60)
    
    sys.exit(0 if success1 else 1)
