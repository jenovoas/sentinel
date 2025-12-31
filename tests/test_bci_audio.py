import sys
import os
import time

# Add sentinel_core to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/core')))

try:
    from sentinel_core.brain.bci_controller import bci_controller
    print("✅ BCI Controller imported successfully.")
    
    print("🔊 Testing Qualia: KERNEL_BLOCK...")
    bci_controller.trigger_qualia("KERNEL_BLOCK")
    time.sleep(2)
    
    print("🔊 Testing Base-60 Pattern (Residue 0)...")
    bci_controller.play_base60_pattern(0)
    time.sleep(1)
    
    print("🔊 Testing Qualia: SYSTEM_SECURE...")
    bci_controller.trigger_qualia("SYSTEM_SECURE")
    time.sleep(2)
    
    print("✅ BCI Audio Test Completed.")
    
except ImportError as e:
    print(f"❌ Failed to import BCI dependencies: {e}")
except Exception as e:
    print(f"❌ Error during BCI test: {e}")
