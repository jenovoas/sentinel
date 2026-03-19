#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -----------------------------------------------------------------------------
# EXPERIMENTO 011: CAPACIDAD LÍQUIDA (1KB PROOF)
# -----------------------------------------------------------------------------
# Objetivo:
#   Demostrar que la red distribuida puede almacenar >1 KB de datos
#   sin violar los límites físicos de amplitud (EXP-010).
# -----------------------------------------------------------------------------

import sys
import os
import secrets
sys.path.append(os.getcwd())

from quantum.yatra_core import S60
from quantum.liquid_lattice_storage import LiquidLatticeStorage

def run_experiment_011():
    print("🔬 EXP-011: LIQUID LATTICE CAPACITY TEST (1KB)")
    print("-" * 60)
    
    # 1. Configurar Red Grande
    # 16 bytes/nodo. Para 1KB (1024 bytes) necesitamos 64 nodos.
    # Anillo 3 tiene ~37 nodos? No.
    # Nodos totales = 1 + 6 + 12 + 18...
    # R=3: 1+6+12+18 = 37. Insuficiente.
    # R=5: 1+6+12+18+24+30 = 91. Suficiente.
    
    print("🏗️ Construyendo Red Hexagonal (Rings=5)...")
    lattice = LiquidLatticeStorage(rings=5)
    print(f"   Nodos Activos: {len(lattice.nodes)}")
    
    # 2. Generar Payload de 1KB
    print("\n📦 Generando Payload de 1024 Bytes (Alta Entropía)...")
    payload = secrets.token_bytes(1024)
    payload_hash = hash(payload)
    print(f"   Hash Original: {payload_hash}")
    
    # 3. Inyección Holográfica
    print("\n💉 Inyectando Datos en la Matriz...")
    try:
        lattice.inject_holograph(payload)
    except Exception as e:
        print(f"❌ ERROR CRÍTICO DE INYECCIÓN: {e}")
        return

    # 4. Prueba de Estabilidad (Tiempo)
    print("\n⏳ Simulando Paso del Tiempo y Difusión (3 ticks)...")
    # En un sistema real, el tiempo degrada la fase.
    # Usamos stabilize_fluid para mantener la integridad.
    lattice.stabilize_fluid(cycles=3)
    
    # 5. Recuperación
    print("\n🔍 Recuperando Datos...")
    recovered = lattice.retrieve_holograph()
    recovered_hash = hash(recovered)
    print(f"   Hash Recuperado: {recovered_hash}")
    
    # 6. Validación
    print("-" * 60)
    print("RESULTADOS:")
    
    if recovered == payload:
        print("✅ ÉXITO: Integridad Perfecta (100%)")
        print("   Capacidad de 1KB validada sin colapso físico.")
    else:
        print("❌ FALLO: Corrupción de Datos.")
        print(f"   Longitud Original: {len(payload)}")
        print(f"   Longitud Recuperada: {len(recovered)}")
        # Diff sample
        if len(recovered) > 0:
             print(f"   Sample Diff: {payload[:10]} vs {recovered[:10]}")
    
    # 7. Verificación Física (Amplitudes)
    print("\n📡 Auditoría Física (Amplitudes de Cristal):")
    max_amp = S60(0)
    unsafe_count = 0
    safe_limit_exp10 = int(float("1e80")) # Using string to avoid huge literal warning if any
    # S60 comparison setup
    
    for n in lattice.nodes:
        if n.energy > max_amp:
            max_amp = n.energy
            
    print(f"   Amplitud Máxima Detectada: {max_amp}")
    
    # Check if max_amp < 10^80
    # S60 conversion to int for checking
    max_val_int = int(max_amp)
    limit = 10**80
    
    if max_val_int < limit:
        print("✅ FÍSICA ESTABLE: Amplitud por debajo del Límite de Agujero Negro.")
    else:
        print("⚠️ ALERTA: Singularidad Detectada! (Amplitud excesiva)")

if __name__ == "__main__":
    run_experiment_011()
