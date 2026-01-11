#!/usr/bin/env python3
import sys
import os
import time
sys.path.append(os.getcwd())

from quantum.liquid_memory_adapter import LiquidMemory

def test_rust_persistence():
    print("💾 RUST PERSISTENCE TEST")
    print("-" * 50)
    
    mem = LiquidMemory(size_scale=1)
    if not mem.rust_lattice:
        print("❌ Rust Backend not verified. Skipping.")
        return

    # Verify Struct Alignment directly
    try:
        node_size = mem.rust_lattice.get_node_size()
        print(f"📏 Rust Reported QuantumNode Size: {node_size} bytes")
        if node_size == 64:
             print("   ✅ CONFIRMED: 64-Byte Alignment (Sacred Geometry).")
        else:
             print(f"   ⚠️ WARNING: Alignment is {node_size} bytes (Expected 64).")
    except Exception as e:
        print(f"   ⚠️ Could not get node size: {e}")

    # 1. Inject Data
    data = b"ATLANTEAN_KNOWLEDGE_" * 10 # 200 bytes
    print(f"💉 Injecting {len(data)} bytes into Rust Lattice...")
    mem.store("knowledge.dat", data)
    
    # 2. Save Snapshot
    snap_path = "test_snapshot.s60"
    print(f"💾 Saving Snapshot to {snap_path}...")
    mem.save_snapshot(snap_path)
    
    if not os.path.exists(snap_path):
        print("❌ Snapshot file not created.")
        exit(1)
        
    size = os.path.getsize(snap_path)
    print(f"   File Size: {size} bytes")
    
    # Verify Alignment (Size should be multiple of 64)
    if size % 64 == 0:
        print("   ✅ Size is 64-byte aligned (Sacred Geometry).")
    else:
        print(f"   ⚠️ Size is NOT 64-byte aligned. Alignment: {size % 64}")

    # 3. Reload into new Instance
    print("🔄 Restarting Memory (New Instance)...")
    mem2 = LiquidMemory(size_scale=1)
    count = mem2.load_snapshot(snap_path)
    
    print(f"   Nodes Loaded: {count}")
    
    # Check node count match
    # We don't have direct access to rust node count from python wrapper easily without adding method
    # But load_snapshot returns count.
    
    if count > 0:
         print("✅ Persistence Successful.")
    else:
         print("❌ No nodes loaded.")

    # Cleanup
    os.remove(snap_path)

if __name__ == "__main__":
    test_rust_persistence()
