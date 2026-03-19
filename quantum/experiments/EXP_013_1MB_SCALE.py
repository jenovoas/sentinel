#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -----------------------------------------------------------------------------
# EXPERIMENTO 013: 1MB SCALE TEST (MACRO LATTICE)
# -----------------------------------------------------------------------------
# Objetivo:
#   Validar la escalabilidad del Liquid Lattice Storage.
#   Almacenar 1 MB (1,048,576 Bytes).
#   Requiere ~65,536 nodos (Rings ~150).
#   
#   Reto:
#   Rendimiento de Python y estabilidad numérica de la difusión en red masiva.
# -----------------------------------------------------------------------------

import sys
import os
import secrets
import time
sys.path.append(os.getcwd())

from quantum.yatra_core import S60
from quantum.liquid_lattice_storage import LiquidLatticeStorage

def run_experiment_013():
    print("🔬 EXP-013: 1MB SCALE TEST")
    print("-" * 60)
    
    # 1. Calculate Rings needed
    # Payload: 1 MB
    SIZE_MB = 1024 * 1024
    CHUNK_SZ = 16
    needed_chunks = SIZE_MB // CHUNK_SZ
    print(f"📦 Target: 1 MB ({SIZE_MB} bytes)")
    print(f"   Chunks: {needed_chunks}")
    
    # Rings calculation approximation: Nodes ~= 3 * R^2
    # R ~= sqrt(Nodes/3)
    needed_rings = int((needed_chunks / 3)**0.5) + 5 # Buffer
    print(f"   Estimated Rings: {needed_rings}")
    
    # To keep the test reasonable in reasonable time, we might step down 
    # if 65k nodes is too slow for pure Python object overhead in this environment.
    # But let's try R=150.
    
    print("\n🏗️ Building Massive Lattice (This may take a moment)...")
    start_t = time.time()
    # Using a reduced size for 'Fast Verification' if the user environment is limited?
    # Let's try the full scale. If it OOMs or hangs, we adapt.
    # Rings=150 is approx 67,000 nodes. 
    lattice = LiquidLatticeStorage(rings=needed_rings) 
    build_t = time.time() - start_t
    print(f"   Lattice Built in {build_t:.2f}s. Active Nodes: {len(lattice.nodes)}")
    
    if len(lattice.nodes) < needed_chunks:
        print(f"❌ ERROR: Lattice too small. Got {len(lattice.nodes)}, need {needed_chunks}")
        return

    # 2. Generate Payload
    print("\n🎲 Generating High-Entropy Payload...")
    # Using simpler pattern for speed than secrets.token_bytes(1MB) if needed, 
    # but token_bytes is fast.
    payload = secrets.token_bytes(SIZE_MB)
    payload_hash = hash(payload)
    print(f"   Hash: {payload_hash}")
    
    # 3. Injection
    print("\n💉 Mass Injection...")
    inject_start = time.time()
    lattice.inject_holograph(payload)
    inject_time = time.time() - inject_start
    print(f"   Injection Complete in {inject_time:.2f}s")
    
    # 4. Fluid Stabilization (Macro Scale)
    print("\n🌊 Stabilization (1 Cycle for benchmark)...")
    # 65k nodes * neighbors interactions. O(N).
    stab_start = time.time()
    lattice.stabilize_fluid(cycles=1) 
    stab_time = time.time() - stab_start
    print(f"   Stabilization Cycle: {stab_time:.2f}s")
    
    # 5. Retrieval
    print("\n🔍 Mass Retrieval...")
    rec_start = time.time()
    recovered = lattice.retrieve_holograph()
    rec_time = time.time() - rec_start
    print(f"   Retrieval Complete in {rec_time:.2f}s")
    
    # 6. Verification
    rec_hash = hash(recovered)
    print("-" * 60)
    print(f"Original Hash : {payload_hash}")
    print(f"Recovered Hash: {rec_hash}")
    
    if recovered == payload:
        print("\n✅ SUCCESS: 1MB Stored and Retrieved from Quantum Lattice.")
        print(f"   Density: {len(recovered)/len(lattice.nodes):.2f} Bytes/Node (Effective)")
    else:
        print("\n❌ FAILURE: Data Corruption.")
        print(f"   Len Rec: {len(recovered)}")

if __name__ == "__main__":
    run_experiment_013()
