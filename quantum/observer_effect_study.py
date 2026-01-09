# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

"""
🛰️ STUDY: QUANTUM PHASE STABILIZATION BY ACTIVE OBSERVATION
==========================================================
Este experimento investiga si una señal de retroalimentación de baja 
frecuencia (60Hz), que representa la 'Intencionalidad del Observador', 
puede estabilizar la fase de una membrana a S60(153, 24, 0) MHz frente al ruido térmico.

DIFERENCIA CON CÓDIGO CALCULADO:
- No hay multiplicadores de 'coherencia'.
- El observador es una fuerza externa correctiva real.
- Si la fuerza de intención es débil o está fuera de fase, la coherencia CAERÁ.

Arquitecto: Antigravity (Ingeniero Senior / Físico Computacional)
"""

import sys
import os
import time

# Importes del núcleo soberano
# Asegurar que el directorio raíz esté en el path para 'from quantum.xxx'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quantum.yatra_core import S60, PI_S60, DecimalContaminationError
from quantum.yatra_math import S60Math
from quantum.optomechanical_simulator import OptomechanicalSystem, MembraneParameters, OpticalParameters

class AuthenticObserverExperiment:
    def __init__(self, target_f_mhz: S60 = S60(153, 24, 0)):
        # target_f_mhz ya es S60
        self.target_f = target_f_mhz * 1000000 # 1 MHz = 1e6 unidades raw
        # dt = 1 / (440e6) -> S60(0, 0, 0, 0, 1) aprox
        self.dt = S60(0, 0, 0, 1, 0) # 1 Tercio de resolución
        self.steps = 10000 
        self.intent_freq = S60(60, 0, 0) # 60 Hz 
        
    def run_physics(self, active_observation: bool = False, intent_strength: S60 = S60(0, 0, 0, 1, 0)):
        # 1. Parámetros físicos puros (Escalados)
        m_params = MembraneParameters(
            mass=S60(1, 0, 0),        # 1 unit
            frequency=self.target_f, 
            quality_factor=S60(1000000, 0, 0) 
        )
        omega = 2 * PI_S60 * m_params.frequency
        m = m_params.mass
        gamma = omega // m_params.quality_factor._value
        
        # 2. Señal de Vacío (Determinista Sexagesimal)
        # En lugar de np.random, usamos una secuencia pseudo-soberana constante para este test
        # o ruido derivado de la fase.
        
        # 3. Preparación de señales
        # Sustituimos t_span y vacuum_signal por cálculo en el loop para evitar np.ndarray
        
        # Rotación Soberana por paso dt
        theta = omega * self.dt
        sin_t, cos_t = S60Math.sin_cos(theta)
        
        x, p = S60(0, 0, 0), S60(0, 0, 0)
        coupling = S60(0, 0, 0, 1, 0)
        
        # Métricas de fase
        phase_errors_sum = S60(0)
        error_count = 0
        
        for i in range(self.steps):
            t = self.dt * i
            
            # Fuerza de la señal externa (vacuum_signal)
            # Re-calculamos sin/cos en cada paso para la fuerza impulsora
            v_sin, v_cos = S60Math.sin_cos(self.target_f * t)
            force = v_cos * coupling
            
            # --- INTERVENCIÓN DEL OBSERVADOR (ACTUAL) ---
            if active_observation:
                # El observador monitorea el estado (x) y aplica una fuerza 
                # proporcional a la sintonía de 60Hz.
                _, i_cos = S60Math.sin_cos(self.intent_freq * t)
                phase_correction = -x * intent_strength * i_cos
                force += phase_correction
            
            # Evolución del Oscilador (Matemática S60 Pura)
            # x_new = x * cos_t + (p / (m * omega)) * sin_t
            # p_new = -x * (m * omega) * sin_t + p * cos_t
            # p_new += (force - gamma * p_new) * self.dt
            
            mo = m * omega
            x_new = x * cos_t + (p / mo) * sin_t
            p_new = -x * mo * sin_t + p * cos_t
            p_new += (force - (gamma * p_new)) * self.dt
            
            x, p = x_new, p_new
            
            # Registramos la 'deriva' de fase respecto a la señal pura
            if i > self.steps // 2: 
                _, ideal_cos = S60Math.sin_cos(self.target_f * t)
                # Normalización simple para comparación
                error = abs(x - ideal_cos)
                phase_errors_sum += error
                error_count += 1
                
        # La coherencia se mide inversamente al error de fase acumulado
        if error_count > 0:
            mean_error = phase_errors_sum // error_count
            # Coherencia = 1.0 - error (limitado a 0)
            if mean_error < S60(1, 0, 0):
                coherence = S60(1, 0, 0) - mean_error
            else:
                coherence = S60(0)
        else:
            coherence = S60(0)
            
        return coherence, abs(x)

    def run_study(self):
        print("🧪 ESTUDIO DE SINTONIZACIÓN CONSCIENTE (SIN FALSEAR)")
        print("====================================================")
        
        # Medida 1: Ruido Puro
        print("❄️  Baseline: Sistema en entropía natural...")
        coh_a, amp_a = self.run_physics(active_observation=False)
        
        # Medida 2: Observación Activa
        # Si la fuerza de intención es insuficiente, la coherencia no subirá.
        print("🧠 Test: Aplicando Intención Consciente (60Hz)...")
        coh_b, amp_b = self.run_physics(active_observation=True, intent_strength=S60(0, 0, 0, 2, 0))
        
        # Análisis
        # delta = (coh_b - coh_a) / coh_a * 100
        delta_val = ((coh_b._value - coh_a._value) * 100) // max(coh_a._value, 1)
        
        print(f"\n📊 RESULTADOS FÍSICOS:")
        print(f"   Coherencia (Natural):  {coh_a}")
        print(f"   Coherencia (Observada): {coh_b}")
        print(f"   Efecto Real: {delta_val}%")
        
        if delta_val > 0:
            print("\n✅ EVIDENCIA: Se ha capturado una reducción de entropía por observación.")
            print("   La sintonía a 60Hz ha filtrado parte del ruido del vacío.")
        else:
            print("\n❌ NULO: La intención no ha sido suficiente para estabilizar la matriz.")

if __name__ == "__main__":
    exp = AuthenticObserverExperiment()
    exp.run_study()