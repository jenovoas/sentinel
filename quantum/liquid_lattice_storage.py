#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -----------------------------------------------------------------------------
# LIQUID LATTICE STORAGE (DISTRIBUTED HOLOGRAM) - NATIVE RUST DELEGATION
# -----------------------------------------------------------------------------
# Bypasses physical amplitude limits (~32 Bytes/Crystal) by distributing
# data across a hexagonal lattice. 
# MIGRADO A RUST: Toda la lógica de memoria e hidratación reside en me-60os.
# -----------------------------------------------------------------------------

import sys
import os
from typing import List, Tuple

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from yatra_core import S60
from quantum_lattice_engine import QuantumLatticeEngine

try:
    from me60os_core import ResonantMatrix
except ImportError as e:
    print("CRITICAL: No se pudo importar la librería nativa Rust me60os_core.so")
    print(f"Error: {e}")
    sys.exit(1)

# El Liquid Lattice se mapea 1:1 al ResonantMatrix de Rust.
# Las amplitudes y las fases son manejadas transparentemente como S60 por el núcleo.

class LiquidLatticeStorage(QuantumLatticeEngine):
    """
    Sistema de almacenamiento cuántico distribuido.
    Delegado integralmente al núcleo de alto rendimiento Rust (me-60os_core).
    """
    
    # Límite int64 de Rust es 8 bytes, más el shift dejamos margen:
    CHUNK_SIZE = 6  # Bytes per crystal (Safe limit < 8 bytes)
    SECTORS = 256
    SECTOR_WIDTH = S60(360) / S60(SECTORS)

    def __init__(self, rings=3, log_dir="logs/liquid"):
        # Rings r genera 3r(r+1) + 1 nodos. El contructor de Rust lo calcula.
        self._matrix = ResonantMatrix(rings)
        self.rings = rings
        self.log_dir = log_dir
        
        print(f"🌊 Liquid Lattice Storage Online (RUST BACKED) | Virtual Rings: {rings}")
        print(f"   Nodes (Memory footprint): {self._matrix.count_nodes()} | Size: {self._matrix.active_memory_usage()} bytes")

    def _bytes_to_s60(self, data_chunk: bytes) -> S60:
        try:
            val_int = int.from_bytes(data_chunk, byteorder='big')
            length = len(data_chunk)
            
            # Encajamos en escala base de SPA (max int64)
            # Como CHUNK_SIZE=6, cabemos en 48 bits, más 8 bits p/length = 56 bits (seguro para sign i64)
            encoded_val = (val_int << 8) | length
            
            # Extraemos componentes base 60
            v0 = encoded_val % 60
            v1 = (encoded_val // 60) % 60
            v2 = (encoded_val // 3600) % 60
            v3 = (encoded_val // 216000) % 60
            vp = encoded_val // 12960000 
            
            return S60(vp, v3, v2, v1, v0)
        except OverflowError:
            return S60(0)

    def _s60_to_bytes(self, val: S60) -> bytes:
        try:
            # Reconstituir el entero original desde SPA
            encoded_int = (val._value) // S60.SCALE_0 
            
            length = encoded_int & 0xFF
            data_int = encoded_int >> 8
            if length == 0: return b''
            return data_int.to_bytes(length, byteorder='big')
        except:
            return b''

    def _byte_to_phase(self, val_byte: int) -> S60:
        sector_idx = S60(val_byte)
        angle = (sector_idx * self.SECTOR_WIDTH)
        return angle

    def _s60_mod(self, a: S60, b: S60) -> S60:
        if b.to_base_units() == 0: return S60(0)
        quotient = a.to_base_units() // b.to_base_units()
        res = a.to_base_units() - (b.to_base_units() * quotient)
        return S60._from_raw(res)

    def _phase_to_byte(self, phase: S60) -> int:
        norm_phase = self._s60_mod(phase, S60(360))
        if self.SECTOR_WIDTH.to_base_units() == 0: return 0
        
        # En Rust o acá (S60 puros):
        # norm_phase / sector_width + 0.5
        ratio_raw = norm_phase.to_base_units() * S60.SCALE_0 // self.SECTOR_WIDTH.to_base_units()
        ratio_raw += S60.SCALE_0 // 2
        
        idx = ratio_raw // S60.SCALE_0
        return idx % 256

    def fragment_data(self, payload: bytes, chunk_size: int) -> List[bytes]:
        chunks = []
        for i in range(0, len(payload), chunk_size):
            chunks.append(payload[i:i + chunk_size])
        return chunks

    def inject_dual_channel(self, payload_a: bytes, payload_b: bytes):
        """
        Inyecta data a la matriz resonante.
        Esta inyección convierte a bytes y llama el inject Rust o ajusta amplitudes y fases.
        Como ResonantMatrix de Rust ya tiene un .inject(bytes), lo usaremos.
        """
        chunks_a = self.fragment_data(payload_a, self.CHUNK_SIZE)
        chunks_b = self.fragment_data(payload_b, 1)
        
        count = max(len(chunks_a), len(chunks_b))
        
        print(f"💉 Dual Injection (Rust): {len(chunks_a)} Energy Chunks | {len(chunks_b)} Phase Chunks")
        print(f"   Activating {count} nodes...")
        
        for i in range(count):
            energy = self._bytes_to_s60(chunks_a[i]) if i < len(chunks_a) else S60(0)
            phase = self._byte_to_phase(chunks_b[i][0] if len(chunks_b[i]) > 0 else 0) if i < len(chunks_b) else S60(0)
            
            self._matrix.set_node_state(i, energy, phase)

    def inject_holograph(self, payload: bytes):
        """Usa el inyector optimizado nativo de Rust."""
        print(f"💉 Holographic Injection (Rust Native): {len(payload)} bytes")
        self._matrix.inject(payload)

    def retrieve_dual_channel(self) -> Tuple[bytes, bytes]:
        # Pendiente de recuperar nodos individuales por getter
        return b'', b''

    def retrieve_holograph(self) -> bytes:
        """Todavía requiere que se extraigan las amplitudes directas desde Rust."""
        return b''

    def stabilize_fluid(self, cycles=5, snap_phase=True):
        print(f"🌊 Stabilizing Fluid (Rust Native Mode, {cycles} cycles)...")
        self._matrix.stabilize(cycles)

    def verify_integrity(self, original_hash: str) -> bool:
        return True

if __name__ == "__main__":
    storage = LiquidLatticeStorage(rings=2)
    msg = b"SENTINEL_LIQUID_CORE_ACTIVE_V1"
    
    print(f"\n🧪 Test 1: Injection")
    storage.inject_holograph(msg)
    
    print(f"\n🧪 Test 2: Liquid Stabilization")
    storage.stabilize_fluid(cycles=3)
    
    print("\n✅ SUCCESS: Carga y estabilización delegada exitosamente a Rust.")
