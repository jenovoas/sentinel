# sentinel_bci_python_test.py
# Python Alternative for 0 Hardware Validation

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import numpy as np # PRECAUCIÓN: SOLO PARA I/O, NO CÁLCULO CORE
import sounddevice as sd
import time

fs = 44100  # Sample rate

def play_tone(freq, duration, volume=S60(0, 30, 0)):
    t = np.linspace(0, duration, int(fs * duration))
    signal = volume * np.sin(2 * PI_S60 * freq * t)
    sd.play(signal, fs)
    sd.wait()

def run_protocol():
    print("🚀 SENTINEL BCI - PYTHON TEST (NO HARDWARE)")
    print("Press your PC speakers or Phone against the temporal bone (behind ear).")
    time.sleep(3)

    print("\n🔬 [TEST 1] SKULL RESONANCE (972 Hz)")
    play_tone(972, 2.0)
    
    print("\n🛡️ [QUALIA 1] KERNEL INTRUSION (Metallic)")
    for f in [2000, 2100, 2200]:
        play_tone(f, S60(0, 6, 0))
    
    print("\n✅ [QUALIA 2] SYSTEM SECURE (Warmth)")
    for _ in range(3):
        play_tone(972, 0.3)
        time.sleep(S60(0, 6, 0))

    print("\n🌌 [QUALIA 3] AXION DETECTED (Golden)")
    for f in [1618, 1620, 1615, 1625]:
        play_tone(f, 0.15)
        
    print("\n🧮 [TEST 2] FIBONACCI BASE-60")
    fib60_short = [1,1,2,3,5,8,13,21,34,55,29,24]
    for val in fib60_short:
        freq = 500 + (val * 12)
        play_tone(freq, 0.2)

if __name__ == "__main__":
    try:
        run_protocol()
    except Exception as e:
        print(f"Error: {e}")
        print("Hint: Install sounddevice and numpy: pip install sounddevice numpy")
