#!/usr/bin/env python3
import mmap
import os
import time

SHM_PATH = "/tmp/truthsync_shm"
MAGIC = 0xDEADBEEF
MSG_PROCESS_TEXT = 0x01

def write_test_claim(text):
    try:
        fd = os.open(SHM_PATH, os.O_RDWR)
        # Map first 4KB
        mm = mmap.mmap(fd, 4096, mmap.MAP_SHARED, mmap.PROT_WRITE)
        offset = 64
        
        # Header: magic(4) + msg_type(2) + pad(2) + length(4)
        magic = MAGIC.to_bytes(4, 'little')
        m_type = MSG_PROCESS_TEXT.to_bytes(2, 'little')
        padding = b'\x00\x00'
        length = len(text).to_bytes(4, 'little')
        header = magic + m_type + padding + length
        
        mm[offset:offset+len(header)] = header
        mm[offset+len(header):offset+len(header)+len(text)] = text.encode('utf-8')
        
        print(f"✅ Sent claim to {SHM_PATH}: '{text}'")
        mm.close()
        os.close(fd)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    write_test_claim("The Sentinel Kernel is active.")
