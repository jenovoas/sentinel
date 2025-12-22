#!/usr/bin/env python3
"""
Optomechanical Cooling Physics Model

Implements active feedback cooling based on optomechanical levitation.
"""

import math
from collections import deque
from quantum_control.core import PhysicsModel, ResourceState


class OptomechanicalCooling(PhysicsModel):
    """
    Optomechanical cooling model.
    
    Based on:
    - Ground state cooling of levitated nanoparticles
    - Active feedback damping
    - Quadratic force law (v²)
    """
    
    def __init__(self,
                 velocity_threshold: float = 0.8,
                 acceleration_threshold: float = 0.3,
                 cooling_factor: float = 1.5,
                 base_damping: float = 0.8):
        """
        Initialize optomechanical model.
        
        Args:
            velocity_threshold: When to apply strong force
            acceleration_threshold: When to apply predictive force
            cooling_factor: Force multiplier
            base_damping: Base damping factor
        """
        self.velocity_threshold = velocity_threshold
        self.acceleration_threshold = acceleration_threshold
        self.cooling_factor = cooling_factor
        self.base_damping = base_damping
    
    def calculate_force(self, 
                       state: ResourceState,
                       history: deque[ResourceState]) -> float:
        """
        Calculate cooling force using quadratic law.
        
        F = v² × (1 + a)
        
        This responds to kinetic energy, not just velocity.
        """
        velocity = abs(state.velocity)
        acceleration = abs(state.acceleration)
        
        # Quadratic force law
        force = (velocity ** 2) * (1 + acceleration)
        
        # Normalize to 0-1
        return min(force, 1.0)
    
    def calculate_ground_state(self, history: deque[ResourceState]) -> float:
        """
        Calculate dynamic ground state based on thermal noise.
        
        Ground state = noise floor × 1.2
        """
        if len(history) < 10:
            return 0.7  # Default
        
        # Calculate noise floor (variance in position)
        positions = [s.position for s in history]
        mean = sum(positions) / len(positions)
        variance = sum((p - mean) ** 2 for p in positions) / len(positions)
        noise_floor = math.sqrt(variance)
        
        # Ground state = noise + 20% margin
        ground_state = noise_floor * 1.2
        
        # Clamp to reasonable range
        return max(0.5, min(ground_state, 0.8))
    
    def get_damping_factor(self, state: ResourceState) -> float:
        """
        Adaptive damping based on excitation level.
        
        High excitation → low damping (fast response)
        Low excitation → high damping (smooth)
        """
        excitation = abs(state.velocity) + abs(state.acceleration)
        
        if excitation > 1.0:
            return 0.5  # Low damping, aggressive
        elif excitation > 0.5:
            return 0.7  # Medium
        else:
            return 0.9  # High damping, conservative
