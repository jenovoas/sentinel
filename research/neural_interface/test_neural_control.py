#!/usr/bin/env python3
"""
Neural Control - Test Suite

Validates neural entropy control algorithms.
"""

import sys
sys.path.insert(0, '/home/jnovoas/sentinel')

import unittest
from research.neural_interface.neural_control import (
    NeuralEntropyController,
    NeuralState
)


class TestNeuralEntropyController(unittest.TestCase):
    """Test neural entropy controller."""
    
    def setUp(self):
        self.controller = NeuralEntropyController()
    
    def test_initialization(self):
        """Test controller initialization."""
        self.assertEqual(self.controller.target_rate, 40.0)
        self.assertEqual(self.controller.min_rate, 10.0)
        self.assertEqual(self.controller.max_rate, 100.0)
        self.assertEqual(len(self.controller.history), 0)
    
    def test_measure_state(self):
        """Test state measurement."""
        state = self.controller.measure_state(50.0, 0.0)
        
        self.assertIsInstance(state, NeuralState)
        self.assertGreaterEqual(state.spike_rate, 0.0)
        self.assertLessEqual(state.spike_rate, 1.0)
        self.assertEqual(state.spike_velocity, 0.0)  # First measurement
    
    def test_quadratic_force_law(self):
        """Test quadratic force calculation."""
        # Create state with known velocity
        state = NeuralState(
            spike_rate=0.8,
            spike_velocity=0.5,
            spike_acceleration=0.3,
            entropy=0.6,
            timestamp=0.0
        )
        
        force = self.controller.calculate_force(state)
        
        # F = v² × (1 + a) × cooling_factor
        # F = 0.5² × (1 + 0.3) × 1.5
        # F = 0.25 × 1.3 × 1.5 = 0.4875
        expected = 0.25 * 1.3 * 1.5
        self.assertAlmostEqual(force, expected, places=3)
    
    def test_ground_state_adaptation(self):
        """Test dynamic ground state."""
        # Add history with known entropy
        for i in range(20):
            state = NeuralState(
                spike_rate=0.5,
                spike_velocity=0.0,
                spike_acceleration=0.0,
                entropy=0.3 + (i % 5) * 0.01,  # Small variance
                timestamp=float(i)
            )
            self.controller.history.append(state)
        
        ground = self.controller.calculate_ground_state()
        
        # Should be close to mean entropy
        self.assertGreaterEqual(ground, 0.1)
        self.assertLess(ground, 0.5)
    
    def test_adaptive_damping(self):
        """Test adaptive damping factor."""
        # High excitation
        high_state = NeuralState(0.9, 0.5, 0.3, 0.9, 0.0)
        high_damping = self.controller.get_damping_factor(high_state)
        self.assertEqual(high_damping, 0.5)
        
        # Low excitation
        low_state = NeuralState(0.5, 0.1, 0.0, 0.3, 0.0)
        low_damping = self.controller.get_damping_factor(low_state)
        self.assertEqual(low_damping, 0.9)
    
    def test_control_convergence(self):
        """Test that control converges to ground state."""
        spike_rate = 80.0  # Start high
        
        for t in range(50):
            intensity, action = self.controller.update(spike_rate, float(t))
            
            # Apply control effect
            if action == "cool":
                spike_rate -= abs(intensity) * 5.0
            elif action == "heat":
                spike_rate += abs(intensity) * 5.0
            
            spike_rate = max(10.0, min(100.0, spike_rate))
        
        # After 50 steps, should be near target
        final_state = self.controller.history[-1]
        self.assertLess(final_state.entropy, 0.3)  # Low entropy = converged


def run_tests():
    """Run all tests."""
    print("="*70)
    print("🧪 NEURAL CONTROL - TEST SUITE")
    print("="*70)
    print()
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestNeuralEntropyController)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("="*70)
    print("📊 TEST RESULTS")
    print("="*70)
    print()
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    
    print()
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
