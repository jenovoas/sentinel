#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -----------------------------------------------------------------------------
# EXPERIMENTO 012: COMPRESIÓN DE FASE (DUAL CHANNEL)
# -----------------------------------------------------------------------------
# Objetivo:
#   Validar almacenamiento simultáneo en Amplitud (Chan A) y Fase (Chan B).
#   Confirmar que `stabilize_fluid(snap=True)` corrige errores de fase sin
#   corromper los datos discretos.
# -----------------------------------------------------------------------------

import sys
import os
import secrets
sys.path.append(os.getcwd())

from quantum.yatra_core import S60
from quantum.liquid_lattice_storage import LiquidLatticeStorage

def run_experiment_012():
    print("🔬 EXP-012: PHASE COMPRESSION & QUANTUM SNAPPING")
    print("-" * 60)
    
    # 1. Setup Lattice
    # Need enough nodes for the payloads.
    lattice = LiquidLatticeStorage(rings=3) # ~37 nodes
    
    # 2. Generate Dual Payloads
    # Chan A: 16 * 10 = 160 Bytes (Energy)
    # Chan B: 1 * 10 = 10 Bytes (Phase)
    msg_a = b"ENERGY_CHANNEL_CRITICAL_DATA_BLOCK_ALPHA_01" # 43 bytes
    msg_b = b"PHASE_KEY" # 9 bytes
    
    print(f"📦 Payload A (Energy): {msg_a}")
    print(f"📦 Payload B (Phase) : {msg_b}")
    
    # 3. Dual Injection
    print("\n💉 Inyectando en Canales Paralelos...")
    lattice.inject_dual_channel(msg_a, msg_b)
    
    # 4. Introduce Artificial Noise (Drift)
    print("\n🌪️ Inyectando Ruido de Fase (Simulando Deriva)...")
    hologram = lattice._matrix.get_hologram()
    for i, energy_raw, phase_raw in hologram:
        # Añadir ruido aleatorio pequeño (+- 0.5 grados)
        # S(0.5) ~ S60(0, 30, 0)
        noise = S60(0, 30, 0)
        new_phase = S60._from_raw(phase_raw) + noise
        lattice._matrix.set_node_state(i, S60._from_raw(energy_raw), new_phase)
        
    # Check Phase drift before stabilization
    # Just inspect Node 0
    _, _, p0_noisy = lattice._matrix.get_hologram()[0]
    print(f"   [Debug] Node 0 Phase (Noisy): {S60._from_raw(p0_noisy)}")

    # 5. Quantum Snapping Stabilization
    print("\n🌊 Ejecutando 'Sector Snapping' (Corrección de Errores)...")
    lattice.stabilize_fluid(cycles=5, snap_phase=True)
    
    _, _, p0_snapped = lattice._matrix.get_hologram()[0]
    print(f"   [Debug] Node 0 Phase (Snapped): {S60._from_raw(p0_snapped)}")

    # 6. Retrieval
    print("\n🔍 Recuperando Dual-Channel...")
    rec_a, rec_b = lattice.retrieve_dual_channel()
    
    # Validate
    # Truncate recovered to expected length
    rec_a = rec_a[:len(msg_a)]
    rec_b = rec_b[:len(msg_b)]
    
    print(f"   Recovered A: {rec_a}")
    print(f"   Recovered B: {rec_b}")
    
    # Check integrity of B (Phase Data)
    if rec_b == msg_b:
        print("✅ SUCCESS: Phase Data Recovered accurately despite noise.")
    else:
        print("❌ FAILURE: Phase Data Corrupted.")
        print(f"   Exp: {msg_b}")
        print(f"   Got: {rec_b}")
        
    # Check A
    if rec_a == msg_a:
        print("✅ SUCCESS: Energy Data Integrity 100%.")
    else:
        print("❌ FAILURE: Energy Data Corrupted.")

if __name__ == "__main__":
    run_experiment_012()
