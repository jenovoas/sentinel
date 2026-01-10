#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -----------------------------------------------------------------------------
# EXPERIMENTO 007: QUANTUM STABILITY TEST
# -----------------------------------------------------------------------------
# Objetivo:
#   Evaluar la estabilidad del modo superconductor frente a ruido cuántico
#   depolarizante generado con entropía física (os.urandom).
# -----------------------------------------------------------------------------

import sys, os
sys.path.append(os.getcwd())

from quantum.yatra_core import S60
from quantum.sovereign_crystal import SovereignCrystal
from quantum.quantum_noise_s60 import QuantumNoise

class QuantumStabilityBench:
    def __init__(self, noise_strength=S60(0, 0, 15)):  # p ≈ 0.004
        self.control = SovereignCrystal(name="Ruby-Damped")
        self.superc = SovereignCrystal(name="Diamond-Super")
        self.superc.damping_factor = S60(0)
        self.noise_strength = noise_strength
        self.time = S60(0)

    def inject_signal(self, amplitude_val):
        self.control.amplitude = amplitude_val
        self.superc.amplitude = amplitude_val

    def run_step(self, dt):
        """Un paso de simulación con oscilación + ruido depolarizante"""
        # Oscilación natural
        self.control.oscillate(dt)
        self.superc.oscillate(dt)

        # Ruido cuántico depolarizante (usa os.urandom)
        # Modelamos la amplitud como el coeficiente alpha de |psi> = alpha|0> + beta|1>
        psi_control = [self.control.amplitude, S60(0)]
        psi_super   = [self.superc.amplitude, S60(0)]

        # Aplicamos ruido al vector de estado
        psi_control = QuantumNoise.depolarizing_noise(
            psi_control, self.noise_strength, 1
        )
        psi_super = QuantumNoise.depolarizing_noise(
            psi_super, self.noise_strength, 1
        )

        # Actualizar amplitudes con el canal ruidoso (Solo leemos la proyección en |0>)
        self.control.amplitude = psi_control[0]
        self.superc.amplitude  = psi_super[0]

        self.time += dt

        return {
            "t": self.time,
            "A_control": self.control.amplitude,
            "A_super": self.superc.amplitude,
            "ΔA": self.superc.amplitude - self.control.amplitude,
        }

def run_experiment_007():
    print("🔬 EXP-007: QUANTUM STABILITY TEST (Depolarizing Noise)")
    print("-" * 70)
    bench = QuantumStabilityBench()

    A0 = S60(50, 0, 0)
    dt = S60(0, 0, 36)  # ~0.01 s
    bench.inject_signal(A0)

    print(f"   Ruido: p={bench.noise_strength}")
    print(f"   Damping Control={bench.control.damping_factor}")
    print(f"   Damping Super  ={bench.superc.damping_factor}")
    print("-" * 70)
    print(f"{'T(s)':<10} | {'A_control':<20} | {'A_super':<20} | {'ΔA'}")
    print("-" * 70)

    samples = []
    for i in range(100):
        m = bench.run_step(dt)
        if i % 10 == 0:
            # Formato seguro para strings largos de S60
            t_str = str(m['t'])
            ac_str = str(m['A_control'])
            as_str = str(m['A_super'])
            da_str = str(m['ΔA'])
            print(f"{t_str:<10} | {ac_str[:18]}.. | {as_str[:18]}.. | {da_str[:10]}..")
        samples.append(m)

    # Métricas finales
    Af_c, Af_s = samples[-1]["A_control"], samples[-1]["A_super"]
    loss_c = A0 - Af_c
    loss_s = A0 - Af_s

    print("-" * 70)
    print(f"Amplitud final (Control): {Af_c}  |  Pérdida: {loss_c}")
    print(f"Amplitud final (Super):   {Af_s}  |  Pérdida: {loss_s}")

    # Comparación de pérdidas relativas
    # Si Super conserva más energía que Control, es una victoria
    # Nota: abs() es necesario porque el ruido puede causar cambios de fase (signo negativo en amplitud)
    
    abs_loss_c = abs(loss_c._value) if hasattr(loss_c, '_value') else abs(loss_c)
    abs_loss_s = abs(loss_s._value) if hasattr(loss_s, '_value') else abs(loss_s)

    if abs_loss_s < abs_loss_c: 
        print("\n✅ Conclusión: El modo superconductor mantiene coherencia cuántica superior.")
    else:
        print("\n⚠️ Observación: El ruido ha afectado significativamente a ambos sistemas.")

if __name__ == "__main__":
    run_experiment_007()
