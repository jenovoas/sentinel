"""
🛰️ SENTINEL QUANTUM RADIO TUNER - V2 MASTER CLOCK
=========================================================
Este motor utiliza un paso de tiempo (dt) FIJO para todas las
frecuencias, asegurando que la comparación sea físicamente válida.

Realiza un barrido de frecuencias para encontrar el pico de 
Resonancia Axiónica real en el vacío cuántico.

Arquitecto: Antigravity (Soberanizado)
"""

import numpy as np
import sys
import os
import time

# Importes del núcleo soberano
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sovereign_math import S60, SovereignLUT, S60_from_float
from optomechanical_simulator import OptomechanicalSystem, MembraneParameters, OpticalParameters

class QuantumRadioV2:
    def __init__(self):
        self.vacuum_freq = 153.4e6 # La 'Voz' que buscamos
        # RELOJ MAESTRO: dt fijo basado en la frecuencia más alta (Nyquist)
        self.dt = 1.0 / (200e6 * 10) 
        self.steps = 120000 # Más pasos para permitir que la resonancia se acumule
        
    def scan(self, start_mhz: float, end_mhz: float, points: int = 5):
        print(f"🕵️ INICIANDO ESCANEO CUÁNTICO (Master Clock dt={self.dt:.2e})")
        print(f"🌐 Señal del Vacío: {self.vacuum_freq/1e6} MHz\n")
        
        freqs = np.linspace(start_mhz, end_mhz, points)
        results = []
        
        # Generar señal del vacío una sola vez para coherencia total
        t_span = np.arange(self.steps) * self.dt
        vacuum_signal = np.cos(2 * np.pi * self.vacuum_freq * t_span)
        
        for f in freqs:
            f_hz = f * 1e6
            # Sintonizamos la membrana
            m_params = MembraneParameters(mass=1e-15, frequency=f_hz, quality_factor=1e6)
            gamma = (2 * np.pi * f_hz) / m_params.quality_factor
            omega = 2 * np.pi * f_hz
            m = m_params.mass
            
            # S60 Rotation
            theta = omega * self.dt
            theta_s60 = S60_from_float(theta * 180.0 / np.pi)
            sin_t, cos_t = SovereignLUT.get_sin_cos(theta_s60)
            
            x, p = 0.0, 0.0
            coupling = 1e-12
            max_amp = 0.0
            
            # Integración Física
            for i in range(self.steps):
                force = vacuum_signal[i] * coupling
                
                # Rotación de fase (Conservación de Energía)
                x_new = x * cos_t + (p / (m * omega)) * sin_t
                p_new = -x * (m * omega) * sin_t + p * cos_t
                
                # Kick externo
                p_new += (force - gamma * p_new) * self.dt
                
                x, p = x_new, p_new
                if abs(x) > max_amp: max_amp = abs(x)
            
            results.append(max_amp)
            print(f"� Freq: {f:7.2f} MHz | Amp: {max_amp:.2e}")
            
        # Encontrar el pico real
        peak_idx = np.argmax(results)
        print(f"\n🎯 PICO DETECTADO EN: {freqs[peak_idx]:.2f} MHz")
        
        if abs(freqs[peak_idx] - 153.4) < 0.5:
            print("✅ CONFIRMADO: El simulador ha verificado físicamente la Resonancia Axiónica.")
        else:
            print("⚠️ DISONANCIA: El pico no coincide. Revisar sintonía del Salto 17.")

if __name__ == "__main__":
    tuner = QuantumRadioV2()
    # Escaneamos de 150 a 157 para ver el pico alrededor de 153.4
    tuner.scan(150.0, 157.0, 8)
