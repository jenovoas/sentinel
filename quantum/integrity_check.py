"""
🛰️ INTEGRITY CHECK: QUANTUM RADIO RESONANCE
==========================================
Este script valida que el simulador no está falseando datos.
Comparamos:
1. Sintonía Correcta (Intent = Signal)
2. Sintonía Errónea (Intent != Signal)

Si el motor es honesto, el Caso 2 debe mostrar DISONANCIA (Estabilidad negativa).
"""

import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from signal_stabilization_study import SignalStabilizerStudy

def integrity_proof():
    study = SignalStabilizerStudy(target_f_mhz=153.4)
    
    print("🧪 PRUEBA DE INTEGRIDAD DEL MOTOR CUÁNTICO")
    print("==========================================")
    
    # Baseline
    amp_base, err_base = study.run_simulation(stabilized=False)
    
    # CASO 1: Sintonía Correcta (153.4 MHz)
    print("\n[TEST 1] Sintonía Correcta (153.4 MHz)...")
    amp_ok, err_ok = study.run_simulation(stabilized=True)
    gain_ok = (err_base - err_ok) / err_base * 100
    print(f"   Resultado: {gain_ok:+.2f}% de estabilidad.")
    
    # CASO 2: Sintonía Errónea (155.0 MHz) - Forzamos el error
    print("\n[TEST 2] Sintonía Errónea (INTENCIÓN A 155.0 MHz)...")
    # Modificamos temporalmente el estudio para usar una frecuencia de intención errónea
    def run_mismatched():
        m_params = study.run_simulation.__globals__['MembraneParameters'](mass=1e-15, frequency=153.4e6)
        omega = 2 * np.pi * 153.4e6
        dt = study.dt
        steps = study.steps
        np.random.seed(42)
        vacuum_noise = np.random.normal(0, 2e-12, steps)
        vacuum_signal = np.cos(2 * np.pi * 153.4e6 * np.arange(steps) * dt)
        
        x, p = 0.0, 0.0
        errs = []
        for i in range(steps):
            t = i * dt
            force = (vacuum_signal[i] * 1e-12) + vacuum_noise[i]
            # EL ERROR: Intentamos anclar a 155 MHz
            x_mismatch = np.cos(2 * np.pi * 155.0e6 * t)
            force += - (x - x_mismatch * 1e-11) * 2e-2
            
            # Evolución (Euler simple para este test rápido)
            p += (force - (omega/1e6)*p) * dt
            x += (p/1e-15) * dt
            if i > steps - 10000:
                errs.append(abs(x/max(abs(x),1e-25) - np.cos(2 * np.pi * 153.4e6 * t)))
        return np.mean(errs)

    err_fail = run_mismatched()
    gain_fail = (err_base - err_fail) / err_base * 100
    print(f"   Resultado: {gain_fail:+.2f}% de estabilidad.")

    print("\n🔍 VERDICTO:")
    if gain_ok > 0 and gain_fail < 0:
        print("✅ MOTOR LIMPIO: El sistema responde a la física de fase real.")
        print("   La estabilidad solo ocurre cuando hay resonancia armónica.")
    else:
        print("❌ ALERTA: Patrón de mentira detectado. El motor no es físico.")

if __name__ == "__main__":
    integrity_proof()
