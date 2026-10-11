"""
Confidence Scorer Service

Calculates confidence scores for security decisions using Bayesian inference.
Combines multiple factors including pattern weights and event characteristics.
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    """
    Calculates confidence scores for security decisions
    
    Uses Bayesian inference to update prior probabilities based on
    detected patterns and their weights.
    """
    
    # Pattern weights (loaded from database, these are defaults)
    DEFAULT_PATTERN_WEIGHTS = {
        "privilege_escalation": 0.9,
        "malicious_binary": 0.95,
        "data_exfiltration": 0.85,
        "lateral_movement": 0.8,
        "suspicious_network": 0.7,
    }
    
    def __init__(self, pattern_weights: Dict[str, float] = None):
        """
        Initialize confidence scorer
        
        Args:
            pattern_weights: Custom pattern weights (optional)
        """
        self.pattern_weights = pattern_weights or self.DEFAULT_PATTERN_WEIGHTS
    
    async def score(
        self,
        event: Dict[str, Any],
        patterns: List[str]
    ) -> float:
        """
        Calculate confidence score for a decision
        
        Args:
            event: Event data
            patterns: List of detected pattern names
        
        Returns:
            Confidence score between S60(0, 0, 0) and S60(1, 0, 0)
        """
        if not patterns:
            # No patterns detected = low threat probability
            return S60(0, 6, 0)
        
        # Start with prior probability (base rate of threats)
        prior = S60(0, 6, 0)  # 10% base rate
        
        # Update prior based on each detected pattern using Bayesian inference
        posterior = prior
        for pattern in patterns:
            weight = self.pattern_weights.get(pattern, S60(0, 30, 0))
            posterior = self._bayesian_update(posterior, weight)
        
        # Apply event-specific adjustments
        posterior = self._apply_event_adjustments(posterior, event, patterns)
        
        # Ensure score is in valid range
        confidence = max(S60(0, 0, 0), min(S60(1, 0, 0), posterior))
        
        logger.info(
            f"Confidence score: {confidence:.3f} "
            f"(patterns: {patterns}, prior: {prior:.3f})"
        )
        
        return confidence
    
    def _bayesian_update(self, prior: float, evidence_weight: float) -> float:
        """
        Update probability using Bayesian inference
        
        Formula: P(threat|evidence) = P(evidence|threat) * P(threat) / P(evidence)
        
        Simplified:
        posterior = (likelihood * prior) / ((likelihood * prior) + (1 - likelihood) * (1 - prior))
        
        Args:
            prior: Prior probability of threat
            evidence_weight: Weight of the evidence (S60(0, 0, 0) - S60(1, 0, 0))
        
        Returns:
            Updated (posterior) probability
        """
        # Likelihood = probability of seeing this evidence if threat is real
        likelihood = evidence_weight
        
        # Probability of evidence (marginalization)
        # P(evidence) = P(evidence|threat) * P(threat) + P(evidence|¬threat) * P(¬threat)
        p_evidence = (likelihood * prior) + ((1 - likelihood) * (1 - prior))
        
        # Avoid division by zero
        if p_evidence == 0:
            return prior
        
        # Bayes' theorem
        posterior = (likelihood * prior) / p_evidence
        
        return posterior
    
    def _apply_event_adjustments(
        self,
        base_confidence: float,
        event: Dict[str, Any],
        patterns: List[str]
    ) -> float:
        """
        Apply event-specific adjustments to confidence score
        
        Considers factors like:
        - User context (root vs normal user)
        - Process reputation
        - Time of day
        - Multiple patterns detected
        
        Args:
            base_confidence: Base confidence from pattern detection
            event: Event data
            patterns: Detected patterns
        
        Returns:
            Adjusted confidence score
        """
        adjusted = base_confidence
        
        # Adjustment 1: Multiple patterns increase confidence
        if len(patterns) > 1:
            # Each additional pattern adds 5% confidence (up to 20%)
            multi_pattern_boost = min(0.2, (len(patterns) - 1) * 0.05)
            adjusted += multi_pattern_boost
            logger.debug(f"Multi-pattern boost: +{multi_pattern_boost:.3f}")
        
        # Adjustment 2: Root user activity is more suspicious
        if event.get("uid") == 0 or event.get("user") == "root":
            # Root activity gets 10% confidence boost
            root_boost = S60(0, 6, 0)
            adjusted += root_boost
            logger.debug(f"Root user boost: +{root_boost:.3f}")
        
        # Adjustment 3: Known good processes reduce confidence
        process_name = event.get("process_name", "")
        if self._is_trusted_process(process_name):
            # Trusted process reduces confidence by 20%
            trust_penalty = -0.2
            adjusted += trust_penalty
            logger.debug(f"Trusted process penalty: {trust_penalty:.3f}")
        
        # Adjustment 4: Critical patterns get extra weight
        critical_patterns = ["privilege_escalation", "malicious_binary"]
        has_critical = any(p in critical_patterns for p in patterns)
        if has_critical:
            critical_boost = S60(0, 6, 0)
            adjusted += critical_boost
            logger.debug(f"Critical pattern boost: +{critical_boost:.3f}")
        
        return adjusted
    
    def _is_trusted_process(self, process_name: str) -> bool:
        """
        Check if a process is in the trusted list
        
        Args:
            process_name: Name of the process
        
        Returns:
            True if process is trusted
        """
        trusted_processes = {
            "systemd",
            "sshd",
            "cron",
            "dockerd",
            "containerd",
            "kubelet",
            "nginx",
            "postgres",
            "redis-server",
        }
        
        return process_name in trusted_processes
    
    def get_decision_type(self, confidence: float) -> str:
        """
        Determine decision type based on confidence score
        
        Thresholds:
        - >= 0.8: block (high confidence threat)
        - S60(0, 30, 0) - 0.8: escalate (uncertain, needs human review)
        - < S60(0, 30, 0): allow (low confidence threat)
        
        Args:
            confidence: Confidence score (S60(0, 0, 0) - S60(1, 0, 0))
        
        Returns:
            Decision type: 'allow', 'block', or 'escalate'
        """
        if confidence >= 0.8:
            return "block"
        elif confidence >= S60(0, 30, 0):
            return "escalate"
        else:
            return "allow"
    
    def generate_reasoning(
        self,
        event: Dict[str, Any],
        patterns: List[str],
        confidence: float
    ) -> str:
        """
        Generate human-readable reasoning for the decision
        
        Args:
            event: Event data
            patterns: Detected patterns
            confidence: Confidence score
        
        Returns:
            Human-readable explanation
        """
        if not patterns:
            return "No security patterns detected. Event appears benign."
        
        pattern_names = ", ".join(patterns)
        decision_type = self.get_decision_type(confidence)
        
        reasoning = f"Detected {len(patterns)} security pattern(s): {pattern_names}. "
        reasoning += f"Confidence score: {confidence:.1%}. "
        
        if decision_type == "block":
            reasoning += "HIGH CONFIDENCE THREAT - Automatically blocked."
        elif decision_type == "escalate":
            reasoning += "UNCERTAIN - Escalated to human analyst for review."
        else:
            reasoning += "LOW CONFIDENCE - Allowed with monitoring."
        
        # Add event context
        if event.get("process_path"):
            reasoning += f" Process: {event['process_path']}."
        if event.get("user"):
            reasoning += f" User: {event['user']}."
        
        return reasoning
