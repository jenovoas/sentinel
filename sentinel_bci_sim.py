import os
import pty
import struct
import sys
import time

import numpy as np
import serial

# Configuración de Audio (Simulación)
SAMPLE_RATE = 48000
BUFFER_SIZE = 1024


def generate_sine_wave(frequency, duration, volume=0.5):
    """Genera una onda S60 pura matemática (sin jitter de tabla)"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    # Sinusoidal pura: A * sin(2 * pi * f * t)
    audio = volume * np.sin(2 * np.pi * frequency * t)
    return audio


def bci_simulator():
    print("🔮 SENTINEL BCI: GEMELO DIGITAL (S60 SIMULATOR)")
    print("----------------------------------------------")

    # 1. Crear par de pseudo-terminales (PTY)
    master, slave = pty.openpty()
    s_name = os.ttyname(slave)

    print(f"✅ PUERTO VIRTUAL CREADO: {s_name}")
    print(f"👉 Configura tu bci.rs para conectar a: {s_name}")
    print("----------------------------------------------")
    print("🔊 Esperando comandos del Kernel ME-60OS...")

    # Simulamos el puerto serial desde el lado del "Arduino"
    # El lado 'master' es lo que nosotros leemos (lo que escribe el Rust)

    buffer = b""

    try:
        while True:
            # Leemos del puerto virtual (bloqueante, low latency)
            data = os.read(master, 1)
            if not data:
                break

            buffer += data

            # Protocolo: [CMD] [VAL_H] [VAL_L] (3 bytes)
            if len(buffer) >= 3:
                cmd = buffer[0]
                val_h = buffer[1]
                val_l = buffer[2]

                # Reconstruir valor de 16-bit
                val = (val_h << 8) | val_l

                # Decodificar Comandos
                if cmd == 0x01:
                    sys.stdout.write(f"\r💓 HEARTBEAT (S60 Keep-Alive)")
                    sys.stdout.flush()

                elif cmd == 0x02:
                    freq = 1618 + val  # Base Phi + Modulación
                    print(f"\n🚨 THREAT DETECTED (Gamma): {freq} Hz [AMPLITUD MÁXIMA]")
                    # Aquí iría la llamada a sounddevice.play()
                    # generate_audio(freq, 0.2)

                elif cmd == 0x03:
                    freq = 500 + (val * 12)  # Mapeo Fibonacci
                    print(f"\n🌊 LOAD MODULATION (Flow): {freq} Hz [Armónico]")

                # Limpiar buffer procesado
                buffer = buffer[3:]

    except OSError as e:
        print(f"\n❌ Conexión cerrada: {e}")
    except KeyboardInterrupt:
        print("\n👋 Simulador detenido.")


if __name__ == "__main__":
    bci_simulator()
