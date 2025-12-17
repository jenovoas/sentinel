"""
Pydantic schemas for Incident Management API.

Request/response schemas with validation for ITIL v4 compliant incident management.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from app.models.incident import (
    IncidentCategoryEnum,
    IncidentPriorityEnum,
    IncidentStatusEnum,
    ImpactEnum,
    UrgencyEnum
)


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class IncidentCreate(BaseModel):
    """Schema for creating a new incident."""
    title: str = Field(..., min_length=5, max_length=255, description="Incident title")
    description: str = Field(..., min_length=10, description="Detailed description")
    category: IncidentCategoryEnum = Field(..., description="ITIL category")
    impact: ImpactEnum = Field(..., description="Business impact")
    urgency: UrgencyEnum = Field(..., description="Time sensitivity")
    affected_service: Optional[str] = Field(None, max_length=255, description="Affected service name")
    affected_users: Optional[int] = Field(None, ge=0, description="Number of affected users")
    source: Optional[str] = Field("manual", max_length=50, description="Incident source")
    source_event_id: Optional[str] = Field(None, max_length=255, description="Source event ID")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Database connection timeout",
                "description": "Users unable to access application due to database timeouts",
                "category": "software",
                "impact": "high",
                "urgency": "high",
                "affected_service": "user-api",
                "affected_users": 150,
                "source": "manual"
            }
        }


class IncidentUpdate(BaseModel):
    """Schema for updating an incident."""
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[IncidentCategoryEnum] = None
    impact: Optional[ImpactEnum] = None
    urgency: Optional[UrgencyEnum] = None
    status: Optional[IncidentStatusEnum] = None
    assigned_to: Optional[int] = None
    assigned_team: Optional[str] = Field(None, max_length=100)
    resolution_notes: Optional[str] = None
    root_cause: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "in_progress",
                "assigned_team": "SOC-L2",
                "resolution_notes": "Investigating database connection pool settings"
            }
        }


class IncidentAssign(BaseModel):
    """Schema for assigning an incident."""
    assigned_to: Optional[int] = Field(None, description="User ID to assign to")
    assigned_team: Optional[str] = Field(None, max_length=100, description="Team name")
    notes: Optional[str] = Field(None, description="Assignment notes")

    @field_validator('assigned_to', 'assigned_team')
    @classmethod
    def at_least_one_required(cls, v, info):
        """Ensure at least one of assigned_to or assigned_team is provided."""
        if not v and not info.data.get('assigned_team' if info.field_name == 'assigned_to' else 'assigned_to'):
            raise ValueError('Either assigned_to or assigned_team must be provided')
        return v


class IncidentResolve(BaseModel):
    """Schema for resolving an incident."""
    resolution_notes: str = Field(..., min_length=10, description="Resolution description")
    root_cause: Optional[str] = Field(None, description="Root cause analysis")


class IncidentClose(BaseModel):
    """Schema for closing an incident."""
    closure_notes: Optional[str] = Field(None, description="Closure notes")


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class IncidentAuditLogResponse(BaseModel):
    """Schema for incident audit log entry."""
    id: int
    action: str
    user_email: str
    field_changed: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    notes: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class IncidentAttachmentResponse(BaseModel):
    """Schema for incident attachment."""
    id: int
    filename: str
    file_size: int
    mime_type: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class IncidentResponse(BaseModel):
    """Schema for incident response."""
    id: int
    incident_id: str
    title: str
    description: str
    category: IncidentCategoryEnum
    priority: IncidentPriorityEnum
    status: IncidentStatusEnum
    impact: ImpactEnum
    urgency: UrgencyEnum
    
    assigned_to: Optional[int]
    assigned_team: Optional[str]
    
    detection_time: datetime
    response_time: Optional[datetime]
    resolution_time: Optional[datetime]
    closure_time: Optional[datetime]
    
    sla_response_target: Optional[int]
    sla_resolution_target: Optional[int]
    
    affected_service: Optional[str]
    affected_users: Optional[int]
    source: Optional[str]
    
    resolution_notes: Optional[str]
    root_cause: Optional[str]
    
    created_at: datetime
    updated_at: datetime
    created_by: int
    
    # Optional relationships
    audit_logs: Optional[List[IncidentAuditLogResponse]] = None
    attachments: Optional[List[IncidentAttachmentResponse]] = None

    class Config:
        from_attributes = True


class IncidentListItem(BaseModel):
    """Schema for incident list item (lighter than full response)."""
    id: int
    incident_id: str
    title: str
    category: IncidentCategoryEnum
    priority: IncidentPriorityEnum
    status: IncidentStatusEnum
    assigned_team: Optional[str]
    detection_time: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class IncidentListResponse(BaseModel):
    """Schema for paginated incident list."""
    incidents: List[IncidentListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class IncidentStats(BaseModel):
    """Schema for incident statistics (dashboard)."""
    total_incidents: int
    open_incidents: int
    critical_incidents: int  # P1 + P2
    avg_resolution_time_hours: Optional[float]
    sla_compliance_rate: Optional[float]  # Percentage
    
    # By status
    new_count: int
    assigned_count: int
    in_progress_count: int
    resolved_count: int
    closed_count: int
    
    # By priority
    p1_count: int
    p2_count: int
    p3_count: int
    p4_count: int
    
    # By category
    category_breakdown: dict[str, int]


# ============================================================================
# FILTER SCHEMAS
# ============================================================================

class IncidentFilters(BaseModel):
    """Schema for incident filtering."""
    status: Optional[List[IncidentStatusEnum]] = None
    priority: Optional[List[IncidentPriorityEnum]] = None
    category: Optional[List[IncidentCategoryEnum]] = None
    assigned_team: Optional[str] = None
    search: Optional[str] = Field(None, description="Search in title/description")
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")
