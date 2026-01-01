#!/usr/bin/env python3
import sys
import os
import time
import signal
from ctypes import *
from multiprocessing import shared_memory
from bcc import BPF

# --- Configuration ---
SHM_NAME = "truthsync_shm"
SHM_SIZE = 2 * 1024 * 1024
RINGBUF_MAP_NAME = "decision_ringbuf"

# --- Decision Event Structure (Match C) ---
class DecisionEvent(Structure):
    _fields_ = [
        ("pid", c_uint32),
        ("ppid", c_uint32),
        ("action", c_uint8),
        ("_pad", c_uint8 * 3),
        ("threat_score", c_uint32),
        ("timestamp_ns", c_uint64),
        ("filename", c_char * 64),
    ]

# --- Message Types (Match Rust) ---
MSG_PROCESS_TEXT = 0x01
MAGIC = 0xDEADBEEF
HEADER_SIZE = 12 # 4 magic + 2 type + 2 pad + 4 length (approx)
# Rust MessageHeader: magic(u32), msg_type(u16), length(u32)
# With repr(C), it might have padding.
# Axum/Rust repr(C) for MessageHeader:
# u32 magic (4)
# u16 msg_type (2)
# (2 bytes padding)
# u32 length (4)
# Total = 12 bytes

def write_to_shm(shm, msg_type, data):
    # Prepare header
    magic = MAGIC.to_bytes(4, 'little')
    m_type = msg_type.to_bytes(2, 'little')
    padding = b'\x00\x00'
    length = len(data).to_bytes(4, 'little')
    header = magic + m_type + padding + length
    
    # Write to SHM at offset 64 (CONTROL_SIZE in Rust)
    offset = 64
    shm.buf[offset:offset+len(header)] = header
    shm.buf[offset+len(header):offset+len(header)+len(data)] = data

def handle_event(cpu, data, size):
    event = cast(data, POINTER(DecisionEvent)).contents
    filename = event.filename.decode('utf-8', errors='ignore').rstrip('\x00')
    
    print(f"🔔 Event: PID {event.pid} executed {filename} (Score: {event.threat_score})")
    
    # Relay to TruthSync SHM
    try:
        shm = shared_memory.SharedMemory(name=SHM_NAME)
        write_to_shm(shm, MSG_PROCESS_TEXT, filename.encode('utf-8'))
        shm.close()
    except FileNotFoundError:
        print(f"⚠️  SHM {SHM_NAME} not found. Is TruthSync Rust server running?")
    except Exception as e:
        print(f"❌ SHM Error: {e}")

def main():
    print("🚀 Sentinel Ringbuf-to-SHM Relay Starting...")
    
    # Define dummy BPF to get access to ringbuf
    bpf_text = """
    struct decision_event {
        u32 pid;
        u32 ppid;
        u8 action;
        u8 _pad[3];
        u32 threat_score;
        u64 timestamp_ns;
        char filename[64];
    };
    BPF_RINGBUF_OUTPUT(decision_ringbuf, 65536);
    """
    
    try:
        b = BPF(text=bpf_text)
        print(f"✅ BCC initialized. Listening on '{RINGBUF_MAP_NAME}'...")
        
        # BCC's RingBuf needs to be polled
        b[RINGBUF_MAP_NAME].open_ring_buffer(handle_event)
        
        while True:
            try:
                b.ring_buffer_poll()
                time.sleep(0.001)
            except KeyboardInterrupt:
                print("\n🛑 Relay stopped by user.")
                break
    except Exception as e:
        print(f"❌ Failed to start BPF Relay: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
