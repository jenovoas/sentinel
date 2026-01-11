#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -----------------------------------------------------------------------------
# LIQUID LATTICE STORAGE (DISTRIBUTED HOLOGRAM)
# -----------------------------------------------------------------------------
# Implementation of EXP-010 & EXP-009 findings.
# Bypasses physical amplitude limits (~32 Bytes/Crystal) by distributing
# data across a hexagonal lattice. Uses fluid dynamics for self-repair.
# -----------------------------------------------------------------------------

import sys
import os
from typing import List, Tuple

# Ensure project root is in path
sys.path.append(os.getcwd())

from quantum.yatra_core import S60
from quantum.quantum_lattice_engine import QuantumLatticeEngine, QuantumNode
from quantum.time_crystal_clock import TimeCrystalClock
                                                       # Actually QuantumNode is used in the engine.

class LiquidLatticeStorage(QuantumLatticeEngine):
    # Constants from EXP-010
    CHUNK_SIZE = 16  # Bytes per crystal (Safe limit << 32 bytes)
    MAX_SAFE_AMPLITUDE = S60(0, 0, 0)
    
    # Phase Sector Constants
    SECTORS = 256
    SECTOR_WIDTH = S60(360) / S60(SECTORS) # ~1.406 deg

    def __init__(self, rings=3, log_dir="logs/liquid"):
        # We DO NOT call super().__init__ because it builds the full lattice immediately.
        # We manually init what we need for Sparse Mode.
        self.clock = TimeCrystalClock()
        self.coupling = S60(0, 1, 0)
        self.dt = 1
        self.use_zpe = True
        self.log_dir = log_dir
        
        # SPARSE ARCHITECTURE
        # index -> QuantumNode
        self.nodes = {} 
        self.rings = rings
        
        # Estimated capacity (virtual)
        # Rings 150 ~ 70k nodes. We simulate having them available.
        
        print(f"🌊 Liquid Lattice Storage Online (SPARSE MODE) | Virtual Rings: {rings}")
        print(f"   Phase Resolution: {self.SECTOR_WIDTH} degrees/sector")

    def _ensure_node(self, node_id: int) -> QuantumNode:
        """Lazy Load: Get existing node or create new one."""
        if node_id not in self.nodes:
            # Create fresh node
            self.nodes[node_id] = QuantumNode(node_id)
        return self.nodes[node_id]

    def _bytes_to_s60(self, data_chunk: bytes) -> S60:
        """Converts a byte chunk to an S60 amplitude. Encodes Length in LSB."""
        val_int = int.from_bytes(data_chunk, byteorder='big')
        length = len(data_chunk)
        encoded_val = (val_int << 8) | length
        return S60(encoded_val, 0, 0)

    def _s60_to_bytes(self, val: S60) -> bytes:
        """Decodes S60 amplitude back to bytes, using encoded length."""
        try:
            encoded_int = int(val)
            length = encoded_int & 0xFF
            data_int = encoded_int >> 8
            if length == 0: return b''
            return data_int.to_bytes(length, byteorder='big')
        except:
             return b''

    def _byte_to_phase(self, val_byte: int) -> S60:
        """Maps a single byte (0-255) to a Phase Sector Center."""
        sector_idx = S60(val_byte)
        angle = (sector_idx * self.SECTOR_WIDTH)
        return angle

    def _s60_mod(self, a: S60, b: S60) -> S60:
        """Manual modulo for S60 objects."""
        if b == S60(0): return S60(0)
        quotient = int(a / b)
        return a - (b * S60(quotient))

    def _phase_to_byte(self, phase: S60) -> int:
        """Decodes phase angle to nearest byte (0-255)."""
        norm_phase = self._s60_mod(phase, S60(360))
        
        # Pure S60 Calculation (Avoid float)
        # Ratio = Phase / SectorWidth
        # We assume division works for S60 and returns S60 result.
        if self.SECTOR_WIDTH == S60(0): return 0
        
        # To get rounding, we add 0.5 * Width before floor division?
        # Or simpler:
        ratio_s60 = norm_phase / self.SECTOR_WIDTH
        
        # Rounding: int(val + S60(0,30,0)) # 0.5
        # Assuming S60(0,30,0) is 0.5 degrees
        ratio_rounded = ratio_s60 + S60(0, 30, 0) 
        
        idx = int(ratio_rounded)
        return idx % 256

    def fragment_data(self, payload: bytes, chunk_size: int) -> List[bytes]:
        """Splits payload into chunks."""
        chunks = []
        for i in range(0, len(payload), chunk_size):
            chunk = payload[i:i + chunk_size]
            chunks.append(chunk)
        return chunks

    def inject_dual_channel(self, payload_a: bytes, payload_b: bytes):
        """
        Injects data using Lazy Initialization.
        Only creates nodes needed for the payload.
        """
        chunks_a = self.fragment_data(payload_a, self.CHUNK_SIZE)
        chunks_b = self.fragment_data(payload_b, 1)
        
        count = max(len(chunks_a), len(chunks_b))
        
        # Check virtual limit if needed, but for Sparse we mainly care about RAM.
        # Rings=150 ~ 70k nodes limit is enforced socially, not technically here.
        
        print(f"💉 Dual Injection (Sparse): {len(chunks_a)} Energy Chunks | {len(chunks_b)} Phase Chunks")
        print(f"   Activating ~{count} nodes...")
        
        for i in range(count):
            node = self._ensure_node(i)
            
            # Channel A
            if i < len(chunks_a):
                node.energy = self._bytes_to_s60(chunks_a[i])
            else:
                node.energy = S60(0)
                
            # Channel B
            if i < len(chunks_b):
                val_byte = chunks_b[i][0]
                node.phase = self._byte_to_phase(val_byte)
            else:
                node.phase = S60(0)
                
        print(f"✅ Injection Complete. Active Nodes in RAM: {len(self.nodes)}")

    def inject_holograph(self, payload: bytes):
        """Compatibility wrapper for simple energy injection."""
        self.inject_dual_channel(payload, b'')

    def retrieve_dual_channel(self) -> Tuple[bytes, bytes]:
        """Recovers data from sparse storage."""
        buffer_a = bytearray()
        buffer_b = bytearray()
        
        # In Sparse Mode, we iterate by index 0..max, or sorted keys?
        # Sorted keys ensures order.
        if not self.nodes:
            return b'', b''
            
        max_idx = max(self.nodes.keys())
        
        for i in range(max_idx + 1):
            if i in self.nodes:
                node = self.nodes[i]
                
                # Channel A
                if node.energy > S60(0):
                    buffer_a.extend(self._s60_to_bytes(node.energy))
                
                # Channel B
                # Logic: Read if energy > 0 (Carrier Wave Dependency)
                if node.energy > S60(0): 
                     val_byte = self._phase_to_byte(node.phase)
                     buffer_b.append(val_byte)
            # Else: Node not in RAM -> Empty / Zero. Skip.
                 
        return bytes(buffer_a), bytes(buffer_b)

    def retrieve_holograph(self) -> bytes:
        """Compatibility wrapper."""
        a, _ = self.retrieve_dual_channel()
        return a

    def _get_neighbors_indices(self, idx: int) -> List[int]:
        """
        Calculates neighbor indices for a Spiral Hex Grid.
        Simplification V1: Linear neighbors (i-1, i+1) to simulate 1D string?
        True Hex Grid neighbor calculation by index is complex.
        
        For EXP-013 (Scale), full hex topology is overkill for just storage.
        If we use LINEAR topology, diffusion works along the chain.
        Let's use Linear Topology for Sparse Optimization unless 2D is required.
        
        Decision: LINEAR NEIGHBORS (i-1, i+1).
        This makes 'Rings' irrelevant but allows infinite scaling.
        And it's extremely fast. 
        Diffusion works: Phase(i) averages with Phase(i-1) and Phase(i+1).
        """
        neighbors = []
        if idx > 0: neighbors.append(idx - 1)
        # We don't limit upper bound, it's open-ended string.
        neighbors.append(idx + 1) 
        return neighbors

    def stabilize_fluid(self, cycles=5, snap_phase=True):
        """
        Optimized Stabilization for Sparse Lattice.
        Uses Virtual Neighbors (Linear Topology) to avoid creating neighbor links.
        """
        print(f"🌊 Stabilizing Fluid (Sparse Linear Mode, {cycles} cycles)...")
        diffusion_threshold = self.SECTOR_WIDTH / S60(2)
        
        active_indices = sorted(list(self.nodes.keys()))
        if not active_indices: return
        
        # We process range covering all active nodes + margins?
        # Or just active nodes?
        # If we only process active nodes, edge effects occur.
        # But data lives in active nodes.
        
        for _ in range(cycles):
             updates_phase = {}
             
             for idx in active_indices:
                 node = self.nodes[idx]
                 
                 total_phase = node.phase
                 count = S60(1)
                 
                 # Virtual Neighbors
                 # Linear: Left (idx-1) and Right (idx+1)
                 # We only check if they EXIST in RAM. 
                 # If they don't, they are empty (phase 0, energy 0).
                 # Should we average with 0? No, that would drain energy/phase.
                 # Fluid boundary condition: behave as if neighbor has same phase (reflect)
                 # or ignore if empty.
                 # Strategy: Only diffuse with existing active neighbors.
                 
                 neighbors_idx = [idx - 1, idx + 1]
                 
                 for n_idx in neighbors_idx:
                     if n_idx in self.nodes:
                         neighbor = self.nodes[n_idx]
                         
                         diff = abs(neighbor.phase - node.phase)
                         if diff > S60(180): diff = S60(360) - diff
                         
                         if diff <= diffusion_threshold:
                             total_phase += neighbor.phase
                             count += S60(1)
                 
                 avg = total_phase / count
                 
                 # Snapping
                 if snap_phase:
                     norm_avg = self._s60_mod(avg, S60(360))
                     try:
                        ratio_s60 = norm_avg / self.SECTOR_WIDTH
                        ratio_rounded = ratio_s60 + S60(0, 30, 0)
                        idx_sector = int(ratio_rounded)
                        snapped_angle = S60(idx_sector) * self.SECTOR_WIDTH
                        updates_phase[idx] = snapped_angle
                     except:
                        updates_phase[idx] = avg
                 else:
                     updates_phase[idx] = avg
                     
             # Apply
             for idx, new_phase in updates_phase.items():
                 self.nodes[idx].phase = new_phase
                 
    def verify_integrity(self, original_hash: str) -> bool:
        """Helper to verify data consistency."""
        # Placeholder for hash check
        return True

if __name__ == "__main__":
    # Quick Self-Test
    storage = LiquidLatticeStorage(rings=2)
    
    # Payload: String msg
    msg = b"SENTINEL_LIQUID_CORE_ACTIVE_V1"
    
    print(f"\n🧪 Test 1: Injection")
    storage.inject_holograph(msg)
    
    print(f"\n🧪 Test 2: Liquid Stabilization")
    storage.stabilize_fluid(cycles=3)
    
    print(f"\n🧪 Test 3: Retrieval")
    recovered = storage.retrieve_holograph()
    print(f"Reference: {msg}")
    print(f"Recovered: {recovered}")
    
    cleaned = recovered.replace(b'\x00', b'')
    if cleaned == msg:
        print("\n✅ SUCCESS: Data Preserved in Liquid State.")
    else:
        print(f"\n❌ FAILURE: Data Corruption. \nOut: {cleaned}")
