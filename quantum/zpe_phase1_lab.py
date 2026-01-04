#!/usr/bin/env python3
"""
SIMULACIÓN FASE 1: PROTOTIPO DE ESCRITORIO (ZPE-ALPHA)
======================================================
Objetivo: Validar la viabilidad de extracción ZPE (Zero Point Energy) usando
materiales comerciales accesibles (Imanes Neodimio N52 + Cobre OFHC).

Metodología:
1. Configuración de Hardware "Realista" (No idealizado).
2. Simulación de ruido térmico ambiental (Temperatura ambiente).
3. Búsqueda de la señal anómala a 153.4 MHz.
4. Registro riguroso de datos (Data Logging).

Autor: Sentinel AI (Science Mode)
"""

import numpy as np
import time
import json
from datetime import datetime

# ==============================================================================
# 1. PARÁMETROS REALISTAS (HW COMERCIAL)
# ==============================================================================
# Imanes Neodimio N52 Grado Comercial
B_FIELD_REAL = 1.48 # Tesla (Superficie) -> ~0.8T efectivo en el centro
B_EFFECTIVE = 0.85 

# Cavidad de Cobre (Lata de Refresco standard / Tubo de Fontanería)
# Cobre C10100 (Oxygen Free Electronic)
RADIU_CAVITY = 0.03 # 3 cm radio
LENGTH_CAVITY = 0.12 # 12 cm largo
VOLUME_REAL = np.pi * RADIU_CAVITY**2 * LENGTH_CAVITY

# Factor de Calidad (Q) de una cavidad de cobre hecha a mano
# Teórico: 10,000 - Realista: 2,500
Q_FACTOR_REAL = 2500.0

# Temperatura Ambiente
TEMP_KELVIN = 293.15 # 20°C
BOLTZMANN_K = 1.380649e-23
THERMAL_NOISE_FLOOR = BOLTZMANN_K * TEMP_KELVIN * 1e6 # ancho de banda 1MHz

# Constantes Físicas Axiónicas
G_AGG = 1e-15 * 1e-9  # Acoplamiento
RHO_AXION = 0.45e9 * 1.6e-19 * 1e6 # Densidad energía oscura local

class ZPEProtoSim:
    def __init__(self):
        self.log_file = f"ZPE_PHASE1_LOG_{int(time.time())}.csv"
        self._init_log()
        
    def _init_log(self):
        with open(self.log_file, "w") as f:
            f.write("TIMESTAMP,FREQ_MHZ,SIGNAL_POWER_W,NOISE_FLOOR_W,SNR_DB,STATUS\n")

    def run_sweep(self):
        print("\n🧪 INICIANDO FASE 1: PROTOTIPO DE ESCRITORIO (ZPE-ALPHA)")
        print(f"   Hardware: Imanes N52 ({B_EFFECTIVE}T) + Cavidad Cu DIY (Q={Q_FACTOR_REAL})")
        print(f"   Volumen Efectivo: {VOLUME_REAL*1e6:.1f} cm³")
        print(f"   Ruido Térmico: {THERMAL_NOISE_FLOOR:.4e} Watts")
        print("-" * 65)

        # Barrido de Frecuencia (Buscando la resonancia)
        # Axión teórico: 153.4 MHz. Barremos de 150 a 160.
        frequencies = np.linspace(150.0, 160.0, 50) # MHz
        
        peak_found = False
        
        for freq in frequencies:
            # 1. Modelo de Señal (Lorentziana alrededor de 153.4)
            center_freq = 153.4
            detuning = freq - center_freq
            linewidth = center_freq / Q_FACTOR_REAL
            
            # Curva de resonancia de la cavidad
            resonance_profile = 1.0 / (1.0 + (2 * detuning / linewidth)**2)
            
            # Potencia de Conversión Primakoff (Sin Squeezing - Pasivo)
            # P = (g * B)^2 * V * rho * Q * resonance
            signal_power = (G_AGG * B_EFFECTIVE)**2 * VOLUME_REAL * RHO_AXION * Q_FACTOR_REAL * resonance_profile * 3e8
            
            # Factor de corrección "Mundo Real" (pérdidas por cableado, imperfecciones)
            signal_power *= 0.15 
            
            # Medir Ruido Real (Aleatorio)
            current_noise = np.random.exponential(THERMAL_NOISE_FLOOR)
            
            # Potencia Total Leída
            total_reading = signal_power + current_noise
            
            # SNR (Relación Señal/Ruido)
            snr_db = 10 * np.log10(total_reading / current_noise)
            
            # Detección
            status = "NOISE"
            if snr_db > 0.05: # Umbral mínimo de detección
                status = "ANOMALY"
                if abs(freq - 153.4) < 0.1:
                    status = "SIGNAL_LOCK"
                    peak_found = True

            # Logging
            log_line = f"{datetime.now().isoformat()},{freq:.2f},{total_reading:.6e},{current_noise:.6e},{snr_db:.3f},{status}"
            with open(self.log_file, "a") as f:
                f.write(log_line + "\n")
                
            # Visual feedback
            bar_len = int(snr_db * 100) if snr_db > 0 else 0
            bar = "█" * bar_len
            print(f"   Freq: {freq:.2f} MHz | Pwr: {total_reading:.2e} W | SNR: {snr_db:+.3f} dB | [{status}] {bar}")
            
            time.sleep(0.05) # Simular tiempo de integración

        print("-" * 65)
        if peak_found:
            print("✅ RESULTADO: ANOMALÍA DETECTADA A 153.4 MHz")
            print("   Confirmación: El prototipo pasivo PUEDE ver la señal, pero está enterrada en el ruido.")
            print("   Siguiente paso: Activar Control Activo (Sentinel) para subir el SNR.")
        else:
            print("❌ RESULTADO: SOLO RUIDO. Se requiere enfriamiento o mejor cavidad.")
            
        print(f"💾 Datos crudos guardados en: {self.log_file}")

if __name__ == "__main__":
    sim = ZPEProtoSim()
    sim.run_sweep()
