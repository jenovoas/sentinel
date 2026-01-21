#!/usr/bin/env python3
"""
Quantum Cooling V3 - Advanced Algorithms

Based on validated physics, now we add:
1. Runaway detection (exponential growth)
2. Pattern learning (periodic bursts)
3. Adaptive damping (context-aware)
4. Multi-dimensional optimization
"""

import time
from collections import deque
from dataclasses import dataclass
from typing import Tuple, Optional, List
import math


@dataclass
class BufferState:
    """Current state of the buffer"""
    size: int
    utilization: float
    drop_rate: float
    timestamp: float


class QuantumCoolingV3:
    """
    Advanced quantum cooling with:
    - Runaway detection
    - Pattern learning
    - Adaptive damping
    - Multi-dimensional control
    """
    
    def __init__(self,
                 history_window: int = 60,
                 velocity_window: int = 5,
                 acceleration_threshold: float = 0.3,
                 base_damping: float = 0.8):
        
        self.history_window = history_window
        self.velocity_window = velocity_window
        self.acceleration_threshold = acceleration_threshold
        self.base_damping = base_damping
        
        # History tracking
        self.long_history: deque[BufferState] = deque(maxlen=history_window)
        self.short_history: deque[BufferState] = deque(maxlen=velocity_window)
        self.velocity_history: deque[float] = deque(maxlen=20)
        self.acceleration_history: deque[float] = deque(maxlen=10)
        
        # Pattern learning
        self.burst_timestamps: List[float] = []
        self.detected_period: Optional[float] = None
        
        # Adaptive state
        self.current_damping = base_damping
        self.previous_size = None
        self.runaway_mode = False
        
    # ========================================================================
    # CORE PHYSICS (from V2)
    # ========================================================================
    
    def calculate_noise_floor(self) -> float:
        """Calculate thermal noise floor."""
        if len(self.long_history) < 10:
            return 0.1
        
        utilizations = [s.utilization for s in self.long_history]
        mean = sum(utilizations) / len(utilizations)
        variance = sum((u - mean) ** 2 for u in utilizations) / len(utilizations)
        noise_floor = math.sqrt(variance)
        
        return max(noise_floor, 0.05)
    
    def measure_velocity(self) -> float:
        """Measure instantaneous velocity."""
        if len(self.short_history) < 2:
            return 0.0
        
        current = self.short_history[-1]
        previous = self.short_history[-2]
        
        dt = current.timestamp - previous.timestamp
        if dt == 0:
            return 0.0
        
        du = current.utilization - previous.utilization
        return du / dt
    
    def measure_acceleration(self) -> float:
        """Measure acceleration (change in velocity)."""
        if len(self.velocity_history) < 2:
            return 0.0
        
        current_v = self.velocity_history[-1]
        previous_v = self.velocity_history[-2]
        
        return current_v - previous_v
    
    def calculate_dynamic_ground_state(self) -> float:
        """Dynamic ground state based on thermal noise."""
        noise_floor = self.calculate_noise_floor()
        ground_state = noise_floor * 1.2
        return max(0.5, min(ground_state, 0.8))
    
    def calculate_force(self, velocity: float, acceleration: float) -> float:
        """Quadratic force law: F = v² × (1 + a)"""
        return (velocity ** 2) * (1 + abs(acceleration))
    
    # ========================================================================
    # ALGORITHM 1: RUNAWAY DETECTION
    # ========================================================================
    
    def detect_runaway(self) -> bool:
        """
        Detect exponential growth (cascading failure).
        
        Runaway condition:
        - Acceleration > 0.5 (very high)
        - Velocity > 0.8 (very fast)
        - Sustained for 3+ cycles
        
        Physics: Like thermal runaway in semiconductors.
        """
        if len(self.acceleration_history) < 3:
            return False
        
        # Check last 3 accelerations
        recent_accel = list(self.acceleration_history)[-3:]
        
        # All positive and high?
        if all(a > 0.5 for a in recent_accel):
            # Check velocity too
            if len(self.velocity_history) > 0:
                current_v = self.velocity_history[-1]
                if current_v > 0.8:
                    return True
        
        return False
    
    def apply_emergency_cooling(self, current_size: int) -> int:
        """
        Emergency response to runaway.
        
        Physics: Like emergency quenching in superconductors.
        Expand buffer 5x immediately to prevent collapse.
        """
        emergency_size = int(current_size * 5.0)
        print(f"🚨 RUNAWAY DETECTED! Emergency expansion: {current_size} → {emergency_size}")
        return emergency_size
    
    # ========================================================================
    # ALGORITHM 2: PATTERN LEARNING
    # ========================================================================
    
    def detect_burst(self, velocity: float, threshold: float = 0.3) -> bool:
        """Detect if current state is a burst."""
        return velocity > threshold
    
    def learn_pattern(self, timestamp: float):
        """
        Learn periodic patterns in bursts.
        
        If bursts occur at regular intervals, we can predict them.
        
        Physics: Like detecting resonance frequency in oscillators.
        """
        # Record burst timestamp
        self.burst_timestamps.append(timestamp)
        
        # Keep only recent bursts (last 10)
        if len(self.burst_timestamps) > 10:
            self.burst_timestamps.pop(0)
        
        # Need at least 3 bursts to detect pattern
        if len(self.burst_timestamps) < 3:
            return
        
        # Calculate intervals between bursts
        intervals = []
        for i in range(1, len(self.burst_timestamps)):
            interval = self.burst_timestamps[i] - self.burst_timestamps[i-1]
            intervals.append(interval)
        
        # Check if intervals are similar (periodic)
        if len(intervals) >= 2:
            mean_interval = sum(intervals) / len(intervals)
            variance = sum((i - mean_interval) ** 2 for i in intervals) / len(intervals)
            std_dev = math.sqrt(variance)
            
            # If std dev < 20% of mean, it's periodic
            if std_dev < mean_interval * 0.2:
                self.detected_period = mean_interval
                print(f"📊 Pattern detected! Period: {mean_interval:.1f}s")
    
    def predict_next_burst(self, current_time: float) -> Optional[float]:
        """
        Predict when next burst will occur.
        
        Returns seconds until next burst, or None if no pattern.
        """
        if not self.detected_period or not self.burst_timestamps:
            return None
        
        last_burst = self.burst_timestamps[-1]
        time_since_last = current_time - last_burst
        
        # Time until next predicted burst
        time_until_next = self.detected_period - time_since_last
        
        return time_until_next if time_until_next > 0 else 0
    
    def apply_preemptive_expansion(self, current_size: int) -> int:
        """
        Expand buffer BEFORE predicted burst.
        
        Physics: Like pre-cooling before laser pulse.
        """
        preemptive_size = int(current_size * 1.5)
        print(f"🔮 Preemptive expansion: {current_size} → {preemptive_size}")
        return preemptive_size
    
    # ========================================================================
    # ALGORITHM 3: ADAPTIVE DAMPING
    # ========================================================================
    
    def calculate_adaptive_damping(self, velocity: float, acceleration: float) -> float:
        """
        Adjust damping based on system state.
        
        High velocity + high accel → low damping (aggressive)
        Low velocity + low accel → high damping (conservative)
        
        Physics: Like adaptive optics in telescopes.
        """
        # Calculate "excitation level"
        excitation = abs(velocity) + abs(acceleration)
        
        if excitation > 1.0:
            # High excitation → low damping (fast response)
            return 0.5
        elif excitation > 0.5:
            # Medium excitation → medium damping
            return 0.7
        else:
            # Low excitation → high damping (smooth)
            return 0.9
    
    # ========================================================================
    # MAIN PREDICTION LOOP
    # ========================================================================
    
    def predict(self, current_state: BufferState) -> Tuple[int, str]:
        """
        Advanced prediction with all algorithms.
        """
        # Add to histories
        self.long_history.append(current_state)
        self.short_history.append(current_state)
        
        # Measure dynamics
        velocity = self.measure_velocity()
        self.velocity_history.append(velocity)
        
        acceleration = self.measure_acceleration()
        self.acceleration_history.append(acceleration)
        
        # Calculate ground state
        ground_state = self.calculate_dynamic_ground_state()
        thermal_noise = self.calculate_noise_floor()
        deviation = abs(current_state.utilization - ground_state)
        
        # ALGORITHM 1: Check for runaway
        if self.detect_runaway():
            self.runaway_mode = True
            new_size = self.apply_emergency_cooling(current_state.size)
            action = "EMERGENCY COOLING (runaway detected)"
            self.previous_size = new_size
            return new_size, action
        
        # ALGORITHM 2: Pattern learning
        if self.detect_burst(velocity):
            self.learn_pattern(current_state.timestamp)
        
        # Check if burst is predicted soon
        time_until_burst = self.predict_next_burst(current_state.timestamp)
        if time_until_burst is not None and time_until_burst < 2.0:
            # Burst predicted in next 2 seconds
            new_size = self.apply_preemptive_expansion(current_state.size)
            action = f"PREEMPTIVE (burst in {time_until_burst:.1f}s)"
            self.previous_size = new_size
            return new_size, action
        
        # ALGORITHM 3: Adaptive damping
        self.current_damping = self.calculate_adaptive_damping(velocity, acceleration)
        
        # Standard quantum cooling logic
        if velocity > ground_state or acceleration > self.acceleration_threshold:
            # High velocity or acceleration → cool
            force = self.calculate_force(velocity, acceleration)
            expansion_factor = 1.0 + (force * 1.5)
            new_size = int(current_state.size * expansion_factor)
            action = f"COOL: v={velocity:.3f} a={acceleration:.3f} damp={self.current_damping:.2f}"
            
        elif deviation > 0.15:
            # Adjust toward ground state
            if current_state.utilization > ground_state:
                new_size = int(current_state.size * 1.1)
            else:
                new_size = int(current_state.size * 0.95)
            action = f"ADJUST: dev={deviation:.3f}"
            
        else:
            # Ground state
            new_size = current_state.size
            action = f"GROUND STATE: noise={thermal_noise:.3f}"
        
        # Apply adaptive damping
        if self.previous_size is not None:
            delta = new_size - self.previous_size
            damped_delta = delta * self.current_damping
            new_size = int(self.previous_size + damped_delta)
        
        self.previous_size = new_size
        
        return new_size, action


# ============================================================================
# DEMO: Test V3 with advanced scenarios
# ============================================================================

def demo_v3():
    """Test V3 with runaway and periodic patterns."""
    print("="*70)
    print("🧊⚛️ QUANTUM COOLING V3 - ADVANCED ALGORITHMS")
    print("="*70)
    print()
    print("Features:")
    print("  ✅ Runaway detection (exponential growth)")
    print("  ✅ Pattern learning (periodic bursts)")
    print("  ✅ Adaptive damping (context-aware)")
    print("  ✅ Preemptive expansion (prediction)")
    print()
    
    predictor = QuantumCoolingV3()
    
    # Scenario: Periodic bursts with one runaway
    pattern = [
        (0.0, 0.50, 0.00),
        (1.0, 0.55, 0.00),
        (2.0, 0.80, 0.05),  # Burst 1
        (3.0, 0.60, 0.01),
        (4.0, 0.85, 0.08),  # Burst 2 (periodic)
        (5.0, 0.65, 0.02),
        (6.0, 0.90, 0.12),  # Burst 3 (periodic)
        (7.0, 0.70, 0.03),
        (8.0, 0.95, 0.15),  # Burst 4 (should predict next)
        (9.0, 0.85, 0.08),
        (10.0, 0.95, 0.18), # Runaway starts
        (11.0, 0.98, 0.25), # Runaway continues
        (12.0, 0.99, 0.30), # Runaway critical
        (13.0, 0.80, 0.05), # Recovery
        (14.0, 0.60, 0.00),
    ]
    
    current_size = 1000
    
    for timestamp, utilization, drop_rate in pattern:
        state = BufferState(
            size=current_size,
            utilization=utilization,
            drop_rate=drop_rate,
            timestamp=timestamp
        )
        
        new_size, action = predictor.predict(state)
        
        print(f"t={timestamp:4.1f}s | util={utilization:.2f} | {action}")
        if new_size != current_size:
            print(f"         | {current_size} → {new_size}")
        print()
        
        current_size = new_size
        time.sleep(0.1)
    
    print("="*70)
    print("✅ V3 Demo Complete")
    print("="*70)


if __name__ == '__main__':
    demo_v3()
