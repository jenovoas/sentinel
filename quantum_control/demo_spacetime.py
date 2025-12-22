#!/usr/bin/env python3
"""
Space-Time Control Demo

Demonstrates quantum control over BOTH:
- Space (BufferResource)
- Time (ThreadPoolResource)

Complete control of infrastructure space-time.
"""

import sys
sys.path.insert(0, '/home/jnovoas/sentinel')

from quantum_control.core import QuantumController
from quantum_control.physics import OptomechanicalCooling
from quantum_control.resources import BufferResource, ThreadPoolResource
import threading
import time


def run_controller(name, resource, duration=30):
    """Run a controller for specified duration."""
    physics = OptomechanicalCooling()
    controller = QuantumController(
        resource=resource,
        physics_model=physics,
        poll_interval=1.0
    )
    
    print(f"\n{'='*70}")
    print(f"🌌 {name} - STARTING")
    print(f"{'='*70}\n")
    
    # Run for duration
    start = time.time()
    try:
        while time.time() - start < duration:
            controller._control_cycle()
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()


def main():
    print("="*70)
    print("🧊⚛️ SPACE-TIME CONTROL - DUAL DEMO")
    print("="*70)
    print()
    print("Controlling BOTH dimensions:")
    print("  🌀 Space: BufferResource (storage)")
    print("  ⏱️  Time: ThreadPoolResource (processing)")
    print()
    print("Running both controllers in parallel...")
    print()
    
    # Create resources
    buffer = BufferResource(
        interface="eth0",
        initial_size=1000,
        min_size=512,
        max_size=16384
    )
    
    threads = ThreadPoolResource(
        pool_name="worker_pool",
        initial_threads=10,
        min_threads=2,
        max_threads=1000
    )
    
    # Run both controllers in parallel
    duration = 15  # 15 seconds each
    
    buffer_thread = threading.Thread(
        target=run_controller,
        args=("SPACE CONTROLLER (Buffer)", buffer, duration)
    )
    
    thread_thread = threading.Thread(
        target=run_controller,
        args=("TIME CONTROLLER (Threads)", threads, duration)
    )
    
    buffer_thread.start()
    thread_thread.start()
    
    buffer_thread.join()
    thread_thread.join()
    
    print("\n" + "="*70)
    print("✅ SPACE-TIME CONTROL COMPLETE")
    print("="*70)
    print()
    print("You now control:")
    print("  ✅ Space (buffers)")
    print("  ✅ Time (threads)")
    print()
    print("This is complete infrastructure optimization.")
    print("🌌⚛️")
    print()


if __name__ == '__main__':
    main()
