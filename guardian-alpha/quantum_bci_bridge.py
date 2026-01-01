#!/usr/bin/env python3
import sys
import os
import re
import time
from collections import deque
from datetime import datetime

# --- Configuration ---
TRACE_PIPE = "/sys/kernel/debug/tracing/trace_pipe"
MAX_INGESTION_LAG_SECONDS = 5.0  # Alert if events are >5s old
MAX_CLOCK_DRIFT_SECONDS = 2.0    # Reject events with >2s clock drift
LAG_SAMPLE_WINDOW = 100          # Track last 100 events for statistics

# --- Import Sentinel Core ---
# Adjust path to find sentinel_core
current_dir = os.path.dirname(os.path.abspath(__file__))
core_path = os.path.abspath(os.path.join(current_dir, "../src/core"))
sys.path.append(core_path)

try:
    from sentinel_core.brain.bci_controller import bci_controller
    print("✅ [BRIDGE] Sentinel BCI Controller connected.")
except ImportError as e:
    print(f"❌ [BRIDGE] Failed to import BCI Controller: {e}")
    sys.exit(1)


# --- Ingestion Lag Monitor (Anti-Hallucination for HA) ---
class IngestionLagMonitor:
    """
    Monitors ingestion lag to detect buffer overflows, network issues,
    or clock drift in HA deployments.
    
    Prevents "hallucinations" where old events are processed as current.
    """
    
    def __init__(self, max_lag=MAX_INGESTION_LAG_SECONDS, max_drift=MAX_CLOCK_DRIFT_SECONDS):
        self.max_lag = max_lag
        self.max_drift = max_drift
        self.lag_samples = deque(maxlen=LAG_SAMPLE_WINDOW)
        self.drift_warnings = 0
        self.lag_warnings = 0
        self.events_processed = 0
        
        # Uptime caching to reduce I/O (read every 100ms max)
        self._cached_uptime = 0.0
        self._cache_timestamp = 0.0
        self._cache_ttl = 0.1  # 100ms cache
        
    def _get_system_uptime(self):
        """
        Get system monotonic time with caching.
        
        Uses CLOCK_MONOTONIC to match kernel trace clock.
        Cache is valid for 100ms (sufficient for event processing).
        """
        now = time.time()
        if now - self._cache_timestamp > self._cache_ttl:
            # Use CLOCK_MONOTONIC to match kernel trace 'local' clock
            self._cached_uptime = time.clock_gettime(time.CLOCK_MONOTONIC)
            self._cache_timestamp = now
        return self._cached_uptime
        
    def extract_kernel_timestamp(self, line):
        """
        Extract timestamp from kernel trace line.
        
        Supports two formats:
        1. Standard: "command-PID [CPU] ...11 TIMESTAMP: message"
        2. Latency: "command-PID [CPU] TIMESTAMP us: message"
        
        Example: "ls-12345 [001] ...11 12345.678901: QUANTUM-AI..."
        """
        # Try standard format first (most common)
        match = re.search(r'\s+(\d+\.\d+):\s+', line)
        if match:
            return float(match.group(1))
        
        # Try latency format (if latency-format is enabled)
        match = re.search(r'\[[\d]+\]\s+(\d+\.\d+)\s+us:', line)
        if match:
            return float(match.group(1))
        
        return None
    
    def validate_event(self, line):
        """
        Validates event timestamp and calculates ingestion lag.
        
        Returns:
            (valid: bool, lag: float, reason: str)
        """
        kernel_time = self.extract_kernel_timestamp(line)
        
        if kernel_time is None:
            return (True, 0.0, "No timestamp found (legacy format)")
        
        # Current system time (CLOCK_MONOTONIC, matches kernel trace)
        system_uptime = self._get_system_uptime()
        
        # Calculate lag (how old is this event?)
        lag = system_uptime - kernel_time
        
        # Detect clock drift (negative lag = event from future!)
        # Note: Small negative lags (<100ms) are normal due to per-CPU clock drift
        if lag < -self.max_drift:
            self.drift_warnings += 1
            return (False, lag, f"Clock drift detected: event is {abs(lag):.2f}s in the future")
        
        # Detect excessive lag (buffer overflow or network issue)
        if lag > self.max_lag:
            self.lag_warnings += 1
            return (False, lag, f"Excessive ingestion lag: {lag:.2f}s (max: {self.max_lag}s)")
        
        # Valid event (including small negative lags from CPU drift)
        self.lag_samples.append(lag)
        self.events_processed += 1
        return (True, lag, "OK")
    
    def get_statistics(self):
        """Returns lag statistics for monitoring."""
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
        """Prints lag statistics to console."""
        stats = self.get_statistics()
        print(f"\n📊 [LAG MONITOR] Statistics:")
        print(f"   Events processed: {stats['events_processed']}")
        print(f"   Avg lag: {stats['avg_lag']*1000:.2f}ms")
        print(f"   Max lag: {stats['max_lag']*1000:.2f}ms")
        print(f"   Min lag: {stats['min_lag']*1000:.2f}ms")
        print(f"   Drift warnings: {stats['drift_warnings']}")
        print(f"   Lag warnings: {stats['lag_warnings']}")


# Global monitor instance
lag_monitor = IngestionLagMonitor()


def handle_log_line(line):
    """Parses a kernel log line and triggers BCI events."""
    line = line.strip()
    
    # Validate timestamp and check for lag/drift
    valid, lag, reason = lag_monitor.validate_event(line)
    
    if not valid:
        print(f"⚠️ [LAG MONITOR] Event rejected: {reason}")
        print(f"   Line: {line[:80]}...")
        return
    
    # Log lag if significant (>100ms)
    if lag > 0.1:
        print(f"⏱️ [LAG MONITOR] Event lag: {lag*1000:.1f}ms")
    
    # Example Log: "QUANTUM-AI BLOCK: score=85, residue=11"
    match_block = re.search(r"QUANTUM-AI BLOCK: score=(\d+), residue=(\d+)", line)
    
    if match_block:
        score = int(match_block.group(1))
        residue = int(match_block.group(2))
        
        print(f"🚨 [KERNEL DETECT] THREAT BLOCKED! Score: {score}, Base-60 Residue: {residue}")
        
        # 1. Trigger Audio Qualia
        bci_controller.trigger_qualia("KERNEL_BLOCK")
        
        # 2. Reinforce with Base-60 Mathematical feedback (optional, async)
        # We assume bci_controller handles threading/async internally or is fast enough.
        # Ideally, playing a tone usually blocks, so be careful. 
        # Check if play_base60_pattern is non-blocking or short.
        # For now, we prioritize the alert.
        time.sleep(0.1) 
        bci_controller.play_base60_pattern(residue)
        return

    # Check for MONITOR/ALLOW if implemented in C printk
    if "QUANTUM-AI MONITOR" in line:
        print(f"👀 [KERNEL DETECT] Suspicious activity monitored.")
        bci_controller.trigger_qualia("MONITOR_SUSPICIOUS")
        return

def main():
    print(f"🔌 [BRIDGE] Connecting to Kernel Trace Pipe: {TRACE_PIPE}")
    print("   (Ensure eBPF module 'quantum_ai_integration' is loaded)")
    print(f"⏱️ [LAG MONITOR] Max ingestion lag: {MAX_INGESTION_LAG_SECONDS}s")
    print(f"🕐 [LAG MONITOR] Max clock drift: {MAX_CLOCK_DRIFT_SECONDS}s")
    
    if not os.path.exists(TRACE_PIPE):
        print(f"❌ Error: {TRACE_PIPE} not found. Are you running as root/sudo?")
        print("   Also check if debugfs is mounted: mount -t debugfs none /sys/kernel/debug")
        sys.exit(1)

    print("✅ [BRIDGE] Linked. Waiting for Neural/Kernel Events...")
    
    # Statistics printing interval
    last_stats_print = time.time()
    STATS_INTERVAL = 60.0  # Print stats every 60 seconds
    
    try:
        with open(TRACE_PIPE, "r", encoding="utf-8", errors="ignore") as pipe:
            while True:
                line = pipe.readline()
                if line:
                    # Filter for our specific tag to avoid processing everything
                    if "QUANTUM-AI" in line:
                        handle_log_line(line)
                        
                        # Print statistics periodically
                        if time.time() - last_stats_print > STATS_INTERVAL:
                            lag_monitor.print_statistics()
                            last_stats_print = time.time()
                else:
                    # Non-blocking read might handle emptiness differently, 
                    # but standard open() hangs until data comes in trace_pipe.
                    time.sleep(0.1)
    except PermissionError:
        print("❌ Permission Denied. Please run with sudo.")
    except KeyboardInterrupt:
        print("\n🔌 [BRIDGE] Disconnecting...")
        # Print final statistics
        lag_monitor.print_statistics()

if __name__ == "__main__":
    main()
