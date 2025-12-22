#!/usr/bin/env python3
"""
Quantum Control Framework - Demo

Demonstrates universal quantum control on a buffer resource.
"""

import sys
sys.path.insert(0, '/home/jnovoas/sentinel')

from quantum_control.core import QuantumController
from quantum_control.physics import OptomechanicalCooling
from quantum_control.resources import BufferResource


def main():
    print("="*70)
    print("🧊⚛️ UNIVERSAL QUANTUM CONTROL - DEMO")
    print("="*70)
    print()
    print("Demonstrating quantum control on network buffer...")
    print()
    
    # Create resource
    buffer = BufferResource(
        interface="eth0",
        initial_size=1000,
        min_size=512,
        max_size=16384
    )
    
    # Create physics model
    physics = OptomechanicalCooling(
        velocity_threshold=0.8,
        acceleration_threshold=0.3,
        cooling_factor=1.5,
        base_damping=0.8
    )
    
    # Create controller
    controller = QuantumController(
        resource=buffer,
        physics_model=physics,
        poll_interval=1.0
    )
    
    # Run for 30 seconds
    print("Running for 30 seconds (Ctrl+C to stop)...")
    print()
    
    try:
        import time
        start = time.time()
        controller.start()
    except KeyboardInterrupt:
        controller.stop()


if __name__ == '__main__':
    main()
