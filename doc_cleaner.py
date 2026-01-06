#!/usr/bin/env python3
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import os
import re

# Dictionary of hype words and their technical equivalents
REPLACEMENTS = {
    r'militarmente determinista': 'determinista de baja latencia',
    r'inexpugnable': 'seguro por diseño',
    r'infranqueable': 'seguro',
    r'ciencia ficción': 'estado actual de la técnica',
    r'santo grial': 'solución integral',
    r'DIAMOND': 'OPERATIONAL',
    r'SROP': 'PROD',
    r'oro puro': 'verificable',
    r'100,000 veces': 'significativamente',
    r'imposible': 'no factible',
    r'perfecto': 'validado',
    r'absoluto': 'verificado',
    r'estado del arte': 'estándar técnico'
}

def clean_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    for pattern, replacement in REPLACEMENTS.items():
        content = re.sub(pattern, replacement, content, flags=re.I)

    # Specific cleanup for remaining "SROP" etc
    content = re.sub(r'SROP\s+DIAMOND', 'STABLE PRODUCTION', content, flags=re.I)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("🧹 Sentinel Doc Refiner: Eliminando retórica innecesaria...")
    count = 0
    for root, _, files in os.walk('.'):
        if '.git' in root or '.venv' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                if clean_file(path):
                    print(f"✅ Refinado: {path}")
                    count += 1
    
    print(f"\n✨ Limpieza completada. {count} archivos actualizados.")

if __name__ == "__main__":
    main()
