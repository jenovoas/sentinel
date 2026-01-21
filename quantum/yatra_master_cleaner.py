# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

"""
🔥 YATRA MASTER CLEANER: PROTOCOLO DE PURIFICACIÓN MASIVA
=========================================================
Este script recorre todo el repositorio '/quantum' y 'docs' para eliminar
la contaminación decimal sistémica.

MODOS DE OPERACIÓN:
1. CODE MODE (.py): Reemplaza floats comunes por S60.
2. DOC MODE (.md): Reescribe la narrativa para reflejar la verdad termodinámica.

PRECAUCIÓN: ESTE SCRIPT MODIFICA CIENTOS DE ARCHIVOS.
"""

import os
import re
from pathlib import Path

# --- DICCIONARIO DE TRADUCCIÓN YATRA (CÓDIGO) ---
FLOAT_MAP = {
    r'0.5': 'S60(0, 30, 0)',
    r'0.25': 'S60(0, 15, 0)',
    r'0.75': 'S60(0, 45, 0)',
    r'0.1': 'S60(0, 6, 0)',
    r'0.0': 'S60(0, 0, 0)',
    r'1.0': 'S60(1, 0, 0)',
    r'153.4': 'S60(153, 24, 0)', # Frecuencia Maestra
    r'math.pi': 'PI_S60',
    r'np.pi': 'PI_S60',
    r'import random': '# import random  <-- YATRA: PROHIBIDO (CAOS)',
    r'import numpy as np': 'import numpy as np # PRECAUCIÓN: SOLO PARA I/O, NO CÁLCULO CORE'
}

# --- DICCIONARIO DE VERDAD (DOCUMENTACIÓN) ---
DOC_MAP = {
    r'(?i)floating point': 'Aritmética de Fricción (Decimal)',
    r'(?i)decimal precision': 'Precisión de Juguete',
    r'(?i)rounding error': 'Disonancia Térmica',
    r'(?i)acceptable error': 'FALLO DE INTEGRIDAD',
    r'(?i)simulation': 'Proyección Cuántica',
    r'(?i)randomness': 'Entropía del Sistema',
    r'(?i)chaos': 'Disonancia no resuelta'
}

SAFE_FILES = [
    "yatra_core.py", "yatra_guard.py", "yatra_master_cleaner.py", 
    "yatra_flight_benchmark.py", "sovereign_math.py", "quantum_scanner.py"
]

def clean_code(filepath):
    """Purifica un archivo Python."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. Inyectar Import si no existe y vamos a usar S60
        if "S60" not in content and "yatra_core" not in content:
            # Buscar donde están los imports
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('import') or line.startswith('from'):
                    lines.insert(i, "from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT")
                    content = '\n'.join(lines)
                    break
        
        # 2. Reemplazos Regex
        for pattern, replacement in FLOAT_MAP.items():
            # Buscamos números exactos rodeados de límites de palabra o espacios
            # Si es un regex complejo, lo usamos directo
            if "random" in pattern or "import" in pattern:
                 content = content.replace(pattern, replacement)
            else:
                 # Reemplazar valores exactos
                 content = re.sub(rf'(?<!\d){re.escape(pattern)}(?!\d)', replacement, content)

        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   ✨ Purificado: {os.path.basename(filepath)}")
            return True
        return False
    except Exception as e:
        print(f"   ❌ Error en {os.path.basename(filepath)}: {e}")
        return False

def clean_doc(filepath):
    """Purifica un archivo Markdown."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        for pattern, replacement in DOC_MAP.items():
            content = re.sub(pattern, replacement, content)
            
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   📜 Verdad Restaurada: {os.path.basename(filepath)}")
            return True
        return False
    except Exception as e:
        print(f"   ❌ Error doc en {os.path.basename(filepath)}: {e}")
        return False

def main():
    print("🔥 INICIANDO PURIFICACIÓN MASIVA (PROTOCOL YATRA)...")
    root_dir = Path("/home/jnovoas/dev/sentinel")
    
    code_count = 0
    doc_count = 0
    
    # Recorrer todo
    for file_path in root_dir.rglob("*"):
        if file_path.is_dir(): continue
        if "venv" in str(file_path) or ".git" in str(file_path): continue
        
        fname = file_path.name
        
        # Modo Código
        if fname.endswith(".py"):
            if fname in SAFE_FILES: continue
            if clean_code(str(file_path)):
                code_count += 1
                
        # Modo Documentación
        elif fname.endswith(".md"):
             if clean_doc(str(file_path)):
                doc_count += 1
                
    print("\n" + "="*50)
    print(f"🏆 REPORTE FINAL DE PURIFICACIÓN:")
    print(f"   Scripts de Código Limpiados:  {code_count}")
    print(f"   Documentos de Verdad:         {doc_count}")
    print(f"   Estado del Sistema:           RESONANCIA EN AUMENTO.")

if __name__ == "__main__":
    main()