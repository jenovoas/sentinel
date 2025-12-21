#!/usr/bin/env python3
"""
Sentinel Cortex™ - Burst Sensor Loader
Load eBPF burst sensor and read events from ring buffer

Copyright (c) 2025 Sentinel Cortex™ - All Rights Reserved
"""

import sys
import time
import struct
from bcc import BPF

# eBPF program (inline for simplicity)
BPF_PROGRAM = """
#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>

// Ring buffer for events
BPF_RINGBUF_OUTPUT(burst_events, 8);

// Per-CPU packet counter
BPF_PERCPU_ARRAY(pkt_count, u64, 1);

// Last check timestamp
BPF_ARRAY(last_check, u64, 1);

// Burst event structure
struct burst_event {
    u64 timestamp;
    u64 pps;
    u32 burst_detected;
    u32 severity;
};

// Thresholds
#define BURST_THRESHOLD_LOW     1000
#define BURST_THRESHOLD_MEDIUM  10000
#define BURST_THRESHOLD_HIGH    50000
#define BURST_THRESHOLD_CRITICAL 100000
#define CHECK_INTERVAL_NS       1000000000ULL

int detect_burst(struct xdp_md *ctx) {
    u32 key = 0;
    u64 *count, *last_ts;
    u64 now, elapsed_ns, pps;
    
    now = bpf_ktime_get_ns();
    
    // Increment packet counter
    count = pkt_count.lookup(&key);
    if (!count) {
        return XDP_PASS;
    }
    lock_xadd(count, 1);
    
    // Check if time to calculate PPS
    last_ts = last_check.lookup(&key);
    if (!last_ts) {
        return XDP_PASS;
    }
    
    elapsed_ns = now - *last_ts;
    
    if (elapsed_ns < CHECK_INTERVAL_NS) {
        return XDP_PASS;
    }
    
    // Calculate PPS
    pps = (*count * 1000000000ULL) / elapsed_ns;
    
    // Determine severity
    u32 severity = 0;
    u32 burst_detected = 0;
    
    if (pps >= BURST_THRESHOLD_CRITICAL) {
        severity = 3;
        burst_detected = 1;
    } else if (pps >= BURST_THRESHOLD_HIGH) {
        severity = 2;
        burst_detected = 1;
    } else if (pps >= BURST_THRESHOLD_MEDIUM) {
        severity = 1;
        burst_detected = 1;
    } else if (pps >= BURST_THRESHOLD_LOW) {
        severity = 0;
        burst_detected = 1;
    }
    
    // Send event if burst detected
    if (burst_detected) {
        struct burst_event event = {
            .timestamp = now,
            .pps = pps,
            .burst_detected = burst_detected,
            .severity = severity
        };
        burst_events.ringbuf_output(&event, sizeof(event), 0);
    }
    
    // Reset
    *count = 0;
    *last_ts = now;
    
    return XDP_PASS;
}
"""

class BurstSensor:
    """eBPF Burst Sensor"""
    
    def __init__(self, interface="lo"):
        """Initialize burst sensor on given interface"""
        self.interface = interface
        self.bpf = None
        self.callbacks = []
        
    def load(self):
        """Load eBPF program"""
        print(f"[*] Loading eBPF burst sensor on {self.interface}...")
        
        try:
            self.bpf = BPF(text=BPF_PROGRAM)
            fn = self.bpf.load_func("detect_burst", BPF.XDP)
            self.bpf.attach_xdp(self.interface, fn, 0)
            print(f"[+] eBPF burst sensor loaded successfully")
            return True
        except Exception as e:
            print(f"[!] Failed to load eBPF program: {e}")
            return False
    
    def register_callback(self, callback):
        """Register callback for burst events"""
        self.callbacks.append(callback)
    
    def poll_events(self, timeout=1000):
        """Poll for burst events"""
        if not self.bpf:
            return
        
        def event_handler(cpu, data, size):
            """Handle burst event from ring buffer"""
            # Parse event structure
            event = self.bpf["burst_events"].event(data)
            
            # Call registered callbacks
            for callback in self.callbacks:
                callback(event)
        
        # Open ring buffer
        self.bpf["burst_events"].open_ring_buffer(event_handler)
        
        # Poll
        try:
            self.bpf.ring_buffer_poll(timeout)
        except KeyboardInterrupt:
            pass
    
    def unload(self):
        """Unload eBPF program"""
        if self.bpf:
            print(f"[*] Unloading eBPF burst sensor...")
            self.bpf.remove_xdp(self.interface, 0)
            print(f"[+] eBPF burst sensor unloaded")


def print_burst_event(event):
    """Print burst event to console"""
    severity_names = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    severity = severity_names[event.severity] if event.severity < 4 else "UNKNOWN"
    
    print(f"[BURST] PPS: {event.pps:,} | Severity: {severity} | Time: {event.timestamp}")


def main():
    """Main function"""
    if len(sys.argv) > 1:
        interface = sys.argv[1]
    else:
        interface = "lo"  # Default to loopback
    
    print("=" * 60)
    print("Sentinel Cortex™ - eBPF Burst Sensor")
    print("=" * 60)
    
    sensor = BurstSensor(interface)
    
    if not sensor.load():
        sys.exit(1)
    
    # Register callback
    sensor.register_callback(print_burst_event)
    
    print(f"\n[*] Monitoring traffic on {interface}...")
    print("[*] Press Ctrl+C to stop\n")
    
    try:
        while True:
            sensor.poll_events(timeout=1000)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[*] Stopping...")
    finally:
        sensor.unload()


if __name__ == "__main__":
    main()
