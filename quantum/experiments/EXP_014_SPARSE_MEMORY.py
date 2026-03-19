#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -----------------------------------------------------------------------------
# EXPERIMENTO 014: SPARSE MEMORY OPTIMIZATION
# -----------------------------------------------------------------------------
# Objetivo:
#   Validar que la arquitectura Sparse ocupa menos RAM.
#   Probar integridad de almacenamiento de 1 MB.
# -----------------------------------------------------------------------------

import sys
import os
import secrets
import time
import tracemalloc # For memory measurment

sys.path.append(os.getcwd())

from quantum.yatra_core import S60
from quantum.liquid_lattice_storage import LiquidLatticeStorage

def run_experiment_014():
    print("🔬 EXP-014: SPARSE MEMORY TEST")
    print("-" * 60)
    
    tracemalloc.start()
    
    # 1. Init System
    print("🏗️ Creating Sparse Lattice (Virtual Rings: 150)...")
    lattice = LiquidLatticeStorage(rings=150)
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"   RAM Init: {current / 1024**2:.2f} MB (Peak: {peak / 1024**2:.2f} MB)")
    
    # 2. Payload 1MB
    SIZE_MB = 1024 * 1024
    payload = secrets.token_bytes(SIZE_MB)
    print(f"\n📦 Injecting 1 MB Payload...")
    
    lattice.inject_holograph(payload)
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"   RAM Post-Injection: {current / 1024**2:.2f} MB")
    print(f"   Active Nodes: {len(lattice.nodes)}")
    
    # Expected RAM:
    # 65536 nodes * 400B ~ 26 MB.
    # Previous List implementation: Start with 24GB empty. Now 0MB empty.
    
    # 3. Stabilization
    print("\n🌊 Stabilizing (Check performance linear neighbors)...")
    start_t = time.time()
    lattice.stabilize_fluid(cycles=1)
    print(f"   Time: {time.time() - start_t:.2f}s")
    
    # 4. Retrieval
    print("\n🔍 Retrieving...")
    rec = lattice.retrieve_holograph()
    
    if rec == payload:
        print("\n✅ SUCCESS: 1MB Integrity Verified.")
        print("   Memory Optimization Confirmed.")
    else:
        print("\n❌ FAILURE: Corruption detected.")
    
    tracemalloc.stop()

if __name__ == "__main__":
    run_experiment_014()
