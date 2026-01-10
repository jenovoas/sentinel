#!/usr/bin/env python3
"""
🛡️ YATRA-GUARD: PRE-COMMIT HOOK
================================
Git pre-commit hook que valida pureza Yatra antes de cada commit.

Instalación:
    cp quantum/yatra_guard_precommit.py .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit

O usar directamente:
    python3 quantum/yatra_guard_precommit.py
"""

import sys
import os

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantum.yatra_guard import YatraGuard

def main():
    """Ejecuta YatraGuard en archivos staged para commit."""
    print("\n🛡️ YATRA-GUARD PRE-COMMIT VALIDATION")
    print("=" * 60)
    
    guard = YatraGuard()
    
    # Obtener archivos staged
    import subprocess
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True,
            text=True,
            check=True
        )
        staged_files = result.stdout.strip().split('\n')
    except subprocess.CalledProcessError:
        print("⚠️  No se pudo obtener archivos staged. Continuando sin validación.")
        return 0
    
    # Filtrar solo archivos protegidos
    protected_staged = [
        f for f in staged_files 
        if f in guard.PROTECTED_FILES and f.endswith('.py')
    ]
    
    if not protected_staged:
        print("✅ No hay archivos protegidos en este commit.")
        return 0
    
    print(f"\n📋 Validando {len(protected_staged)} archivo(s) protegido(s)...")
    
    violations = 0
    for filepath in protected_staged:
        full_path = os.path.join(guard.root_dir, filepath)
        if not os.path.exists(full_path):
            continue
        
        print(f"\n🔍 Verificando: {filepath}")
        is_pure = guard.check_purity(full_path, silent=False)
        
        if not is_pure:
            violations += 1
            print(f"   ❌ VIOLACIÓN DETECTADA")
        else:
            print(f"   ✅ PURO")
    
    print("\n" + "=" * 60)
    
    if violations > 0:
        print(f"🚫 COMMIT BLOQUEADO: {violations} violación(es) Yatra detectada(s)")
        print("\nPara corregir:")
        print("1. Elimina floats y reemplaza con S60")
        print("2. Elimina import math/random/numpy")
        print("3. Elimina llamadas a .to_float()")
        print("\nO usa: git commit --no-verify (NO RECOMENDADO)")
        return 1
    else:
        print("✅ COMMIT APROBADO: Pureza Yatra verificada")
        return 0

if __name__ == "__main__":
    sys.exit(main())
