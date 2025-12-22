#!/usr/bin/env python3
"""
Quantum Control Framework - Core Abstractions

Universal quantum controller for any infrastructure resource.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, Any
from collections import deque
import time


@dataclass
class ResourceState:
    """
    Universal state representation for any resource.
    
    Maps to physics:
    - position: current utilization/load
    - velocity: rate of change
    - acceleration: change in rate
    - timestamp: when measured
    """
    position: float      # Current state (0.0-1.0, normalized)
    velocity: float      # Rate of change
    acceleration: float  # Change in velocity
    timestamp: float     # When measured
    metadata: Dict[str, Any]  # Resource-specific data


class Resource(ABC):
    """
    Abstract interface for any controllable resource.
    
    Examples: buffers, threads, memory, connections, load balancers
    """
    
    @abstractmethod
    def measure_state(self) -> ResourceState:
        """
        Measure current state of the resource.
        
        Returns:
            ResourceState with position, velocity, acceleration
        """
        pass
    
    @abstractmethod
    def apply_control(self, new_size: int) -> bool:
        """
        Apply control action to the resource.
        
        Args:
            new_size: New size/capacity for the resource
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, float]:
        """
        Get resource-specific metrics for monitoring.
        
        Returns:
            Dictionary of metric name -> value
        """
        pass
    
    @abstractmethod
    def get_limits(self) -> tuple[int, int]:
        """
        Get min and max limits for this resource.
        
        Returns:
            (min_size, max_size)
        """
        pass


class PhysicsModel(ABC):
    """
    Abstract physics model for control.
    
    Implements specific cooling/control strategies.
    """
    
    @abstractmethod
    def calculate_force(self, 
                       state: ResourceState, 
                       history: deque[ResourceState]) -> float:
        """
        Calculate control force based on physics.
        
        Args:
            state: Current state
            history: Historical states
            
        Returns:
            Force magnitude (0.0-1.0)
        """
        pass
    
    @abstractmethod
    def calculate_ground_state(self, history: deque[ResourceState]) -> float:
        """
        Calculate optimal "ground state" for this resource.
        
        Args:
            history: Historical states
            
        Returns:
            Target position (0.0-1.0)
        """
        pass
    
    @abstractmethod
    def get_damping_factor(self, state: ResourceState) -> float:
        """
        Get damping factor for oscillation suppression.
        
        Args:
            state: Current state
            
        Returns:
            Damping factor (0.0-1.0)
        """
        pass


class QuantumController:
    """
    Universal quantum controller.
    
    Applies physics-based control to any resource.
    """
    
    def __init__(self,
                 resource: Resource,
                 physics_model: PhysicsModel,
                 history_window: int = 60,
                 poll_interval: float = 1.0):
        """
        Initialize controller.
        
        Args:
            resource: Resource to control
            physics_model: Physics model to use
            history_window: How many states to track
            poll_interval: Seconds between control cycles
        """
        self.resource = resource
        self.physics = physics_model
        self.history_window = history_window
        self.poll_interval = poll_interval
        
        # State tracking
        self.history: deque[ResourceState] = deque(maxlen=history_window)
        self.previous_size: Optional[int] = None
        
        # Statistics
        self.total_cycles = 0
        self.total_adjustments = 0
        self.running = False
    
    def start(self):
        """Start the control loop."""
        print("="*70)
        print("🧊⚛️ QUANTUM CONTROLLER - STARTING")
        print("="*70)
        print()
        print(f"Resource: {self.resource.__class__.__name__}")
        print(f"Physics: {self.physics.__class__.__name__}")
        print(f"Poll interval: {self.poll_interval}s")
        print()
        
        self.running = True
        
        try:
            while self.running:
                self._control_cycle()
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            print("\n\n⚠️  Shutting down...")
            self.stop()
    
    def _control_cycle(self):
        """Execute one control cycle."""
        # 1. Measure current state
        state = self.resource.measure_state()
        self.history.append(state)
        self.total_cycles += 1
        
        # 2. Calculate control force
        force = self.physics.calculate_force(state, self.history)
        
        # 3. Calculate ground state
        ground_state = self.physics.calculate_ground_state(self.history)
        
        # 4. Determine action
        deviation = abs(state.position - ground_state)
        
        if force > 0.5 or deviation > 0.15:
            # Need to adjust
            new_size = self._calculate_new_size(state, force)
            
            # Apply damping
            damping = self.physics.get_damping_factor(state)
            if self.previous_size is not None:
                delta = new_size - self.previous_size
                damped_delta = int(delta * damping)
                new_size = self.previous_size + damped_delta
            
            # Apply limits
            min_size, max_size = self.resource.get_limits()
            new_size = max(min_size, min(new_size, max_size))
            
            # Apply control
            if new_size != self.previous_size:
                success = self.resource.apply_control(new_size)
                if success:
                    self.total_adjustments += 1
                    print(f"[{time.strftime('%H:%M:%S')}] Adjusted: {self.previous_size} → {new_size}")
            
            self.previous_size = new_size
        else:
            # Ground state, no action needed
            pass
    
    def _calculate_new_size(self, state: ResourceState, force: float) -> int:
        """Calculate new size based on force."""
        # Get current size from metadata
        current_size = state.metadata.get('current_size', 1000)
        
        # Expansion factor based on force
        expansion_factor = 1.0 + (force * 1.5)
        
        new_size = int(current_size * expansion_factor)
        return new_size
    
    def stop(self):
        """Stop the controller."""
        self.running = False
        
        print()
        print("="*70)
        print("📊 QUANTUM CONTROLLER - STATS")
        print("="*70)
        print()
        print(f"Total cycles: {self.total_cycles}")
        print(f"Total adjustments: {self.total_adjustments}")
        print(f"Adjustment rate: {self.total_adjustments / max(self.total_cycles, 1) * 100:.1f}%")
        print()
        print("Controller stopped.")
        print()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get controller statistics."""
        return {
            'total_cycles': self.total_cycles,
            'total_adjustments': self.total_adjustments,
            'running': self.running
        }
