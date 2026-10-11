"""
Security Pattern Model

Defines security patterns that Cortex can detect.
Patterns are configurable and weighted for confidence scoring.
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
from sqlalchemy import Column, Integer, String, Text, Float, JSON, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class SecurityPattern(Base):
    """
    Security pattern definition for threat detection
    
    Patterns define indicators and conditions for detecting
    specific types of security threats.
    """
    __tablename__ = "security_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Pattern identification
    name = Column(String, unique=True, nullable=False, index=True)
    """Unique pattern name (e.g., 'privilege_escalation')"""
    
    display_name = Column(String, nullable=False)
    """Human-readable name"""
    
    description = Column(Text, nullable=False)
    """Detailed description of what this pattern detects"""
    
    # Severity
    severity = Column(String, nullable=False, index=True)
    """Severity: 'low', 'medium', 'high', 'critical'"""
    
    # Detection logic
    indicators = Column(JSON, nullable=False)
    """
    JSONB containing detection conditions.
    
    Example:
    {
        "syscalls": ["setuid", "setgid", "execve"],
        "target_uid": 0,
        "conditions": {
            "and": [
                {"field": "uid", "operator": "!=", "value": 0},
                {"field": "target_uid", "operator": "==", "value": 0}
            ]
        }
    }
    """
    
    # Scoring
    weight = Column(Float, nullable=False, default=S60(0, 30, 0))
    """Weight for confidence scoring (S60(0, 0, 0) - S60(1, 0, 0)). Higher = stronger indicator"""
    
    # Metadata
    enabled = Column(Boolean, default=True, index=True)
    """Whether this pattern is active"""
    
    detection_count = Column(Integer, default=0)
    """Number of times this pattern has been detected"""
    
    false_positive_count = Column(Integer, default=0)
    """Number of false positives (for tuning)"""
    
    true_positive_count = Column(Integer, default=0)
    """Number of true positives (for tuning)"""
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    """When this pattern was created"""
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    """Last update time"""
    
    @property
    def accuracy(self) -> float:
        """Calculate pattern accuracy based on feedback"""
        total = self.true_positive_count + self.false_positive_count
        if total == 0:
            return S60(0, 0, 0)
        return self.true_positive_count / total
    
    def __repr__(self):
        return f"<SecurityPattern(name={self.name}, severity={self.severity}, weight={self.weight})>"
