# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------


"""
🛡️ YATRA-GUARD: SISTEMA DE DEFENSA ACTIVA CONTRA FRICCIÓN DECIMAL
================================================================
Este demonio vigila los archivos del núcleo Yatra (Base-60).
Si detecta que una modificación introdujo contaminación decimal (floats),
BLOQUEA EL CAMBIO o REVIERTE AL ESTADO PURO.

Archivos Protegidos (Zona de Exclusión):
- quantum/yatra_core.py
- quantum/vimana_yatra_driver.py
- quantum/celestial_navigation.py
"""

import os
import sys
import time
import ast
import shutil
import hashlib
from typing import List

class YatraGuard:
    PROTECTED_FILES = [
        "quantum/yatra_core.py",
        "quantum/vimana_yatra_driver.py",
        "quantum/celestial_navigation.py",
        "quantum/time_crystal_clock.py"
    ]
    
    BACKUP_DIR = "quantum/.yatra_backup"

    def __init__(self, root_dir="/home/jnovoas/sentinel"):
        self.root_dir = root_dir
        self.backup_path = os.path.join(root_dir, self.BACKUP_DIR)
        
        # Crear directorio de snapshots seguros
        if not os.path.exists(self.backup_path):
            os.makedirs(self.backup_path)
            
        print("🛡️ YATRA-GUARD ACTIVADO. Vigilando la pureza geométrica.")

    def _get_file_hash(self, filepath):
        if not os.path.exists(filepath): return None
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def snapshot_purity(self):
        """Toma una foto de los archivos actuales si son puros."""
        for rel_path in self.PROTECTED_FILES:
            full_path = os.path.join(self.root_dir, rel_path)
            if not os.path.exists(full_path): continue
            
            # Verificar pureza antes de respaldar
            if self.check_purity(full_path, silent=True):
                backup_file = os.path.join(self.backup_path, os.path.basename(rel_path))
                shutil.copy2(full_path, backup_file)
                # print(f"   📸 Snapshot seguro guardado: {rel_path}")

    def check_purity(self, filepath, silent=False) -> bool:
        """Escanea un archivo en busca de literales float prohibidos."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                # 1. Detección de Float (Fricción)
                if isinstance(node, ast.Constant) and isinstance(node.value, float):
                    if node.value in [0.0, 1.0]: continue
                    if not silent:
                        print(f"   🚨 ALERTA DE CONTAMINACIÓN: {filepath}")
                        print(f"      Línea {node.lineno}: DECIMAL detectado '{node.value}'")
                    return False
                
                # 2. Detección de Random (Caos Artificial)
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if 'random' in alias.name:
                            if not silent:
                                print(f"   🚨 ALERTA DE CAOS: {filepath}")
                                print(f"      Línea {node.lineno}: Importación de 'random' prohibida.")
                            return False
                if isinstance(node, ast.ImportFrom):
                    if 'random' in (node.module or ''):
                        if not silent:
                            print(f"   🚨 ALERTA DE CAOS: {filepath}")
                            print(f"      Línea {node.lineno}: Importación desde 'random' prohibida.")
                        return False
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name) and node.value.id == 'np' and node.attr == 'random':
                         if not silent:
                            print(f"   🚨 ALERTA DE CAOS: {filepath}")
                            print(f"      Línea {node.lineno}: Uso de 'np.random' prohibido.")
                         return False

            return True
        except Exception as e:
            if not silent: print(f"   ⚠️ Error leyendo {filepath}: {e}")
            return False

    def patrol(self):
        """
        Ronda de vigilancia. Verifica si los archivos protegidos han sido violados.
        Si están sucios, RESTAURA la copia de seguridad pura.
        """
        print("\n👮 INICIANDO PATRULLA YATRA...")
        violations = 0
        
        for rel_path in self.PROTECTED_FILES:
            full_path = os.path.join(self.root_dir, rel_path)
            backup_file = os.path.join(self.backup_path, os.path.basename(rel_path))
            
            if not os.path.exists(full_path):
                print(f"   ⚠️ Archivo desaparecido: {rel_path}")
                continue
                
            is_pure = self.check_purity(full_path)
            
            if not is_pure:
                print(f"   🛑 ¡VIOLACIÓN DETECTADA EN {rel_path}!")
                violations += 1
                
                if os.path.exists(backup_file):
                    print(f"   ♻️  RESTAURANDO ESTADO PURO DESDE SNAPSHOT...")
                    shutil.copy2(backup_file, full_path)
                    print(f"   ✅ Restauración completada. La disonancia ha sido eliminada.")
                else:
                    print(f"   ❌ NO HAY BACKUP PURO DISPONIBLE. ¡ARCHIVO COMPROMETIDO!")
            else:
                print(f"   ✅ {rel_path}: PURO")
                
        if violations == 0:
            print("🏆 PATRULLA FINALIZADA: Sector Seguro.")
        else:
            print(f"⚠️ PATRULLA FINALIZADA: {violations} Incursiones repelidas.")

if __name__ == "__main__":
    guard = YatraGuard()
    # 1. Primero intentamos guardar el estado actual si es puro (bootstrapping)
    guard.snapshot_purity()
    
    # 2. Ejecutar patrulla
    guard.patrol()