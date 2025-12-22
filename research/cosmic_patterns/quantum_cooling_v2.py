#!/usr/bin/env python3
"""
Quantum Cooling Predictor V2 - Advanced Physics

Improvements over V1:
1. Acceleration tracking (not just velocity)
2. Dynamic ground state (adapts to thermal noise)
3. Quadratic force law (velocity²)
4. Oscillation damping (prevents overshoot)

Based on real optomechanical physics.
"""

import time
from collections import deque
from dataclasses import dataclass
from typing import Tuple
import math


@dataclass
class BufferState:
    """Current state of the buffer"""
    size: int
    utilization: float
    drop_rate: float
    timestamp: float


class QuantumCoolingPredictorV2:
    """
    Advanced quantum cooling with acceleration and damping.
    """
    
    def __init__(self, 
                 history_window: int = 60,
                 velocity_window: int = 5,
                 acceleration_threshold: float = 0.3,
                 damping_factor: float = 0.8):
        """
        Args:
            history_window: Long-term history for noise calculation
            velocity_window: Short-term window for velocity
            acceleration_threshold: When to apply strong force
            damping_factor: Oscillation damping (0.0-1.0)
        """
        self.history_window = history_window
        self.velocity_window = velocity_window
        self.acceleration_threshold = acceleration_threshold
        self.damping_factor = damping_factor
        
        # History tracking
        self.long_history: deque[BufferState] = deque(maxlen=history_window)
        self.short_history: deque[BufferState] = deque(maxlen=velocity_window)
        self.velocity_history: deque[float] = deque(maxlen=10)
        
        # Previous buffer size for damping
        self.previous_size = None
        
    def calculate_noise_floor(self) -> float:
        """
        Calculate thermal noise floor of the system.
        
        In physics: thermal noise = baseline random motion
        In buffers: baseline utilization variance
        """
        if len(self.long_history) < 10:
            return 0.1  # Default noise floor
        
        # Calculate variance in utilization
        utilizations = [s.utilization for s in self.long_history]
        mean = sum(utilizations) / len(utilizations)
        variance = sum((u - mean) ** 2 for u in utilizations) / len(utilizations)
        
        # Noise floor = standard deviation
        noise_floor = math.sqrt(variance)
        
        return max(noise_floor, 0.05)  # Minimum 5%
    
    def measure_velocity(self) -> float:
        """
        Measure instantaneous velocity (rate of change).
        
        Uses short window for quick response.
        """
        if len(self.short_history) < 2:
            return 0.0
        
        current = self.short_history[-1]
        previous = self.short_history[-2]
        
        dt = current.timestamp - previous.timestamp
        if dt == 0:
            return 0.0
        
        du = current.utilization - previous.utilization
        velocity = du / dt
        
        return velocity
    
    def measure_acceleration(self) -> float:
        """
        Measure acceleration (change in velocity).
        
        KEY INSIGHT: Acceleration predicts future bursts!
        If velocity is increasing, burst is getting worse.
        """
        if len(self.velocity_history) < 2:
            return 0.0
        
        current_velocity = self.velocity_history[-1]
        previous_velocity = self.velocity_history[-2]
        
        # Acceleration = change in velocity
        acceleration = current_velocity - previous_velocity
        
        return acceleration
    
    def calculate_dynamic_ground_state(self) -> float:
        """
        Dynamic ground state based on thermal noise.
        
        In physics: ground state depends on temperature
        In buffers: optimal utilization depends on noise
        """
        noise_floor = self.calculate_noise_floor()
        
        # Ground state = noise floor + 20% margin
        ground_state = noise_floor * 1.2
        
        # Clamp to reasonable range
        return max(0.5, min(ground_state, 0.8))
    
    def calculate_force(self, velocity: float, acceleration: float) -> float:
        """
        Calculate cooling force using quadratic law.
        
        F = v² × (1 + a)
        
        This is closer to real physics than linear force.
        """
        # Quadratic force law
        force = (velocity ** 2) * (1 + abs(acceleration))
        
        return force
    
    def dampen_oscillations(self, new_size: int) -> int:
        """
        Apply damping to prevent overshoot and oscillations.
        
        Critical damping: smooth convergence without oscillation.
        """
        if self.previous_size is None:
            return new_size
        
        # Calculate change
        delta = new_size - self.previous_size
        
        # Apply damping factor
        damped_delta = delta * self.damping_factor
        
        # New size with damping
        damped_size = int(self.previous_size + damped_delta)
        
        return damped_size
    
    def predict(self, current_state: BufferState) -> Tuple[int, str]:
        """
        Main prediction with advanced physics.
        """
        # Add to histories
        self.long_history.append(current_state)
        self.short_history.append(current_state)
        
        # Measure velocity
        velocity = self.measure_velocity()
        self.velocity_history.append(velocity)
        
        # Measure acceleration
        acceleration = self.measure_acceleration()
        
        # Calculate dynamic ground state
        ground_state = self.calculate_dynamic_ground_state()
        thermal_noise = self.calculate_noise_floor()
        
        # Current deviation
        deviation = abs(current_state.utilization - ground_state)
        
        # Decision logic
        if velocity > ground_state or acceleration > self.acceleration_threshold:
            # High velocity OR high acceleration → apply strong force
            force = self.calculate_force(velocity, acceleration)
            
            # Expansion with overcooling (1.5x force)
            expansion_factor = 1.0 + (force * 1.5)
            new_size = int(current_state.size * expansion_factor)
            
            # Apply damping
            new_size = self.dampen_oscillations(new_size)
            
            action = f"COOL: v={velocity:.3f} a={acceleration:.3f} → {new_size}"
            
        elif deviation > 0.15:
            # Gentle adjustment toward ground state
            if current_state.utilization > ground_state:
                new_size = int(current_state.size * 1.1)
            else:
                new_size = int(current_state.size * 0.95)
            
            # Apply damping
            new_size = self.dampen_oscillations(new_size)
            
            action = f"ADJUST: dev={deviation:.3f} → {new_size}"
            
        else:
            # Ground state achieved
            new_size = current_state.size
            action = f"GROUND STATE: noise={thermal_noise:.3f}"
        
        # Update previous size
        self.previous_size = new_size
        
        return new_size, action


def simulate_traffic_burst_v2():
    """
    Simulate with advanced quantum cooling.
    """
    print("="*70)
    print("🧊⚛️ QUANTUM COOLING PREDICTOR V2 - ADVANCED PHYSICS")
    print("="*70)
    print()
    print("Features:")
    print("  ✅ Acceleration tracking")
    print("  ✅ Dynamic ground state")
    print("  ✅ Quadratic force law (v²)")
    print("  ✅ Oscillation damping")
    print()
    
    predictor = QuantumCoolingPredictorV2(
        history_window=60,
        velocity_window=5,
        acceleration_threshold=0.3,
        damping_factor=0.8
    )
    
    initial_buffer_size = 1000
    current_buffer_size = initial_buffer_size
    
    # More realistic traffic pattern with acceleration
    traffic_pattern = [
        # Time, utilization, drop_rate
        (0.0, 0.5, 0.0),   # Normal
        (1.0, 0.52, 0.0),  # Slow increase
        (2.0, 0.55, 0.0),  # Slow increase
        (3.0, 0.60, 0.0),  # Accelerating
        (4.0, 0.70, 0.01), # Accelerating more!
        (5.0, 0.85, 0.03), # Burst!
        (6.0, 0.95, 0.08), # Peak acceleration
        (7.0, 0.98, 0.12), # Maximum
        (8.0, 0.99, 0.15), # Critical
        (9.0, 0.96, 0.10), # Decelerating
        (10.0, 0.90, 0.05), # Cooling
        (11.0, 0.80, 0.02), # Recovering
        (12.0, 0.70, 0.01), # Stabilizing
        (13.0, 0.60, 0.0),  # Ground state
        (14.0, 0.55, 0.0),  # Steady
        (15.0, 0.52, 0.0),  # Steady
    ]
    
    total_drops_without = 0
    total_drops_with = 0
    
    for timestamp, utilization, drop_rate in traffic_pattern:
        state = BufferState(
            size=current_buffer_size,
            utilization=utilization,
            drop_rate=drop_rate,
            timestamp=timestamp
        )
        
        new_size, action = predictor.predict(state)
        
        # Calculate drops
        drops_without = int(drop_rate * 1000)
        expansion_ratio = new_size / current_buffer_size if current_buffer_size > 0 else 1.0
        drops_with = int(drops_without / expansion_ratio)
        
        total_drops_without += drops_without
        total_drops_with += drops_with
        
        print(f"t={timestamp:4.1f}s | util={utilization:.2f} | {action}")
        print(f"         | drops: {drops_without:3d} → {drops_with:3d} (saved {drops_without - drops_with:3d})")
        print()
        
        current_buffer_size = new_size
        time.sleep(0.1)
    
    # Results
    print("="*70)
    print("📊 RESULTS")
    print("="*70)
    print()
    print(f"Initial buffer: {initial_buffer_size}")
    print(f"Final buffer: {current_buffer_size}")
    print(f"Peak buffer: {max(s.size for s in predictor.long_history)}")
    print(f"Expansion: {current_buffer_size / initial_buffer_size:.2f}x")
    print()
    print(f"Drops WITHOUT V2: {total_drops_without}")
    print(f"Drops WITH V2: {total_drops_with}")
    print(f"Improvement: {(1 - total_drops_with / max(total_drops_without, 1)) * 100:.1f}%")
    print()
    print("✅ Advanced quantum cooling with acceleration + damping")
    print()


if __name__ == '__main__':
    simulate_traffic_burst_v2()
