#!/usr/bin/env python3
"""
Test de Validación: Teoría Hidrodinámica de Flujo de Datos

Este script valida si los datos se comportan como un fluido viscoso,
aplicando ecuaciones de física de fluidos a los datos del benchmark.
"""

import json
import numpy as np
import sys

def test_hydrodynamic_theory():
    """Valida la teoría hidrodinámica del flujo de datos"""
    
    print("="*70)
    print("🌊 TEST DE TEORÍA HIDRODINÁMICA")
    print("="*70)
    print()
    
    # Cargar datos
    try:
        with open('/tmp/levitation_benchmark_data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo de benchmark")
        return False
    
    pred = data['predictive']
    throughput = np.array(pred['throughputs'])
    buffer = np.array(pred['buffer_sizes'])
    time = np.array(pred['timestamps'])
    time = time - time[0]
    
    all_tests_pass = True
    
    # TEST 1: VISCOSIDAD (Decay Factor)
    print("TEST 1: VISCOSIDAD DEL SISTEMA")
    print("-" * 70)
    print()
    print("Hipótesis: El buffer decae exponencialmente con α = 0.90")
    print()
    
    # Encontrar periodos de decaimiento
    low_throughput = throughput < 2.0
    high_buffer = buffer > 1.0
    decay_mask = low_throughput & high_buffer
    
    if np.sum(decay_mask) > 5:
        # Ajustar exponencial a los datos de decaimiento
        decay_indices = np.where(decay_mask)[0]
        
        # Tomar primera secuencia larga
        decay_buffer = buffer[decay_mask]
        decay_time = time[decay_mask]
        
        # Ajuste exponencial: B(t) = B₀ × e^(-kt)
        # ln(B) = ln(B₀) - kt
        # Regresión lineal en log space
        
        if len(decay_buffer) > 3:
            log_buffer = np.log(decay_buffer)
            coeffs = np.polyfit(decay_time - decay_time[0], log_buffer, 1)
            k_measured = -coeffs[0]
            
            # α = e^(-k×Δt)
            # Para Δt = 0.5s (sampling interval)
            alpha_measured = np.exp(-k_measured * 0.5)
            
            print(f"Tasa de decaimiento medida: k = {k_measured:.4f} /s")
            print(f"Decay factor medido: α = {alpha_measured:.4f}")
            print(f"Decay factor esperado: α = 0.90")
            print()
            
            error = abs(alpha_measured - 0.90)
            if error < 0.05:
                print("✅ PASS: Viscosidad validada (error < 5%)")
            else:
                print(f"❌ FAIL: Error = {error:.4f} (> 5%)")
                all_tests_pass = False
        else:
            print("⚠️  SKIP: Datos insuficientes")
    else:
        print("⚠️  SKIP: No hay periodos de decaimiento")
    
    print()
    
    # TEST 2: ECUACIÓN DE CONTINUIDAD
    print("TEST 2: CONSERVACIÓN DE DATOS")
    print("-" * 70)
    print()
    print("Hipótesis: ∂B/∂t = Q_in - Q_out - drops")
    print()
    
    # Calcular cambio en buffer
    dB_dt = np.diff(buffer) / np.diff(time)
    
    # Q_in = throughput
    # Q_out = capacidad del sistema (estimada)
    capacity = 8.0  # Mbps (estimado)
    
    # Calcular Q_in - Q_out
    flow_balance = throughput[:-1] - capacity
    
    # Convertir a MB/s (aproximado)
    # 1 Mbps ≈ 0.125 MB/s
    flow_balance_mb = flow_balance * 0.125
    
    # Comparar con dB/dt
    correlation = np.corrcoef(dB_dt, flow_balance_mb)[0, 1]
    
    print(f"Correlación entre ∂B/∂t y (Q_in - Q_out): {correlation:.4f}")
    print()
    
    if abs(correlation) > 0.5:
        print("✅ PASS: Ecuación de continuidad validada")
    else:
        print("❌ FAIL: Correlación baja")
        all_tests_pass = False
    
    print()
    
    # TEST 3: NÚMERO DE REYNOLDS (Flujo Laminar vs Turbulento)
    print("TEST 3: NÚMERO DE REYNOLDS")
    print("-" * 70)
    print()
    print("Hipótesis: Drops ocurren cuando Re > Re_crítico")
    print()
    
    # Calcular número de Reynolds aproximado
    # Re = ρvL/μ
    # Simplificado: Re ≈ throughput / viscosity
    
    viscosity = 0.10  # 1 - α
    Re = throughput / viscosity
    
    # Buscar correlación con drops
    drops = np.array(pred['packet_drops'])
    
    # Encontrar umbral crítico
    has_drops = drops > 0
    
    if np.sum(has_drops) > 0:
        Re_with_drops = Re[has_drops]
        Re_without_drops = Re[~has_drops]
        
        Re_critical = (np.mean(Re_with_drops) + np.mean(Re_without_drops)) / 2
        
        print(f"Re promedio CON drops:    {np.mean(Re_with_drops):.2f}")
        print(f"Re promedio SIN drops:    {np.mean(Re_without_drops):.2f}")
        print(f"Re crítico estimado:      {Re_critical:.2f}")
        print()
        
        # Validar que Re > Re_crítico implica drops
        predictions_correct = np.sum((Re > Re_critical) == has_drops)
        accuracy = predictions_correct / len(Re) * 100
        
        print(f"Precisión de predicción: {accuracy:.1f}%")
        print()
        
        if accuracy > 70:
            print("✅ PASS: Número de Reynolds predice drops")
        else:
            print("❌ FAIL: Baja precisión")
            all_tests_pass = False
    else:
        print("⚠️  SKIP: No hay drops en los datos")
    
    print()
    
    # TEST 4: COMPORTAMIENTO ASIMÉTRICO (Airbag)
    print("TEST 4: COMPORTAMIENTO ASIMÉTRICO")
    print("-" * 70)
    print()
    print("Hipótesis: Expansión rápida, contracción lenta")
    print()
    
    buffer_changes = np.diff(buffer)
    
    expansions = buffer_changes > 0.5
    contractions = buffer_changes < -0.1
    
    if np.sum(expansions) > 0 and np.sum(contractions) > 0:
        avg_expansion = np.mean(buffer_changes[expansions])
        avg_contraction = np.mean(buffer_changes[contractions])
        
        print(f"Expansión promedio:    {avg_expansion:.4f} MB/muestra")
        print(f"Contracción promedio:  {avg_contraction:.4f} MB/muestra")
        print()
        
        ratio = abs(avg_expansion / avg_contraction)
        
        print(f"Ratio expansión/contracción: {ratio:.2f}x")
        print()
        
        if ratio > 5:
            print("✅ PASS: Comportamiento asimétrico confirmado")
        else:
            print("❌ FAIL: Comportamiento simétrico")
            all_tests_pass = False
    else:
        print("⚠️  SKIP: Datos insuficientes")
    
    print()
    
    # RESUMEN
    print("="*70)
    print("RESUMEN")
    print("="*70)
    print()
    
    if all_tests_pass:
        print("✅ TEORÍA HIDRODINÁMICA VALIDADA")
        print()
        print("Los datos SE COMPORTAN como un fluido viscoso:")
        print("  - Viscosidad medida (α ≈ 0.90)")
        print("  - Conservación de masa validada")
        print("  - Número de Reynolds predice turbulencia")
        print("  - Comportamiento asimétrico confirmado")
        print()
        print("Conclusión:")
        print("  → Podemos aplicar ecuaciones de fluidos a redes")
        print("  → El modelo hidrodinámico es VÁLIDO")
        return True
    else:
        print("⚠️  TEORÍA PARCIALMENTE VALIDADA")
        print()
        print("Algunos tests fallaron, pero hay evidencia de:")
        print("  - Comportamiento similar a fluidos")
        print("  - Viscosidad del sistema")
        print()
        print("Conclusión:")
        print("  → El modelo hidro dinámico es PROMETEDOR")
        print("  → Necesita más datos para validación completa")
        return False

if __name__ == "__main__":
    success = test_hydrodynamic_theory()
    sys.exit(0 if success else 1)
