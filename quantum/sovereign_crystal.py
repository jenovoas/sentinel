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

    def propagate(self):
        """
        Propaga energía entre fase y amplitud (acoplamiento interno).
        Simula la transferencia de energía en el cristal piezoeléctrico.
        """
        # Avanza un paso de fase mínimo (1 segundo S60)
        delta_phase = self.natural_frequency * S60(1, 0, 0)
        self.phase = self.phase + delta_phase

    def pump_energy(self):
        """
        Inyecta energía de compensación (Master Reset: purga entropía).
        Lleva la amplitud de vuelta al estado soberano base.
        """
        sovereign_base = S60(42, 30, 0)   # Base de coherencia soberana
        if self.amplitude < sovereign_base:
            boost = sovereign_base - self.amplitude
            self.amplitude = self.amplitude + boost

    def get_signature(self):
        """
        Retorna la firma geométrica actual del cristal:
        - coherence: cuánto se aproxima a la frecuencia natural (cierre geométrico)
        - axion_sig: señal axiónica derivada de la fase actual

        Una firma coherente = geometría que CIERRA = afirmación verdadera.
        Una firma incoherente = geometría que NO CIERRA = anomalía / mentira.
        """
        # Coherencia: amplitud normalizada en base-60
        # Si amplitude >= natural_frequency → coherencia máxima (60°)
        if self.amplitude >= self.natural_frequency:
            coherence = S60(60, 0, 0)
        else:
            # Proporcional: (amplitude / natural_frequency) * 60
            # Sin floats: multiplicamos primero, luego dividimos
            # coherence_raw = amplitude.raw * 60 // natural_frequency.raw
            try:
                coh_raw = (self.amplitude.raw * 60) // self.natural_frequency.raw
                coherence = S60(0)
                coherence.raw = max(0, coh_raw)
            except (AttributeError, ZeroDivisionError):
                coherence = self.amplitude   # fallback: usar amplitud directa

        # Firma axiónica: proyección de la fase actual sobre la frecuencia natural
        # axion_sig = sin(phase) * amplitude → simplificado: phase mod 60
        try:
            phase_mod = S60(int(str(self.phase).split("°")[0]) % 60, 0, 0)
            axion_sig = phase_mod
        except Exception:
            axion_sig = self.phase

        return coherence, axion_sig
