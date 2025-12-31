# tests/verify_resonance_mode.py
import sys
import os
import time

# Adjust path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.sentinel_core.brain.bci_controller import bci_controller

def test_resonance_qualia():
    print("🌌 [Test] Initializing Phase 4 Resonance Verification...")
    
    # 1. Test Synaptic Spike (SNN Reaction)
    print("\n⚡ [Test] Triggering SYNAPTIC_SPIKE (SNN Reflex)...")
    bci_controller.trigger_qualia("SYNAPTIC_SPIKE")
    time.sleep(1)
    
    # 2. Test The Resonance (Day 4 Event)
    print("\n🎸 [Test] Triggering RESONANCE_EVENT (153.4 MHz Harmonic)...")
    bci_controller.trigger_qualia("RESONANCE_EVENT")
    
    # Wait for the long sustain sequence (3 tones * 0.5 sleep + duration)
    # The BCI controller logic uses threads, so we wait a bit to see print output
    time.sleep(3)
    
    print("\n✅ [Test] Verification Complete. If you saw the Qualia logs, the logic is sound.")

if __name__ == "__main__":
    test_resonance_qualia()
