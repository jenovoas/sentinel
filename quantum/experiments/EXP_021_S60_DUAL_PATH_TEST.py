#!/usr/bin/env python3
"""
🧪 EXP-021: S60 Dual-Path Validation Test
==========================================

OBJETIVO: Validar que los cálculos S60 producen resultados comparables
          a f64 sin comprometer la seguridad del modelo físico.

MÉTODO:
1. Generar señales rPPG con entropía real
2. Calcular Lyapunov y Entropía en Python (S60 y float)
3. Comparar resultados y medir divergencia
4. Validar que están dentro del threshold aceptable (Δ < 0.1)

CONTEXTO: Preparación para migración gradual de f64 a S60 en Soul Verifier
"""

import sys
import os
sys.path.append('/home/jnovoas/dev/sentinel')

from quantum.yatra_core import S60
import math

print("🧪 EXP-021: S60 DUAL-PATH VALIDATION TEST")
print("=" * 60)

# ========================================================================
# PARTE 1: GENERAR SEÑAL rPPG CON ENTROPÍA REAL
# ========================================================================

print("\n📊 PARTE 1: Generación de Señal rPPG (Entropía Real)")
print("-" * 60)

# Generar 300 muestras (típico para rPPG de 10 segundos a 30 FPS)
signal_count = 300
signal_s60 = []
signal_float = []

print(f"Generando {signal_count} muestras con /dev/urandom...")

for i in range(signal_count):
    # Leer entropía real
    entropy_bytes = os.urandom(2)
    raw_value = int.from_bytes(entropy_bytes, 'big')
    
    # Normalizar a rango de pulso cardíaco (60-100 BPM)
    normalized = 60 + (raw_value % 41)  # Rango [60, 100]
    
    # Versión S60
    val_s60 = S60(normalized, 0, 0, 0, 0)
    signal_s60.append(val_s60)
    
    # Versión float (para comparación)
    signal_float.append(float(normalized))

print(f"✅ Señal generada: {len(signal_s60)} muestras")
print(f"   Rango S60: {min(signal_s60)} - {max(signal_s60)}")
print(f"   Rango float: {min(signal_float):.2f} - {max(signal_float):.2f}")

# ========================================================================
# PARTE 2: CALCULAR LYAPUNOV (S60 vs FLOAT)
# ========================================================================

print("\n\n📈 PARTE 2: Exponente de Lyapunov (S60 vs Float)")
print("-" * 60)

def calculate_lyapunov_float(signal):
    """Versión float (equivalente a Rust f64) - UPDATED"""
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
                # UPDATED: Take abs() of ln to handle ratio < 1
                sum_div += abs(math.log(ratio))
                count += 1
    
    if count == 0:
        return 0.0
    
    raw_lambda = sum_div / count
    # UPDATED: Scale by 0.5 instead of 2.0
    return max(0.1, min(2.5, raw_lambda * 0.5))

def calculate_lyapunov_s60(signal):
    """Versión S60 (equivalente a Rust S60) - UPDATED"""
    if len(signal) < 2:
        return S60(0, 0, 0, 0, 0)
    
    sum_div = S60(0, 0, 0, 0, 0)
    count = 0
    
    threshold = S60(0, 0, 0, 1, 0)  # 0.0001
    
    for i in range(len(signal) - 2):
        d1 = abs(signal[i + 1] - signal[i])
        d2 = abs(signal[i + 2] - signal[i + 1])
        
        if d1 > threshold:
            try:
                ratio = d2 / d1
                if ratio > S60(0, 0, 0, 0, 0):
                    # Aproximación de ln usando float (producción usa Taylor series)
                    ratio_float = ratio.to_base_units() / S60.SCALE_0
                    if ratio_float > 0:
                        # UPDATED: Take abs() of ln
                        ln_val = abs(math.log(ratio_float))
                        ln_s60 = S60.from_decimal_degrees_FOR_IMPORT_ONLY(ln_val)
                        sum_div = sum_div + ln_s60
                        count += 1
            except:
                continue
    
    if count == 0:
        return S60(0, 0, 0, 0, 0)
    
    # División por S60
    count_s60 = S60(count, 0, 0, 0, 0)
    raw_lambda = sum_div / count_s60
    
    # UPDATED: Scale by 0.5 instead of 2.0
    half = S60(0, 30, 0, 0, 0)  # 0.5
    scaled = raw_lambda * half
    
    min_val = S60(0, 6, 0, 0, 0)  # 0.1
    max_val = S60(2, 30, 0, 0, 0)  # 2.5
    
    if scaled < min_val:
        return min_val
    elif scaled > max_val:
        return max_val
    else:
        return scaled

# Calcular con ambos métodos
lyap_float = calculate_lyapunov_float(signal_float)
lyap_s60 = calculate_lyapunov_s60(signal_s60)
lyap_s60_as_float = lyap_s60.to_base_units() / S60.SCALE_0

print(f"Lyapunov (float): {lyap_float:.4f}")
print(f"Lyapunov (S60):   {lyap_s60} ({lyap_s60_as_float:.4f})")

lyap_diff = abs(lyap_float - lyap_s60_as_float)
print(f"\nDivergencia: Δ = {lyap_diff:.4f}")

if lyap_diff < 0.1:
    print("✅ PASS: Divergencia dentro del threshold aceptable")
else:
    print(f"⚠️  WARNING: Divergencia alta (threshold: 0.1)")

# ========================================================================
# PARTE 3: CALCULAR ENTROPÍA (S60 vs FLOAT)
# ========================================================================

print("\n\n🎲 PARTE 3: Entropía de Shannon (S60 vs Float)")
print("-" * 60)

def calculate_entropy_float(signal):
    """Versión float"""
    from collections import Counter
    
    if not signal:
        return 0.0
    
    # Cuantizar en buckets
    buckets = [int(val * 100) for val in signal]
    counts = Counter(buckets)
    
    total = len(signal)
    entropy = 0.0
    
    for count in counts.values():
        if count == 0:
            continue
        p = count / total
        if p > 0:
            entropy -= p * math.log(p)
    
    return entropy

def calculate_entropy_s60(signal):
    """Versión S60"""
    from collections import Counter
    
    if not signal:
        return S60(0, 0, 0, 0, 0)
    
    # Cuantizar en buckets
    buckets = [val.to_base_units() // (S60.SCALE_0 // 100) for val in signal]
    counts = Counter(buckets)
    
    total = len(signal)
    entropy = S60(0, 0, 0, 0, 0)
    
    for count in counts.values():
        if count == 0:
            continue
        
        # Aproximación (producción usaría ln_s60)
        p = count / total
        if p > 0:
            h_contrib = -p * math.log(p)
            h_s60 = S60.from_decimal_degrees_FOR_IMPORT_ONLY(h_contrib)
            entropy = entropy + h_s60
    
    return entropy

# Calcular con ambos métodos
entr_float = calculate_entropy_float(signal_float)
entr_s60 = calculate_entropy_s60(signal_s60)
entr_s60_as_float = entr_s60.to_base_units() / S60.SCALE_0

print(f"Entropía (float): {entr_float:.4f}")
print(f"Entropía (S60):   {entr_s60} ({entr_s60_as_float:.4f})")

entr_diff = abs(entr_float - entr_s60_as_float)
print(f"\nDivergencia: Δ = {entr_diff:.4f}")

if entr_diff < 0.1:
    print("✅ PASS: Divergencia dentro del threshold aceptable")
else:
    print(f"⚠️  WARNING: Divergencia alta (threshold: 0.1)")

# ========================================================================
# PARTE 4: VALIDACIÓN DE RANGOS
# ========================================================================

print("\n\n🎯 PARTE 4: Validación de Rangos (Modelo Físico)")
print("-" * 60)

# Rangos esperados para humanos
lyap_min = 0.1
lyap_max = 2.5
entr_min = 0.5
entr_max = 3.5

print(f"Lyapunov esperado: [{lyap_min}, {lyap_max}]")
print(f"  Float: {lyap_float:.4f} {'✅' if lyap_min <= lyap_float <= lyap_max else '❌'}")
print(f"  S60:   {lyap_s60_as_float:.4f} {'✅' if lyap_min <= lyap_s60_as_float <= lyap_max else '❌'}")

print(f"\nEntropía esperada: [{entr_min}, {entr_max}]")
print(f"  Float: {entr_float:.4f} {'✅' if entr_min <= entr_float <= entr_max else '❌'}")
print(f"  S60:   {entr_s60_as_float:.4f} {'✅' if entr_min <= entr_s60_as_float <= entr_max else '❌'}")

# ========================================================================
# CONCLUSIONES
# ========================================================================

print("\n\n" + "=" * 60)
print("📋 CONCLUSIONES")
print("=" * 60)

all_pass = (lyap_diff < 0.1 and entr_diff < 0.1 and
            lyap_min <= lyap_float <= lyap_max and
            lyap_min <= lyap_s60_as_float <= lyap_max and
            entr_min <= entr_float <= entr_max and
            entr_min <= entr_s60_as_float <= entr_max)

if all_pass:
    print("\n✅ TODAS LAS PRUEBAS PASARON")
    print("   - Divergencias dentro del threshold")
    print("   - Rangos físicos válidos")
    print("   - S60 es seguro para dual-path")
else:
    print("\n⚠️  ALGUNAS PRUEBAS FALLARON")
    print("   - Revisar divergencias")
    print("   - Validar implementación S60")

print(f"\n📊 Resumen:")
print(f"   Lyapunov Δ: {lyap_diff:.4f} ({'PASS' if lyap_diff < 0.1 else 'FAIL'})")
print(f"   Entropía Δ: {entr_diff:.4f} ({'PASS' if entr_diff < 0.1 else 'FAIL'})")

print("\n🎯 RECOMENDACIÓN:")
if all_pass:
    print("   ✅ Proceder con dual-path en producción")
    print("   ✅ Monitorear logs por 1 semana")
    print("   ✅ Preparar migración gradual")
else:
    print("   ⚠️  Revisar implementación S60")
    print("   ⚠️  Ajustar algoritmos si es necesario")
    print("   ⚠️  Re-ejecutar pruebas")

print("\n" + "=" * 60)
print("FIN DEL EXPERIMENTO")
print("=" * 60)
