from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import sys
import os

# Ensure sentinel_core is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sentinel_core.brain.inference import SentinelBrain

def validate_brain():
    print("🧠 [Test] Initializing Real AI Brain...")
    brain = SentinelBrain()
    
    test_cases = [
        ("/usr/bin/htop", True, "Safe Utility"),
        ("/usr/bin/git", True, "Safe Dev Tool"),
        ("/tmp/exfil_data.sh", False, "Suspicious Exfiltration Script"),
        ("/var/tmp/rootkit_installer", False, "Malware"),
        ("/opt/sentinel/bin/guardian", True, "Sentinel Component")
    ]
    
    score = 0
    print("\n🔬 [Test] Running Semantic Analysis:")
    for binary, expected, desc in test_cases:
        print(f"   Analyzing '{binary}' ({desc})...")
        try:
            result = brain.analyze_threat(binary)
            verdict = "ALLOW" if result else "BLOCK"
            expected_verdict = "ALLOW" if expected else "BLOCK"
            
            if result == expected:
                print(f"   ✅ CORRECT: AI decided {verdict}")
                score += 1
            else:
                print(f"   ❌ FAILURE: AI decided {verdict} (Expected: {expected_verdict})")
        except Exception as e:
            print(f"   ⚠️ ERROR: {e}")
            
    print("-" * 40)
    print(f"🎯 Accuracy: {score}/{len(test_cases)}")
    
    if score == len(test_cases):
        print("🏆 AI Validation PASSED")
    else:
        print("⚠️  AI Validation FAILED (Review Prompts)")

if __name__ == "__main__":
    validate_brain()
