import os
import time
import mmap
import argparse
import sys

# Simulate a process with multiple threat patterns in memory
def simulate_attack(multi_threat=False):
    print(f"[SIMULATOR] Starting malicious process PID: {os.getpid()}")
    
    # 1. Create an RWX anonymous mapping for the primary payload
    size = 4096
    try:
        mm = mmap.mmap(-1, size, flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS, prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)
        
        if multi_threat:
            print("[SIMULATOR] Injecting MULTI-THREAT payload (NOP + /bin/sh + AIOpsDoom)...")
            # Multi-threat: NOP sled + shell-like string + attack signature
            payload = b"\x90\x90\x90\x90\x90/bin/sh ... AIOpsDoom Production Injection ... execve('/bin/bash')"
        else:
            print("[SIMULATOR] Injecting standard AIOpsDoom signature...")
            payload = b"AIOpsDoom Injection Test"
            
        mm.write(payload)
        print("[SIMULATOR] Payload injected into RWX memory. Waiting for The Hunter...")
        
    except Exception as e:
        print(f"[SIMULATOR] Error creating RWX memory: {e}")
        print("[SIMULATOR] Falling back to standard heap injection...")
        # Fallback to heap if RWX is restricted
        buf = bytearray(b"AIOpsDoom Heap Injection Pattern")
        # Keep a reference so it's not GC'd
        global _leak
        _leak = buf

    try:
        while True:
            time.sleep(1)
            print("[SIMULATOR] Still alive (waiting for SIGKILL)...")
    except KeyboardInterrupt:
        print("\n[SIMULATOR] Exiting.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sentinel Threat Simulator")
    parser.add_argument("--multi-threat", action="store_true", help="Inject multiple malicious patterns")
    args = parser.parse_args()
    
    simulate_attack(multi_threat=args.multi_threat)
