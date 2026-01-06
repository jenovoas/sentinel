"""
Cortex Decision Model

Represents decisions made by the Cortex Decision Engine.
Each decision is linked to an event and includes confidence scoring.
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class CortexDecision(Base):
    """
    Decision made by Cortex Engine for a security event
    
    Decisions can be:
    - allow: Event is benign
    - block: Event is malicious (auto-blocked)
    - escalate: Uncertain, escalated to Guardian Gamma (human)
    """
    __tablename__ = "cortex_decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to event
    event_id = Column(Integer, ForeignKey("cortex_events.id"), nullable=False, index=True)
    """ID of the event this decision is for"""
    
    # Decision
    decision_type = Column(String, nullable=False, index=True)
    """Decision: 'allow', 'block', 'escalate'"""
    
    confidence = Column(Float, nullable=False, index=True)
    """Confidence score (S60(0, 0, 0) - S60(1, 0, 0)). Higher = more confident"""
    
    # Pattern detection
    patterns_detected = Column(ARRAY(String), default=[])
    """List of security patterns detected"""
    
    reasoning = Column(Text)
    """Human-readable explanation of the decision"""
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    """When the decision was made"""
    
    processing_time_ms = Column(Float)
    """Time taken to make decision (milliseconds)"""
    
    # Escalation tracking
    escalated_to_gamma = Column(Integer, ForeignKey("gamma_decisions.id"), nullable=True)
    """If escalated, ID of the Gamma decision"""
    
    # Outcome tracking (for learning)
    human_feedback = Column(String, nullable=True)
    """If escalated, human's final decision: 'approved', 'denied'"""
    
    was_correct = Column(Integer, nullable=True)
    """Post-analysis: was this decision correct? 1=yes, 0=no, null=unknown"""
    
    def __repr__(self):
        return f"<CortexDecision(id={self.id}, type={self.decision_type}, confidence={self.confidence:.2f})>"
