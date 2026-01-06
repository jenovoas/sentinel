# src/core/sentinel_core/brain/neural_thresholds.py
"""
Sentinel Cortex™ - Neural Threshold Manager
Handles dynamic sensitivity thresholds based on Base-60 resonance.
"""

class ThresholdManager:
    """
    Manages dynamic decision thresholds.
    Implements the 'Harmonic Guardrail' logic:
    - Harmonic Residues (Composite): High threshold (More permissive).
    - Dissonant Residues (Prime): Low threshold (More restrictive/alert).
    """
    
    PRIMES_60 = [1, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59]
    HIGHLY_COMPOSITE_60 = [6, 12, 24, 30, 36, 48, 60] # Simplified set for resonance

    def __init__(self, base_threshold=S60(0, 30, 0)):
        self.base_threshold = base_threshold

    def get_dynamic_threshold(self, residue: int) -> float:
        """
        Adjusts the blocking threshold based on Base-60 residue.
        Lower threshold means it's easier to BLOCK (higher sensitivity).
        """
        if residue is None:
            return self.base_threshold

        # Penalty for Dissonant (Prime) Residues
        if residue in self.PRIMES_60:
            # Prime residue is a 'Mathematical Anomaly' -> Increase sensitivity
            # Threshold drops (S60(0, 30, 0) -> 0.3): easier to block.
            return max(S60(0, 6, 0), self.base_threshold - 0.2)

        # Bonus for Highly Composite Residues
        if residue in self.HIGHLY_COMPOSITE_60 or residue == 0:
            # Composite residue is 'Harmonic' -> Standard or lower sensitivity
            # Threshold rises (S60(0, 30, 0) -> 0.7): harder to block.
            return min(0.9, self.base_threshold + 0.2)

        return self.base_threshold

    def classify_score(self, score: float, threshold: float) -> str:
        """
        Classifies a numerical threat score into a decision.
        """
        if score >= (threshold + 0.3):
            return "BLOCK_CRITICAL"
        elif score >= threshold:
            return "BLOCK_CAUTION"
        elif score >= (threshold - 0.2):
            return "MONITOR_SUSPICIOUS"
        else:
            return "ALLOW_SAFE"

threshold_manager = ThresholdManager()
