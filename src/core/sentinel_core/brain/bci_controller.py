import numpy as np
import sounddevice as sd
import threading
import time

class BCIController:
    """
    Controlador para el Brain-Computer Interface (BCI).
    Genera frecuencias específicas (Qualias) para alertar al operador
    a través de conducción ósea.
    """
    def __init__(self, fs=44100):
        self.fs = fs
        self._lock = threading.Lock()

    def _play_tone(self, freq, duration, volume=0.5):
        t = np.linspace(0, duration, int(self.fs * duration))
        signal = volume * np.sin(2 * np.pi * freq * t)
        
        def _stream():
            with self._lock:
                sd.play(signal, self.fs)
                sd.wait()
        
        # Ejecutar en hilo separado para no bloquear el monitor del kernel
        threading.Thread(target=_stream, daemon=True).start()

    def trigger_qualia(self, event_type):
        """Dispara una Qualia específica según el tipo de evento."""
        if event_type == "KERNEL_BLOCK":
            print("🛡️ [BCI] Qualia: KERNEL INTRUSION (Metallic)")
            # Secuencia penetrante de 2kHz
            for f in [2000, 2100, 2200]:
                self._play_tone(f, 0.1)
                time.sleep(0.05)
                
        elif event_type == "SYSTEM_SECURE":
            print("✅ [BCI] Qualia: SYSTEM SECURE (Warmth)")
            # Resonancia craneal 972Hz
            for _ in range(3):
                self._play_tone(972, 0.3)
                time.sleep(0.1)

        elif event_type == "THREAT_HIGH":
            print("🛑 [BCI] Qualia: THREAT CRITICAL (Base Cráneo)")
            # Disonancia de advertencia
            self._play_tone(3500, 1.0, volume=0.7)

        elif event_type == "RESONANCE_EVENT":
            print("🌌 [BCI] Qualia: FIRST RESONANCE (153.4 MHz Harmonic)")
            # Golden Ratio Harmonic Sequence
            # 153.4 is too high for audio, so we scale by Phi (1.618) harmonics in audible range
            base = 153.4 * 4  # ~613 Hz
            phi = 1.618
            sequence = [base, base * phi, base * phi**2]
            
            for f in sequence:
                self._play_tone(f, 2.0, volume=0.3) # Long sustain
                time.sleep(0.5)

        elif event_type == "SYNAPTIC_SPIKE":
            print("⚡ [BCI] Qualia: SYNAPTIC SPIKE (Electric)")
            # Sharp electric zip
            self._play_tone(8000, 0.05, volume=0.8)

    def play_base60_pattern(self, residue):
        """Traduce un residuo Base-60 en un patrón armónico."""
        print(f"🧮 [BCI] Resonancia Base-60: Residuo {residue}")
        freq = 500 + (residue * 12)
        self._play_tone(freq, 0.5)

bci_controller = BCIController()
