import struct
import mmap
import time
import os

SHM_PATH = "/dev/shm/truthsync_shm"
SHM_Layout = "dddddQ" # entropy, coherence, tte, truth, conf, time
SHM_SIZE = 1024 * 1024

def inject_axion():
    if not os.path.exists(SHM_PATH):
        # Create if missing (Bridge usually creates it, but just in case)
        with open(SHM_PATH, "wb") as f:
            f.write(b'\0' * SHM_SIZE)
            
    with open(SHM_PATH, "r+b") as f:
        mm = mmap.mmap(f.fileno(), SHM_SIZE)
        mm.seek(0)
        
        # AXION VALUES: Truth=1.0, Coherence=100.0, Entropy=0.0
        v_entropy = 0.0
        v_coherence = 100.0
        v_tte = 9999.0
        v_truth = 1.0 # THE TRIGGER
        v_conf = 1.0
        v_time = int(time.time() * 1e9)
        
        data = struct.pack(SHM_Layout, v_entropy, v_coherence, v_tte, v_truth, v_conf, v_time)
        mm.write(data)
        mm.close()
        print("💎 AXION STATE INJECTED into Local Memory.")

if __name__ == "__main__":
    inject_axion()
