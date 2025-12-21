"""
Database model for Guardian Gamma decisions
"""

from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class GammaDecision(Base):
    """
    Human-in-the-loop decision queue.
    
    Stores decisions from Guardian Alpha/Beta that require human validation.
    """
    __tablename__ = "gamma_decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    guardian_source = Column(String(10), nullable=False)  # 'alpha' or 'beta'
    decision_type = Column(String(50), nullable=False)
    context = Column(JSON, nullable=False)  # Decision context
    evidence = Column(JSON)  # Supporting evidence
    confidence = Column(Float)  # AI confidence (0-1)
    
    status = Column(String(20), default='pending')  # pending/approved/denied/timeout
    human_decision = Column(String(20))  # approved/denied/timeout
    human_feedback = Column(Text)  # Human feedback for learning
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    decided_at = Column(DateTime(timezone=True))
    timeout_at = Column(DateTime(timezone=True))
