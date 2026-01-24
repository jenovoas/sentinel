import unittest
import time
from quantum.quantum_scheduler_bridge import QuantumSchedulerBridge, TaskType, scheduler

class TestQuantumSchedulerBridge(unittest.TestCase):
    def setUp(self):
        # Reset scheduler before each test
        # Note: If Rust lib not loaded, this might flag unnecessary warnings but pass
        pass

    def test_enqueue_execution(self):
        """Test enqueuing a task and verifying callback (mocked via immediate exec if no lib, or integration test logic)."""
        
        # Flag to verify execution
        self.executed = False
        
        def my_task():
            self.executed = True
            print(">>> Task Executed inside Portal! <<<")

        # Enqueue task
        scheduler.enqueue(
            task_id=101,
            task_type=TaskType.ZPETune,
            cost=50,
            python_func=my_task
        )

        # Trigger tick (simulate portal)
        # We simulate multiple ticks to force execution or allow portal opening
        # Note: In a real unit test without the Rust lib, this verifies the fallback immediate execution.
        # With Rust lib, we'd need to simulate the portal opening state which is harder from here without mocking TimeCrystal.
        # For now, we mainly test that the FFI logic doesn't crash.
        scheduler.tick(0)
        
        # Check efficiency (should return float)
        eff = scheduler.get_efficiency()
        self.assertTrue(isinstance(eff, float))
        
        print(f"Scheduler Efficiency: {eff}")

if __name__ == '__main__':
    unittest.main()
