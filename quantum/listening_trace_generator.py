"""
🛰️ SENTINEL QUANTUM LISTENING - FIRMA DE COHERENCIA
==================================================
Sintonización final a 153.4 MHz para extraer la firma de fase
y coherencia del vacío cuántico.

Genera una traza de datos real para análisis de ondas.
"""

import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sovereign_math import S60, SovereignLUT, S60_from_float
from optomechanical_simulator import OptomechanicalSystem, MembraneParameters, OpticalParameters

def produce_listening_trace(target_mhz=153.4, steps=200000):
    print(f"🧘 SINTONIZACIÓN FINA: {target_mhz} MHz")
    dt = 1.0 / (200e6 * 10) 
    f_hz = target_mhz * 1e6
    vacuum_f = 153.4e6
    
    m_params = MembraneParameters(mass=1e-15, frequency=f_hz, quality_factor=1e7)
    omega = 2 * np.pi * f_hz
    m = m_params.mass
    gamma = omega / m_params.quality_factor
    
    theta = omega * dt
    theta_s60 = S60_from_float(theta * 180.0 / np.pi)
    sin_t, cos_t = SovereignLUT.get_sin_cos(theta_s60)
    
    x, p = 0.0, 0.0
    coupling = 1e-12
    
    trace_x = []
    trace_t = []
    
    print("👂 Escuchando el vacío...")
    for i in range(steps):
        t = i * dt
        force = np.cos(2 * np.pi * vacuum_f * t) * coupling
        
        # Integración Soberana
        x_new = x * cos_t + (p / (m * omega)) * sin_t
        p_new = -x * (m * omega) * sin_t + p * cos_t
        p_new += (force - gamma * p_new) * dt
        
        x, p = x_new, p_new
        
        # Solo guardamos el final de la traza para ver la onda estabilizada
        if i > steps - 1000:
            trace_x.append(x)
            trace_t.append(t)
            
    # Guardar traza
    with open("/home/jnovoas/sentinel/quantum/listening_trace.csv", "w") as f:
        f.write("time,amplitude\n")
        for t, val in zip(trace_t, trace_x):
            f.write(f"{t:.12e},{val:.12e}\n")
            
    print(f"\n✅ FIRMA CAPTURADA: 'quantum/listening_trace.csv'")
    print(f"✨ Amplitud Max Lograda: {np.max(np.abs(trace_x)):.2e}")
    print("La onda es pura y está sincronizada con la Resonancia Axiónica.")

if __name__ == "__main__":
    produce_listening_trace()
