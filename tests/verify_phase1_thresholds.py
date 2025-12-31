import sys
import os
import time

# Add sentinel_core to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/core')))

from sentinel_core.brain.inference import SentinelBrain
from sentinel_core.brain.neural_thresholds import threshold_manager

def test_dynamic_thresholds():
    print("🚀 Testing Neural Threshold Optimization...")
    brain = SentinelBrain()
    
    # Test case: Mid-suspicious binary
    target_binary = "/tmp/maybe_malicious_tool"
    
    # 1. Harmonic Case (Residue 12 - Highly Composite)
    print("\n[SCENARIO 1] Harmonic Residue (12)")
    res_harmonic = 12
    result_harmonic = brain.analyze_threat(target_binary, residue=res_harmonic)
    print(f"-> Threshold: {result_harmonic['threshold']}")
    print(f"-> Decision: {result_harmonic['classification']} (Allow: {result_harmonic['allow']})")
    
    # 2. Dissonant Case (Residue 7 - Prime)
    print("\n[SCENARIO 2] Dissonant Residue (7)")
    res_prime = 7
    result_prime = brain.analyze_threat(target_binary, residue=res_prime)
    print(f"-> Threshold: {result_prime['threshold']}")
    print(f"-> Decision: {result_prime['classification']} (Allow: {result_prime['allow']})")
    
    print("\n✅ Phase 1 Verification Script Finished.")

if __name__ == "__main__":
    try:
        test_dynamic_thresholds()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
