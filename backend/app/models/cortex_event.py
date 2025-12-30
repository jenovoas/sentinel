"""
Cortex Event Model

Represents security events processed by the Cortex Decision Engine.
Events come from Guardian Alpha/Beta (eBPF monitoring).
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from sqlalchemy.sql import func
from app.database import Base


class CortexEvent(Base):
    """
    Security event submitted to Cortex for analysis
    
    Events are enriched with context before pattern detection.
    """
    __tablename__ = "cortex_events"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Event metadata
    event_type = Column(String, nullable=False, index=True)
    """Type of event: 'syscall', 'network', 'memory', 'file'"""
    
    source = Column(String, nullable=False, index=True)
    """Source Guardian: 'guardian_alpha', 'guardian_beta'"""
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    """When the event occurred"""
    
    # Raw event data
    raw_data = Column(JSON, nullable=False)
    """Original event data from Guardian (JSONB for efficient querying)"""
    
    # Enriched data
    process_name = Column(String, index=True)
    """Process that triggered the event"""
    
    process_path = Column(String)
    """Full path to the process binary"""
    
    user = Column(String, index=True)
    """User who executed the process"""
    
    pid = Column(Integer)
    """Process ID"""
    
    ppid = Column(Integer)
    """Parent Process ID"""
    
    risk_score = Column(Float, default=0.0)
    """Initial risk score (0.0 - 1.0)"""
    
    # Relationships handled via foreign keys in CortexDecision
    
    def __repr__(self):
        return f"<CortexEvent(id={self.id}, type={self.event_type}, source={self.source})>"
