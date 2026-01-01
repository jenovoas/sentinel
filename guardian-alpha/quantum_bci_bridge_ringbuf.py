#!/usr/bin/env python3
"""
Sentinel Quantum-AI BCI Bridge - Ringbuf Version
High-performance event processing using BPF ringbuf instead of trace_pipe
"""

import asyncio
import sys
import os
import struct
import time
from collections import deque
from ctypes import *

# --- Configuration ---
MAX_INGESTION_LAG_SECONDS = 5.0
MAX_CLOCK_DRIFT_SECONDS = 2.0
LAG_SAMPLE_WINDOW = 100

# --- Import Sentinel Core ---
current_dir = os.path.dirname(os.path.abspath(__file__))
core_path = os.path.abspath(os.path.join(current_dir, "../src/core"))
sys.path.append(core_path)

try:
    from sentinel_core.brain.bci_controller import bci_controller
    HAS_BCI = True
    print("✅ [BRIDGE] Sentinel BCI Controller connected.")
except ImportError as e:
    HAS_BCI = False
    print(f"⚠️  [BRIDGE] BCI Controller not available: {e}")
    print("   Running in monitoring-only mode (no audio)")
    
    # Mock BCI controller
    class MockBCI:
        def trigger_qualia(self, qualia_type):
            print(f"   [MOCK BCI] Would trigger: {qualia_type}")
        
        def play_base60_pattern(self, residue):
            print(f"   [MOCK BCI] Would play pattern: {residue}")
    
    bci_controller = MockBCI()

# Try to import BPF library
try:
    from bcc import BPF
    HAS_BCC = True
    print("✅ [BRIDGE] BCC library available (ringbuf mode)")
except ImportError:
    HAS_BCC = False
    print("⚠️  [BRIDGE] BCC not available, falling back to trace_pipe mode")


# --- Decision Event Structure (matches C struct) ---
class DecisionEvent(Structure):
    _fields_ = [
        ("pid", c_uint32),
        ("ppid", c_uint32),
        ("action", c_uint8),
        ("threat_score", c_uint32),
        ("timestamp_ns", c_uint64),
        ("filename", c_char * 64),
    ]


# --- Ingestion Lag Monitor ---
class IngestionLagMonitor:
    """Monitors ingestion lag for HA deployments"""
    
    def __init__(self, max_lag=MAX_INGESTION_LAG_SECONDS, max_drift=MAX_CLOCK_DRIFT_SECONDS):
        self.max_lag = max_lag
        self.max_drift = max_drift
        self.lag_samples = deque(maxlen=LAG_SAMPLE_WINDOW)
        self.drift_warnings = 0
        self.lag_warnings = 0
        self.events_processed = 0
        
        # Uptime caching
        self._cached_uptime = 0.0
        self._cache_timestamp = 0.0
        self._cache_ttl = 0.1  # 100ms
        
    def _get_system_uptime(self):
        """Get system monotonic time (matches kernel trace clock)"""
        now = time.time()
        if now - self._cache_timestamp > self._cache_ttl:
            self._cached_uptime = time.clock_gettime(time.CLOCK_MONOTONIC)
            self._cache_timestamp = now
        return self._cached_uptime
    
    def validate_event(self, timestamp_ns):
        """
        Validates event timestamp from ringbuf.
        
        Args:
            timestamp_ns: Kernel timestamp in nanoseconds
            
        Returns:
            (valid: bool, lag: float, reason: str)
        """
        kernel_time = timestamp_ns / 1e9  # Convert to seconds
        system_time = self._get_system_uptime()
        
        lag = system_time - kernel_time
        
        # Allow small negative lags (per-CPU clock drift)
        if lag < -self.max_drift:
            self.drift_warnings += 1
            return (False, lag, f"Clock drift: {abs(lag):.2f}s in future")
        
        # Detect excessive lag
        if lag > self.max_lag:
            self.lag_warnings += 1
            return (False, lag, f"Excessive lag: {lag:.2f}s (max: {self.max_lag}s)")
        
        # Valid event
        self.lag_samples.append(lag)
        self.events_processed += 1
        return (True, lag, "OK")
    
    def get_statistics(self):
        """Returns lag statistics"""
        if not self.lag_samples:
            return {
                "avg_lag": 0.0,
                "max_lag": 0.0,
                "min_lag": 0.0,
                "events_processed": self.events_processed,
                "drift_warnings": self.drift_warnings,
                "lag_warnings": self.lag_warnings
            }
        
        return {
            "avg_lag": sum(self.lag_samples) / len(self.lag_samples),
            "max_lag": max(self.lag_samples),
            "min_lag": min(self.lag_samples),
            "events_processed": self.events_processed,
            "drift_warnings": self.drift_warnings,
            "lag_warnings": self.lag_warnings
        }
    
    def print_statistics(self):
        """Prints lag statistics"""
        stats = self.get_statistics()
        print(f"\n📊 [LAG MONITOR] Statistics:")
        print(f"   Events processed: {stats['events_processed']}")
        print(f"   Avg lag: {stats['avg_lag']*1000:.2f}ms")
        print(f"   Max lag: {stats['max_lag']*1000:.2f}ms")
        print(f"   Min lag: {stats['min_lag']*1000:.2f}ms")
        print(f"   Drift warnings: {stats['drift_warnings']}")
        print(f"   Lag warnings: {stats['lag_warnings']}")


# Global monitor
lag_monitor = IngestionLagMonitor()


# --- Event Handler ---
def handle_decision_event(event):
    """Process a decision event from ringbuf"""
    
    # Validate timestamp
    valid, lag, reason = lag_monitor.validate_event(event.timestamp_ns)
    
    if not valid:
        print(f"⚠️ [LAG MONITOR] Event rejected: {reason}")
        return
    
    # Log lag if significant
    if lag > 0.1:
        print(f"⏱️ [LAG MONITOR] Event lag: {lag*1000:.1f}ms")
    
    # Decode filename
    filename = event.filename.decode('utf-8', errors='ignore').rstrip('\x00')
    
    # Process based on action
    if event.action == 2:  # BLOCK
        print(f"🚨 [KERNEL DETECT] THREAT BLOCKED!")
        print(f"   PID: {event.pid}, Score: {event.threat_score}")
        print(f"   File: {filename}")
        
        bci_controller.trigger_qualia("KERNEL_BLOCK")
        time.sleep(0.1)
        # Base-60 pattern based on PID
        residue = event.pid % 60
        bci_controller.play_base60_pattern(residue)
        
    elif event.action == 1:  # MONITOR
        print(f"👀 [KERNEL DETECT] Suspicious activity monitored")
        print(f"   PID: {event.pid}, Score: {event.threat_score}")
        print(f"   File: {filename}")
        
        bci_controller.trigger_qualia("MONITOR_SUSPICIOUS")


# --- Ringbuf Polling (Async) ---
async def poll_ringbuf_async(bpf, ringbuf_name="decision_ringbuf"):
    """
    Asynchronously poll ringbuf for events.
    Non-blocking, high-performance.
    """
    print(f"🔄 [BRIDGE] Polling ringbuf: {ringbuf_name}")
    
    # Get ringbuf map
    ringbuf = bpf.get_table(ringbuf_name)
    
    # Statistics interval
    last_stats = time.time()
    STATS_INTERVAL = 60.0
    
    def callback(ctx, data, size):
        """Callback for each ringbuf event"""
        event = cast(data, POINTER(DecisionEvent)).contents
        handle_decision_event(event)
        
        # Print stats periodically
        nonlocal last_stats
        if time.time() - last_stats > STATS_INTERVAL:
            lag_monitor.print_statistics()
            last_stats = time.time()
    
    # Open ringbuf
    ringbuf.open_ring_buffer(callback)
    
    print("✅ [BRIDGE] Ringbuf opened, waiting for events...")
    
    try:
        while True:
            # Poll with 100ms timeout (non-blocking)
            bpf.ring_buffer_poll(timeout=100)
            await asyncio.sleep(0.01)  # Yield to event loop
    except KeyboardInterrupt:
        print("\n🔌 [BRIDGE] Disconnecting...")
        lag_monitor.print_statistics()


# --- Fallback: Trace Pipe (Blocking) ---
def poll_trace_pipe_blocking():
    """Fallback to trace_pipe if BCC not available"""
    import re
    
    TRACE_PIPE = "/sys/kernel/debug/tracing/trace_pipe"
    
    print(f"🔌 [BRIDGE] Connecting to trace_pipe (fallback mode)")
    
    if not os.path.exists(TRACE_PIPE):
        print(f"❌ Error: {TRACE_PIPE} not found")
        sys.exit(1)
    
    print("✅ [BRIDGE] Linked. Waiting for events...")
    
    try:
        with open(TRACE_PIPE, "r", encoding="utf-8", errors="ignore") as pipe:
            while True:
                line = pipe.readline()
                if line and "QUANTUM-AI" in line:
                    # Parse legacy format
                    if "BLOCK" in line:
                        print(f"🚨 [KERNEL DETECT] THREAT BLOCKED (trace_pipe)")
                        bci_controller.trigger_qualia("KERNEL_BLOCK")
                    elif "MONITOR" in line:
                        print(f"👀 [KERNEL DETECT] Suspicious activity (trace_pipe)")
                        bci_controller.trigger_qualia("MONITOR_SUSPICIOUS")
    except KeyboardInterrupt:
        print("\n🔌 [BRIDGE] Disconnecting...")


# --- Main ---
async def main_async():
    """Main async entry point (ringbuf mode)"""
    
    print("🔍 [BRIDGE] Looking for quantum_bprm_check program...")
    
    # Use bpftool to find the decision_ringbuf map
    import subprocess
    
    try:
        # Get map ID
        result = subprocess.run(
            ["bpftool", "map", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse output to find decision_ringbuf
        map_id = None
        for line in result.stdout.split('\n'):
            if 'decision_ringbu' in line:  # Name is truncated
                map_id = line.split(':')[0]
                break
        
        if not map_id:
            print("⚠️  [BRIDGE] decision_ringbuf not found")
            print("   Falling back to trace_pipe...")
            poll_trace_pipe_blocking()
            return
        
        print(f"✅ [BRIDGE] Found decision_ringbuf (ID: {map_id})")
        
        # TODO: Implement ringbuf polling with map FD
        # For now, this requires libbpf-python which may not be installed
        print("⚠️  [BRIDGE] Ringbuf polling not fully implemented yet")
        print("   Falling back to trace_pipe...")
        
        # Check if trace_pipe is available
        TRACE_PIPE = "/sys/kernel/debug/tracing/trace_pipe"
        if not os.path.exists(TRACE_PIPE):
            print(f"❌ Error: {TRACE_PIPE} not found")
            return
        
        # Try to open (will fail if busy)
        try:
            poll_trace_pipe_blocking()
        except OSError as e:
            if e.errno == 16:  # EBUSY
                print(f"❌ Error: trace_pipe is busy")
                print("   Another process is reading from it")
                print("   Kill it with: sudo pkill -f trace_pipe")
            else:
                raise
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running bpftool: {e}")
        print("   Make sure bpftool is installed")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main entry point"""
    if HAS_BCC:
        # Use async ringbuf polling
        try:
            asyncio.run(main_async())
        except KeyboardInterrupt:
            print("\n🔌 [BRIDGE] Shutting down...")
            lag_monitor.print_statistics()
    else:
        # Fallback to trace_pipe
        try:
            poll_trace_pipe_blocking()
        except KeyboardInterrupt:
            print("\n🔌 [BRIDGE] Shutting down...")
        except OSError as e:
            if e.errno == 16:
                print(f"❌ Error: trace_pipe is busy")
                print("   Kill competing process: sudo pkill -f trace_pipe")
            else:
                raise


if __name__ == "__main__":
    main()
