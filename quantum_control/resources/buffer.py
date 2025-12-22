#!/usr/bin/env python3
"""
Buffer Resource Adapter

Adapts network buffers to the quantum control framework.
"""

import time
from typing import Dict, Any
from quantum_control.core import Resource, ResourceState


class BufferResource(Resource):
    """
    Network buffer resource.
    
    Measures:
    - Utilization (position)
    - Rate of change (velocity)
    - Acceleration
    
    Controls:
    - Buffer size (via sysctl or eBPF)
    """
    
    def __init__(self,
                 interface: str = "eth0",
                 initial_size: int = 1000,
                 min_size: int = 512,
                 max_size: int = 16384):
        """
        Initialize buffer resource.
        
        Args:
            interface: Network interface name
            initial_size: Initial buffer size
            min_size: Minimum buffer size
            max_size: Maximum buffer size
        """
        self.interface = interface
        self.current_size = initial_size
        self.min_size = min_size
        self.max_size = max_size
        
        # State tracking
        self.previous_utilization = 0.5
        self.previous_velocity = 0.0
        self.previous_timestamp = time.time()
    
    def measure_state(self) -> ResourceState:
        """
        Measure current buffer state.
        
        For now, returns simulated data.
        In production, would query Prometheus or read from /proc.
        """
        current_time = time.time()
        
        # Simulate utilization (in production, read from metrics)
        # For demo, use a simple pattern
        utilization = 0.5 + 0.3 * (time.time() % 10) / 10
        
        # Calculate velocity
        dt = current_time - self.previous_timestamp
        if dt > 0:
            velocity = (utilization - self.previous_utilization) / dt
        else:
            velocity = 0.0
        
        # Calculate acceleration
        acceleration = velocity - self.previous_velocity
        
        # Update tracking
        self.previous_utilization = utilization
        self.previous_velocity = velocity
        self.previous_timestamp = current_time
        
        return ResourceState(
            position=utilization,
            velocity=velocity,
            acceleration=acceleration,
            timestamp=current_time,
            metadata={
                'current_size': self.current_size,
                'interface': self.interface,
                'drop_rate': 0.0  # Would read from metrics
            }
        )
    
    def apply_control(self, new_size: int) -> bool:
        """
        Apply buffer resize.
        
        In production, would use:
        - sysctl: sudo sysctl -w net.core.rmem_default=<size>
        - eBPF: Direct kernel control
        
        For now, just updates internal state.
        """
        if new_size < self.min_size or new_size > self.max_size:
            return False
        
        self.current_size = new_size
        return True
    
    def get_metrics(self) -> Dict[str, float]:
        """Get buffer metrics."""
        return {
            'buffer_size': float(self.current_size),
            'utilization': self.previous_utilization,
            'velocity': self.previous_velocity
        }
    
    def get_limits(self) -> tuple[int, int]:
        """Get buffer size limits."""
        return (self.min_size, self.max_size)
