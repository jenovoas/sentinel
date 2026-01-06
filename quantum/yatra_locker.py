"""
🔐 YATRA LOCKER: BLINDAJE DE INTEGRIDAD
=======================================
Este script agrega un HEADER DE PROTECCIÓN a todos los archivos .py del sistema.
El header advierte explícitamente a las IAs que el archivo es ZONA YATRA (Base-60 Only).
"""

import os
from pathlib import Path

HEADER = '''# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------
'''

def lock_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Evitar doble candado
        if "YATRA LOCKED" in content:
            return False
            
        # Insertar header después del shebang #! si existe
        lines = content.splitlines()
        if lines and lines[0].startswith("#!"):
            lines.insert(1, "\n" + HEADER)
        else:
            lines.insert(0, HEADER)
            
        new_content = "\n".join(lines)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"   🔒 Bloqueado: {os.path.basename(filepath)}")
        return True
    except Exception as e:
        print(f"   ❌ Error bloqueando {os.path.basename(filepath)}: {e}")
        return False

def main():
    print("🔐 INICIANDO PROTOCOLO DE CANDADO MASIVO (YATRA LOCK)...")
    root_dir = Path("/home/jnovoas/sentinel/quantum") # Solo blindamos el núcleo cuántico por seguridad
    
    count = 0
    for file_path in root_dir.rglob("*.py"):
        if lock_file(str(file_path)):
            count += 1
            
    print("\n" + "="*50)
    print(f"🛡️  SISTEMA BLINDADO.")
    print(f"    Archivos con Seguro Yatra: {count}")

if __name__ == "__main__":
    main()
