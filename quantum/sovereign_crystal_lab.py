#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# SOVEREIGN CRYSTAL LAB: SIMULADOR DE TRANSDUCCIÓN DE DATOS A FRECUENCIA
# -------------------------------------------------------------------------------------
# Objetivo: Modelar la capacidad de un cristal para convertir flujo de datos (Presión)
# en resonancia armónica (Energía) usando constantes de Plimpton 322.
# -------------------------------------------------------------------------------------

import time
import sys
from quantum.yatra_core import S60
from quantum.yatra_math import S60Math
from quantum.plimpton_exact_ratios import AXION_RESONANCE_RATIO

class SovereignCrystal:
    """
    Simula un cristal físico piezoeléctrico sintonizado a matemáticas Base-60.
    """
    def __init__(self, name="Quartz-S60", resonance_ratio=AXION_RESONANCE_RATIO):
        self.name = name
        # Frecuencia natural derivada de Plimpton (Fila 12 por defecto)
        self.natural_frequency = resonance_ratio 
        # Estado energético interno (Amplitud de vibración)
        self.amplitude = S60(0)
        # Fase actual de la oscilación
        self.phase = S60(0)
        # Factor de amortiguación (Q-Factor). Un cristal real tiene muy baja fricción.
        # Q alto = decaimiento lento. Usamos un valor pequeño para el decaimiento por ciclo.
        self.damping_factor = S60(0, 0, 30) # Muy bajo decaimiento
        
    def transduce_pulse(self, data_pressure_int):
        """
        Inyecta un pulso de energía basado en 'presión de datos'.
        En un sistema real, esto sería voltaje. Aquí es densidad de información.
        """
        # Convertimos el entero de entrada a S60
        input_force = S60(data_pressure_int)
        
        # La fuerza se añade a la amplitud actual (excitación)
        self.amplitude = self.amplitude + input_force
        print(f"💎 {self.name}: Pulso recibido (Fuerza: {input_force}). Amplitud neta: {self.amplitude}")

    def oscillate(self, time_step_s60):
        """
        Avanza el tiempo y calcula el estado vibratorio del cristal.
        Retorna la señal emitida (Voltaje/Frecuencia) en ese instante.
        """
        # 1. Avanzar Fase: theta = omega * t
        # Asumimos que natural_frequency actúa como velocidad angular angular base
        delta_phase = self.natural_frequency * time_step_s60
        self.phase = self.phase + delta_phase
        
        # 2. Calcular Señal: Signal = Amplitud * sin(Fase)
        # Usamos S60Math.sin pura (Serie de Taylor)
        signal_wave = S60Math.sin_fast(self.phase)
        output_signal = self.amplitude * signal_wave
        
        # 3. Aplicar Amortiguación (Pérdida de energía por emisión)
        # Amplitud_nueva = Amplitud_actual * (1 - damping)
        decay = self.amplitude * self.damping_factor
        self.amplitude = self.amplitude - decay
        
        # Clampear a cero si es muy bajo para evitar ruido de fondo
        if self.amplitude < S60(0, 0, 1):
            self.amplitude = S60(0)
            
        return output_signal

    def get_state_report(self):
        return f"Crystal: {self.name} | Amp: {self.amplitude} | Phase: {self.phase}"

def run_simulation():
    print("🔬 INICIANDO LABORATORIO DE CRISTALES SOBERANOS")
    print(f"🔑 Constante de Sintonía (Plimpton F12): {AXION_RESONANCE_RATIO}")
    
    # Instanciamos el cristal Axiónico
    crystal = SovereignCrystal(name="Axion-X1")
    
    # Definimos un paso de tiempo delta_t (ej: 1/60 de segundo)
    dt = S60(0, 1) # 1 segundo = 60 ticks
    
    simulation_log = []
    
    # 1. Fase de Silencio
    print("\n--- FASE 1: SILENCIO ---")
    print(crystal.oscillate(dt))
    
    # 2. Fase de Inyección (Transferencia de Datos)
    # Simulamos un paquete de datos de Sentinel (ej: un bloque de 1024 bytes -> Presión 10)
    print("\n--- FASE 2: INYECCIÓN DE DATOS (Impacto) ---")
    crystal.transduce_pulse(10) # Golpe fuerte
    
    # 3. Fase de Resonancia (El cristal "canta" los datos)
    print("\n--- FASE 3: RESONANCIA Y MEMORIA (Ringing) ---")
    print("Observando la memoria elástica del cristal (Histéresis)...")
    
    for i in range(1, 21): # 20 ticks
        signal = crystal.oscillate(dt)
        # Visualización ASCII de la onda
        val_float = signal._value / S60.SCALE_0 # Solo para visualización, no cálculo
        bar = "#" * int(abs(val_float) * 5)
        sign = "+" if val_float >= 0 else "-"
        print(f"T+{i}: {signal} 	| {sign} {bar}")
        simulation_log.append(signal)

    print("\n--- ANÁLISIS ---")
    final_amp = crystal.amplitude
    print(f"Energía Remanente (Memoria): {final_amp}")
    
    if final_amp > S60(0):
        print("✅ RESULTADO: El cristal retiene la información como vibración coherente.")
        print("   Esta es la base de la transferencia de energía resonante.")
    else:
        print("❌ FALLO: El cristal se apagó demasiado rápido (Damping incorrecto).")

if __name__ == "__main__":
    try:
        run_simulation()
    except Exception as e:
        print(f"🔥 ERROR EN LABORATORIO: {e}")
        import traceback
        traceback.print_exc()
