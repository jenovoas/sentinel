#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# COMPONENTE: SOVEREIGN CRYSTAL (OSCILADOR PIEZOELÉCTRICO S60)
# -------------------------------------------------------------------------------------

from quantum.yatra_core import S60
from quantum.yatra_math import S60Math
from quantum.plimpton_exact_ratios import AXION_RESONANCE_RATIO

class SovereignCrystal:
    """
    Simula un cristal físico piezoeléctrico sintonizado a matemáticas Base-60.
    Actúa como una celda de memoria resonante.
    """
    def __init__(self, name="Quartz-S60", resonance_ratio=AXION_RESONANCE_RATIO):
        self.name = name
        # Frecuencia natural derivada de Plimpton (Fila 12 por defecto)
        self.natural_frequency = resonance_ratio 
        # Estado energético interno (Amplitud de vibración)
        self.amplitude = S60(0)
        # Fase actual de la oscilación
        self.phase = S60(0)
        # Factor de amortiguación (Q-Factor). 
        # S60(0, 0, 30) es una pérdida pequeña por ciclo.
        self.damping_factor = S60(0, 0, 30)
        
    def transduce_pulse(self, data_pressure_int):
        """
        Inyecta un pulso de energía basado en 'presión de datos'.
        """
        # Convertimos el entero de entrada a S60
        input_force = S60(data_pressure_int)
        
        # La fuerza se añade a la amplitud actual (excitación constructiva)
        self.amplitude = self.amplitude + input_force

    def apply_entropy(self, time_step_s60):
        """
        Aplica la degradación termodinámica (entropía) natural.
        La pérdida es proporcional a la Amplitud y al Tiempo.
        """
        # Decay = A * lambda * dt
        decay = (self.amplitude * self.damping_factor) * time_step_s60
        self.amplitude = self.amplitude - decay
        
        # Ground state check
        if self.amplitude < S60(0, 0, 1):
            self.amplitude = S60(0)
            
        return decay

    def oscillate(self, time_step_s60):
        """
        Avanza el tiempo, calcula estado vibratorio y aplica entropía.
        """
        # 1. Avanzar Fase: theta = omega * t
        delta_phase = self.natural_frequency * time_step_s60
        self.phase = self.phase + delta_phase
        
        # 2. Calcular Señal
        signal_wave = S60Math.sin_fast(self.phase)
        output_signal = self.amplitude * signal_wave
        
        # 3. Aplicar Entropía (Física real)
        self.apply_entropy(time_step_s60)
            
        return output_signal
    
    def get_amplitude(self):
        """Retorna la energía almacenada actual."""
        return self.amplitude
