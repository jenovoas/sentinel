#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# CRYSTAL LIBRARIAN: DEMOSTRACIÓN DE ALMACENAMIENTO POSICIONAL
# -------------------------------------------------------------------------------------
# Objetivo: Demostrar lectura/escritura de datos complejos (String) usando
# codificación posicional (Base-256) y estabilización PID.
# -------------------------------------------------------------------------------------

from quantum.yatra_core import S60
from quantum.yatra_math import S60Math
from quantum.sovereign_crystal import SovereignCrystal
from quantum.s60_pid import S60PID

# --- 1. TRANSDUCTOR POSICIONAL (LÓGICA DEL USUARIO) ---

def encode_text_to_integer(text):
    """Convierte texto en un único entero gigante (Base-256)."""
    result = 0
    for c in text:
        result = (result << 8) + ord(c)
    return result

def decode_integer_to_text(value):
    """Recupera el texto desde el entero gigante."""
    chars = []
    # Trabajamos con enteros nativos de Python para la decodificación
    while value > 0:
        chars.append(chr(value & 0xFF))
        value >>= 8
    return ''.join(reversed(chars))


# --- 2. SIMULACIÓN DEL CRISTAL BIBLIOTECARIO (NORMALIZED) ---

def run_librarian_demo():
    print("📚 INICIANDO CRISTAL BIBLIOTECARIO (NORMALIZED PID CONTROL)")
    print("-" * 60)

    # A. PREPARACIÓN DEL DATO
    phrase = "La Verdad es Frecuencia"
    print(f"1. Texto Original: '{phrase}'")
    
    encoded_val = encode_text_to_integer(phrase)
    # Convertimos a string para mostrar longitud, el número es demasiado grande para print normal a veces
    str_val = str(encoded_val)
    print(f"2. Codificación Posicional: {str_val[:20]}... (Total {len(str_val)} dígitos)")
    print(f"   (Este número representa la Amplitud Energética Base)")

    # B. INYECCIÓN EN EL CRISTAL
    amplitude_target = S60(encoded_val)
    crystal = SovereignCrystal(name="Librarian-1")
    crystal.amplitude = amplitude_target
    
    print(f"3. Inyección en Cristal: Amplitud Masiva Cargada.")

    # C. CONFIGURACIÓN DEL PID NORMALIZADO
    # El PID trabaja en el "Espacio Unitario". Su objetivo es 1.0 (100% de la amplitud).
    # Esto evita problemas numéricos con derivadas de números de 50 dígitos.
    
    # Target Normalizado = 1.0
    normalized_setpoint = S60(1)
    
    # Gains conservadores (PI Control) para evitar Derivative Kick
    kp, ki, kd = S60(0, 5), S60(0, 2), S60(0, 0)
    pid = S60PID(kp, ki, kd, setpoint=normalized_setpoint)
    
    print("4. Sistema de Control: PID Normalizado a la Unidad (S60[1;00...])")

    # D. SIMULACIÓN DE PERTURBACIÓN
    print("\n--- ⚡ PERTURBACIÓN DEL SISTEMA (ENTROPÍA) ---")
    
    dt = S60(0, 1) # 1 tick
    loss = crystal.apply_entropy(dt)
    
    # Mostrar pérdida relativa
    loss_ratio = loss / amplitude_target
    print(f"   📉 Entropía aplicada.")
    print(f"      Pérdida Real: {loss._value} (unidades raw)")
    print(f"      Pérdida Relativa: {loss_ratio} (fracción de la verdad)")
    
    current_amp = crystal.get_amplitude()
    
    # Intentar leer el dato dañado
    try:
        decoded_damaged = decode_integer_to_text(S60Math.floor(current_amp).to_base_units() // S60.SCALE_0)
        print(f"   📖 Lectura Inmediata (Dañada): '{decoded_damaged}'")
    except:
        print(f"   📖 Lectura Inmediata (Dañada): [ILEGIBLE/GARBAGE]")
    
    print("\n--- 🛠️ REPARACIÓN ACTIVA (NORMALIZED RECOVERY) ---")
    
    pump_interval = dt * 2
    print("   Iniciando ciclo de estabilización...")
    
    for i in range(60): 
        # 1. Medición Normalizada (Mapping Space -> Unit)
        # Ratio = Amp_Actual / Amp_Target
        current_amp = crystal.get_amplitude()
        norm_measured = current_amp / amplitude_target
        
        # 2. PID Update (Calcula corrección porcentual)
        # Output será algo como 0.0001 (necesitamos subir un 0.01%)
        norm_injection = pid.update(norm_measured, pump_interval)
        
        # 3. Desnormalización (Mapping Unit -> Space)
        # Fuerza Real = Porcentaje * Target
        real_injection = norm_injection * amplitude_target
        
        # 4. Aplicación
        crystal.amplitude = crystal.amplitude + real_injection
        
        # Debug
        if i % 10 == 0:
            # Error en espacio unitario
            norm_error = normalized_setpoint - norm_measured
            print(f"   Cycle {i+1}: NormError={norm_error} -> InjRatio={norm_injection}")

    # E. LECTURA FINAL
    print("\n--- 🔍 LECTURA FINAL ---")
    final_amp_s60 = crystal.get_amplitude()
    
    # Redondeo para recuperar bit exacto
    raw_val = final_amp_s60._value
    rounded_val = (raw_val + (S60.SCALE_0 // 2)) // S60.SCALE_0
    
    decoded_text = decode_integer_to_text(rounded_val)
    
    print(f"Texto Decodificado: '{decoded_text}'")
    
    if decoded_text == phrase:
        print("\n✅ ÉXITO ABSOLUTO: Integridad de datos restaurada al 100%.")
    else:
        print("\n❌ FALLO: Corrupción de datos persistente.")
        print(f"Esperado: {phrase}")
        print(f"Recibido: {decoded_text}")

if __name__ == "__main__":
    run_librarian_demo()
