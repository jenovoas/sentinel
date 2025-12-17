"""
ITIL Incident Management Models.

SQLAlchemy models for ITIL v4 compliant incident management with full audit trail
for regulatory compliance (CMF, Ley 21.663, ISO 20000).

ITIL Practices Implemented:
    - Incident Logging
    - Categorization
    - Prioritization
    - Investigation & Diagnosis
    - Resolution & Recovery
    - Incident Closure
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


# ============================================================================
# ENUMS - ITIL Standard Categories
# ============================================================================

class IncidentCategoryEnum(str, PyEnum):
    """ITIL v4 Incident Categories."""
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    SECURITY = "security"
    ACCESS = "access"
    PERFORMANCE = "performance"
    DATA = "data"
    OTHER = "other"


class IncidentPriorityEnum(str, PyEnum):
    """ITIL Priority Levels (Impact × Urgency)."""
    P1 = "P1"  # Critical - High Impact, High Urgency
    P2 = "P2"  # High - High Impact, Medium Urgency OR Medium Impact, High Urgency
    P3 = "P3"  # Medium - Medium Impact, Medium Urgency
    P4 = "P4"  # Low - Low Impact, Low Urgency


class IncidentStatusEnum(str, PyEnum):
    """ITIL Incident Lifecycle States."""
    NEW = "new"  # Just created, not yet assigned
    ASSIGNED = "assigned"  # Assigned to team/person
    IN_PROGRESS = "in_progress"  # Being investigated/resolved
    RESOLVED = "resolved"  # Solution implemented, awaiting confirmation
    CLOSED = "closed"  # Confirmed resolved, archived


class ImpactEnum(str, PyEnum):
    """ITIL Impact Assessment."""
    HIGH = "high"  # Affects multiple users/services
    MEDIUM = "medium"  # Affects single service/department
    LOW = "low"  # Affects single user


class UrgencyEnum(str, PyEnum):
    """ITIL Urgency Assessment."""
    HIGH = "high"  # Immediate action required
    MEDIUM = "medium"  # Action required soon
    LOW = "low"  # Can wait


# ============================================================================
# MODELS
# ============================================================================

class Incident(Base):
    """
    Core Incident entity following ITIL v4 Incident Management practice.
    
    ITIL Compliance:
        - Unique incident ID
        - Categorization (category)
        - Prioritization (priority, impact, urgency)
        - SLA tracking (detection_time, response_time, resolution_time)
        - Assignment (assigned_to, assigned_team)
        - Status tracking (status)
        - Audit trail (via IncidentAuditLog relationship)
    
    Regulatory Compliance:
        - Multi-tenant isolation (tenant_id)
        - Full audit trail (audit_logs relationship)
        - Timestamps for all state changes
    """
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(50), unique=True, nullable=False, index=True)  # Format: INC-YYYYMMDD-XXXXX
    
    # Multi-tenancy
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # ITIL Fields
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(IncidentCategoryEnum), nullable=False, index=True)
    priority = Column(Enum(IncidentPriorityEnum), nullable=False, index=True)
    status = Column(Enum(IncidentStatusEnum), nullable=False, default=IncidentStatusEnum.NEW, index=True)
    
    # Impact & Urgency (used to calculate priority)
    impact = Column(Enum(ImpactEnum), nullable=False)
    urgency = Column(Enum(UrgencyEnum), nullable=False)
    
    # Assignment
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Assigned user
    assigned_team = Column(String(100), nullable=True)  # Team name (SOC, SRE, etc.)
    
    # SLA Tracking
    detection_time = Column(DateTime(timezone=True), nullable=False)  # When incident was detected
    response_time = Column(DateTime(timezone=True), nullable=True)  # When first response occurred
    resolution_time = Column(DateTime(timezone=True), nullable=True)  # When resolved
    closure_time = Column(DateTime(timezone=True), nullable=True)  # When closed
    
    # SLA Targets (minutes)
    sla_response_target = Column(Integer, nullable=True)  # Target response time in minutes
    sla_resolution_target = Column(Integer, nullable=True)  # Target resolution time in hours
    
    # Additional Context
    affected_service = Column(String(255), nullable=True)  # Service affected
    affected_users = Column(Integer, nullable=True)  # Number of users affected
    source = Column(String(50), nullable=True)  # Source: SIEM, monitoring, manual, etc.
    source_event_id = Column(String(255), nullable=True)  # Original event ID from source
    
    # Resolution
    resolution_notes = Column(Text, nullable=True)
    root_cause = Column(Text, nullable=True)
    post_mortem = Column(JSON, nullable=True)  # Auto-generated post-mortem
    
    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="incidents")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    creator = relationship("User", foreign_keys=[created_by])
    audit_logs = relationship("IncidentAuditLog", back_populates="incident", cascade="all, delete-orphan")
    attachments = relationship("IncidentAttachment", back_populates="incident", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Incident {self.incident_id} - {self.title} ({self.status})>"


class IncidentAuditLog(Base):
    """
    Audit trail for incident changes (who/what/when/why).
    
    Regulatory Compliance:
        - Complete audit trail for CMF/Ley 21.663
        - Immutable records (no updates/deletes)
        - Tracks all state changes
    """
    __tablename__ = "incident_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False, index=True)
    
    # Who
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user_email = Column(String(255), nullable=False)  # Denormalized for audit
    
    # What
    action = Column(String(100), nullable=False)  # created, assigned, escalated, resolved, closed, etc.
    field_changed = Column(String(100), nullable=True)  # Field that changed (if applicable)
    old_value = Column(Text, nullable=True)  # Previous value
    new_value = Column(Text, nullable=True)  # New value
    notes = Column(Text, nullable=True)  # Additional context
    
    # When
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Relationships
    incident = relationship("Incident", back_populates="audit_logs")
    user = relationship("User")

    def __repr__(self):
        return f"<IncidentAuditLog {self.action} by {self.user_email} at {self.timestamp}>"


class IncidentAttachment(Base):
    """
    File attachments for incidents (screenshots, logs, evidence).
    """
    __tablename__ = "incident_attachments"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False, index=True)
    
    # File metadata
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Storage path (S3, local, etc.)
    file_size = Column(Integer, nullable=False)  # Bytes
    mime_type = Column(String(100), nullable=False)
    
    # Upload metadata
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    incident = relationship("Incident", back_populates="attachments")
    uploader = relationship("User")

    def __repr__(self):
        return f"<IncidentAttachment {self.filename}>"
