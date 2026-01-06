#!/usr/bin/env python3
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import mmap
import struct
import json
import time
import os
import sys

SHM_PATH = "/var/run/sentinel/truthsync_shm"
SHM_SIZE = 1024 * 1024

def read_metrics():
    if not os.path.exists(SHM_PATH):
        return {"error": "SHM_NOT_FOUND"}
        
    try:
        with open(SHM_PATH, "r+b") as f:
            mm = mmap.mmap(f.fileno(), SHM_SIZE)
            mm.seek(0)
            data = mm.read(32)
            entropy, coherence, tte, ts = struct.unpack("dddQ", data)
            
            return {
                "timestamp": ts,
                "read_time": time.time(),
                "metrics": {
                    "entropy": entropy,
                    "coherence": coherence,
                    "tte_us": tte
                },
                "status": "active"
            }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    metrics = read_metrics()
    print(json.dumps(metrics, indent=2))
