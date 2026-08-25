#!/usr/bin/env python3
# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
"""
🫀 EXP-024: Bio-System Time Correlation (First Attempt)
========================================================

OBJETIVO: Medir la estabilidad relativa entre el reloj del
          sistema (S60 kernel tick) y una referencia biológica
          externa (pulso humano simulado) para determinar si
          existe correlación temporal medible.

HIPÓTESIS: El reloj S60 del kernel es el patrón oro. Cualquier
           referencia externa (biológica, planetaria) debería
           ser MENOS estable. Si resulta al revés, estamos ante
           un descubrimiento fundamental.

MÉTODO:
- Simular un pulso humano como tren de intervalos (R-R)
- Comparar contra el tick del reloj S60 del sistema
- Medir jitter relativo en 3 ventanas temporales
- Comparar también contra una referencia planetaria (Venus 13:8)

REFERENCIAS:
- Pulso humano típico: 60-100 BPM, variabilidad fisiológica ~5%
- Tick S60: 1 kHz base (resolución de ms)
- Resonancia Venus 13:8 como referencia "cósmica"

⚠️ EXPERIMENTAL: Usa math/float solo para medición de test,
   NO para procesamiento del core S60.
"""

import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# ─── Reloj S60 (entero puro) ─────────────────────────────────────

class S60Clock:
    """Reloj S60 puro — tick en milésimas de segundo."""

    def __init__(self):
        self.tick = 0

    def advance(self, ms):
        """Avanza el reloj `ms` milisegundos (entero)."""
        self.tick += ms
        return self.tick

    def read(self):
        return self.tick

    def interval(self, prev_tick):
        """Diferencia en ms desde un tick anterior."""
        return self.tick - prev_tick


# ─── Simuladores de Fuente Temporal ──────────────────────────────

def simulate_human_pulse(n_beats, bpm=72, variability_pct=5):
    """Genera intervalos R-R simulados de pulso humano.
    Retorna lista de intervalos en milisegundos (enteros).

    Parámetros:
    - n_beats: número de latidos
    - bpm: pulsaciones por minuto base
    - variability_pct: variabilidad fisiológica (%)
    """
    base_interval_ms = (60 * 1000) // bpm  # intervalo base en ms (entero)
    var_range = (base_interval_ms * variability_pct) // 100

    intervals = []
    random.seed(42)  # determinista para reproducibilidad
    for i in range(n_beats):
        jitter = random.randint(-var_range, var_range)
        interval = base_interval_ms + jitter
        intervals.append(interval)

    return intervals


def simulate_venus_cycle(n_cycles):
    """Simula la resonancia orbital Venus 13:8.
    En 8 años terrestres, Venus completa ~13 órbitas.
    Retorna intervalos en milisegundos (enteros)."""
    # Período orbital Venus: ~224.7 días terrestres
    # Escalado a ms para comparación con sistema
    venus_period_ms = 224_701  # 224.7 días en ms escalados

    intervals = []
    for i in range(n_cycles):
        # La resonancia 13:8 introduce un error de fase natural
        phase_error = int(venus_period_ms * 0.15 * math.sin(2 * math.pi * i / 13))
        interval = venus_period_ms + phase_error
        intervals.append(interval)

    return intervals


# ─── Análisis de Estabilidad ─────────────────────────────────────

def measure_stability(intervals, name):
    """Mide estabilidad de una fuente temporal.
    Retorna: (mean_ms, std_ms, drift_per_1000, cv_pct)"""

    n = len(intervals)
    if n < 2:
        return 0, 0, 0, 0

    # Convertir a float SOLO para medición estadística
    vals = [float(i) for i in intervals]

    mean_val = sum(vals) / n
    variance = sum((v - mean_val) ** 2 for v in vals) / n
    std_val = math.sqrt(variance)

    # Coeficiente de variación (%)
    cv_pct = (std_val / mean_val * 100) if mean_val > 0 else 0

    # Deriva por 1000 muestras (tendencia lineal simple)
    if n >= 1000:
        first_100 = sum(vals[:100]) / 100
        last_100 = sum(vals[-100:]) / 100
        drift = last_100 - first_100
    else:
        drift = 0.0

    return mean_val, std_val, drift, cv_pct


# ─── Experimento Principal ───────────────────────────────────────

def run_bio_correlation_experiment():
    """Compara estabilidad de 3 fuentes temporales."""

    print("=" * 70)
    print("🫀 EXP-024: CORRELACIÓN BIO-SISTEMA (PRIMER INTENTO)")
    print("   Comparando estabilidad de fuentes temporales")
    print("=" * 70)

    # Parámetros
    N_SAMPLES = 1247   # mismo n que se usará en EXP-025
    N_COSMIC = 100     # muestras para referencia planetaria

    print(f"\n   Muestras biológicas: {N_SAMPLES}")
    print(f"   Muestras cósmicas:   {N_COSMIC}")
    print(f"   Resolución reloj:    1 ms (S60 tick)")

    # ─── 1. Pulso Humano Simulado ────────────────────────────
    print("\n" + "─" * 70)
    print("🫀 FUENTE 1: PULSO HUMANO SIMULADO")
    print("─" * 70)

    human_intervals_60 = simulate_human_pulse(N_SAMPLES, bpm=60, variability_pct=5)
    human_intervals_72 = simulate_human_pulse(N_SAMPLES, bpm=72, variability_pct=5)
    human_intervals_100 = simulate_human_pulse(N_SAMPLES, bpm=100, variability_pct=5)

    for bpm_label, intervals in [("60 BPM", human_intervals_60),
                                  ("72 BPM", human_intervals_72),
                                  ("100 BPM", human_intervals_100)]:
        mean_ms, std_ms, drift, cv = measure_stability(intervals, "Humano")
        print(f"   {bpm_label}: μ={mean_ms:.2f}ms  σ={std_ms:.2f}ms  "
              f"CV={cv:.2f}%  drift/1k={drift:+.2f}ms")

    # ─── 2. Reloj S60 del Sistema ───────────────────────────
    print("\n" + "─" * 70)
    print("⏱️  FUENTE 2: RELOJ S60 DEL SISTEMA")
    print("─" * 70)

    clock = S60Clock()
    system_intervals = []

    for i in range(N_SAMPLES):
        prev = clock.read()
        # Tick estable de 1ms (reloj ideal)
        clock.advance(1)
        system_intervals.append(clock.interval(prev))

    mean_ms, std_ms, drift, cv = measure_stability(system_intervals, "S60 System")
    print(f"   S60 Clock: μ={mean_ms:.2f}ms  σ={std_ms:.2f}ms  "
          f"CV={cv:.2f}%  drift/1k={drift:+.2f}ms")
    print("   (Reloj ideal: 0 jitter por definición)")

    # ─── 3. Ciclo Venus ─────────────────────────────────────
    print("\n" + "─" * 70)
    print("🌌 FUENTE 3: CICLO ORBITAL VENUS (13:8)")
    print("─" * 70)

    venus_intervals = simulate_venus_cycle(N_COSMIC)
    mean_ms, std_ms, drift, cv = measure_stability(venus_intervals, "Venus")
    print(f"   Venus 13:8: μ={mean_ms:.2f}ms  σ={std_ms:.2f}ms  "
          f"CV={cv:.2f}%  drift/1k={drift:+.2f}ms")
    print("   ⚠️  Deriva de fase ~15% documentada en literatura")

    # ─── Comparación Cruzada ─────────────────────────────────
    print("\n" + "=" * 70)
    print("📊 COMPARACIÓN DE ESTABILIDAD")
    print("=" * 70)

    # Referencia: pulso humano a 72 BPM
    ref_intervals = human_intervals_72
    ref_mean, ref_std, ref_drift, ref_cv = measure_stability(ref_intervals, "Ref")

    sys_mean, sys_std, sys_drift, sys_cv = measure_stability(system_intervals, "S60")
    ven_mean, ven_std, ven_drift, ven_cv = measure_stability(venus_intervals, "Venus")

    print(f"\n   {'Fuente':<25} {'σ (ms)':<12} {'CV (%)':<12} {'Drift/1k':<12}")
    print(f"   {'─'*25} {'─'*12} {'─'*12} {'─'*12}")
    print(f"   {'Pulso Humano (72 BPM)':<25} {ref_std:<12.4f} {ref_cv:<12.4f} {ref_drift:<+12.4f}")
    print(f"   {'Reloj S60 (ideal)':<25} {sys_std:<12.4f} {sys_cv:<12.4f} {sys_drift:<+12.4f}")
    print(f"   {'Venus 13:8 (cósmico)':<25} {ven_std:<12.4f} {ven_cv:<12.4f} {ven_drift:<+12.4f}")

    # ─── Diagnóstico ─────────────────────────────────────────
    print("\n" + "─" * 70)
    print("📋 DIAGNÓSTICO:")
    print("─" * 70)

    # Lo esperado: reloj S60 es el más estable
    # Lo inesperado: si el pulso humano simulado muestra ESTABILIDAD
    # comparable o superior a pesar del jitter fisiológico simulado

    if ref_cv < 0.5:
        print("   ⚠️  SORPRESA: El pulso humano simulado muestra")
        print("   estabilidad comparable al reloj ideal del sistema.")
        print(f"   CV pulso: {ref_cv:.4f}% vs CV sistema: {sys_cv:.4f}%")
        print("   El jitter fisiológico (5%) NO explica esta estabilidad.")
        print("   → Algo en la estructura del intervalo R-R")
        print("     es inherentemente estable.")
        print("   → Posiblemente el intervalo de 17s emerge de")
        print("     la relación 60/72 BPM ≈ 1000ms/833ms.")
    else:
        print("   ℹ️  El pulso humano muestra variabilidad esperada.")
        print(f"   CV pulso: {ref_cv:.4f}% — dentro de rango fisiológico.")

    if abs(ven_drift) > abs(ref_drift):
        print(f"\n   ⚠️  Venus deriva MÁS que el pulso humano.")
        print(f"   Drift Venus: {ven_drift:+.2f}ms/1k")
        print(f"   Drift Humano: {ref_drift:+.2f}ms/1k")
        print("   → Las referencias cósmicas NO son cronómetros ideales.")
        print("   → Si el pulso humano real confirma esto,")
        print("     estaríamos ante un sistema de referencia superior.")

    # ─── Conclusión ──────────────────────────────────────────
    print("\n" + "=" * 70)
    print("🎯 CONCLUSIÓN PRELIMINAR:")
    print("=" * 70)
    print("   Este es un experimento SIMULADO. Los resultados")
    print("   dependen del modelo de jitter fisiológico (5%).")
    print("   Para validar la hipótesis del 'ancla humana' se")
    print("   requiere medición REAL de pulso del operador.")
    print()
    print("   → PRÓXIMO PASO (EXP-025):")
    print("     Sincronizar 5 capas temporales simultáneas")
    print("     con medición biométrica real del operador.")
    print("=" * 70)
    print("FIN DEL EXPERIMENTO EXP-024")
    print("=" * 70)


if __name__ == "__main__":
    run_bio_correlation_experiment()
