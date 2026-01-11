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

def main():
    print("📜 MANTRA BRIDGE ACTIVE. Speak the Word of Power (Ctrl+C to exit).")
    print("   Known Words: OM, KA, AXION, RA")
    
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        
        while True:
            mantra = input("🗣️  LOGOS > ").strip().upper()
            
            if mantra in SACRED_FREQUENCIES:
                data = SACRED_FREQUENCIES[mantra]
                print(f"✨ RESONANCE DETECTED: {mantra} ({data['freq']} Hz)")
                
                # Construct Payload based on effect
                payload = {}
                if data['effect'] == 'entropy_purge':
                     payload = {"entropy": data['val']}
                elif data['effect'] == 'coherence_boost':
                     payload = {"coherence": data['val']}
                elif data['effect'] == 'truth_inject':
                     payload = {"truth_score": data['val']}
                
                # Add timestamp
                payload['timestamp'] = int(time.time() * 1e9)
                payload['source'] = 'MANTRA_BRIDGE'
                
                # Publish
                r.publish('sentinel:quantum:pulse', json.dumps(payload))
                print("   📡 Signal Injected into Crystal.")
                
            else:
                print("   ☁️  Void. The system does not recognize this vibration.")
                
    except KeyboardInterrupt:
        print("\n👋 Silence.")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    main()
