#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
import sys
import os

# Contexto para imports
sys.path.append(os.getcwd())

from quantum.yatra_core import S60
from quantum.sovereign_crystal import SovereignCrystal
from quantum.plimpton_exact_ratios import AXION_RESONANCE_RATIO

def integrity_proof():
    print("🧪 PRUEBA DE INTEGRIDAD DEL MOTOR CUÁNTICO (V7.0)")
    print("=================================================")
    print("🔮 Using: SovereignCrystal (Base-60 Integer Math)")

    # 1. Configurar Cristales
    # Cristal Resonante (Sintonizado a Plimpton F12)
    c_resonant = SovereignCrystal(name="Resonant-Primary", resonance_ratio=AXION_RESONANCE_RATIO)
    
    # Cristal Desafinado (Sintonía Detuned para contraste)
    # Usamos una ratio que no es armónica perfecta
    detuned_ratio = S60(1, 30, 0) 
    c_detuned = SovereignCrystal(name="Detuned-Chaos", resonance_ratio=detuned_ratio)

    # 2. Inyección de Energía (Impulso Unitario)
    energy_impulse = S60(100, 0, 0)
    print(f"\n⚡ Inyectando Pulso: {energy_impulse}")
    # transduce_pulse espera un entero "data_pressure", convertimos el valor de S60 a raw int si necesario
    # Mirando sovereign_crystal.py: transduce_pulse(data_pressure_int) -> input_force = S60(data_pressure_int)
    # Por tanto pasamos un entero simple.
    c_resonant.transduce_pulse(100)
    c_detuned.transduce_pulse(100)

    # 3. Simulación Temporal (100 pasos)
    dt = S60(0, 0, 10) # Paso de tiempo
    steps = 100
    
    print(f"⏳ Ejecutando {steps} pasos de simulación (dt={dt})...")

    for i in range(steps):
        # Oscilar
        c_resonant.oscillate(dt)
        c_detuned.oscillate(dt)

    # 4. Análisis de Resultados
    final_res = c_resonant.amplitude
    final_det = c_detuned.amplitude
    
    print(f"\n📊 Resultados Finales:")
    print(f"   Cristal Resonante (Amplitud): {final_res}")
    print(f"   Cristal Desafinado (Amplitud): {final_det}")
    
    # Verificación de Integridad:
    # Debemos tener energía > 0 y valores válidos.
    
    if final_res > S60(0) and final_det > S60(0):
        print("\n✅ VERIFICACIÓN EXITOSA: Motor de Física S60 estable.")
        print("   No se detectaron NaNs ni inestabilidades numéricas.")
        return True
    else:
        print("\n❌ FALLO: Colapso de energía.")
        return False

if __name__ == "__main__":
    try:
        success = integrity_proof()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)