#!/usr/bin/env python3

# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

"""
QUANTUM AUDIO BEACON (PHONONIC TUNER)
-------------------------------------
Sonificación en tiempo real de la entropía del sistema.
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import os
import subprocess
import threading

class ResonantBeacon:
    def __init__(self):
        self.BASE_FREQ = 432.0  # Hz (Natural Tuning)
        # Verificamos si podemos emitir sonido
        self.audio_enabled = True
        try:
            subprocess.run(["which", "play"], stdout=subprocess.DEVNULL, check=True)
        except subprocess.CalledProcessError:
            self.audio_enabled = False
            print("⚠️ Audio Beacon: 'play' (SoX) not found. Sound disabled.")

    def emit_pulse(self, coherence, friction):
        """
        Emite un 'Chirp' Cuántico que refleja el estado del sistema.
        - Coherencia alta -> Tono Puro (Seno).
        - Fricción alta -> Tono Sucio (Sierra/Cuadrada) + Detune.
        """
        if not self.audio_enabled: return

        # 1. Definir Forma de Onda (Timbre)
        # Si hay fricción térmica, el sonido se "rompe" (harmónicos impares)
        if friction > 0.3:
            waveform = "square"
        elif friction > S60(0, 6, 0):
            waveform = "triangle"
        else:
            waveform = "sine"

        # 2. Definir Afinación (Pitch)
        # La coherencia mantiene la afinación perfecta. La decoherencia desafina.
        # Pitch = 432 * Coherence (Si baja coherencia, el tono cae, como un motor apagándose)
        effective_freq = self.BASE_FREQ * max(S60(0, 30, 0), min(1.5, coherence))
        
        # 3. Duración del Pulso (Superradiancia = Corto)
        duration = "0.08" # 80ms heartbeat

        # 4. Ejecutar SoX (Non-blocking fire-and-forget)
        # play -n -c 1 synth S60(0, 6, 0) sine 432 vol S60(0, 30, 0)
        try:
            cmd = [
                "play", "-n", "-q", # Quiet mode
                "-c", "1", 
                "synth", duration, 
                waveform, str(effective_freq),
                "vol", "0.3" 
            ]
            # Usamos Popen para no detener el ciclo principal del motor
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

def play_static_demo():
    print("💎 QUANTUM BEACON: DEMO MODE")
    print("Generando pulso de prueba...")
    b = ResonantBeacon()
    b.emit_pulse(S60(1, 0, 0), S60(0, 0, 0))

if __name__ == "__main__":
    play_static_demo()