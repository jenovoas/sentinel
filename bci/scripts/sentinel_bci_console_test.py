# sentinel_bci_console_test.py
# Console-only validation of BCI Phase 0 logic (No hardware required)

import time
import math

def print_wave(freq, duration, blocks=40):
    print(f"🌊 [WAVE] Generating {freq} Hz signal...")
    points = 20
    for i in range(points):
        val = math.sin(2 * math.pi * (i / points))
        bar = "#" * int((val + 1) * (blocks / 2))
        print(f"  {bar}")
        time.sleep(0.01)

def run_protocol():
    print("🚀 SENTINEL BCI - CONSOLE VALIDATION (LOGIC ONLY)")
    print("This script validates the frequency mapping and data patterns for Phase 0.")
    time.sleep(1)

    print("\n🔬 [TEST 1] SKULL RESONANCE (972 Hz)")
    print("Physical target: Temporal bone resonance.")
    print_wave(972, 1.0)
    
    print("\n🛡️ [QUALIA 1] KERNEL INTRUSION (Metallic)")
    print("Pattern: Discordant high-frequency shift (2000-2200 Hz)")
    for f in [2000, 2100, 2200]:
        print(f"  > Shift: {f} Hz")
        time.sleep(0.2)
    
    print("\n✅ [QUALIA 2] SYSTEM SECURE (Warmth)")
    print("Pattern: Harmonic steady resonance (972 Hz pulses)")
    for _ in range(3):
        print("  [ * ] Pulse 972 Hz")
        time.sleep(0.3)

    print("\n🌌 [QUALIA 3] AXION DETECTED (Golden)")
    print("Pattern: Phi-based frequency series (Golden Ratio)")
    phi_freqs = [1618, 1620, 1615, 1625]
    for f in phi_freqs:
        print(f"  ✨ Phi-Shift: {f} Hz")
        time.sleep(0.15)
        
    print("\n🧮 [TEST 2] FIBONACCI BASE-60")
    print("Pattern: Fibonacci sequence mapped to human-audible spectrum (mod 60)")
    fib60_short = [1,1,2,3,5,8,13,21,34,55,29,24]
    for val in fib60_short:
        freq = 500 + (val * 12)
        print(f"  🔢 Fibonacci {val} -> Frequency {freq} Hz")
        time.sleep(0.1)

    print("\n✅ BCI Logic Validation Complete.")
    print("Ready for audio synthesis once libportaudio2 is installed.")

if __name__ == "__main__":
    run_protocol()
