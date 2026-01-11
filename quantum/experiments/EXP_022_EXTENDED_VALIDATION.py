#!/usr/bin/env python3
"""
📊 EXP-022: Extended Statistical Validation (1000+ Signals)
===========================================================

OBJETIVO: Validar S60 con análisis estadístico robusto
          - 1000+ señales con entropía real
          - Medir mean/std de divergencias
          - Detectar edge cases
          - Validar para producción

CRITERIOS DE ÉXITO:
- Mean divergence < 0.01
- Std divergence < 0.05
- 99% de señales con Δ < 0.1
- Sin fallos en edge cases
"""

import sys
import os
import math
import time
sys.path.append('/home/jnovoas/dev/sentinel')

from quantum.yatra_core import S60

print("📊 EXP-022: EXTENDED STATISTICAL VALIDATION")
print("=" * 70)

# ========================================================================
# CONFIGURACIÓN
# ========================================================================

NUM_SIGNALS = 1000
SIGNAL_LENGTH = 300  # 10 segundos a 30 FPS
THRESHOLD_MEAN = 0.01
THRESHOLD_STD = 0.05
THRESHOLD_99PCT = 0.1

print(f"\n⚙️  Configuración:")
print(f"   Señales a generar: {NUM_SIGNALS}")
print(f"   Longitud por señal: {SIGNAL_LENGTH} muestras")
print(f"   Threshold mean: {THRESHOLD_MEAN}")
print(f"   Threshold std: {THRESHOLD_STD}")
print(f"   Threshold 99%: {THRESHOLD_99PCT}")

# ========================================================================
# FUNCIONES DE CÁLCULO (CALIBRADAS)
# ========================================================================

def calculate_lyapunov_float(signal):
    """Float version (calibrated)"""
    if len(signal) < 2:
        return 0.0
    
    sum_div = 0.0
    count = 0
    
    for i in range(len(signal) - 2):
        d1 = abs(signal[i + 1] - signal[i])
        d2 = abs(signal[i + 2] - signal[i + 1])
        
        if d1 > 0.0001:
            ratio = d2 / d1
            if ratio > 0.0:
                sum_div += abs(math.log(ratio))
                count += 1
    
    if count == 0:
        return 0.0
    
    raw_lambda = sum_div / count
    return max(0.1, min(2.5, raw_lambda * 0.5))

def calculate_lyapunov_s60(signal):
    """S60 version (calibrated)"""
    if len(signal) < 2:
        return S60(0, 0, 0, 0, 0)
    
    sum_div = S60(0, 0, 0, 0, 0)
    count = 0
    threshold = S60(0, 0, 0, 1, 0)
    
    for i in range(len(signal) - 2):
        d1 = abs(signal[i + 1] - signal[i])
        d2 = abs(signal[i + 2] - signal[i + 1])
        
        if d1 > threshold:
            try:
                ratio = d2 / d1
                if ratio > S60(0, 0, 0, 0, 0):
                    ratio_float = ratio.to_base_units() / S60.SCALE_0
                    if ratio_float > 0:
                        ln_val = abs(math.log(ratio_float))
                        ln_s60 = S60.from_decimal_degrees_FOR_IMPORT_ONLY(ln_val)
                        sum_div = sum_div + ln_s60
                        count += 1
            except:
                continue
    
    if count == 0:
        return S60(0, 0, 0, 0, 0)
    
    count_s60 = S60(count, 0, 0, 0, 0)
    raw_lambda = sum_div / count_s60
    half = S60(0, 30, 0, 0, 0)
    scaled = raw_lambda * half
    
    min_val = S60(0, 6, 0, 0, 0)
    max_val = S60(2, 30, 0, 0, 0)
    
    if scaled < min_val:
        return min_val
    elif scaled > max_val:
        return max_val
    else:
        return scaled

# ========================================================================
# GENERACIÓN Y ANÁLISIS
# ========================================================================

print(f"\n\n🔬 Generando {NUM_SIGNALS} señales con entropía real...")
print("-" * 70)

start_time = time.time()

divergences_lyap = []
divergences_entr = []
lyap_float_values = []
lyap_s60_values = []

failed_signals = 0

for sig_idx in range(NUM_SIGNALS):
    # Generar señal con entropía real
    signal_float = []
    signal_s60 = []
    
    for i in range(SIGNAL_LENGTH):
        entropy_bytes = os.urandom(2)
        raw_value = int.from_bytes(entropy_bytes, 'big')
        normalized = 60 + (raw_value % 41)  # Rango [60, 100] BPM
        
        signal_float.append(float(normalized))
        signal_s60.append(S60(normalized, 0, 0, 0, 0))
    
    # Calcular Lyapunov
    try:
        lyap_float = calculate_lyapunov_float(signal_float)
        lyap_s60 = calculate_lyapunov_s60(signal_s60)
        lyap_s60_float = lyap_s60.to_base_units() / S60.SCALE_0
        
        divergence = abs(lyap_float - lyap_s60_float)
        divergences_lyap.append(divergence)
        lyap_float_values.append(lyap_float)
        lyap_s60_values.append(lyap_s60_float)
        
    except Exception as e:
        failed_signals += 1
        continue
    
    # Progreso cada 100 señales
    if (sig_idx + 1) % 100 == 0:
        elapsed = time.time() - start_time
        rate = (sig_idx + 1) / elapsed
        eta = (NUM_SIGNALS - sig_idx - 1) / rate
        print(f"   Procesadas: {sig_idx + 1}/{NUM_SIGNALS} ({rate:.1f} sig/s, ETA: {eta:.1f}s)")

total_time = time.time() - start_time

print(f"\n✅ Generación completada en {total_time:.2f}s")
print(f"   Señales exitosas: {len(divergences_lyap)}")
print(f"   Señales fallidas: {failed_signals}")

# ========================================================================
# ANÁLISIS ESTADÍSTICO
# ========================================================================

print("\n\n📊 ANÁLISIS ESTADÍSTICO")
print("=" * 70)

if len(divergences_lyap) > 0:
    mean_div = sum(divergences_lyap) / len(divergences_lyap)
    variance = sum((d - mean_div) ** 2 for d in divergences_lyap) / len(divergences_lyap)
    std_div = math.sqrt(variance)
    
    max_div = max(divergences_lyap)
    min_div = min(divergences_lyap)
    
    # Percentiles
    sorted_divs = sorted(divergences_lyap)
    p50 = sorted_divs[len(sorted_divs) // 2]
    p95 = sorted_divs[int(len(sorted_divs) * 0.95)]
    p99 = sorted_divs[int(len(sorted_divs) * 0.99)]
    
    # Conteo bajo threshold
    under_threshold = sum(1 for d in divergences_lyap if d < THRESHOLD_99PCT)
    pct_under = (under_threshold / len(divergences_lyap)) * 100
    
    print(f"\n📈 Divergencia Lyapunov (S60 vs Float):")
    print(f"   Mean:     {mean_div:.6f} {'✅' if mean_div < THRESHOLD_MEAN else '❌'} (threshold: {THRESHOLD_MEAN})")
    print(f"   Std Dev:  {std_div:.6f} {'✅' if std_div < THRESHOLD_STD else '❌'} (threshold: {THRESHOLD_STD})")
    print(f"   Min:      {min_div:.6f}")
    print(f"   Max:      {max_div:.6f}")
    print(f"   Median:   {p50:.6f}")
    print(f"   P95:      {p95:.6f}")
    print(f"   P99:      {p99:.6f}")
    print(f"   < {THRESHOLD_99PCT}: {pct_under:.2f}% {'✅' if pct_under >= 99 else '❌'} (target: 99%)")
    
    # Distribución de valores
    mean_lyap_float = sum(lyap_float_values) / len(lyap_float_values)
    mean_lyap_s60 = sum(lyap_s60_values) / len(lyap_s60_values)
    
    print(f"\n📊 Distribución de Valores:")
    print(f"   Float mean: {mean_lyap_float:.4f}")
    print(f"   S60 mean:   {mean_lyap_s60:.4f}")
    
    # Edge cases
    edge_cases = []
    for i, div in enumerate(divergences_lyap):
        if div > 0.05:  # Divergencia significativa
            edge_cases.append((i, div, lyap_float_values[i], lyap_s60_values[i]))
    
    if edge_cases:
        print(f"\n⚠️  Edge Cases Detectados ({len(edge_cases)}):")
        for idx, div, f_val, s_val in edge_cases[:5]:  # Mostrar primeros 5
            print(f"   Signal #{idx}: Δ={div:.6f}, float={f_val:.4f}, s60={s_val:.4f}")
    else:
        print(f"\n✅ No edge cases detectados (todas Δ < 0.05)")

# ========================================================================
# CONCLUSIONES
# ========================================================================

print("\n\n" + "=" * 70)
print("📋 CONCLUSIONES")
print("=" * 70)

all_pass = (
    mean_div < THRESHOLD_MEAN and
    std_div < THRESHOLD_STD and
    pct_under >= 99 and
    failed_signals == 0
)

if all_pass:
    print("\n✅ TODAS LAS VALIDACIONES PASARON")
    print("   - Divergencia mean dentro del threshold")
    print("   - Divergencia std dentro del threshold")
    print("   - 99%+ de señales con Δ < 0.1")
    print("   - Sin fallos en procesamiento")
    print("\n🎯 RECOMENDACIÓN: PROCEDER CON PRODUCCIÓN")
    print("   - S60 es estadísticamente equivalente a f64")
    print("   - Listo para dual-path en staging")
    print("   - Preparar migración gradual")
else:
    print("\n⚠️  ALGUNAS VALIDACIONES FALLARON")
    if mean_div >= THRESHOLD_MEAN:
        print(f"   ❌ Mean divergence alta: {mean_div:.6f}")
    if std_div >= THRESHOLD_STD:
        print(f"   ❌ Std divergence alta: {std_div:.6f}")
    if pct_under < 99:
        print(f"   ❌ Solo {pct_under:.2f}% bajo threshold")
    if failed_signals > 0:
        print(f"   ❌ {failed_signals} señales fallidas")
    
    print("\n🎯 RECOMENDACIÓN: REVISAR IMPLEMENTACIÓN")

print("\n" + "=" * 70)
print("FIN DEL EXPERIMENTO")
print("=" * 70)
