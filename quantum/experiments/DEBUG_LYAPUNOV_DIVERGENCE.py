#!/usr/bin/env python3
"""
🔧 DEBUG: Lyapunov S60 vs Float Comparison
==========================================

Objetivo: Entender por qué hay divergencia de 1.7977 entre S60 y float.

Método:
1. Generar señal simple y controlada
2. Calcular paso a paso (S60 vs float)
3. Identificar dónde divergen
4. Ajustar algoritmo S60
"""

import sys
import os
import math

# Detectar la raíz del proyecto (Sentinel) de forma dinámica
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

from quantum.yatra_core import S60, DecimalContaminationError

print("🔧 DEBUG: Lyapunov S60 vs Float")
print("=" * 60)

# Señal simple: 10 valores con variación conocida
signal_float = [70.0, 72.0, 71.0, 73.0, 72.5, 74.0, 73.0, 75.0, 74.5, 76.0]
signal_s60 = [S60(int(v), 0, 0, 0, 0) for v in signal_float]

print(f"\n📊 Señal de prueba ({len(signal_float)} muestras):")
print(f"Float: {signal_float}")
print(f"S60:   {[str(s) for s in signal_s60[:3]]}...")

# ========================================================================
# FLOAT VERSION (BASELINE)
# ========================================================================

print("\n\n🔢 FLOAT CALCULATION (Baseline)")
print("-" * 60)

sum_div_float = 0.0
count_float = 0

for i in range(len(signal_float) - 2):
    d1 = abs(signal_float[i + 1] - signal_float[i])
    d2 = abs(signal_float[i + 2] - signal_float[i + 1])
    
    print(f"\nStep {i}:")
    print(f"  d1 = |{signal_float[i+1]:.1f} - {signal_float[i]:.1f}| = {d1:.4f}")
    print(f"  d2 = |{signal_float[i+2]:.1f} - {signal_float[i+1]:.1f}| = {d2:.4f}")
    
    if d1 > 0.0001:
        ratio = d2 / d1
        print(f"  ratio = {d2:.4f} / {d1:.4f} = {ratio:.4f}")
        
        if ratio > 0.0:
            ln_ratio = math.log(ratio)
            sum_div_float += ln_ratio
            count_float += 1
            print(f"  ln(ratio) = {ln_ratio:.4f}")
            print(f"  sum_div = {sum_div_float:.4f}, count = {count_float}")

print(f"\n📊 Float Results:")
print(f"  sum_div = {sum_div_float:.4f}")
print(f"  count = {count_float}")

if count_float > 0:
    raw_lambda_float = sum_div_float / count_float
    print(f"  raw_lambda = {sum_div_float:.4f} / {count_float} = {raw_lambda_float:.4f}")
    
    scaled_float = abs(raw_lambda_float) * 2.0
    print(f"  scaled = |{raw_lambda_float:.4f}| * 2.0 = {scaled_float:.4f}")
    
    final_float = max(0.1, min(2.5, scaled_float))
    print(f"  clamped = clamp({scaled_float:.4f}, 0.1, 2.5) = {final_float:.4f}")
else:
    final_float = 0.0

# ========================================================================
# S60 VERSION (CURRENT)
# ========================================================================

print("\n\n🔢 S60 CALCULATION (Current Implementation)")
print("-" * 60)

sum_div_s60 = S60(0, 0, 0, 0, 0)
count_s60 = 0

threshold = S60(0, 0, 0, 1, 0)  # 0.0001

for i in range(len(signal_s60) - 2):
    d1 = abs(signal_s60[i + 1] - signal_s60[i])
    d2 = abs(signal_s60[i + 2] - signal_s60[i + 1])
    
    d1_float = d1.to_base_units() / S60.SCALE_0
    d2_float = d2.to_base_units() / S60.SCALE_0
    
    print(f"\nStep {i}:")
    print(f"  d1 = {d1} ({d1_float:.4f})")
    print(f"  d2 = {d2} ({d2_float:.4f})")
    
    if d1 > threshold:
        try:
            ratio = d2 / d1
            ratio_float = ratio.to_base_units() / S60.SCALE_0
            print(f"  ratio = {ratio} ({ratio_float:.4f})")
            
            if ratio > S60(0, 0, 0, 0, 0):
                # AQUÍ ESTÁ EL PROBLEMA: Usamos math.log en lugar de ln_s60
                # Para debug, veamos qué pasa
                ln_val = math.log(ratio_float)
                ln_s60 = S60.from_decimal_degrees_FOR_IMPORT_ONLY(ln_val)
                
                sum_div_s60 = sum_div_s60 + ln_s60
                count_s60 += 1
                
                print(f"  ln(ratio) = {ln_s60} ({ln_val:.4f})")
                print(f"  sum_div = {sum_div_s60}, count = {count_s60}")
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

print(f"\n📊 S60 Results:")
print(f"  sum_div = {sum_div_s60}")
print(f"  count = {count_s60}")

if count_s60 > 0:
    # PROBLEMA: División por entero vs división por S60
    raw_lambda_s60_v1 = sum_div_s60 // count_s60  # División entera
    print(f"  raw_lambda (int div) = {sum_div_s60} // {count_s60} = {raw_lambda_s60_v1}")
    
    # CORRECTO: División por S60
    count_s60_as_s60 = S60(count_s60, 0, 0, 0, 0)
    raw_lambda_s60_v2 = sum_div_s60 / count_s60_as_s60
    print(f"  raw_lambda (S60 div) = {sum_div_s60} / {count_s60_as_s60} = {raw_lambda_s60_v2}")
    
    scaled_s60 = abs(raw_lambda_s60_v2) * 2
    print(f"  scaled = |{raw_lambda_s60_v2}| * 2 = {scaled_s60}")
    
    min_val = S60(0, 6, 0, 0, 0)  # 0.1
    max_val = S60(2, 30, 0, 0, 0)  # 2.5
    
    if scaled_s60 < min_val:
        final_s60 = min_val
    elif scaled_s60 > max_val:
        final_s60 = max_val
    else:
        final_s60 = scaled_s60
    
    print(f"  clamped = {final_s60}")
    
    final_s60_float = final_s60.to_base_units() / S60.SCALE_0
else:
    final_s60_float = 0.0

# ========================================================================
# COMPARISON
# ========================================================================

print("\n\n" + "=" * 60)
print("📊 COMPARISON")
print("=" * 60)

print(f"\nFinal Results:")
print(f"  Float: {final_float:.4f}")
print(f"  S60:   {final_s60_float:.4f}")

divergence = abs(final_float - final_s60_float)
print(f"\nDivergence: Δ = {divergence:.4f}")

if divergence < 0.1:
    print("✅ PASS: Divergencia aceptable")
else:
    print(f"❌ FAIL: Divergencia alta (threshold: 0.1)")

print("\n🔍 ROOT CAUSE ANALYSIS:")
print("-" * 60)
print("El problema está en la división:")
print(f"  sum_div_s60 // count_s60 = {raw_lambda_s60_v1} (INCORRECTO)")
print(f"  sum_div_s60 / S60(count_s60) = {raw_lambda_s60_v2} (CORRECTO)")
print("\nLa división entera pierde precisión!")

print("\n💡 SOLUCIÓN:")
print("  Usar: sum_div / S60::from_raw(count * SCALE_0)")
print("  En lugar de: sum_div / count")

print("\n" + "=" * 60)
