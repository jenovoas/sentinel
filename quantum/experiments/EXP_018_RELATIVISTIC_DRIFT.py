#!/usr/bin/env python3
import sys
import os
import time

sys.path.append(os.getcwd())
from quantum.time_crystal_clock import TimeCrystalClock
from quantum.experiments.EXP_017_VIMANA_LEVITATION import VimanaController
from quantum.yatra_core import S60

# -----------------------------------------------------------------------------
# EXP-018: RELATIVISTIC DRIFT TEST (Time vs Gravity)
# -----------------------------------------------------------------------------
# Hipótesis:
# En física relativista, la gravedad afecta el tiempo.
# Si G-Zero reduce la "Masa Efectiva" (y por tanto la curvatura local),
# ¿Debería el TimeCrystalClock experimentar menos "Drift" o cambiar su frecuencia?
#
# En este experimento, corremos el Reloj bajo diferentes cargas de "Masa"
# y medimos la estabilidad temporal (Drift).
# -----------------------------------------------------------------------------

def run_experiment():
    print("🔬 EXP-018: RELATIVISTIC DRIFT PROTOCOL")
    print("-" * 60)
    
    clock = TimeCrystalClock()
    vimana = VimanaController()
    
    # Baseline
    print(f"💎 Clock Interval: {clock.TICK_INTERVAL_NS} ns")
    print(f"🛸 Base Mass:      {vimana.M_STATIC} kg")
    print("-" * 60)
    print(f"{'POWER':<6} | {'M_EFF (kg)':<10} | {'DRIFT (avg ns)':<15} | {'STATUS':<15}")
    print("-" * 60)

    power_levels = [0, 25, 50, 75, 90, 100]
    
    for power in power_levels:
        # 1. Set Environment (Simulated Mass)
        m_eff, red = vimana.calculate_mass(float(power), 1.0)
        
        # 2. Run Clock for a burst (simulate passage of time under this gravity)
        # We run 50 ticks per power level
        clock_samples = 50
        burst_drifts = []
        
        t_start = time.perf_counter_ns()
        for _ in range(clock_samples):
            # Pass Mass Reduction Factor as Relativistic Bias
            # red is 0.0 (inertial) to ~0.96 (G-Zero)
            clock.tick(relativistic_bias=red)
            
            # Capture last drift
            if clock.drift_history:
                burst_drifts.append(clock.drift_history[-1])
        t_end = time.perf_counter_ns()
        
        # 3. Analyze
        if burst_drifts:
            avg_drift = sum(burst_drifts) // len(burst_drifts)
        else:
            avg_drift = 0
            
        status = "INERTIAL"
        if red > 0.95: status = "G-ZERO"
        
        print(f"{power:<6}% | {m_eff:<10.3f} | {avg_drift:<15} | {status}")
        
    print("-" * 60)
    print("✅ Experiment Complete.")
    
    # Interpretation hint
    print("\n🤔 INTERPRETATION:")
    print("Si el DRIFT cambia significativamente con la POTENCIA, existe acoplamiento.")
    print("Si el DRIFT es constante, el sistema 'Vimana' actual es isócrono (no afecta al tiempo).")

if __name__ == "__main__":
    run_experiment()
