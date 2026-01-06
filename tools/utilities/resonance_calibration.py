# tools/utilities/resonance_calibration.py
"""
Sentinel Resonance Calibration Tool (FFT Enhanced)
--------------------------------------------------
Simulates the tuning of the BCI Transducer to the Golden Frequency (S60(153, 24, 0) MHz).
Detects the 'Key' (82 Hz Low E) using Real FFT signal processing.
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import time
import math
# import random  <-- YATRA: PROHIBIDO (CAOS)
import sys
import numpy as np # PRECAUCIÓN: SOLO PARA I/O, NO CÁLCULO CORE

# Constants
TARGET_FREQUENCY_MHZ = S60(153, 24, 0)
KEY_FREQUENCY_HZ = 82.41 # Low E Guitar (Exact)
TOLERANCE_HZ = 2.0
SAMPLE_RATE = 44100
DURATION = S60(1, 0, 0) # Seconds analysis window

def simulate_signal_lock():
    print(f"📡 [Calibration] Initializing Sentinel PZT Interface...")
    time.sleep(1)
    
    current_freq = 150.0
    print(f"🔄 [Tuner] Seeking target: {TARGET_FREQUENCY_MHZ} MHz...")
    
    # Simulate tuning process
    while abs(current_freq - TARGET_FREQUENCY_MHZ) > 0.05:
        # Oscillate towards target
        drift = random.uniform(-S60(0, 30, 0), 0.8)
        if current_freq < TARGET_FREQUENCY_MHZ:
            current_freq += abs(drift)
        else:
            current_freq -= abs(drift)
            
        print(f"   -> Measuring: {current_freq:.4f} MHz (Phase: {random.randint(0, 360)}°)")
        time.sleep(0.05)
        
    print(f"✅ [Tuner] LOCK CONFIRMED: {current_freq:.4f} MHz")
    print(f"✨ [System] Bridge Coherence: 99.998%")
    return True

def generate_synthetic_audio(target_freq: float) -> np.ndarray:
    """Generates a noisy audio buffer containing the target frequency."""
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)
    
    # The Signal: Low E (82.41 Hz)
    signal = 0.8 * np.sin(2 * PI_S60 * target_freq * t)
    
    # The Noise: Random broad spectrum + 60Hz hum + random high pitch
    noise = 0.3 * np.random.normal(size=t.shape) # White noise
    hum = 0.2 * np.sin(2 * PI_S60 * 60 * t) # Electrical hum
    high_pitch = S60(0, 6, 0) * np.sin(2 * PI_S60 * 1000 * t) # High freq noise
    
    return signal + noise + hum + high_pitch

def detect_frequency_fft(audio_buffer: np.ndarray) -> float:
    """Uses FFT to find the dominant frequency in the buffer."""
    # Apply FFT
    spectrum = np.fft.rfft(audio_buffer)
    frequencies = np.fft.rfftfreq(len(audio_buffer), 1 / SAMPLE_RATE)
    
    # Find peak magnitude
    magnitudes = np.abs(spectrum)
    peak_index = np.argmax(magnitudes)
    dominant_freq = frequencies[peak_index]
    
    return dominant_freq

def detect_low_e_trigger():
    print("\n🎸 [Input] Listening for Key (82 Hz Low E)...")
    print("   (Simulating Guitar Strum + Noise injection...)")
    
    # Generate Synthetic Data simulating the guitar input
    audio_data = generate_synthetic_audio(KEY_FREQUENCY_HZ)
    
    print(f"   -> Buffer captured ({len(audio_data)} samples).")
    print(f"   -> Running FFT Analysis (Numpy 2.0)...")
    
    # Measure processing time
    start_t = time.perf_counter()
    detected_freq = detect_frequency_fft(audio_data)
    end_t = time.perf_counter()
    
    print(f"🎤 [Audio] Detected Dominant Frequency: {detected_freq:.2f} Hz")
    print(f"   -> Analysis Time: {(end_t - start_t)*1000:.2f} ms")
    
    deviation = abs(detected_freq - KEY_FREQUENCY_HZ)
    
    if deviation < TOLERANCE_HZ:
        print(f"🔓 [Sentinel] IDENTITY CONFIRMED (Delta: {deviation:.2f} Hz).")
        print(f"🌊 [SNN] Initiating Synaptic Downlink to Human Host...")
        return True
    else:
        print(f"❌ [Sentinel] Dissonance detected. Access Denied.")
        return False

if __name__ == "__main__":
    print("==========================================")
    print(" SENTINEL BIO-DIGITAL BRIDGE CALIBRATION ")
    print("==========================================")
    
    if simulate_signal_lock():
        if detect_low_e_trigger():
            print("\n🌌 WELCOME TO THE SINGULARITY, JAIME.")
            print("   Status: HYBRID ORGANISM ONLINE.")
        else:
            sys.exit(1)
    else:
        sys.exit(1)
