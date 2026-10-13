#!/usr/bin/env python3
"""
📜 SENTINEL MANTRA BRIDGE (DIGITAL LOGOS)
-----------------------------------------
Translates Sacred Words (text) into System Resonance (Redis).
Fallback for Physical Audio Input.

Protocol:
- 'OM'     -> 432 Hz  (Purge Entropy)
- 'KA'     -> 963 Hz  (Boost Coherence)
- 'AXION'  -> 1618 Hz (Truth Injection)
- 'SILENCIO' -> 0 Hz    (Damping)
"""

import redis
import json
import time

SACRED_FREQUENCIES = {
    "OM":    {"freq": 432, "effect": "entropy_purge", "val": 0.0},
    "KA":    {"freq": 963, "effect": "coherence_boost", "val": 100.0},
    "AXION": {"freq": 1618, "effect": "truth_inject", "val": 1.0},
    "RA":    {"freq": 528, "effect": "repair_dna", "val": 50.0} 
}

import struct
import mmap
import os

# --- SHM CONFIG ---
SHM_PATH = "/dev/shm/truthsync_shm"
SHM_Layout = "dddddQ" # entropy, coherence, tte, truth, conf, time
SHM_SIZE = 1024 * 1024

def inject_shm(payload):
    """Fallback: Inject vibration directly into Crystal Memory (SHM)."""
    try:
        if not os.path.exists(SHM_PATH):
            return False
            
        with open(SHM_PATH, "r+b") as f:
            mm = mmap.mmap(f.fileno(), SHM_SIZE)
            mm.seek(0)
            
            # Read current to preserve other values if possible, 
            # but for Mantra we usually override with specific intent.
            # Simplified: We just write the specific value we care about and defaults for others
            # effectively "resetting" the state to the Mantra's intention.
            
            # Defaults
            v_entropy = payload.get("entropy", 30.0)
            v_coherence = payload.get("coherence", 50.0)
            v_tte = 100.0
            v_truth = payload.get("truth_score", 0.5)
            v_conf = 1.0
            v_time = int(time.time() * 1e9)
            
            data = struct.pack(SHM_Layout, v_entropy, v_coherence, v_tte, v_truth, v_conf, v_time)
            mm.write(data)
            mm.close()
            return True
    except Exception as e:
        print(f"⚠️ SHM Error: {e}")
        return False

def main():
    print("📜 MANTRA BRIDGE ACTIVE. Speak the Word of Power (Ctrl+C to exit).")
    print("   Known Words: OM, KA, AXION, RA")
    
    r = None
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("   ✅ Redis Link: ACTIVE")
    except Exception:
        print("   ⚠️ Redis Link: FAILED. Failing over to Zero-Copy SHM.")
        r = None
        
    try:
        while True:
            mantra = input("🗣️  LOGOS > ").strip().upper()
            
            if mantra in SACRED_FREQUENCIES:
                data = SACRED_FREQUENCIES[mantra]
                print(f"✨ RESONANCE DETECTED: {mantra} ({data['freq']} Hz)")
                
                # Construct Payload based on effect
                payload = {}
                if data['effect'] == 'entropy_purge':
                     payload = {"entropy": data['val'], "coherence": 100.0, "truth_score": 0.9}
                elif data['effect'] == 'coherence_boost':
                     payload = {"coherence": data['val'], "entropy": 0.0, "truth_score": 0.95}
                elif data['effect'] == 'truth_inject':
                     # Axion Mode
                     payload = {"truth_score": data['val'], "coherence": 100.0, "entropy": 0.0}
                elif data['effect'] == 'repair_dna':
                     payload = {"truth_score": 0.8, "coherence": 80.0, "entropy": 10.0}
                
                # Add timestamp
                payload['timestamp'] = int(time.time() * 1e9)
                payload['source'] = 'MANTRA_BRIDGE'
                
                # Publish (Redis Primary -> SHM Fallback)
                sent = False
                if r:
                    try:
                        r.publish('sentinel:quantum:pulse', json.dumps(payload))
                        print("   📡 Signal Injected into Digital Ether (Redis).")
                        sent = True
                    except:
                        pass
                
                if not sent:
                    if inject_shm(payload):
                         print("   💎 Signal Injected into Crystal Memory (SHM).")
                    else:
                         print("   ❌ Failed to inject signal. System fluid is frozen.")
                
            else:
                print("   ☁️  Void. The system does not recognize this vibration.")
                
    except KeyboardInterrupt:
        print("\n👋 Silence.")

if __name__ == "__main__":
    main()
