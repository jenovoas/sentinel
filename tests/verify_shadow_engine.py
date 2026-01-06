# tests/verify_shadow_engine.py
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import sys
import os

# Adjust path to find src module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.sentinel_core.brain.shadow_reality_engine import prophet

def test_shadow_prediction():
    print("🔮 [Test] Initializing Shadow Reality Engine...")
    
    # Scenario 1: Stable System (Score 10 - Harmonic 10)
    print("🌌 [Test] Predicting future for Stable State (Score 10.0)...")
    prediction = prophet.predict_future(10.0)
    
    print(f"   -> Prediction: Threat {prediction['predicted_threat']:.2f}")
    print(f"   -> Trend: {prediction['trend']}")
    print(f"   -> Confidence: {prediction['confidence']:.2f}")
    
    # Scenario 2: Chaos System (Score 47 - Prime/Dissonant)
    print("\n🌪️ [Test] Predicting future for Chaos State (Score 47.0)...")
    prediction_chaos = prophet.predict_future(47.0)
    
    print(f"   -> Prediction: Threat {prediction_chaos['predicted_threat']:.2f}")
    print(f"   -> Trend: {prediction_chaos['trend']}")
    
    if prediction_chaos['predicted_threat'] > 47.0:
        print("✅ [Test] Chaos correctly predicted escalation.")
    else:
        print("⚠️ [Test] Chaos projection was stable (unexpected).")

if __name__ == "__main__":
    test_shadow_prediction()
