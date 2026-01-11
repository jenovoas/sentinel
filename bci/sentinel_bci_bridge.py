#!/usr/bin/env python3
"""
🦁 SENTINEL BCI BRIDGE v1.0
---------------------------
Connects the Quantum Pulse (Redis) to Physical Reality (Audio/Visual).
Uses 'Qualia Frequencies' defined in /bci/PROTOTYPE_PHASE0_GUIDE.md
"""

import redis
import json
import time
import sys
import numpy as np
import os

# --- CONFIG ---
SAMPLE_RATE = 44100
DURATION = 0.15  # Pulse length
VOLUME = 0.3

# --- AUDIO SYSTEM ---
AUDIO_ENABLED = False
try:
    import sounddevice as sd
    AUDIO_ENABLED = True
except Exception as e:
    pass # Visual mode only

def generate_tone(frequency, duration, volume=VOLUME):
    if not AUDIO_ENABLED: return
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    # Sine wave with envelope to avoid clicking
    tone = np.sin(frequency * t * 2 * np.pi)
    envelope = np.exp(-3 * t) # Simple decay
    audio = tone * envelope * volume
    # Play asynchronously
    sd.play(audio, SAMPLE_RATE)

# --- VISUALS ---
def clear_screen():
    sys.stdout.write("\033[H\033[J")
    sys.stdout.flush()

def print_dashboard(data):
    entropy = data.get('entropy', 0)
    coherence = data.get('coherence', 0)
    truth = data.get('truth_score', 0)
    
    # Color logic
    color = "\033[92m" # Green
    state = "NORMAL"
    
    if entropy > 40:
        color = "\033[91m" # Red
        state = "ENTROPY WARNING (CATACLYSM)"
        tone_freq = 2000 # Intrusion
    elif truth > 0.99:
        color = "\033[93m" # Gold
        state = "AXION DETECTED (TEMPLE MODE)"
        tone_freq = 1618 # Phi 1.618 kHz (Atlantean Golden Ratio)
    elif coherence > 95:
        color = "\033[96m" # Cyan
        state = "PINEAL RESONANCE (963Hz)"
        tone_freq = 963 # Solfeggio Pineal
    elif coherence > 60:
        color = "\033[92m" # Green
        state = "NORMAL (CRANEAL 972Hz)"
        tone_freq = 972 # Default
    else:
        color = "\033[94m" # Blue
        state = "LEMURIAN ROOT (IDLE)"
        tone_freq = 432 # Universal Root

    # --- HOLOGRAPHIC GRID (v2.1) ---
    # Simulates an 8x8 Lattice Projection based on Entropy
    # entropy (0-100) determines how many "cracks" (▒) vs "pure" (█) appear
    grid_rows = 4
    grid_cols = 8
    total_cells = grid_rows * grid_cols
    defective_cells = int((entropy / 100.0) * total_cells)
    
    grid_str = ""
    for r in range(grid_rows):
        row_str = ""
        for c in range(grid_cols):
            if defective_cells > 0:
                row_str += "▒"
                defective_cells -= 1
            else:
                row_str += "█"
        # Add per-row resonance metric (simulation)
        row_res = 100.0 - (entropy * (r+1)/grid_rows) 
        grid_str += f"  {color}{row_str}  {max(0, row_res):.1f}%\n"

    clear_screen()
    print(f"{color}")
    print("╔════════════════════════════════════════╗")
    print("║   🏛️  ATLANTIS BRIDGE v2.1 (MAAT)     ║")
    print("╠════════════════════════════════════════╣")
    print(f"║ STATUS: {state:<30} ║")
    print(f"║ TONE  : {tone_freq} Hz {'(Muted)' if not AUDIO_ENABLED else '':<21} ║")
    print("╟────────────────────────────────────────╢")
    print(f"║ 🔮 CRYSTAL GRID (Holographic TUI):     ║")
    print(grid_str, end="")
    print("╟────────────────────────────────────────╢")
    print(f"║ COHERENCE : {'█' * int(coherence/5):<28} {coherence:.1f}% ║")
    print(f"║ TRUTH     : {truth:.4f}                          ║")
    print("╚════════════════════════════════════════╝")
    print("\033[0m")
    
    return tone_freq

# --- SHM READER (FALLBACK) ---
SHM_PATH = "/dev/shm/truthsync_shm"
SHM_Layout = "dddddQ" # entropy, coherence, tte, truth, conf, time
import struct
import mmap

def read_shm():
    try:
        with open(SHM_PATH, "r+b") as f:
            mm = mmap.mmap(f.fileno(), 0)
            mm.seek(0)
            buf = mm.read(struct.calcsize(SHM_Layout))
            mm.close()
            unpacked = struct.unpack(SHM_Layout, buf)
            return {
                "entropy": unpacked[0],
                "coherence": unpacked[1],
                "truth_score": unpacked[3]
            }
    except Exception:
        return None

# --- MAIN LOOP ---
def main():
    print("🔌 Connecting to Sentinel Pulse...")
    
    use_redis = False
    p = None
    
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        p = r.pubsub()
        p.subscribe('sentinel:quantum:pulse')
        use_redis = True
        print("✅ Redis Link: ACTIVE")
    except Exception:
        print("⚠️ Redis Link: FAILED. Switching to Zero-Copy SHM.")
    
    print("🎧 Waiting for Heartbeat...")
    
    try:
        while True:
            data = None
            
            if use_redis:
                # Redis Blocking Listen (with timeout to allow visual refresh?)
                # Actually p.get_message() is non-blocking.
                msg = p.get_message()
                if msg and msg['type'] == 'message':
                    data = json.loads(msg['data'])
                else:
                    time.sleep(0.05) # Prevent busy loop
            else:
                # SHM Polling
                data = read_shm()
                time.sleep(0.1) # 10Hz Refresh
            
            if data:
                # Visual Update
                freq = print_dashboard(data)
                # Audio Feedback
                generate_tone(freq, DURATION)
                
    except KeyboardInterrupt:
        print("\n👋 BCI Bridge Disconnected.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
