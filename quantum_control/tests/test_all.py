#!/usr/bin/env python3
"""
Quantum Control Framework - Test Suite

Comprehensive tests for all components.
"""

import sys
sys.path.insert(0, '/home/jnovoas/sentinel')

import unittest
from quantum_control.core import QuantumController, ResourceState
from quantum_control.physics import OptomechanicalCooling
from quantum_control.resources import BufferResource, ThreadPoolResource, MemoryResource


class TestOptomechanicalCooling(unittest.TestCase):
    """Test optomechanical cooling physics model."""
    
    def setUp(self):
        self.physics = OptomechanicalCooling()
    
    def test_force_calculation(self):
        """Test quadratic force law."""
        state = ResourceState(
            position=0.8,
            velocity=0.5,
            acceleration=0.3,
            timestamp=0.0,
            metadata={}
        )
        
        force = self.physics.calculate_force(state, [])
        
        # F = v² × (1 + a) = 0.5² × (1 + 0.3) = 0.25 × 1.3 = 0.325
        self.assertAlmostEqual(force, 0.325, places=3)
    
    def test_ground_state_calculation(self):
        """Test dynamic ground state."""
        # Create history with known variance
        history = [
            ResourceState(0.5, 0.0, 0.0, i, {}) for i in range(10)
        ]
        
        ground_state = self.physics.calculate_ground_state(history)
        
        # Should be close to 0.5 (no variance)
        self.assertGreater(ground_state, 0.4)
        self.assertLess(ground_state, 0.9)
    
    def test_adaptive_damping(self):
        """Test adaptive damping factor."""
        # High excitation
        high_state = ResourceState(0.9, 1.0, 0.5, 0.0, {})
        high_damping = self.physics.get_damping_factor(high_state)
        self.assertEqual(high_damping, 0.5)  # Low damping for high excitation
        
        # Low excitation
        low_state = ResourceState(0.5, 0.1, 0.0, 0.0, {})
        low_damping = self.physics.get_damping_factor(low_state)
        self.assertEqual(low_damping, 0.9)  # High damping for low excitation


class TestBufferResource(unittest.TestCase):
    """Test buffer resource adapter."""
    
    def setUp(self):
        self.buffer = BufferResource(
            initial_size=1000,
            min_size=512,
            max_size=16384
        )
    
    def test_measure_state(self):
        """Test state measurement."""
        state = self.buffer.measure_state()
        
        self.assertIsInstance(state, ResourceState)
        self.assertGreaterEqual(state.position, 0.0)
        self.assertLessEqual(state.position, 1.0)
        self.assertEqual(state.metadata['current_size'], 1000)
    
    def test_apply_control(self):
        """Test buffer resize."""
        # Valid resize
        success = self.buffer.apply_control(2000)
        self.assertTrue(success)
        self.assertEqual(self.buffer.current_size, 2000)
        
        # Invalid resize (too small)
        success = self.buffer.apply_control(100)
        self.assertFalse(success)
        
        # Invalid resize (too large)
        success = self.buffer.apply_control(20000)
        self.assertFalse(success)
    
    def test_get_limits(self):
        """Test limit retrieval."""
        min_size, max_size = self.buffer.get_limits()
        self.assertEqual(min_size, 512)
        self.assertEqual(max_size, 16384)


class TestThreadPoolResource(unittest.TestCase):
    """Test thread pool resource adapter."""
    
    def setUp(self):
        self.threads = ThreadPoolResource(
            initial_threads=10,
            min_threads=2,
            max_threads=1000
        )
    
    def test_measure_state(self):
        """Test state measurement."""
        state = self.threads.measure_state()
        
        self.assertIsInstance(state, ResourceState)
        self.assertEqual(state.metadata['current_threads'], 10)
    
    def test_apply_control(self):
        """Test thread pool resize."""
        success = self.threads.apply_control(50)
        self.assertTrue(success)
        self.assertEqual(self.threads.current_threads, 50)


class TestMemoryResource(unittest.TestCase):
    """Test memory resource adapter."""
    
    def setUp(self):
        self.memory = MemoryResource(
            initial_heap=1024,
            min_heap=256,
            max_heap=8192
        )
    
    def test_measure_state(self):
        """Test state measurement."""
        state = self.memory.measure_state()
        
        self.assertIsInstance(state, ResourceState)
        self.assertEqual(state.metadata['current_heap'], 1024)
    
    def test_apply_control(self):
        """Test heap resize."""
        success = self.memory.apply_control(2048)
        self.assertTrue(success)
        self.assertEqual(self.memory.current_heap, 2048)


class TestQuantumController(unittest.TestCase):
    """Test quantum controller."""
    
    def setUp(self):
        self.buffer = BufferResource()
        self.physics = OptomechanicalCooling()
        self.controller = QuantumController(
            resource=self.buffer,
            physics_model=self.physics,
            poll_interval=1.0
        )
    
    def test_initialization(self):
        """Test controller initialization."""
        self.assertEqual(self.controller.total_cycles, 0)
        self.assertEqual(self.controller.total_adjustments, 0)
        self.assertFalse(self.controller.running)
    
    def test_control_cycle(self):
        """Test single control cycle."""
        self.controller._control_cycle()
        
        self.assertEqual(self.controller.total_cycles, 1)
        self.assertEqual(len(self.controller.history), 1)
    
    def test_get_stats(self):
        """Test statistics retrieval."""
        stats = self.controller.get_stats()
        
        self.assertIn('total_cycles', stats)
        self.assertIn('total_adjustments', stats)
        self.assertIn('running', stats)


def run_tests():
    """Run all tests."""
    print("="*70)
    print("🧪 QUANTUM CONTROL FRAMEWORK - TEST SUITE")
    print("="*70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestOptomechanicalCooling))
    suite.addTests(loader.loadTestsFromTestCase(TestBufferResource))
    suite.addTests(loader.loadTestsFromTestCase(TestThreadPoolResource))
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryResource))
    suite.addTests(loader.loadTestsFromTestCase(TestQuantumController))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
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
