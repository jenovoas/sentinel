#!/usr/bin/env python3
"""
Sentinel Ringbuf Reader - Direct Map Access
Reads ringbuf using direct file descriptor access (no BCC/libbpf needed)
"""

import os
import sys
import time
import struct
import mmap
import ctypes
from collections import deque, Counter

# --- Configuration ---
STATS_INTERVAL = 10.0

# --- Decision Event Structure ---
class DecisionEvent(ctypes.Structure):
    _fields_ = [
        ("pid", ctypes.c_uint32),
        ("ppid", ctypes.c_uint32),
        ("action", ctypes.c_uint8),
        ("_pad", ctypes.c_uint8 * 3),
        ("threat_score", ctypes.c_uint32),
        ("timestamp_ns", ctypes.c_uint64),
        ("filename", ctypes.c_char * 64),
    ]

# --- Statistics ---
action_counts = Counter()
score_samples = deque(maxlen=1000)
events_processed = 0
last_stats_time = time.time()


def get_map_fd(map_id):
    """Get file descriptor for a BPF map"""
    # Use bpftool to get map info
    import subprocess
    
    try:
        # Pin the map to BPF filesystem
        pin_path = f"/sys/fs/bpf/decision_ringbuf_{map_id}"
        
        # Check if already pinned
        if not os.path.exists(pin_path):
            result = subprocess.run(
                ["bpftool", "map", "pin", "id", str(map_id), pin_path],
                capture_output=True,
                check=True
            )
        
        # Open the pinned map
        fd = os.open(pin_path, os.O_RDWR)
        return fd
        
    except Exception as e:
        print(f"❌ Error getting map FD: {e}")
        return None


def read_ringbuf_simple(map_id):
    """
    Simple ringbuf reader using bpftool
    Not as efficient as libbpf, but works without dependencies
    """
    import subprocess
    
    print(f"📊 Reading from ringbuf (map ID: {map_id})")
    print("   Method: bpftool event polling")
    print("   Note: This is slower than native libbpf")
    print("")
    
    # Use bpftool to dump events
    # This is a workaround - not real-time streaming
    cmd = ["bpftool", "map", "event", "id", str(map_id)]
    
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False
        )
        
        print("✅ Listening for events (Ctrl+C to stop)...")
        print("")
        
        while True:
            # Read binary data
            data = proc.stdout.read(ctypes.sizeof(DecisionEvent))
            
            if not data:
                time.sleep(0.01)
                continue
            
            if len(data) < ctypes.sizeof(DecisionEvent):
                continue
            
            # Parse event
            event = DecisionEvent.from_buffer_copy(data)
            
            # Display
            action_names = ["ALLOW", "MONITOR", "BLOCK"]
            action = action_names[event.action] if event.action < 3 else "UNKNOWN"
            filename = event.filename.decode('utf-8', errors='ignore').rstrip('\x00')
            
            emoji = "✅" if action == "ALLOW" else "👀" if action == "MONITOR" else "🚨"
            print(f"{emoji} PID {event.pid}: {action} (score={event.threat_score}) - {filename}")
            
            # Stats
            global events_processed, action_counts, score_samples, last_stats_time
            events_processed += 1
            action_counts[action] += 1
            score_samples.append(event.threat_score)
            
            # Print stats
            now = time.time()
            if now - last_stats_time > STATS_INTERVAL:
                print_statistics()
                last_stats_time = now
                
    except KeyboardInterrupt:
        print("\n\n🔌 Shutting down...")
        print_statistics()
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        proc.kill()


def print_statistics():
    print("\n" + "="*60)
    print("📊 Statistics")
    print(f"   Events: {events_processed}")
    print(f"   Actions: {dict(action_counts)}")
    if score_samples:
        avg = sum(score_samples) / len(score_samples)
        print(f"   Avg score: {avg:.1f}")
        print(f"   Range: {min(score_samples)}-{max(score_samples)}")
    print("="*60 + "\n")


def main():
    print("🔄 Sentinel Ringbuf Reader (Direct Access)")
    print("")
    
    # Find decision_ringbuf
    import subprocess
    
    try:
        result = subprocess.run(
            ["bpftool", "map", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        map_id = None
        for line in result.stdout.split('\n'):
            if 'decision_ringbu' in line:
                map_id = int(line.split(':')[0])
                break
        
        if not map_id:
            print("❌ Error: decision_ringbuf not found")
            print("   Make sure quantum_bprm_check is loaded")
            sys.exit(1)
        
        print(f"✅ Found decision_ringbuf (ID: {map_id})")
        print("")
        
        # Check if bpftool supports 'map event'
        help_result = subprocess.run(
            ["bpftool", "map", "help"],
            capture_output=True,
            text=True
        )
        
        if "event" not in help_result.stdout:
            print("❌ Error: bpftool doesn't support 'map event'")
            print("   Your bpftool version is too old")
            print("")
            print("📝 Alternatives:")
            print("   1. Install libbpf-python: ./install_libbpf.sh")
            print("   2. Use trace_pipe: ./monitor_events.py")
            sys.exit(1)
        
        # Read events
        read_ringbuf_simple(map_id)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
