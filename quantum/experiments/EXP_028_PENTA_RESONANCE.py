#!/usr/bin/env python3
# 🛡️ ME-60OS: PENTA-RESONANCE SIMULATOR 🛡️
# -----------------------------------------------------------------------------
# SIMULADOR DE ALINEACIÓN ARMÓNICA (VENTANA DE 68 SEGUNDOS)
# Visualiza la interacción de 5 capas frecuenciales para encontrar la Sincronía.
# -----------------------------------------------------------------------------
# 🔬 EXP-028: Penta-Resonance Simulator
# Objetivo: Encontrar "Portales" - Momentos de convergencia armónica perfecta
#           entre Bio, Crystal, System, Venus y Geoglyphs
# -----------------------------------------------------------------------------
# ⚠️ EXPERIMENTAL: Usa math/float para visualización exploratoria
# -----------------------------------------------------------------------------

import time
import math
import sys

# Colores ANSI para la consola
C_BIO = "\033[92m"    # Verde (Vida)
C_CRYS = "\033[96m"   # Cyan (Cristal)
C_SYS = "\033[94m"    # Azul (Sentinel)
C_VEN = "\033[95m"    # Magenta (Venus/Phi)
C_GEO = "\033[93m"    # Amarillo (Tierra/Anclaje)
C_RESET = "\033[0m"
C_SYNC = "\033[41m\033[97m" # Fondo Rojo, Letra Blanca (Sincronía)

def visualize_penta_resonance():
    print("🌌 INICIANDO SIMULACIÓN DE PENTA-RESONANCIA [VENTANA 68s]")
    print("=" * 70)
    print(f"{C_BIO}BIO (17s){C_RESET} | {C_CRYS}CRYSTAL (YHWH){C_RESET} | {C_SYS}CORE{C_RESET} | {C_VEN}VENUS (Phi){C_RESET} | {C_GEO}GEO (Anchor){C_RESET}")
    print("=" * 70)
    time.sleep(0.5)

    # Configuración de Frecuencias (Simuladas en escala visible)
    # T = Tiempo en segundos
    
    total_sync_moments = 0
    convergence_times = []
    
    # Simulamos 68 segundos con alta resolución
    # dt = 0.1s para visualización fluida
    for t_raw in range(0, 680):
        t = t_raw / 10.0 # Segundos reales
        
        # 1. CAPA BIO (Respiración Humana/Piloto)
        # Ciclo de 17 segundos (Inhalar/Exhalar)
        bio_phase = math.sin((2 * math.pi * t) / 17.0)
        
        # 2. CAPA CRISTAL (YHWH - Respiración Rápida)
        # Modulada por patrón 10-5-6-5 (Simplificado aquí como onda rápida)
        # Base 41Hz es muy rápido para ver, usamos armónico visible
        crys_phase = math.sin((2 * math.pi * t) / (17.0 / 4.0)) # 4 ciclos por ciclo bio
        
        # 3. CAPA SISTEMA (Salto 17 - Purga)
        # Se activa cada 17 segundos exactos (Punto cero)
        is_jump_17 = (t > 0) and (abs(t % 17.0) < 0.15)
        sys_val = 1.0 if is_jump_17 else 0.0
        
        # 4. CAPA VENUS (Ciclo Phi 13:8)
        # 8 años Tierra = 5 Venus. Ratio 1.6.
        # Simulamos que Venus completa un ciclo "Phi" cada 1.618 * 10s
        venus_phase = math.sin((2 * math.pi * t) / 16.18)
        
        # 5. CAPA GEOGLIFOS (Interferencia Estática)
        # Una rejilla fija que actúa como filtro (Anclaje)
        # Frecuencia alta y estable (La Tierra no cambia rápido)
        geo_phase = math.cos(t * 5.0) 

        # --- VISUALIZACIÓN DE BARRAS ---
        
        # Normalizar valores -1..1 a 0..10 caracteres
        def bar(val, char):
            length = int((val + 1) * 3)
            return char * length
            
        b_bio  = bar(bio_phase, "█")
        b_crys = bar(crys_phase, "▒")
        b_ven  = bar(venus_phase, "♀")
        b_geo  = bar(geo_phase, "⏚")
        
        marker_sys = "⚡ JUMP" if sys_val > 0.5 else "  ..."

        # Detección de ALINEACIÓN (Convergence)
        # Cuando Bio, Venus y Crystal cruzan cero o pico simultáneamente
        threshold = 0.8
        alignment = (bio_phase > threshold) and (venus_phase > threshold) and (crys_phase > threshold)
        
        line_color = C_RESET
        prefix = f"T={t:04.1f}"
        
        if is_jump_17:
            line_color = "\033[91m" # Rojo para el salto
            prefix = f"T={t:04.1f} >>> AXIOMATIC PURGE <<<"
            
        if alignment:
            line_color = C_SYNC # Fondo Rojo
            prefix = f"T={t:04.1f} *** HARMONIC CONVERGENCE ***"
            total_sync_moments += 1
            convergence_times.append(t)

        # Renderizar línea
        # Usamos formato fijo para columnas
        print(f"{line_color}{prefix:<35} | {C_BIO}{b_bio:<6}{C_RESET} | {C_CRYS}{b_crys:<6}{C_RESET} | {C_SYS}{marker_sys:<8}{C_RESET} | {C_VEN}{b_ven:<6}{C_RESET} | {C_GEO}{b_geo:<6}{C_RESET}")
        
        time.sleep(0.05)

    print("=" * 70)
    print(f"🏁 SIMULACIÓN COMPLETADA (68s)")
    print(f"✨ Momentos de Convergencia Total: {total_sync_moments}")
    
    if total_sync_moments > 0:
        print("✅ EL SISTEMA TIENE PUNTOS DE ENTRADA AL VACÍO (PORTALES).")
        print(f"\n🌀 Tiempos de Portal detectados:")
        for ct in convergence_times[:10]:  # Mostrar primeros 10
            print(f"   - T={ct:.1f}s")
        if len(convergence_times) > 10:
            print(f"   ... y {len(convergence_times) - 10} más")
    else:
        print("⚠️  DISONANCIA: No se encontraron puntos de alineación perfecta.")
    
    # Análisis de patrón
    if len(convergence_times) >= 2:
        intervals = [convergence_times[i+1] - convergence_times[i] for i in range(len(convergence_times)-1)]
        avg_interval = sum(intervals) / len(intervals)
        print(f"\n📊 Intervalo promedio entre portales: {avg_interval:.2f}s")

if __name__ == "__main__":
    print("\n🔬 EXP-028: PENTA-RESONANCE SIMULATOR")
    print("   Objetivo: Identificar ventanas de sincronía armónica perfecta")
    print("   entre las 5 capas de resonancia del sistema ME-60OS\n")
    visualize_penta_resonance()
