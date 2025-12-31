#!/usr/bin/env python3
import sys
import os
import time

# Ensure project root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../src/core"))
if project_root not in sys.path:
    sys.path.append(project_root)

from sentinel_core.ebpf.monitor import GuardianMonitor
from sentinel_core.brain.bci_controller import bci_controller

def run_simulation(target_binary):
    print(f"🚀 INICIANDO SIMULACIÓN DE BLOQUEO KERNEL: {target_binary}")
    print("-" * 50)
    
    monitor = GuardianMonitor()
    
    # Simulamos lo que llegaría por el trace_pipe
    # kernel_line = f"bpftool prog show: Guardian [BLOCK]: Unknown binary {target_binary}"
    print(f"📥 [SIM] Kernel detecta ejecución de archivo no autorizado: {target_binary}")
    
    # Lanzamos el proceso de manejo del evento
    monitor._handle_block_event(target_binary)
    
    print("-" * 50)
    print("✅ SIMULACIÓN COMPLETADA.")

if __name__ == "__main__":
    # 1. Test con binario seguro (ej. curl)
    run_simulation("/usr/bin/curl")
    
    time.sleep(2)
    print("\n" + "="*50 + "\n")
    
    # 2. Test con binario sospechoso (ej. rootkit simulado)
    run_simulation("/tmp/hidden_rootkit_installer")
