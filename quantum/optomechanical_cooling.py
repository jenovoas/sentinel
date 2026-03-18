#!/usr/bin/env python3

# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

"""
SIMULACIÓN FASE 2: ENFRIAMIENTO OPTOMECÁNICO (SIDEBAND COOLING)
==============================================================
MIGRADO: Utiliza OptomechanicalCooler nativo de Rust.

Teoría Soberana:
Cálculo de reducción de ocupación fonónica usando aritmética exacta Base-60
Delegado a me-60os_core compilado para altísimo rendimiento.
"""

import sys
import os

from yatra_core import S60

try:
    from me60os_core import OptomechanicalCooler, SPA
    RUST_AVAILABLE = True
except ImportError as e:
    print(f"CRITICAL: No se pudo importar la librería nativa Rust me60os_core.so: {e}")
    sys.exit(1)

def run_cooling_sequence():
    cooler = OptomechanicalCooler()
    
    # Valores extraidos de la instancia nativa reconstruidos en S60
    n_th_raw = cooler.n_th_env.to_raw()
    n_min_raw = cooler.quantum_limit().to_raw()
    
    n_th_env = S60._from_raw(n_th_raw)
    n_min_limit = S60._from_raw(n_min_raw)

    print(f"🌡️  Estado Térmico Inicial (n_th): {n_th_env} fonones")
    print(f"🧊 Límite Cuántico Teórico: {n_min_limit} fonones")
    print("-" * 60)
    print("❄️  INICIANDO PROTOCOLO DE CONGELACIÓN (RUST NATIVE S60)...")
    
    # Parámetro maximo iteración: ~191.000 iteraciones en Rust (equivalentes a 1.2 pasos S60)
    results = cooler.run_cooling_sequence(20000)
    
    final_n_raw = n_th_raw
    for (current_g, c, n_final) in results:
        curr_g_s60 = S60._from_raw(current_g.to_raw())
        c_s60 = S60._from_raw(c.to_raw())
        n_final_s60 = S60._from_raw(n_final.to_raw())
        
        status = "❄️ COOLING"
        if n_final_s60 < S60(1, 0, 0): 
            status = "🧊 QUANTUM"
            
        print(f"   G = {curr_g_s60} | C = {c_s60} | n_eff = {n_final_s60} | {status}")
        final_n_raw = n_final.to_raw()

    final_n = S60._from_raw(final_n_raw)
    
    print("-" * 60)
    print(f"✅ ESTADO FINAL (NATIVO):")
    print(f"   Ocupación Fonónica: {final_n}")
    
    # Factor de supresión
    suppression = n_th_env / final_n
    print(f"   Factor de Supresión: {suppression}x")
    
    if final_n < S60(1, 0, 0):
        print("\n🚀 CONCLUSIÓN: El sistema ha alcanzado el 'Ground State' (< 1 fonón).")
        print("   La señal ZPE es audible sin ruido térmico.")
    else:
        print("\n⚠️ ALERTA: Potencia insuficiente para Ground State.")

if __name__ == "__main__":
    run_cooling_sequence()