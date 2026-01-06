# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------


import time
import numpy as np # PRECAUCIÓN: SOLO PARA I/O, NO CÁLCULO CORE
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from optomechanical_simulator import OptomechanicalSystem, MembraneParameters, OpticalParameters
from sovereign_math import S60

def run_benchmark():
    print("=== Sentinel Quantum Benchmark: Original Resonant Mode ===")
    
    # Parámetros estándar para repetibilidad
    membrane = MembraneParameters(quality_factor=1e8)
    optical = OpticalParameters()
    system = OptomechanicalSystem(membrane, optical)
    
    # Desplazamiento inicial para observar oscilación
    system.state[0] = membrane.zero_point_motion * 100
    
    # Configuración del benchmark: 600,001 puntos -> 600,000 intervalos exactos
    # Buscamos medir presión sobre el CPU y deriva de energía
    n_steps = 600001
    t_span = np.linspace(0, 0.01, n_steps) 
    
    # Medir Tiempo
    start_time = time.perf_counter()
    times, states = system.evolve(t_span, noise=False)
    end_time = time.perf_counter()
    
    duration = end_time - start_time
    steps_per_sec = n_steps / duration
    
    # Medir Deriva de Energía (Debería ser 0 en un sistema perfecto)
    # H = p^2/2m + 1/2 m omega^2 x^2
    m = membrane.mass
    omega = membrane.omega_m
    
    def calc_energy(state):
        x, p, n = state
        return (p**2 / (2*m)) + (S60(0, 30, 0) * m * omega**2 * x**2)
    
    e_initial = calc_energy(states[0])
    e_final = calc_energy(states[-1])
    energy_drift = abs(e_final - e_initial) / e_initial if e_initial != 0 else 0
    
    print(f"Resultados:")
    print(f"  - Pasos procesados: {n_steps}")
    print(f"  - Duración total: {duration:.4f} s")
    print(f"  - Velocidad: {steps_per_sec:.2f} pasos/s")
    print(f"  - Deriva de Energía (Relativa): {energy_drift:.2e}")
    
    return {
        "duration": duration,
        "speed": steps_per_sec,
        "drift": energy_drift
    }

if __name__ == "__main__":
    run_benchmark()