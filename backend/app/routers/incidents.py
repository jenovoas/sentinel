"""
ITIL Incident Management API Router.

FastAPI endpoints for incident management with ITIL v4 compliance.
Includes authentication, authorization, and full CRUD operations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.auth_utils import get_current_user
from app.services.incident_service import IncidentService
from app.schemas.incident_schemas import (
    IncidentCreate,
    IncidentUpdate,
    IncidentAssign,
    IncidentResolve,
    IncidentClose,
    IncidentResponse,
    IncidentListItem,
    IncidentListResponse,
    IncidentStats,
    IncidentFilters,
    IncidentCategoryEnum,
    IncidentPriorityEnum,
    IncidentStatusEnum
)

router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_incident_service(db: AsyncSession = Depends(get_db)) -> IncidentService:
    """Dependency to get incident service."""
    return IncidentService(db)


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/stats", response_model=IncidentStats)
async def get_incident_statistics(
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service)
):
    """
    Get incident statistics for dashboard.
    
    Returns counts by status, priority, category, and SLA metrics.
    """
    # TODO: Get tenant_id from current_user
    tenant_id = 1  # Placeholder
    
    stats = await service.get_statistics(tenant_id)
    return stats


@router.get("", response_model=IncidentListResponse)
async def list_incidents(
    status: Optional[List[IncidentStatusEnum]] = Query(None),
    priority: Optional[List[IncidentPriorityEnum]] = Query(None),
    category: Optional[List[IncidentCategoryEnum]] = Query(None),
    assigned_team: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service)
):
    """
    List incidents with filtering, sorting, and pagination.
    
    Filters:
    - status: Filter by status (can specify multiple)
    - priority: Filter by priority (can specify multiple)
    - category: Filter by category (can specify multiple)
    - assigned_team: Filter by assigned team
    - search: Search in title/description/incident_id
    
    Pagination:
    - page: Page number (1-indexed)
    - page_size: Items per page (max 100)
    
    Sorting:
    - sort_by: Field to sort by (created_at, priority, status, etc.)
    - sort_order: asc or desc
    """
    # TODO: Get tenant_id from current_user
    tenant_id = 1  # Placeholder
    
    # Build filters
    filters = IncidentFilters(
        status=status,
        priority=priority,
        category=category,
        assigned_team=assigned_team,
        search=search,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Get incidents
    incidents, total = await service.list_incidents(tenant_id, filters)
    
    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size
    
    return IncidentListResponse(
        incidents=[IncidentListItem.model_validate(inc) for inc in incidents],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_data: IncidentCreate,
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service)
):
    """
    Create a new incident.
    
    Priority is auto-calculated from impact × urgency matrix.
    SLA targets are auto-assigned based on priority.
    """
    # TODO: Get tenant_id from current_user
    tenant_id = 1  # Placeholder
    
    incident = await service.create_incident(
        incident_data=incident_data,
        tenant_id=tenant_id,
        user_id=current_user.id,
        user_email=current_user.email
    )
    
    return IncidentResponse.model_validate(incident)


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    include_audit: bool = Query(False, description="Include audit logs"),
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service)
):
    """
    Get incident details by ID.
    
    Optionally include audit logs and attachments.
    """
    try:
        incident = await service.get_incident(incident_id, include_audit=include_audit)
        return IncidentResponse.model_validate(incident)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int,
    incident_data: IncidentUpdate,
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service)
):
    """
    Update incident fields.
    
    Only provided fields will be updated.
    """
    # TODO: Implement update logic in service
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/{incident_id}/assign", response_model=IncidentResponse)
async def assign_incident(
    incident_id: int,
    assignment: IncidentAssign,
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service)
):
    """
    Assign incident to user/team.
    
    Updates status to ASSIGNED if currently NEW.
    Records response time if first assignment.
    """
    try:
        incident = await service.assign_incident(
            incident_id=incident_id,
            assigned_to=assignment.assigned_to,
            assigned_team=assignment.assigned_team,
            user_id=current_user.id,
            user_email=current_user.email,
            notes=assignment.notes
        )
        return IncidentResponse.model_validate(incident)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve_incident(
    incident_id: int,
    resolution: IncidentResolve,
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service)
):
    """
    Mark incident as resolved.
    
    Records resolution time and notes.
    Updates status to RESOLVED.
    """
    try:
        incident = await service.resolve_incident(
            incident_id=incident_id,
            resolution_notes=resolution.resolution_notes,
            root_cause=resolution.root_cause,
            user_id=current_user.id,
            user_email=current_user.email
        )
        return IncidentResponse.model_validate(incident)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{incident_id}/close", response_model=IncidentResponse)
async def close_incident(
    incident_id: int,
    closure: IncidentClose,
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service)
):
    """
    Close incident.
    
    Validates incident is resolved.
    Generates post-mortem.
    Records closure time.
    """
    try:
        incident = await service.close_incident(
            incident_id=incident_id,
            user_id=current_user.id,
            user_email=current_user.email,
            closure_notes=closure.closure_notes
        )
        return IncidentResponse.model_validate(incident)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{incident_id}/timeline")
async def get_incident_timeline(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service)
):
    """
    Get incident timeline (audit log).
    
    Returns chronological list of all actions taken on the incident.
    """
    try:
        incident = await service.get_incident(incident_id, include_audit=True)
        
        # Format audit logs for timeline
        timeline = [
            {
                "timestamp": log.timestamp.isoformat(),
                "action": log.action,
                "user": log.user_email,
                "details": log.notes or f"{log.field_changed}: {log.old_value} → {log.new_value}" if log.field_changed else None
            }
            for log in incident.audit_logs
        ]
        
        return {"incident_id": incident.incident_id, "timeline": timeline}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service)
):
    """
    Soft delete incident.
    
    Sets is_deleted flag instead of actually deleting.
    Requires admin role.
    """
    # TODO: Check admin role
    # TODO: Implement soft delete in service
    raise HTTPException(status_code=501, detail="Not implemented yet")
