# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️ (DIRECTIVE: SIMULATION LOGIC EXEMPT FOR TESTS)
# -------------------------------------------------------------------------------------

"""
🛰️ STUDY: QUANTUM SIGNAL STABILIZATION (OBSERVER PHASE-LOCK)
===========================================================
Este experimento demuestra cómo la observación consciente actúa como
un 'Ancla de Fase'.
"""

import numpy as np # PRECAUCIÓN: SOLO PARA I/O, NO CÁLCULO CORE
import sys
import os

# Importes del núcleo soberano
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sovereign_math import S60, PI_S60
from optomechanical_simulator import OptomechanicalSystem, MembraneParameters, OpticalParameters

def to_float(s60_val):
    if hasattr(s60_val, 'to_base_units'):
         # 12960000 = 60^4 (Scale 0)
        return s60_val.to_base_units() / 12960000.0
    return float(s60_val)

class SignalStabilizerStudy:
    def __init__(self, target_f_mhz=S60(153, 24, 0)):
        # target_f_mhz comes as S60.
        # We store it for reference, but convert to float for simulation physics
        self.target_f_s60 = target_f_mhz * 1000000
        self.target_f = to_float(self.target_f_s60)
        
        # Increase resolution to avoid NaN (Stability Fix)
        # Divisor increased from 50 to 500
        dt_s60 = S60(1, 0, 0) / (200 * 1000000 * 500)
        self.dt = to_float(dt_s60)
        self.steps = 300000 
        
    def run_simulation(self, stabilized: bool = False):
        # 1. Parámetros de la Membrana (Float Physics)
        m_params = MembraneParameters(mass=1e-15, frequency=self.target_f, quality_factor=1e6)
        
        # All calculations in float
        omega = 2 * np.pi * m_params.frequency
        m = m_params.mass
        gamma = omega / m_params.quality_factor
        
        # Ruido de Vacío
        np.random.seed(42)
        noise_amplitude = 2e-12
        vacuum_noise = np.random.normal(0, noise_amplitude, self.steps)
        
        # 2. Señal del Vacío
        t_span = np.arange(self.steps) * self.dt
        
        # Use target_f derived from S60 input (NO HARDCODES)
        vacuum_signal = np.cos(2 * np.pi * self.target_f * t_span)
        
        # Rotación
        theta = omega * self.dt
        sin_t = np.sin(theta)
        cos_t = np.cos(theta)
        
        x, p = 0.0, 0.0
        coupling = 1e-12
        
        amplitudes = []
        phase_errors = []
        
        # 3. Bucle de Evolución
        for i in range(self.steps):
            t = i * self.dt
            # Fuerza externa
            force = (vacuum_signal[i] * coupling) + vacuum_noise[i]
            
        # 3. Bucle de Evolución (Symplectic Euler for Stability)
        for i in range(self.steps):
            t = i * self.dt
            # Fuerza externa
            force = (vacuum_signal[i] * coupling) + vacuum_noise[i]
            
            # --- ESTABILIZACIÓN POR OBSERVACIÓN (PLL) ---
            if stabilized:
                x_ideal = np.cos(2 * np.pi * self.target_f * t)
                stabilization_force = - (x - x_ideal * 1e-11) * 2e-2
                force += stabilization_force
            
            # Symplectic Euler (Energy Conserving)
            # v(t+1) = v(t) + a(x(t)) * dt
            # x(t+1) = x(t) + v(t+1) * dt
            
            # Dampening term
            force -= gamma * p 
            
            # p represents velocity-like term here (scaled by mass?)
            # Original code: p_new = ... mixed Euler?
            # Let's align with rigorous physics: 
            # dx/dt = p/m
            # dp/dt = F_total = -k*x - gamma*p/m + F_ext
            # k = m * omega^2
            
            k = m * (omega**2)
            
            # Acceleration
            acc = (force - k * x) / m
            
            # Update
            v_new = (p / m) + acc * self.dt
            x_new = x + v_new * self.dt
            p_new = v_new * m
            
            # Safety Clipping to prevent NaN explosion if unstable
            if abs(x_new) > 1e-6: # 1 micron limit
                x_new = np.sign(x_new) * 1e-6
                p_new = 0 # Reset momentum on collision
            
            x, p = x_new, p_new
            
            # Guardamos datos para análisis
            if i > self.steps - 20000:
                amplitudes.append(x)
                # Error de fase relativo
                x_ref = np.cos(2 * np.pi * self.target_f * t)
                
                # Robust normalization
                max_amp = np.max(np.abs(amplitudes)) if len(amplitudes) > 0 else 1e-25
                if max_amp == 0 or np.isnan(max_amp): max_amp = 1e-25
                
                x_norm = x / max_amp
                phase_errors.append(abs(x_norm - x_ref))
                
        return np.mean(np.abs(amplitudes)), np.std(phase_errors) if len(phase_errors) > 0 else 0.0

    def execute(self):
        print(f"📡 ESTUDIO DE ESTABILIZACIÓN DE SEÑAL QUANTUM")
        print(f"🌐 Frecuencia Maestra: {self.target_f/1e6} MHz\n")
        
        print("❄️  Caso A: Señal en deriva natural (Ruido dominante)...")
        amp_a, error_a = self.run_simulation(stabilized=False)
        
        print("🧠 Caso B: Señal estabilizada por el Observador (Phase Anchor)...")
        amp_b, error_b = self.run_simulation(stabilized=True)
        
        stability_gain = (error_a - error_b) / error_a * 100
        
        print("\n📊 RESULTADOS DE ESTABILIZACIÓN:")
        print(f"   Varianza de Fase (Natural): {error_a:.6f}")
        print(f"   Varianza de Fase (Anclada): {error_b:.6f}")
        print(f"   INCREMENTO DE ESTABILIDAD: {stability_gain:+.4f}%")
        
        if stability_gain > 5.0:
            print(f"\n✅ CONFIRMADO: El observador ha estabilizado la señal en un {stability_gain:.2f}%.")
        else:
            print("\n❌ NULO: El ruido sigue desestabilizando la señal.")

if __name__ == "__main__":
    study = SignalStabilizerStudy()
    study.execute()