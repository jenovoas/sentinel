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
        "quantum/yatra_math.py",
        "quantum/core_simulator.py",
        "quantum/sentinel_quantum_core.py",
        "quantum/hexagonal_control.py",
        "quantum/vimana_drone_sim.py",
        "quantum/vimana_orbital_ascent_sim.py",
        "quantum/vimana_mission_sim.py",
        "quantum/vimana_shield_validation.py",
        "quantum/zpe_simulation.py",
        "quantum/zpe_phase1_lab.py",
        "quantum/observer_effect_study.py",
        "quantum/verify_meijer_scale.py",
        "quantum/quantum_scanner.py",
        "quantum/time_crystal_analysis.py",
        "quantum/quantum_lattice.py"
    ]
    
    BACKUP_DIR = "quantum/.yatra_backup"

    def __init__(self, root_dir=None):
        if root_dir is None:
            # Detect root dir from current file path
            self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.root_dir = root_dir
            
        self.backup_path = os.path.join(self.root_dir, self.BACKUP_DIR)
        
        # Crear directorio de snapshots seguros
        if not os.path.exists(self.backup_path):
            os.makedirs(self.backup_path)
            
        print(f"🛡️ YATRA-GUARD ACTIVADO en {self.root_dir}. Vigilando el Canon Soberano.")

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
        """Escanea un archivo en busca de literales float prohibidos y librerías sucias."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
                
            for node in ast.walk(tree):
                # 1. Detección de Float (Fricción)
                if isinstance(node, ast.Constant) and isinstance(node.value, float):
                    # Permitir 0.0 y 1.0 solo si es absolutamente necesario (idealmente usar S60(0/1))
                    if node.value in [0.0, 1.0]: continue
                    if not silent:
                        print(f"   🚨 CONTAMINACIÓN: {filepath}")
                        print(f"      Línea {node.lineno}: DECIMAL detectado '{node.value}'")
                    return False
                
                # 2. Detección de Librerías Sucias (NumPy, SciPy, Random, Matplotlib, Math)
                # WHITELIST: yatra_math está permitido (es nuestro)
                dirty_libs = ['numpy', 'scipy', 'matplotlib', 'random']
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Bloquear 'import math' pero permitir 'import quantum.yatra_math'
                        if alias.name == 'math':
                            if not silent:
                                print(f"   🚨 CONTAMINACIÓN: {filepath}")
                                print(f"      Línea {node.lineno}: 'import math' prohibido (usa yatra_math).")
                            return False
                        # Bloquear otras librerías sucias
                        if any(lib in alias.name for lib in dirty_libs):
                            if not silent:
                                print(f"   🚨 CONTAMINACIÓN: {filepath}")
                                print(f"      Línea {node.lineno}: Importación de '{alias.name}' prohibida.")
                            return False
                if isinstance(node, ast.ImportFrom):
                    # Permitir 'from quantum.yatra_math import ...'
                    if node.module and 'yatra_math' in node.module:
                        continue  # Permitido
                    # Bloquear 'from math import ...'
                    if node.module == 'math':
                        if not silent:
                            print(f"   🚨 CONTAMINACIÓN: {filepath}")
                            print(f"      Línea {node.lineno}: 'from math import' prohibido (usa yatra_math).")
                        return False
                    # Bloquear otras librerías sucias
                    if any(lib in (node.module or '') for lib in dirty_libs):
                        if not silent:
                            print(f"   🚨 CONTAMINACIÓN: {filepath}")
                            print(f"      Línea {node.lineno}: Importación desde '{node.module}' prohibida.")
                        return False
                
                # 3. Detección de .to_float() (método que no existe en S60)
                if isinstance(node, ast.Attribute):
                    if node.attr == 'to_float':
                        if not silent:
                            print(f"   🚨 CONTAMINACIÓN: {filepath}")
                            print(f"      Línea {node.lineno}: Llamada a '.to_float()' prohibida (método no existe en S60).")
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
        print("\n👮 EJECUTANDO PATRULLA SOBERANA...")
        violations = 0
        
        for rel_path in self.PROTECTED_FILES:
            full_path = os.path.join(self.root_dir, rel_path)
            backup_file = os.path.join(self.backup_path, os.path.basename(rel_path))
            
            if not os.path.exists(full_path):
                continue
                
            is_pure = self.check_purity(full_path)
            
            if not is_pure:
                print(f"   🛑 VIOLACIÓN EN {rel_path}!")
                violations += 1
                
                if os.path.exists(backup_file):
                    print(f"   ♻️  RESTAURANDO ESTADO PURO...")
                    shutil.copy2(backup_file, full_path)
                else:
                    print(f"   ❌ SIN RESPALDO PURO. ¡SISTEMA EXPUESTO!")
            else:
                pass # Puro
                
        if violations == 0:
            print("🏆 SECTOR SEGURO: 100% SOBERANÍA DETECTADA.")
        else:
            print(f"⚠️ PATRULLA FINALIZADA: {violations} Incursiones repelidas.")

if __name__ == "__main__":
    guard = YatraGuard()
    # 1. Primero intentamos guardar el estado actual si es puro (bootstrapping)
    guard.snapshot_purity()
    
    # 2. Ejecutar patrulla
    guard.patrol()