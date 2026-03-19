#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# EXPERIMENTO 004: ALMACENAMIENTO ARMÓNICO DE ALTA DENSIDAD
# -------------------------------------------------------------------------------------
# Objetivo: Demostrar que un solo estado vibratorio S60 (Amplitud) puede contener
# una secuencia compleja de datos (String) codificada como armónicos Base-60.
#
# Hipótesis:
# La amplitud de un cristal no es escalar; es un vector de fase comprimido.
# Usando la estructura S60[d; m, s, t, q], podemos almacenar datos en la
# micro-estructura del espacio (minutos, segundos...) y en la macro-estructura (grados).
# -------------------------------------------------------------------------------------

import sys
import os

# Asegurar path para módulos quantum
sys.path.append(os.getcwd())

from quantum.yatra_core import S60
from quantum.sovereign_crystal import SovereignCrystal

class HarmonicEncoder:
    """
    Codificador de Texto a Frecuencia S60.
    Trata el texto como un número en base 256 y lo convierte a Base 60.
    """
    
    @staticmethod
    def text_to_s60(text: str) -> S60:
        """
        Convierte texto a una Amplitud S60 única.
        Estrategia: BigInt (Bytes) -> S60 Internal Units.
        Preservamos la información exacta bit a bit.
        """
        # 1. Convertir texto a entero masivo (Base 256)
        # 'A' (65) -> ...
        byte_data = text.encode('utf-8')
        huge_int = int.from_bytes(byte_data, byteorder='big')
        
        # 2. Mapear a S60
        # El sistema S60 usa unidades internas de 1/60^4.
        # Para máxima densidad, mapeamos el entero directamente a las unidades internas.
        # Esto significa que los datos ocuparán primero los "Cuartos" (q), luego "Tercios" (t)...
        # fluyendo de lo microscópico (cuántico) a lo macroscópico (grados).
        return S60._from_raw(huge_int)

    @staticmethod
    def s60_to_text(amplitude: S60) -> str:
        """
        Decodifica una Amplitud S60 de vuelta a texto.
        """
        raw_val = amplitude._value
        
        # Inverso de from_bytes
        # Necesitamos saber la longitud, pero podemos deducirla
        try:
            # Calcular bytes necesarios: (bit_length + 7) // 8
            num_bytes = (raw_val.bit_length() + 7) // 8
            if num_bytes == 0: return ""
            
            decoded_bytes = raw_val.to_bytes(num_bytes, byteorder='big')
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            return f"<DECODE_ERROR: {e}>"

def run_experiment():
    print("🔬 EXP-004: INICIANDO PRUEBA DE ALMACENAMIENTO ARMÓNICO")
    print("-" * 60)
    
    # 1. Datos de Prueba
    original_data = "SENTINEL-ZPE-V2"
    print(f"📄 Dato Original: '{original_data}'")
    
    # 2. Codificación
    amplitude = HarmonicEncoder.text_to_s60(original_data)
    print(f"🎼 Frecuencia Codificada (S60): {amplitude}")
    
    # Mostrar desglose armónico
    # S60 se muestra como [d; m, s, t, q]
    # Esto nos dice "dónde" viven los datos en el espectro
    print(f"   -> Macro-Estructura (Grados): {amplitude._value // 12960000}")
    print(f"   -> Micro-Estructura (Sub-60): {amplitude._value % 12960000} unids")
    
    # 3. Inyección en Cristal
    print("\n💎 Inyectando en SovereignCrystal...")
    crystal = SovereignCrystal(name="Storage-Ruby-01")
    # Para almacenamiento digital exacto, necesitamos superconductividad (Damping 0)
    # o un sistema PID activo (como en time_crystal_memory).
    # Para esta prueba de CAPACIDAD, desactivamos la entropía.
    crystal.damping_factor = S60(0)
    
    # Forzamos la amplitud directamente (simulando transducción perfecta)
    crystal.amplitude = amplitude
    
    # get_state_report no existe en sovereign_crystal.py, accedemos directo
    print(f"   Estado del Cristal: Amp={crystal.amplitude} | Phase={crystal.phase}")
    
    # 4. Simulación de Tiempo (Estabilidad)
    print("\n⏳ Esperando 1 ciclo de oscilación (T+1)...")
    dt = S60(0, 1) # 1 segundo
    crystal.oscillate(dt)
    
    current_amp = crystal.amplitude
    print(f"   Amplitud Post-Oscilación: {current_amp}")
    
    # 5. Decodificación y Verificación
    print("\n🔓 Decodificando...")
    recovered_text = HarmonicEncoder.s60_to_text(current_amp)
    print(f"📄 Dato Recuperado: '{recovered_text}'")
    
    if recovered_text == original_data:
        print("\n✅ ÉXITO: Almacenamiento Perfectamente Sin Pérdida (Zero-Loss).")
        print("   La información se ha preservado en la estructura armónica del entero.")
    else:
        print(f"\n❌ FALLO: Corrupción de datos. Esperado '{original_data}', recibido '{recovered_text}'")
        
    print("-" * 60)

if __name__ == "__main__":
    run_experiment()
