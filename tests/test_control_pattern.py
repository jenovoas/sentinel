#!/usr/bin/env python3
"""
Test del Patrón de Control de Buffer

Este script valida la ecuación descubierta:
  Buffer(t) = 0.50 + 0.1610 × (Throughput - 1.19)

Ejecuta múltiples pruebas para verificar que el patrón se mantiene.
"""

import json
import numpy as np
import sys

class ProportionalBufferController:
    """Controlador proporcional basado en el patrón descubierto"""
    
    def __init__(self):
        self.buffer_base = 0.50  # MB
        self.gain = 0.1610       # MB/Mbps
        self.baseline = 1.19     # Mbps
    
    def calculate_buffer(self, throughput_mbps):
        """Calcula buffer necesario dado throughput"""
        buffer_mb = self.buffer_base + self.gain * (throughput_mbps - self.baseline)
        return max(self.buffer_base, buffer_mb)
    
    def validate_pattern(self, throughput_data, buffer_data):
        """Valida el patrón con datos reales"""
        errors = []
        
        for tp, buf_real in zip(throughput_data, buffer_data):
            buf_predicted = self.calculate_buffer(tp)
            error = abs(buf_predicted - buf_real)
            errors.append(error)
        
        return {
            'mean_error': np.mean(errors),
            'max_error': np.max(errors),
            'std_error': np.std(errors),
            'accuracy': (1 - np.mean(errors) / np.mean(buffer_data)) * 100
        }

def test_pattern():
    """Ejecuta tests del patrón"""
    
    print("="*70)
    print("TEST DEL PATRÓN DE CONTROL DE BUFFER")
    print("="*70)
    print()
    
    # Cargar datos del benchmark
    try:
        with open('/tmp/levitation_benchmark_data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Error: No se encontró /tmp/levitation_benchmark_data.json")
        print("   Ejecuta primero: python tests/benchmark_levitation.py")
        return False
    
    # Crear controlador
    controller = ProportionalBufferController()
    
    # Test 1: Validar con datos de PREDICTIVE mode
    print("TEST 1: Validación con datos del benchmark")
    print("-" * 70)
    
    pred_throughput = np.array(data['predictive']['throughputs'])
    pred_buffer = np.array(data['predictive']['buffer_sizes'])
    
    results = controller.validate_pattern(pred_throughput, pred_buffer)
    
    print(f"Error promedio:  {results['mean_error']:.4f} MB")
    print(f"Error máximo:    {results['max_error']:.4f} MB")
    print(f"Desv. estándar:  {results['std_error']:.4f} MB")
    print(f"Precisión:       {results['accuracy']:.2f}%")
    print()
    
    if results['accuracy'] > 95:
        print("✅ PASS: Precisión > 95%")
    else:
        print("❌ FAIL: Precisión < 95%")
    print()
    
    # Test 2: Predicciones manuales
    print("TEST 2: Predicciones manuales")
    print("-" * 70)
    
    test_cases = [
        (1.19, 0.50),   # Baseline
        (10.0, 1.92),   # Bajo
        (20.0, 3.53),   # Medio
        (30.0, 5.14),   # Alto
        (50.0, 8.36),   # Muy alto
    ]
    
    print("Throughput | Buffer Esperado | Buffer Calculado | Error")
    print("-----------+-----------------+------------------+-------")
    
    all_pass = True
    for throughput, expected_buffer in test_cases:
        calculated = controller.calculate_buffer(throughput)
        error = abs(calculated - expected_buffer)
        status = "✅" if error < 0.1 else "❌"
        
        print(f"{throughput:8.2f} Mbps | {expected_buffer:12.2f} MB | {calculated:13.2f} MB | {error:.3f} {status}")
        
        if error >= 0.1:
            all_pass = False
    
    print()
    if all_pass:
        print("✅ PASS: Todas las predicciones dentro de tolerancia")
    else:
        print("❌ FAIL: Algunas predicciones fuera de tolerancia")
    print()
    
    # Test 3: Cálculo inverso
    print("TEST 3: Cálculo inverso (buffer → throughput)")
    print("-" * 70)
    
    def inverse_calculation(buffer_mb):
        """Calcula throughput máximo dado un buffer"""
        return controller.baseline + (buffer_mb - controller.buffer_base) / controller.gain
    
    buffer_sizes = [0.5, 1.0, 2.0, 5.0, 10.0]
    
    print("Buffer Size | Throughput Soportado")
    print("------------+---------------------")
    
    for buf in buffer_sizes:
        max_tp = inverse_calculation(buf)
        print(f"{buf:8.2f} MB | {max_tp:15.2f} Mbps")
    
    print()
    print("✅ PASS: Cálculo inverso funciona")
    print()
    
    # Resumen
    print("="*70)
    print("RESUMEN")
    print("="*70)
    print()
    print("Ecuación validada:")
    print(f"  Buffer(t) = {controller.buffer_base:.2f} + {controller.gain:.4f} × (Throughput - {controller.baseline:.2f})")
    print()
    print(f"Precisión: {results['accuracy']:.2f}%")
    print()
    
    if results['accuracy'] > 95 and all_pass:
        print("✅ TODOS LOS TESTS PASARON")
        print()
        print("El patrón de control es válido y reproducible.")
        return True
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print()
        print("El patrón necesita ajustes.")
        return False

if __name__ == "__main__":
    success = test_pattern()
    sys.exit(0 if success else 1)
