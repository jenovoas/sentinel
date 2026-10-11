#!/usr/bin/env python3
"""
Populate eBPF LSM Whitelist
Agrega comandos básicos permitidos al whitelist map
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import sys
from bcc import BPF

# Comandos básicos permitidos
ALLOWED_COMMANDS = [
    "ls",
    "cat",
    "echo",
    "pwd",
    "whoami",
    "date",
    "uname",
    "hostname",
    "python",
    "python3",
    "bash",
    "sh",
    "vim",
    "nano",
    "git",
]

def populate_whitelist():
    """Pobla el whitelist map con comandos permitidos"""
    
    print("🔐 Poblando whitelist del eBPF LSM...")
    print("=" * 60)
    
    # Cargar el programa eBPF
    try:
        # Abrir el map desde el pinned location
        whitelist_map = BPF.get_table("/sys/fs/bpf/guardian_alpha", "whitelist_map")
        
        for cmd in ALLOWED_COMMANDS:
            # Convertir comando a bytes (key)
            key = cmd.encode('utf-8').ljust(256, b'\0')
            
            # Valor: 1 = allowed
            value = 1
            
            # Agregar al map
            whitelist_map[key] = value
            
            print(f"✅ Agregado: {cmd}")
        
        print("\n" + "=" * 60)
        print(f"✅ Whitelist poblado con {len(ALLOWED_COMMANDS)} comandos")
        print("\n📋 Comandos permitidos:")
        for cmd in ALLOWED_COMMANDS:
            print(f"   - {cmd}")
        
        print("\n⚠️  Cualquier otro comando será BLOQUEADO")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Asegúrate de que:")
        print("   1. El eBPF LSM esté cargado")
        print("   2. Tengas permisos de root (sudo)")
        print("   3. BCC esté instalado (pip install bcc)")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(populate_whitelist())
