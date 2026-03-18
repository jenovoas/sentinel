#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -----------------------------------------------------------------------------
# LIQUID MEMORY ADAPTER - NATIVE RUST DELEGATION
# -----------------------------------------------------------------------------
# Bridging the Interface Gap:
# Uses POSIX shared memory via Rust Core (me-60os_core.PySharedBuffer).
# Integrates with LiquidLatticeStorage (Rust backed) for Data + Phase storage.
# -----------------------------------------------------------------------------

import sys
import os
import hashlib
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from yatra_core import S60
from liquid_lattice_storage import LiquidLatticeStorage
try:
    from gpu_controller import gpu_controller
except ImportError:
    gpu_controller = None

try:
    from me60os_core import PySharedBuffer
    RUST_AVAILABLE = True
except ImportError as e:
    print("CRITICAL: No se pudo importar la librería nativa Rust me60os_core.so")
    print(f"Error: {e}")
    sys.exit(1)

class LiquidMemory:
    """
    High-Level Interface for Sentinel's Cognitive Memory.
    Uses LiquidLatticeStorage as physical medium and PySharedBuffer for IO speed.
    """
    
    def __init__(self, size_scale=1):
        rings = 5 if size_scale <= 1 else 15
        if size_scale >= 10: rings = 50 
        
        print(f"🧠 Liquid Memory Init (RUST BACKED) | Scale: {size_scale} | Rings: {rings}")
        print(f"   Bio-Sync: 17s Pulse | 68s Master Reset")
        
        # El backend es ahora Rust a través de nuestro wrapper adaptado
        self.lattice = LiquidLatticeStorage(rings=rings)
        self.file_table = {} 
        self.active_buffers = []

    def store(self, key: str, data: bytes) -> bool:
        """Stores a named block of data."""
        print(f"🧠 Storing Key: '{key}' ({len(data)} bytes)...")
        try:
            key_hash = hashlib.sha256(key.encode()).digest()
            min_data_len = 32 * 16 # 512 bytes
            
            data_padded = data
            if len(data) < min_data_len:
                padding_needed = min_data_len - len(data)
                data_padded = data + b'\x00' * padding_needed
            
            # 1. Use Shared Buffer for ultra-fast host mapping
            buf_name = f"/liquid_{key_hash[:8].hex()}"
            try:
                # O_CREAT require el nombre con slash "/" en POSIX shm_open standard
                shm = PySharedBuffer(buf_name, len(data_padded), True)
                shm.write(0, data_padded)
                self.active_buffers.append(shm)
                
            except Exception as e:
                print(f"⚠️ SHM Backend Error: {e}. Continuar guardando en Lattice...")

            # 2. Resonant Injection into LiquidLattice
            # Se usa el dual channel para almacenar amplitudes y calcular coherencia
            self.lattice.inject_dual_channel(data_padded, key_hash)
            
            # Estabilizar fase como en bio-sync
            self.lattice.stabilize_fluid(cycles=1)
            
            self.file_table[key] = {
                'len': len(data), 
                'hash': hashlib.sha256(data).hexdigest(),
                'shm_name': buf_name
            }
            return True
            
        except Exception as e:
            print(f"❌ Storage Error: {e}")
            return False

    def retrieve(self, key: str) -> bytes:
        """Retrieves data by key. Si SHM existe, usa SHM para lectura rápida."""
        if key not in self.file_table:
            print(f"⚠️ Key '{key}' not found in virtual table.")
            return None
            
        print(f"🧠 Retrieving Key: '{key}'...")
        file_info = self.file_table[key]
        buf_name = file_info.get('shm_name')
        stored_len = file_info['len']
        
        # Try to read from fast SHM bridge
        try:
            # 512 bytes es el minimo por padding
            read_len = max(stored_len, 512)
            shm = PySharedBuffer(buf_name, read_len, False)
            data = shm.read(0, stored_len)
            shm.close() # No lo borramos, solo cerramos handler de lectura
            return data
        except Exception as e:
            print(f"⚠️ SHM Read Failed for '{key}': {e}. Falling back to Lattice Read.")
        
        # Fallback a Lattice
        data, key_sig = self.lattice.retrieve_dual_channel()
        expected_sig = hashlib.sha256(key.encode()).digest()
        actual_sig = key_sig[:32]
        
        if len(actual_sig) == 32 and actual_sig != expected_sig:
             print(f"⚠️ Security Alert: Phase Signature Mismatch for Key '{key}'")
             
        if len(data) > stored_len:
             data = data[:stored_len]
        
        return data

    def save_snapshot(self, path: str = "liquid_snapshot.s60"):
       """La API ResonantMatrix ya lo maneja por detrás en Rust, pero 
       en este archivo es útil invocar sync_to_shm."""
       pass
        
    def load_snapshot(self, path: str = "liquid_snapshot.s60"):
       pass

    def __del__(self):
        # Limpiar Buffers compartidos asignados de forma segura
        buffers = getattr(self, 'active_buffers', [])
        for buf in buffers:
            try:
                buf.unlink()
            except:
                pass

# Compatibility Wrapper for interaction scripts
def get_memory_service():
    return LiquidMemory()

if __name__ == "__main__":
    memory = LiquidMemory()
    msg = b"MEMORIA_HOLOMORFA_AAS_V1_INIT"
    memory.store("core_system", msg)
    rec_msg = memory.retrieve("core_system")
    print(f"📩 Recuperado: {rec_msg}")
    assert msg == rec_msg
    print("✅ Prueba de Adaptador Liquid Memory exitosa.")
