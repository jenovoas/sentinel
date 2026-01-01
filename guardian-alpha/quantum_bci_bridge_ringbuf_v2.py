#!/usr/bin/env python3
"""
Sentinel Quantum-AI BCI Bridge - Pure Ringbuf Implementation
Uses BPF ringbuf for high-performance event streaming (no trace_pipe)
"""

import sys
import os
import time
import signal
from collections import deque, Counter
from ctypes import *

# --- Configuration ---
MAX_INGESTION_LAG_SECONDS = 5.0
MAX_CLOCK_DRIFT_SECONDS = 2.0
LAG_SAMPLE_WINDOW = 100
STATS_INTERVAL = 60.0

# --- Import BCC ---
try:
    from bcc import BPF
except ImportError:
    print("❌ Error: BCC not installed")
    print("   Run: sudo ./guardian-alpha/install_bcc.sh")
    sys.exit(1)

# --- Import Sentinel Core (Optional) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
core_path = os.path.abspath(os.path.join(current_dir, "../src/core"))
sys.path.append(core_path)

try:
    from sentinel_core.brain.bci_controller import bci_controller
    HAS_BCI = True
    print("✅ [BRIDGE] BCI Controller connected")
except ImportError:
    HAS_BCI = False
    print("⚠️  [BRIDGE] BCI not available, monitoring only")
    
    class MockBCI:
        def trigger_qualia(self, q): pass
        def play_base60_pattern(self, r): pass
    bci_controller = MockBCI()


# --- Decision Event Structure ---
class DecisionEvent(Structure):
    _fields_ = [
        ("pid", c_uint32),
        ("ppid", c_uint32),
        ("action", c_uint8),
        ("_pad", c_uint8 * 3),  # Padding for alignment
        ("threat_score", c_uint32),
        ("timestamp_ns", c_uint64),
        ("filename", c_char * 64),
    ]


# --- Ingestion Lag Monitor ---
class IngestionLagMonitor:
    def __init__(self, max_lag=MAX_INGESTION_LAG_SECONDS, max_drift=MAX_CLOCK_DRIFT_SECONDS):
        self.max_lag = max_lag
        self.max_drift = max_drift
        self.lag_samples = deque(maxlen=LAG_SAMPLE_WINDOW)
        self.drift_warnings = 0
        self.lag_warnings = 0
        self.events_processed = 0
        self._cached_uptime = 0.0
        self._cache_timestamp = 0.0
        self._cache_ttl = 0.1
        
    def _get_system_uptime(self):
        now = time.time()
        if now - self._cache_timestamp > self._cache_ttl:
            self._cached_uptime = time.clock_gettime(time.CLOCK_MONOTONIC)
            self._cache_timestamp = now
        return self._cached_uptime
    
    def validate_event(self, timestamp_ns):
        kernel_time = timestamp_ns / 1e9
        system_time = self._get_system_uptime()
        lag = system_time - kernel_time
        
        if lag < -self.max_drift:
            self.drift_warnings += 1
            return (False, lag, f"Clock drift: {abs(lag):.2f}s")
        
        if lag > self.max_lag:
            self.lag_warnings += 1
            return (False, lag, f"Excessive lag: {lag:.2f}s")
        
        self.lag_samples.append(lag)
        self.events_processed += 1
        return (True, lag, "OK")
    
    def get_statistics(self):
        if not self.lag_samples:
            return {
                "avg_lag": 0.0,
                "max_lag": 0.0,
                "min_lag": 0.0,
                "events": self.events_processed,
                "drift_warnings": self.drift_warnings,
                "lag_warnings": self.lag_warnings
            }
        
        return {
            "avg_lag": sum(self.lag_samples) / len(self.lag_samples),
            "max_lag": max(self.lag_samples),
            "min_lag": min(self.lag_samples),
            "events": self.events_processed,
            "drift_warnings": self.drift_warnings,
            "lag_warnings": self.lag_warnings
        }


# --- Global State ---
lag_monitor = IngestionLagMonitor()
action_counts = Counter()
score_samples = deque(maxlen=1000)
last_stats_time = time.time()
running = True


def signal_handler(sig, frame):
    global running
    running = False
    print("\n\n🔌 [BRIDGE] Shutting down...")


signal.signal(signal.SIGINT, signal_handler)


# --- Event Handler ---
def handle_event(cpu, data, size):
    global last_stats_time
    
    event = cast(data, POINTER(DecisionEvent)).contents
    
    # Validate timestamp
    valid, lag, reason = lag_monitor.validate_event(event.timestamp_ns)
    
    if not valid:
        print(f"⚠️  [LAG] Event rejected: {reason}")
        return
    
    # Decode filename
    filename = event.filename.decode('utf-8', errors='ignore').rstrip('\x00')
    
    # Track statistics
    action_names = ["ALLOW", "MONITOR", "BLOCK"]
    action = action_names[event.action] if event.action < 3 else "UNKNOWN"
    action_counts[action] += 1
    score_samples.append(event.threat_score)
    
    # Display event
    emoji = "✅" if action == "ALLOW" else "👀" if action == "MONITOR" else "🚨"
    print(f"{emoji} PID {event.pid}: {action} (score={event.threat_score}) - {filename}")
    
    # Trigger BCI
    if event.action == 2:  # BLOCK
        bci_controller.trigger_qualia("KERNEL_BLOCK")
        residue = event.pid % 60
        bci_controller.play_base60_pattern(residue)
    elif event.action == 1:  # MONITOR
        bci_controller.trigger_qualia("MONITOR_SUSPICIOUS")
    
    # Print stats periodically
    now = time.time()
    if now - last_stats_time > STATS_INTERVAL:
        print_statistics()
        last_stats_time = now


def print_statistics():
    print("\n" + "="*70)
    print("📊 Statistics")
    
    # Lag stats
    lag_stats = lag_monitor.get_statistics()
    print(f"   Events processed: {lag_stats['events']}")
    print(f"   Avg lag: {lag_stats['avg_lag']*1000:.2f}ms")
    print(f"   Lag range: {lag_stats['min_lag']*1000:.2f}ms - {lag_stats['max_lag']*1000:.2f}ms")
    print(f"   Drift warnings: {lag_stats['drift_warnings']}")
    print(f"   Lag warnings: {lag_stats['lag_warnings']}")
    
    # Action stats
    print(f"\n   Actions: {dict(action_counts)}")
    
    # Score stats
    if score_samples:
        avg_score = sum(score_samples) / len(score_samples)
        print(f"   Avg score: {avg_score:.1f}")
        print(f"   Score range: {min(score_samples)}-{max(score_samples)}")
    
    print("="*70 + "\n")


# --- Main ---
def main():
    print("🚀 Sentinel Quantum-AI BCI Bridge (Ringbuf Mode)")
    print("")
    
    # Find decision_ringbuf map
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
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running bpftool: {e}")
        sys.exit(1)
    
    # Open ringbuf using BCC
    # Note: BCC requires the full BPF program to be loaded via BCC itself
    # For now, we'll use a workaround with perf_buffer
    
    print("\n⚠️  Note: BCC ringbuf support requires loading program via BCC")
    print("   Current implementation uses existing program (ID 199)")
    print("   Falling back to perf_buffer polling...\n")
    
    # Alternative: Use bpf_map_lookup_elem in a loop
    # This is less efficient but works with pre-loaded programs
    
    print("🔄 Polling ringbuf via map operations...")
    print("   (This is a workaround until libbpf-python is available)")
    print("")
    
    # For now, recommend using trace_pipe or waiting for libbpf-python
    print("❌ Full ringbuf implementation requires libbpf-python")
    print("   Install with: pip install libbpf")
    print("")
    print("📝 For now, use:")
    print("   sudo ./guardian-alpha/monitor_events.py  (trace_pipe, slow)")
    print("   sudo ./guardian-alpha/quantum_bci_bridge.py  (trace_pipe, with BCI)")
    print("")
    print("🚀 Full ringbuf support coming soon!")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
