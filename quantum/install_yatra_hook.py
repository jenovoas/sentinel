#!/usr/bin/env python3
"""
🛡️ YATRA-GUARD: INSTALADOR DE PRE-COMMIT HOOK
==============================================
Instala YatraGuard como pre-commit hook en el repositorio.

Uso:
    python3 install_yatra_hook.py
"""

import os
import sys
import shutil

def main():
    print("\n🛡️ INSTALADOR DE YATRA-GUARD PRE-COMMIT HOOK")
    print("=" * 60)
    
    # Determinar rutas
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    hook_source = os.path.join(script_dir, 'yatra_guard_precommit.py')
    hook_dest = os.path.join(repo_root, '.git', 'hooks', 'pre-commit')
    
    # Verificar que existe el archivo fuente
    if not os.path.exists(hook_source):
        print(f"❌ Error: No se encuentra {hook_source}")
        return 1
    
    # Verificar que existe el directorio de hooks
    hooks_dir = os.path.dirname(hook_dest)
    if not os.path.exists(hooks_dir):
        print(f"❌ Error: No se encuentra el directorio {hooks_dir}")
        print("   ¿Estás en un repositorio git?")
        return 1
    
    # Backup del hook existente si existe
    if os.path.exists(hook_dest):
        backup = hook_dest + '.backup'
        print(f"📦 Creando backup: {backup}")
        shutil.copy2(hook_dest, backup)
    
    # Copiar el hook
    print(f"📝 Instalando hook: {hook_dest}")
    shutil.copy2(hook_source, hook_dest)
    
    # Hacer ejecutable
    os.chmod(hook_dest, 0o755)
    print("✅ Hook instalado y marcado como ejecutable")
    
    # Verificar instalación
    print("\n🔍 Verificando instalación...")
    if os.path.exists(hook_dest) and os.access(hook_dest, os.X_OK):
        print("✅ Pre-commit hook instalado correctamente")
        print("\n📋 El hook se ejecutará automáticamente antes de cada commit.")
        print("   Para desactivarlo temporalmente usa: git commit --no-verify")
        return 0
    else:
        print("❌ Error en la instalación")
        return 1

if __name__ == "__main__":
    sys.exit(main())
