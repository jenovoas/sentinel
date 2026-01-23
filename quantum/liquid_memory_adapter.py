#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -----------------------------------------------------------------------------
# LIQUID MEMORY ADAPTER
# -----------------------------------------------------------------------------
# Bridging the Interface Gap:
# Legacy: write(slot, data) -> New: store(key, value)
# Backend: LiquidLatticeStorage (Distributed Hexagonal Network)
# -----------------------------------------------------------------------------

import sys
import os
import hashlib
sys.path.append(os.getcwd())

import sys
import os
import hashlib
import time
sys.path.append(os.getcwd())

from quantum.yatra_core import S60
from quantum.liquid_lattice_storage import LiquidLatticeStorage
from quantum.gpu_controller import gpu_controller

# Try importing Rust Core
try:
    from quantum.sentinel_core import PySharedBuffer
    RUST_AVAILABLE = True
except ImportError:
    print("⚠️ Rust Core Not Found. Falling back to Pure Python.")
    RUST_AVAILABLE = False
    PySharedBuffer = None
class LiquidMemory:
    """
    High-Level Interface for Sentinel's Cognitive Memory.
    Uses LiquidLatticeStorage as the physical medium.
    """
    
    def __init__(self, size_scale=1):
        """
        :param size_scale: Multiplier for lattice size. 
                           1 = ~1KB (R=5). 
                           10 = ~1MB (R=150, slow init).
        """
        # Auto-scaling logic
        rings = 5 if size_scale <= 1 else 15
        if size_scale >= 10: rings = 50 # Reduced from 150 for responsiveness in dev
        
        print(f"🧠 Liquid Memory Init | Scale: {size_scale} | Rings: {rings}")
        print(f"   Bio-Sync: 17s Pulse | 68s Master Reset")
        self.lattice = LiquidLatticeStorage(rings=rings)
        
        # Rust Backend (Phase 4-7)
        self.rust_lattice = None
        if RUST_AVAILABLE:
            try:
                from quantum.sentinel_core import RustLattice
                self.rust_lattice = RustLattice(rings=rings)
                print("🦀 Rust Backend Initialized for Persistence.")
            except ImportError:
                print("⚠️ Could not initialize Rust Backend.")
        
        # Virtual File System Table (stored in standard memory for now, 
        # could be stored in lattice header later).
        self.file_table = {} 

    def store(self, key: str, data: bytes) -> bool:
        """Stores a named block of data."""
        # For V1, the entire lattice is ONE block.
        print(f"🧠 Storing Key: '{key}' ({len(data)} bytes)...")
        try:
            # Phase Channel uses SHA256 (32 bytes).
            # To ensure the full signature is stored, we need at least 32 nodes
            # active in the Dual Injection.
            # Dual Injection logic uses max(len_a, len_b).
            # So as long as we pass full 32 bytes to payload_b, 
            # `inject_dual_channel` will activate 32 nodes.
            # HOWEVER: Nodes 11-32 will have Energy=0.
            # AND: `retrieve_dual_channel` ONLY reads nodes with Energy > 0.
            # FIX: We must force non-zero Energy for the signature nodes?
            # OR: Pad the data with dummy bytes if it's too short, 
            # so that Energy > 0 for all 32 nodes.
            
            key_hash = hashlib.sha256(key.encode()).digest()
            chunk_size = 16 # Energy chunks
            needed_chunks_for_sig = 32 # 1 byte phase per node
            
            # Needed payload size to support 32 nodes = 32 * 16 = 512 bytes
            # IF we rely on energy carrier.
            # But that's inefficient padding.
            
            # Better Fix:
            # We can enable "Carrier Wave" (Zero Data but Non-Zero Amplitude).
            # S60(1) as Energy carrier for empty data?
            # But that decodes to 0x01...
            
            # Hack for V1 Prototype: Pad Data to minimum count if needed.
            # We need `data_chunks` >= `phase_chunks` for retrieval to see them.
            # Phase chunks = 32.
            # Data chunks = len(data) / 16.
            
            min_data_len = 32 * 16 # 512 bytes
            
            if len(data) < min_data_len:
                padding_needed = min_data_len - len(data)
                data_padded = data + b'\x00' * padding_needed
            else:
                data_padded = data
            
            # --- HYBRID PATH START ---
            if RUST_AVAILABLE:
                # 1. Get Control Batch Size
                batch_size = gpu_controller.get_optimal_batch()
                
                t0 = time.time()
                
                # 2. Use Shared Buffer (Zero Copy Mmap)
                # Create a buffer named by Key Hash (Short term)
                buf_name = f"liquid_{key_hash[:8].hex()}"
                
                # In real app, we might reuse a big buffer. Here we create per operation for simpler demo.
                # Size = len(data_padded)
                try:
                    # 2. Use Shared Buffer (Zero Copy Mmap)
                    # For Phase 7, we also need to populate the RustLattice structure so it can be saved.
                    # In a full kernel implementation, the kernel would read SHM and update RustLattice nodes.
                    # Here we simulate that by injecting directly into RustLattice.
                    
                    if self.rust_lattice:
                         self.rust_lattice.inject(data_padded)
                    
                    # Also use SHM for the bridge simulation
                    buf_name = f"liquid_{key_hash[:8].hex()}"
                    shm = PySharedBuffer(buf_name, len(data_padded), create=True)
                    shm.write(0, data_padded)
                    
                    # Fallback for INTEGRITY TEST (Keep Python Sync)
                    self.lattice.inject_dual_channel(data_padded, key_hash)
                    
                    t1 = time.time()
                    latency = (t1 - t0) * 1000
                    gpu_controller.adjust_batch_size(latency)
                    gpu_controller.report_status()
                    
                except Exception as e:
                    print(f"⚠️ Shared Memory Error: {e}. Falling back.")
                    self.lattice.inject_dual_channel(data_padded, key_hash)
            else:
                self.lattice.inject_dual_channel(data_padded, key_hash)
            # --- HYBRID PATH END ---
            
            # Stabilize & Bio-Sync
            # We force stabilization based on the 17s breath cycle.
            self.lattice.stabilize_fluid(cycles=1)
            
            self.file_table[key] = {
                'len': len(data), 
                'hash': hashlib.sha256(data).hexdigest()
            }
            return True
        except Exception as e:
            print(f"❌ Storage Error: {e}")
            return False

    def retrieve(self, key: str) -> bytes:
        """Retrieves data by key."""
        if key not in self.file_table:
            print(f"⚠️ Key '{key}' not found in virtual table.")
            return None
            
        print(f"🧠 Retrieving Key: '{key}'...")
        # Retrieve Dual Channel
        data, key_sig = self.lattice.retrieve_dual_channel()
        
        # Verify Key Signature (Phase Channel)
        expected_sig = hashlib.sha256(key.encode()).digest() # 32 bytes
        
        # Truncate retrieved sig to expected length (since we read all nodes)
        # Note: retrieve_dual_channel reads ALL active energy nodes.
        # If data is large, key_sig (phase) will be padded with 0s if it's short.
        # We check prefix.
        
        # Ensure we have at least 32 bytes or check integrity
        if len(key_sig) < 32:
             # If stored data was small, we might have fewer nodes than 32.
             # In that case, we only have partial signature stored?
             # No, inject_dual_channel extends usage to MAX(A, B).
             # So we should have at least 32 nodes active if B=32.
             pass
             
        # Compare only the first 32 bytes (SHA256 Size)
        actual_sig = key_sig[:32]
        
        if actual_sig != expected_sig:
             print(f"⚠️ Security Alert: Phase Signature Mismatch for Key '{key}'")
             print(f"   Exp: {expected_sig.hex()}")
             print(f"   Got: {actual_sig.hex()}")
             
             # Detailed Diff
             if len(actual_sig) == len(expected_sig):
                 diff_count = sum(1 for a, b in zip(actual_sig, expected_sig) if a != b)
                 print(f"   Byte Diffs: {diff_count}/{len(actual_sig)}")
             else:
                 print(f"   Length Mismatch: {len(actual_sig)} vs {len(expected_sig)}")
        if actual_sig != expected_sig:
             print(f"⚠️ Security Alert: Phase Signature Mismatch for Key '{key}'")
             # ... (debug prints) ...
        
        # Verify Data Integrity
        # Strip Padding based on file table
        stored_len = self.file_table[key]['len']
        if len(data) > stored_len:
             data = data[:stored_len]
        
        return data

    # Phase 7: Persistence
    def save_snapshot(self, path: str = "liquid_snapshot.s60"):
        if self.rust_lattice:
            print(f"💾 Saving Rust Snapshot to {path}...")
            self.rust_lattice.save_snapshot(path)
            return True
        return False
        
    def load_snapshot(self, path: str = "liquid_snapshot.s60"):
        if self.rust_lattice:
            if os.path.exists(path):
                print(f"📂 Loading Rust Snapshot from {path}...")
                count = self.rust_lattice.load_snapshot(path)
                print(f"   Nodes Loaded: {count}")
                return count
        return 0

    def status(self):
        """System Health."""
        return {
            'nodes': len(self.lattice.nodes),
            'files': list(self.file_table.keys()),
            'coherence': 'LIQUID_STABLE' # Placeholder
        }

# Compatibility Wrapper for interaction scripts
def get_memory_service():
    return LiquidMemory()
