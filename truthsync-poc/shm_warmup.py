#!/usr/bin/env python3
"""
Sentinel SHM Warmup - Page Fault Mitigator
Toca cada página de la memoria compartida para asegurar que esté en RAM física.
"""
import sys
from multiprocessing import shared_memory

def warmup_buffer(name, size):
    try:
        shm = shared_memory.SharedMemory(name=name)
        # Tocar cada página (4KB típicamente)
        for i in range(0, shm.size, 4096):
            _ = shm.buf[i]
        print(f"✅ SHM Warmup completo para {name} ({shm.size} bytes)")
        shm.close()
    except FileNotFoundError:
        print(f"⚠️ SHM {name} no encontrado. Saltando warmup.")
    except Exception as e:
        print(f"❌ Error en warmup: {e}")

if __name__ == "__main__":
    # Buffers críticos identificados hoy
    warmup_buffer("truthsync_shm", 1024*1024)
