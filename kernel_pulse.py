
import mmap
import os
import struct
import time
import math
import sys

# Constants
SHM_PATH = "/var/run/sentinel/truthsync_shm"
SHM_SIZE = 1024 * 1024  # 1MB
CONTROL_SIZE = 64

def ensure_shm():
    if not os.path.exists(SHM_PATH):
        with open(SHM_PATH, "wb") as f:
            f.write(b'\x00' * SHM_SIZE)
        os.chmod(SHM_PATH, 0o666)
    
    # Ensure size
    if os.path.getsize(SHM_PATH) != SHM_SIZE:
        with open(SHM_PATH, "wb") as f:
            f.truncate(SHM_SIZE)

def run_pulse():
    ensure_shm()
    
    try:
        with open(SHM_PATH, "r+b") as f:
            # Map the file
            mm = mmap.mmap(f.fileno(), SHM_SIZE)
            
            print(f"💓 Kernel Pulse Generator Active on {SHM_PATH}")
            print("🌊 Generating Entropy Waves (Ctrl+C to stop)...")
            
            start_time = time.time()
            
            while True:
                now = time.time()
                elapsed = now - start_time
                
                # SImulate Entropy (Sine wave + noise)
                entropy = 0.12 + (math.sin(elapsed) * 0.05) + (math.sin(elapsed * 3) * 0.02)
                
                # Simulate Coherence (Inverse of entropy usually)
                coherence = 1.0 - (entropy * 0.5)
                
                # Simulate TTE (Microseconds, mostly stable with blips)
                tte = 3.23
                if (int(elapsed * 10) % 20) == 0: # Random blip
                    tte = 3.85
                
                # Simulate Truth Score (Random high value for demo)
                truth_score = 0.88 + (math.sin(elapsed * 0.5) * 0.05)
                confidence = 3.0 # 3.0 = High

                # Pack data: 5 doubles (8 bytes each) + 1 unsigned long long (8 bytes)
                # Structure: [entropy | coherence | tte | truth_score | confidence | timestamp]
                packed_data = struct.pack("dddddQ", entropy, coherence, tte, truth_score, confidence, int(now * 1000))
                
                # Write to beginning of SHM (Control Area)
                mm.seek(0)
                mm.write(packed_data)
                
                # Sync frequency (60Hz approximate)
                time.sleep(0.016)
                
    except KeyboardInterrupt:
        print("\n🛑 Pulse stopped.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_pulse()
