#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# EXPERIMENTO 006: SUPERCONDUCTOR STABILITY FRAMEWORK
# -------------------------------------------------------------------------------------
# Objetivo: Comparar estabilidad, energía y retención de información entre
# un Cristal Soberano estándar (Amortiguado) y una variante Superconductora (Ideal).
#
# Hipótesis:
# 1. El cristal amortiguado perderá datos (Amplitud -> 0) por entropía simulada.
# 2. El superconductor mantendrá datos perfectos (Amplitud = Constante) A MENOS QUE
#    exista inyección de energía descontrolada (PID runaway), causando divergencia.
# -------------------------------------------------------------------------------------

import sys
import os

sys.path.append(os.getcwd())

from quantum.yatra_core import S60
from quantum.sovereign_crystal import SovereignCrystal

class DualSimulationBench:
    def __init__(self):
        # 1. Grupo de Control (Realidad)
        self.control_crystal = SovereignCrystal(name="Ruby-Damped")
        # Por defecto sovereign_crystal ya tiene damping (S60(0,0,30))
        
        # 2. Grupo Experimental (Ideal)
        self.super_crystal = SovereignCrystal(name="Diamond-Superconductor")
        self.super_crystal.damping_factor = S60(0) # Zero Resistance
        
        self.time_elapsed = S60(0)
    
    def inject_signal(self, amplitude_val):
        """Inyecta la misma señal en ambos sistemas."""
        print(f"⚡ INYECCIÓN: {amplitude_val}")
        # Acceso directo para garantizar condiciones idénticas
        self.control_crystal.amplitude = amplitude_val
        self.super_crystal.amplitude = amplitude_val
        
    def run_step(self, dt):
        """Avanza un paso de tiempo y retorna métricas."""
        # Oscillate retorna la señal de salida (Amplitud * Seno(fase))
        sig_control = self.control_crystal.oscillate(dt)
        sig_super = self.super_crystal.oscillate(dt)
        
        self.time_elapsed += dt
        
        return {
            "time": self.time_elapsed,
            "control_amp": self.control_crystal.amplitude,
            "super_amp": self.super_crystal.amplitude,
            "divergence": self.super_crystal.amplitude - self.control_crystal.amplitude
        }

def run_experiment_006():
    print("🔬 EXP-006: SUPERCONDUCTOR STABILITY TEST")
    print("-" * 60)
    
    bench = DualSimulationBench()
    
    # 1. Inyectar Datos (La "Firma" armónica)
    # Usamos un valor alto para ver la degradación clara
    initial_energy = S60(100, 0, 0) 
    bench.inject_signal(initial_energy)
    
    print(f"   Damping Control: {bench.control_crystal.damping_factor}")
    print(f"   Damping Super:   {bench.super_crystal.damping_factor}")
    print("-" * 60)
    print(f"{'TIME (s)':<10} | {'CONTROL AMP':<20} | {'SUPER AMP':<20} | {'DELTA'}")
    print("-" * 60)
    
    # 2. Simular Evolución (100 pasos de 0.01s = 1 segundo)
    dt = S60(0, 0, 36) # ~0.01s (Tick de reloj)
    steps = 100
    
    divergence_detected = False
    
    for i in range(steps):
        metrics = bench.run_step(dt)
        
        # Imprimir cada 10 pasos
        if i % 10 == 0:
            t_str = str(metrics["time"])
            c_amp = str(metrics["control_amp"])
            s_amp = str(metrics["super_amp"])
            delta = str(metrics["divergence"])
            
            # Formato compacto
            print(f"{t_str:<10} | {c_amp[:18]}.. | {s_amp[:18]}.. | {delta[:10]}..")
            
        # Check de Estabilidad
        if metrics["super_amp"] > initial_energy:
            # Si la energía crece sola, violamos termodinámica (Runaway)
            print(f"⚠️  ALERTA: Divergencia energética en T={metrics['time']}")
            divergence_detected = True
            
    print("-" * 60)
    final_c = bench.control_crystal.amplitude
    final_s = bench.super_crystal.amplitude
    
    loss_c = initial_energy - final_c
    loss_s = initial_energy - final_s
    
    print(f"RESULTADOS FINALES (T=1s):")
    print(f"1. Control (Real): {final_c} (Pérdida: {loss_c})")
    print(f"2. Super (Ideal):  {final_s} (Pérdida: {loss_s})")
    
    if loss_s._value == 0:
        print("\n✅ CONCLUSIÓN: El modo superconductor es ESTABLE y CONSERVATIVO (Entropía Cero).")
        print("   Es un candidato válido para memoria de largo plazo (Deep Storage).")
    elif loss_s._value < 0:
        print("\n❌ FALLO CRÍTICO: Creación de energía espontánea (Perpetuum Mobile). Revisar leyes.")
    else:
        print(f"\n⚠️ ANOMALÍA: Pérdida inesperada en superconductor: {loss_s}")

if __name__ == "__main__":
    run_experiment_006()
