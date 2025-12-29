#!/usr/bin/env python3
"""
Sentinel Monitor - Direct Execution
Ejecuta el monitor con acceso a los paquetes del usuario
"""
import sys
import os

# Agregar el directorio de paquetes del usuario al path
user_site = "/home/jnovoas/.local/lib/python3.13/site-packages"
if user_site not in sys.path:
    sys.path.insert(0, user_site)

# Ahora importar y ejecutar el monitor
from sentinel_core.ebpf.monitor import GuardianMonitor

def main():
    print("🛡️  [Sentinel] Iniciando Guardian Alpha Monitor...")
    print("=" * 50)
    monitor = GuardianMonitor()
    monitor.start()

if __name__ == "__main__":
    main()
