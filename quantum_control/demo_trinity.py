#!/usr/bin/env python3
"""
E = mc² Demo

The Trinity of Infrastructure Control:
- Space (m): BufferResource
- Time (c): ThreadPoolResource  
- Energy (E): MemoryResource

All controlled by the same physics: OptomechanicalCooling
"""

import sys
sys.path.insert(0, '/home/jnovoas/sentinel')

from quantum_control.core import QuantumController
from quantum_control.physics import OptomechanicalCooling
from quantum_control.resources import BufferResource, ThreadPoolResource, MemoryResource
import threading
import time


def run_controller(name, resource, duration=20):
    """Run a controller for specified duration."""
    physics = OptomechanicalCooling()
    controller = QuantumController(
        resource=resource,
        physics_model=physics,
        poll_interval=1.0
    )
    
    print(f"\n{'='*70}")
    print(f"⚛️  {name}")
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
    print("⚛️  E = mc² - THE TRINITY")
    print("="*70)
    print()
    print("Controlling ALL dimensions of infrastructure:")
    print()
    print("  🌀 SPACE (m): BufferResource")
    print("     └─ Storage, data flow, packet buffers")
    print()
    print("  ⏱️  TIME (c): ThreadPoolResource")
    print("     └─ Processing, CPU cycles, execution")
    print()
    print("  ⚡ ENERGY (E): MemoryResource")
    print("     └─ Allocation, heap, garbage collection")
    print()
    print("All using the same physics: OptomechanicalCooling")
    print("All responding to the same law: F = v² × (1 + a)")
    print()
    print("="*70)
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
    
    memory = MemoryResource(
        process_name="app",
        initial_heap=1024,
        min_heap=256,
        max_heap=8192
    )
    
    # Run all three controllers in parallel
    duration = 15
    
    controllers = [
        ("SPACE (Buffer)", buffer),
        ("TIME (Threads)", threads),
        ("ENERGY (Memory)", memory)
    ]
    
    threads_list = []
    for name, resource in controllers:
        t = threading.Thread(
            target=run_controller,
            args=(name, resource, duration)
        )
        t.start()
        threads_list.append(t)
    
    # Wait for all
    for t in threads_list:
        t.join()
    
    print("\n" + "="*70)
    print("✅ THE TRINITY - COMPLETE")
    print("="*70)
    print()
    print("You now control:")
    print("  ✅ Space (buffers, storage)")
    print("  ✅ Time (threads, processing)")
    print("  ✅ Energy (memory, allocation)")
    print()
    print("This is E = mc² for infrastructure.")
    print()
    print("The universe is in your terminal. ⚛️✨")
    print()


if __name__ == '__main__':
    main()
