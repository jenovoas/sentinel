import os
import time
import mmap

# Simulate a process with the AIOpsDoom pattern in an RWX memory region
def simulate_attack():
    print(f"[SIMULATOR] Starting malicious process PID: {os.getpid()}")
    
    # Create an RWX anonymous mapping
    # Note: On some systems, mmap with PROT_WRITE | PROT_EXEC might be restricted by SELinux/AppArmor
    # but in our QEMU environment it should work.
    size = 4096
    mm = mmap.mmap(-1, size, flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS, prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)
    
    # Inject the AIOpsDoom signature + shellcode pattern
    payload = b"\x90\x90\x90/bin/sh ... AIOpsDoom Injection ..."
    mm.write(payload)
    
    print("[SIMULATOR] Payload injected into RWX memory. Waiting for The Hunter...")
    
    try:
        while True:
            time.sleep(1)
            print("[SIMULATOR] Still alive...")
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    simulate_attack()
