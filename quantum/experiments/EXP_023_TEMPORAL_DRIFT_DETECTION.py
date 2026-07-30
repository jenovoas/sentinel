#!/usr/bin/env python3
# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
"""
📊 EXP-023: Temporal Drift Detection (Long-Run Monitoring)
===========================================================

OBJETIVO: Detectar si la equivalencia S60 ≡ f64 se mantiene
          en ventanas de tiempo LARGAS (>1000s simulados),
          o si emerge deriva acumulativa no detectable en
          ráfagas cortas (EXP-022).

HIPÓTESIS: Si S60 y f64 son realmente equivalentes, la
           divergencia debe ser estable en el tiempo. Si
           hay deriva creciente, algo fundamental se nos
           escapa.

MÉTODO:
- Generar 10,000 señales continuas (no ráfagas aisladas)
- Medir divergencia acumulada S60 vs f64 cada 1000 señales
- Graficar la evolución temporal de Δ
- Detectar si Δ crece, se estabiliza o diverge

CRITERIOS DE ÉXITO:
- Δ estable en el tiempo (< 0.01 de variación en Δ)
- Sin divergencia acumulativa
- Sin saltos de fase repentinos

⚠️ EXPERIMENTAL: Usa math/float solo para medición de test,
   NO para procesamiento del core S60.
"""

import sys
import os
import math
import time
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# ─── S60 Puro (sin floats) ───────────────────────────────────────
# Simulamos el tipo S60 con enteros escalados.
# 1 unidad = 1/1000 de segundo (resolución de milisegundo).
# Las operaciones son enteros puros — YATRA-compatible.

def s60_add(a, b):
    """Suma S60: enteros puros, sin float."""
    return a + b

def s60_sub(a, b):
    """Resta S60: enteros puros, sin float."""
    return a - b

def s60_mul(a, b):
    """Multiplicación S60 escalada (a * b / 1000)."""
    return (a * b) // 1000

def s60_div(a, b):
    """División S60 escalada (a * 1000 / b)."""
    if b == 0:
        return 0
    return (a * 1000) // b

def s60_signal_generator(n_samples, seed):
    """Genera señal sintética usando solo aritmética entera S60.
    Simula un oscilador armónico con fase acumulativa."""
    random.seed(seed)
    signal = []
    phase = 0  # fase en milésimas de radianes S60

    for i in range(n_samples):
        # Frecuencia base: 60 BPM = 1 Hz, con variación entera
        freq = 1000 + (random.randint(-50, 50))  # 1.0 ± 0.05 Hz en milésimas
        phase = s60_add(phase, freq)
        # Mantener fase en [0, 2π*1000] ≈ [0, 6283]
        if phase > 6283:
            phase = s60_sub(phase, 6283)
        signal.append(phase)

    return signal

# ─── Medición con floats (solo para test) ────────────────────────

def f64_signal_generator(n_samples, seed):
    """Réplica float de la señal para comparación."""
    random.seed(seed)
    signal = []
    phase = 0.0

    for i in range(n_samples):
        freq = 1.0 + (random.uniform(-0.05, 0.05))
        phase += freq
        if phase > 2.0 * math.pi:
            phase -= 2.0 * math.pi
        signal.append(phase)

    return signal

def compute_divergence(s60_signal, f64_signal):
    """Calcula divergencia normalizada entre señales S60 y f64."""
    n = min(len(s60_signal), len(f64_signal))
    total_delta = 0.0
    max_delta = 0.0

    for i in range(n):
        # Normalizar S60 a rango float [0, 2π] para comparar
        s60_norm = s60_signal[i] / 1000.0
        delta = abs(s60_norm - f64_signal[i])
        total_delta += delta
        if delta > max_delta:
            max_delta = delta

    mean_delta = total_delta / n if n > 0 else 0.0
    return mean_delta, max_delta


# ─── Experimento Principal ───────────────────────────────────────

def run_temporal_drift_experiment():
    """Ejecuta 10 bloques de 1000 señales y mide evolución de Δ."""

    print("=" * 70)
    print("🔬 EXP-023: DETECCIÓN DE DERIVA TEMPORAL")
    print("   Monitorizando divergencia S60 vs f64 en ventanas largas")
    print("=" * 70)

    BLOCK_SIZE = 1000   # señales por bloque
    N_BLOCKS = 10        # 10 bloques = 10,000 señales totales
    SAMPLES_PER_SIGNAL = 300

    drift_log = []

    for block in range(N_BLOCKS):
        block_deltas = []

        for sig in range(BLOCK_SIZE):
            seed = block * BLOCK_SIZE + sig

            s60_sig = s60_signal_generator(SAMPLES_PER_SIGNAL, seed)
            f64_sig = f64_signal_generator(SAMPLES_PER_SIGNAL, seed)

            mean_delta, max_delta = compute_divergence(s60_sig, f64_sig)
            block_deltas.append(mean_delta)

        # Estadísticas del bloque
        block_mean = sum(block_deltas) / len(block_deltas)
        block_max = max(block_deltas)
        block_min = min(block_deltas)

        # Calcular std
        variance = sum((d - block_mean) ** 2 for d in block_deltas) / len(block_deltas)
        block_std = math.sqrt(variance)

        drift_log.append({
            'block': block + 1,
            'signals': (block + 1) * BLOCK_SIZE,
            'mean_delta': block_mean,
            'max_delta': block_max,
            'min_delta': block_min,
            'std_delta': block_std,
        })

        bar = "█" * (block + 1) + "░" * (N_BLOCKS - block - 1)
        print(f"   [{bar}] Bloque {block+1}/{N_BLOCKS} | "
              f"Δ_media={block_mean:.6f} | Δ_max={block_max:.6f} | σ={block_std:.6f}")

    # ─── Análisis de Deriva ───────────────────────────────────
    print("\n" + "=" * 70)
    print("📊 ANÁLISIS DE DERIVA TEMPORAL")
    print("=" * 70)

    first_mean = drift_log[0]['mean_delta']
    last_mean = drift_log[-1]['mean_delta']
    drift_trend = last_mean - first_mean

    print(f"\n   Δ inicial (bloque 1):  {first_mean:.8f}")
    print(f"   Δ final (bloque {N_BLOCKS}): {last_mean:.8f}")
    print(f"   Tendencia de deriva:   {drift_trend:.8f}")

    # Detectar si hay crecimiento de Δ
    means = [d['mean_delta'] for d in drift_log]
    increasing_streak = 0
    max_streak = 0
    for i in range(1, len(means)):
        if means[i] > means[i-1]:
            increasing_streak += 1
            max_streak = max(max_streak, increasing_streak)
        else:
            increasing_streak = 0

    print(f"   Rachas crecientes máx: {max_streak} bloques consecutivos")

    # Verificar estabilidad
    mean_of_means = sum(means) / len(means)
    variation = max(means) - min(means)

    print(f"\n   Variación total de Δ:  {variation:.8f}")
    print(f"   Media global de Δ:     {mean_of_means:.8f}")

    print("\n" + "─" * 70)
    print("📋 DIAGNÓSTICO:")
    print("─" * 70)

    if variation < 0.001 and abs(drift_trend) < 0.0001:
        print("   ✅ Δ ESTABLE. S60 ≡ f64 se mantiene en tiempo largo.")
        print("   La equivalencia numérica es robusta.")
        print("   No se detecta deriva acumulativa.")
    elif abs(drift_trend) > 0.001:
        print("   ⚠️  DERIVA DETECTADA. Δ CRECE con el tiempo.")
        print("   Algo causa divergencia acumulativa entre S60 y f64.")
        print("   Posible causa: error de redondeo acumulado en fase.")
        print("   → INVESTIGAR: ¿es el modelo de señal o la aritmética?")
    elif variation > 0.01:
        print("   ⚠️  INESTABILIDAD DETECTADA. Δ oscila entre bloques.")
        print("   La divergencia no es constante — fluctúa.")
        print("   → INVESTIGAR: ¿hay un ciclo oculto en la divergencia?")
    else:
        print("   ℹ️  Comportamiento mixto. Requiere más muestras.")
        print(f"   Tendencia: {drift_trend:.8f}, Variación: {variation:.8f}")

    # ─── Guardar log ──────────────────────────────────────────
    print("\n" + "─" * 70)
    print("📁 LOG DE BLOQUES:")
    print("─" * 70)
    print(f"   {'Bloque':<8} {'Señales':<10} {'Δ_media':<12} {'Δ_max':<12} {'σ':<12}")
    for d in drift_log:
        print(f"   {d['block']:<8} {d['signals']:<10} {d['mean_delta']:<12.8f} "
              f"{d['max_delta']:<12.8f} {d['std_delta']:<12.8f}")

    print("\n" + "=" * 70)
    print("FIN DEL EXPERIMENTO EXP-023")
    print("=" * 70)

    return drift_log


if __name__ == "__main__":
    run_temporal_drift_experiment()
