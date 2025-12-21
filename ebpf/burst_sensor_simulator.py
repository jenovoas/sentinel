#!/usr/bin/env python3
"""
Sentinel Cortex™ - Burst Sensor Simulator
Simulates eBPF burst detection without requiring kernel access

Copyright (c) 2025 Sentinel Cortex™ - All Rights Reserved
"""

import time
import random
from dataclasses import dataclass

@dataclass
class BurstEvent:
    """Simulated burst event"""
    timestamp: int
    pps: int
    burst_detected: int
    severity: int

class BurstSensorSimulator:
    """Simulates eBPF burst sensor for testing"""
    
    # Thresholds (same as eBPF)
    BURST_THRESHOLD_LOW = 1000
    BURST_THRESHOLD_MEDIUM = 10000
    BURST_THRESHOLD_HIGH = 50000
    BURST_THRESHOLD_CRITICAL = 100000
    
    def __init__(self):
        self.callbacks = []
        self.running = False
    
    def register_callback(self, callback):
        """Register callback for burst events"""
        self.callbacks.append(callback)
    
    def _generate_traffic_pattern(self):
        """Generate realistic traffic patterns"""
        patterns = [
            # (duration_seconds, base_pps, variance)
            (5, 500, 100),          # Normal traffic
            (2, 15000, 2000),       # Medium burst
            (1, 75000, 5000),       # High burst
            (3, 800, 200),          # Back to normal
            (1, 150000, 10000),     # Critical burst
            (5, 600, 150),          # Normal again
        ]
        
        for duration, base_pps, variance in patterns:
            end_time = time.time() + duration
            while time.time() < end_time:
                # Add random variance
                pps = base_pps + random.randint(-variance, variance)
                pps = max(0, pps)  # No negative PPS
                
                yield pps
                time.sleep(0.1)  # 100ms intervals
    
    def _detect_burst(self, pps):
        """Detect burst and determine severity"""
        if pps >= self.BURST_THRESHOLD_CRITICAL:
            return True, 3
        elif pps >= self.BURST_THRESHOLD_HIGH:
            return True, 2
        elif pps >= self.BURST_THRESHOLD_MEDIUM:
            return True, 1
        elif pps >= self.BURST_THRESHOLD_LOW:
            return True, 0
        else:
            return False, 0
    
    def run(self):
        """Run burst sensor simulation"""
        self.running = True
        
        print("[*] Starting burst sensor simulation...")
        print("[*] Simulating realistic traffic patterns...")
        print("")
        
        for pps in self._generate_traffic_pattern():
            if not self.running:
                break
            
            burst_detected, severity = self._detect_burst(pps)
            
            if burst_detected:
                event = BurstEvent(
                    timestamp=int(time.time() * 1_000_000_000),  # Nanoseconds
                    pps=pps,
                    burst_detected=1,
                    severity=severity
                )
                
                # Call registered callbacks
                for callback in self.callbacks:
                    callback(event)
    
    def stop(self):
        """Stop simulation"""
        self.running = False


def print_burst_event(event):
    """Print burst event to console"""
    severity_names = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    severity = severity_names[event.severity] if event.severity < 4 else "UNKNOWN"
    
    # Color coding
    colors = {
        "LOW": "\033[92m",      # Green
        "MEDIUM": "\033[93m",   # Yellow
        "HIGH": "\033[91m",     # Red
        "CRITICAL": "\033[95m", # Magenta
    }
    reset = "\033[0m"
    
    color = colors.get(severity, "")
    print(f"{color}[BURST]{reset} PPS: {event.pps:>7,} | Severity: {severity:>8} | Time: {event.timestamp}")


def main():
    """Main function"""
    print("=" * 60)
    print("Sentinel Cortex™ - eBPF Burst Sensor SIMULATOR")
    print("=" * 60)
    print("")
    print("[*] This is a simulation - no eBPF required")
    print("[*] Simulates realistic traffic patterns")
    print("")
    
    simulator = BurstSensorSimulator()
    simulator.register_callback(print_burst_event)
    
    try:
        simulator.run()
    except KeyboardInterrupt:
        print("\n[*] Stopping simulation...")
        simulator.stop()
    
    print("\n[+] Simulation complete")


if __name__ == "__main__":
    main()
