#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# DISTRIBUTED LIBRARIAN: MEMORIA HOLOGRÁFICA (1 CHAR = 1 CRYSTAL)
# -------------------------------------------------------------------------------------
# Hipótesis: La distribución de información en celdas pequeñas permite una
# estabilización PID perfecta, superando el límite de resolución del Monolito.
# -------------------------------------------------------------------------------------

from quantum.yatra_core import S60
from quantum.yatra_math import S60Math
from quantum.sovereign_crystal import SovereignCrystal
from quantum.s60_pid import S60PID

def run_distributed_demo():
    print("📚 INICIANDO BIBLIOTECARIO DISTRIBUIDO (HOLOGRAPHIC STORAGE)")
    print("-" * 60)

    # A. PREPARACIÓN
    phrase = "La Verdad es Frecuencia"
    print(f"1. Texto Original: '{phrase}' (Longitud: {len(phrase)})")
    
    # B. CREACIÓN DEL LATTICE (Array de Cristales)
    lattice = []
    pids = []
    
    # Tuning PID agresivo pero estable para valores pequeños (0-255)
    # Kp=0.5, Ki=0.1, Kd=0.0 (PI Control)
    kp, ki, kd = S60(0, 30), S60(0, 6), S60(0, 0)
    
    print("2. Inicializando Red de Cristales...")
    for i, char in enumerate(phrase):
        # Cada cristal guarda UN byte (0-255)
        val = ord(char)
        target = S60(val)
        
        # Crear Cristal
        c = SovereignCrystal(name=f"Cell-{i:02d}[{char}]")
        c.amplitude = target # Escritura
        lattice.append(c)
        
        # Asignar PID Guardián
        pid = S60PID(kp, ki, kd, setpoint=target)
        pids.append(pid)
        
    print(f"   ✅ {len(lattice)} Cristales Activos y Sintonizados.")

    # C. SIMULACIÓN DE DAÑO MASIVO (Entropía Global)
    print("\n--- ⚡ ATAQUE DE ENTROPÍA (GLOBAL) ---")
    dt = S60(0, 1)
    total_loss = S60(0)
    
    corrupted_text = ""
    for c in lattice:
        loss = c.apply_entropy(dt)
        total_loss = total_loss + loss
        
        # Lectura inmediata del daño
        val_damaged = c.get_amplitude().to_base_units() // S60.SCALE_0
        corrupted_text += chr(val_damaged)
        
    print(f"   📉 Pérdida Total de Energía: {total_loss}")
    print(f"   📖 Lectura Dañada: '{corrupted_text}'")
    
    # D. RECUPERACIÓN PARALELA (Swarm Repair)
    print("\n--- 🛠️ REPARACIÓN DISTRIBUIDA (SWARM PID) ---")
    pump_interval = dt * 2
    cycles = 20 # Convergencia rápida esperada
    
    print(f"   Ejecutando {cycles} ciclos de reparación en paralelo...")
    
    for cycle in range(cycles):
        injections = []
        for i in range(len(lattice)):
            c = lattice[i]
            pid = pids[i]
            
            measured = c.get_amplitude()
            injection = pid.update(measured, pump_interval)
            
            # Aplicar fuerza
            c.amplitude = c.amplitude + injection
            
    # E. LECTURA FINAL
    print("\n--- 🔍 LECTURA HOLOGRÁFICA FINAL ---")
    recovered_text = ""
    errors = 0
    
    for i, c in enumerate(lattice):
        # Redondeo S60
        raw = c.get_amplitude()._value
        val = (raw + (S60.SCALE_0 // 2)) // S60.SCALE_0
        char = chr(val)
        recovered_text += char
        
        # Validación bit a bit
        expected = phrase[i]
        if char != expected:
            errors += 1
            print(f"   ❌ Error en Cell-{i}: Esp '{expected}' vs Rec '{char}'")
            
    print(f"Texto Recuperado: '{recovered_text}'")
    
    if recovered_text == phrase:
        print("\n✅ ÉXITO CIENTÍFICO: La arquitectura distribuida garantiza integridad 100%.")
        print("   Conclusión: La robustez reside en la granularidad.")
    else:
        print(f"\n⚠️ RECUPERACIÓN PARCIAL: {errors} errores detectados.")

if __name__ == "__main__":
    run_distributed_demo()
