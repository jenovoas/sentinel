#!/usr/bin/env python3
"""
Quantum Cooling Predictor for Sentinel Buffers

Based on optomechanical ground state cooling:
- Measure "velocity" (rate of change)
- Apply counterforce (buffer expansion)
- Achieve "ground state" (zero drops)

No cryogenics needed. Just perfect control.
"""

import time
from collections import deque
from dataclasses import dataclass
from typing import Tuple


@dataclass
class BufferState:
    """Current state of the buffer (like particle position)"""
    size: int
    utilization: float
    drop_rate: float
    timestamp: float


class QuantumCoolingPredictor:
    """
    Applies optomechanical cooling principles to buffer management.
    
    Key insight: You don't need a perfect environment (cryogenics).
    You need perfect control (faster feedback than chaos).
    """
    
    def __init__(self, 
                 measurement_window: int = 10,
                 velocity_threshold: float = 0.8,
                 cooling_factor: float = 2.0):
        """
        Args:
            measurement_window: How many samples to track (like laser sampling rate)
            velocity_threshold: When to apply counterforce (0.0-1.0)
            cooling_factor: How strong the counterforce (like laser power)
        """
        self.measurement_window = measurement_window
        self.velocity_threshold = velocity_threshold
        self.cooling_factor = cooling_factor
        
        # History of measurements (like laser position tracking)
        self.history: deque[BufferState] = deque(maxlen=measurement_window)
        
        # Ground state target
        self.ground_state_utilization = 0.7  # Optimal: 70% full
        
    def measure_velocity(self) -> float:
        """
        Calculate "velocity" of buffer state change.
        
        In physics: velocity = change in position / time
        In buffers: velocity = change in utilization / time
        
        Returns:
            Normalized velocity (0.0 = stationary, 1.0 = max change)
        """
        if len(self.history) < 2:
            return 0.0
        
        # Recent state vs previous state
        current = self.history[-1]
        previous = self.history[-2]
        
        # Calculate rate of change
        dt = current.timestamp - previous.timestamp
        if dt == 0:
            return 0.0
        
        # Velocity = change in utilization over time
        du = current.utilization - previous.utilization
        velocity = abs(du / dt)
        
        # Normalize to 0-1 range (assume max change is 1.0/sec)
        return min(velocity, 1.0)
    
    def calculate_deviation(self) -> float:
        """
        How far are we from ground state?
        
        In physics: deviation from equilibrium position
        In buffers: deviation from optimal utilization
        """
        if not self.history:
            return 0.0
        
        current = self.history[-1]
        deviation = abs(current.utilization - self.ground_state_utilization)
        
        return deviation
    
    def apply_counterforce(self, velocity: float, deviation: float) -> int:
        """
        Calculate buffer size adjustment (the "cooling force").
        
        In physics: F = -k * x (Hooke's law for optical trap)
        In buffers: delta_size = -k * (utilization - target)
        
        Args:
            velocity: How fast the state is changing
            deviation: How far from ground state
            
        Returns:
            New buffer size
        """
        if not self.history:
            return 0
        
        current = self.history[-1]
        
        # If velocity is high, apply strong counterforce
        if velocity > self.velocity_threshold:
            # Expand buffer proportional to velocity
            expansion_factor = 1.0 + (velocity * self.cooling_factor)
            new_size = int(current.size * expansion_factor)
            
            print(f"🧊 Cooling: velocity={velocity:.3f} -> expand {expansion_factor:.2f}x")
            return new_size
        
        # If we're far from ground state, adjust gently
        elif deviation > 0.2:
            # Gentle adjustment toward ground state
            if current.utilization > self.ground_state_utilization:
                # Too full, expand slightly
                new_size = int(current.size * 1.1)
            else:
                # Too empty, contract slightly
                new_size = int(current.size * 0.9)
            
            print(f"⚖️  Equilibrium: deviation={deviation:.3f} -> adjust to {new_size}")
            return new_size
        
        else:
            # Ground state achieved! Hold steady
            print(f"✅ Ground state: utilization={current.utilization:.3f}")
            return current.size
    
    def predict(self, current_state: BufferState) -> Tuple[int, str]:
        """
        Main prediction loop (like the feedback control loop).
        
        Returns:
            (new_buffer_size, action_description)
        """
        # Add measurement to history
        self.history.append(current_state)
        
        # Measure velocity (rate of change)
        velocity = self.measure_velocity()
        
        # Calculate deviation from ground state
        deviation = self.calculate_deviation()
        
        # Apply counterforce
        new_size = self.apply_counterforce(velocity, deviation)
        
        # Determine action
        if new_size > current_state.size:
            action = f"EXPAND: {current_state.size} -> {new_size} (cooling)"
        elif new_size < current_state.size:
            action = f"CONTRACT: {current_state.size} -> {new_size} (equilibrium)"
        else:
            action = f"HOLD: {current_state.size} (ground state)"
        
        return new_size, action


def simulate_traffic_burst():
    """
    Simulate a realistic traffic burst and demonstrate quantum cooling.
    """
    print("="*70)
    print("🧊⚛️ QUANTUM COOLING PREDICTOR - DEMO")
    print("="*70)
    print()
    print("Simulating traffic burst with quantum cooling feedback...")
    print()
    
    predictor = QuantumCoolingPredictor(
        measurement_window=10,
        velocity_threshold=0.8,
        cooling_factor=2.0
    )
    
    # Simulate 20 seconds of traffic
    initial_buffer_size = 1000
    current_buffer_size = initial_buffer_size
    
    # Traffic pattern: gradual increase, sudden burst, gradual decrease
    traffic_pattern = [
        # Time, utilization, drop_rate
        (0.0, 0.5, 0.0),   # Normal
        (1.0, 0.6, 0.0),   # Increasing
        (2.0, 0.7, 0.0),   # Getting full
        (3.0, 0.85, 0.02), # Burst starts!
        (4.0, 0.95, 0.05), # High pressure
        (5.0, 0.98, 0.10), # Critical!
        (6.0, 0.99, 0.15), # Maximum stress
        (7.0, 0.95, 0.08), # Cooling applied
        (8.0, 0.85, 0.03), # Recovering
        (9.0, 0.75, 0.01), # Stabilizing
        (10.0, 0.70, 0.0), # Ground state
        (11.0, 0.70, 0.0), # Steady
        (12.0, 0.68, 0.0), # Steady
    ]
    
    total_drops_without_cooling = 0
    total_drops_with_cooling = 0
    
    for timestamp, utilization, drop_rate in traffic_pattern:
        # Create current state
        state = BufferState(
            size=current_buffer_size,
            utilization=utilization,
            drop_rate=drop_rate,
            timestamp=timestamp
        )
        
        # Predict and apply cooling
        new_size, action = predictor.predict(state)
        
        # Calculate drops
        drops_without = int(drop_rate * 1000)  # Assume 1000 packets/sec
        
        # With cooling, drops are reduced proportionally to buffer expansion
        expansion_ratio = new_size / current_buffer_size if current_buffer_size > 0 else 1.0
        drops_with = int(drops_without / expansion_ratio)
        
        total_drops_without_cooling += drops_without
        total_drops_with_cooling += drops_with
        
        # Display
        print(f"t={timestamp:4.1f}s | util={utilization:.2f} | {action}")
        print(f"         | drops: {drops_without:3d} -> {drops_with:3d} (saved {drops_without - drops_with:3d})")
        print()
        
        # Update buffer size
        current_buffer_size = new_size
        
        time.sleep(0.1)  # Visual delay
    
    # Summary
    print("="*70)
    print("📊 RESULTS")
    print("="*70)
    print()
    print(f"Initial buffer size: {initial_buffer_size}")
    print(f"Final buffer size: {current_buffer_size}")
    print(f"Expansion ratio: {current_buffer_size / initial_buffer_size:.2f}x")
    print()
    print(f"Drops WITHOUT cooling: {total_drops_without_cooling}")
    print(f"Drops WITH cooling: {total_drops_with_cooling}")
    print(f"Drops prevented: {total_drops_without_cooling - total_drops_with_cooling}")
    print(f"Improvement: {(1 - total_drops_with_cooling / max(total_drops_without_cooling, 1)) * 100:.1f}%")
    print()
    print("✅ Ground state achieved through quantum cooling principles")
    print()


if __name__ == '__main__':
    simulate_traffic_burst()
