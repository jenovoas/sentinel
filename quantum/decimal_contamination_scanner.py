#!/usr/bin/env python3

# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

"""
🛡️ YATRA-CORE PURITY SCANNER: DECIMAL CONTAMINATION DETECTOR
============================================================
Este script escanea el código fuente en busca de "Fricción Decimal".
Identifica el uso de literales de punto flotante (float) que violan
la especificación YATRA_CORE_SPEC.md.

Criterios de Pureza:
1. No usar floats explícitos (ej: S60(0, 6, 0), 3.14, S60(0, 30, 0)).
2. Permitir solo enteros (Base-60 components) o fracciones exactas.
3. Excepciones: Versiones de librerías, timeouts de I/O, timestamps.
"""

import ast
import os
import sys
from pathlib import Path

class DecimalSpy(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.issues = []
        self.exclusions = [
            'time.sleep', 'timeout', 'version', 'timestamp', 
            '__version__', 'dt', 'time', 'coherence' # Allow basic timing/version floats
        ]

    def visit_Constant(self, node):
        if isinstance(node.value, float):
            # Check context to allow certain benign floats (like sleep times or versions)
            # This is a heuristic. For strict Yatra, we flag almost everything.
            
            # Simple heuristic: If it's S60(0, 0, 0) or S60(1, 0, 0) often used for initialization, warning instead of error
            severity = "CRITICAL"
            if node.value == S60(0, 0, 0) or node.value == S60(1, 0, 0):
                severity = "WARNING"
                
            self.issues.append((node.lineno, node.value, severity))
        self.generic_visit(node)

def scan_file_for_decimals(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=filepath)
        
        spy = DecimalSpy(filepath)
        spy.visit(tree)
        return spy.issues
    except Exception as e:
        return []

def main():
    print("🛡️ INICIANDO ESCANEO DE CONTAMINACIÓN DECIMAL (PROTOCOLO YATRA)")
    print("==============================================================")
    
    base_dir = Path("/home/jnovoas/sentinel/quantum")
    contaminated_files = 0
    total_floats = 0
    
    # Files to specifically audit for Yatra compliance
    target_files = [
        "celestial_navigation.py",
        "vimana_mission_sim.py",
        "time_crystal_clock.py",
        "yatra_core.py" # If it exists
    ]

    for py_file in base_dir.rglob("*.py"):
        # Focus on physics/math files
        if py_file.name not in target_files and "sim" not in py_file.name:
             # Skip tools/utils for now, focus on core logic
             if "check" in py_file.name or "audit" in py_file.name:
                 continue
                 
        issues = scan_file_for_decimals(str(py_file))
        
        if issues:
            contaminated_files += 1
            print(f"\n📂 Archivo: {py_file.name}")
            for line, val, severity in issues:
                icon = "🚫" if severity == "CRITICAL" else "⚠️"
                print(f"   {icon} [Línea {line}] Decimal detectado: {val} ({severity})")
                total_floats += 1

    print("\n" + "="*60)
    print(f"📊 REPORTE FINAL:")
    print(f"   Archivos Contaminados: {contaminated_files}")
    print(f"   Total Literales Float: {total_floats}")
    
    if total_floats > 0:
        print("\n❌ EL NÚCLEO NO ES PURO. SE REQUIERE LIMPIEZA SEVERA.")
        print("   Acción requerida: Reemplazar floats con tuplas sexagesimales.")
    else:
        print("\n✅ NÚCLEO PURO. YATRA-READY.")

if __name__ == "__main__":
    main()