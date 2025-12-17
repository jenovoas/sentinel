"""
ITIL Incident Management Service.

Business logic for ITIL v4 compliant incident lifecycle management.
Implements all ITIL practices: Detection, Logging, Categorization, Prioritization,
Investigation, Resolution, and Closure.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.incident import (
    Incident,
    IncidentAuditLog,
    IncidentCategoryEnum,
    IncidentPriorityEnum,
    IncidentStatusEnum,
    ImpactEnum,
    UrgencyEnum
)
from app.schemas.incident_schemas import (
    IncidentCreate,
    IncidentUpdate,
    IncidentFilters,
    IncidentStats
)


# ============================================================================
# SLA CONFIGURATION (should be moved to YAML config)
# ============================================================================

SLA_TARGETS = {
    IncidentPriorityEnum.P1: {
        "response_minutes": 15,
        "resolution_hours": 4
    },
    IncidentPriorityEnum.P2: {
        "response_minutes": 30,
        "resolution_hours": 8
    },
    IncidentPriorityEnum.P3: {
        "response_minutes": 120,
        "resolution_hours": 24
    },
    IncidentPriorityEnum.P4: {
        "response_minutes": 240,
        "resolution_hours": 72
    }
}

# Priority matrix: Impact × Urgency → Priority
PRIORITY_MATRIX = {
    (ImpactEnum.HIGH, UrgencyEnum.HIGH): IncidentPriorityEnum.P1,
    (ImpactEnum.HIGH, UrgencyEnum.MEDIUM): IncidentPriorityEnum.P2,
    (ImpactEnum.HIGH, UrgencyEnum.LOW): IncidentPriorityEnum.P3,
    (ImpactEnum.MEDIUM, UrgencyEnum.HIGH): IncidentPriorityEnum.P2,
    (ImpactEnum.MEDIUM, UrgencyEnum.MEDIUM): IncidentPriorityEnum.P3,
    (ImpactEnum.MEDIUM, UrgencyEnum.LOW): IncidentPriorityEnum.P4,
    (ImpactEnum.LOW, UrgencyEnum.HIGH): IncidentPriorityEnum.P3,
    (ImpactEnum.LOW, UrgencyEnum.MEDIUM): IncidentPriorityEnum.P4,
    (ImpactEnum.LOW, UrgencyEnum.LOW): IncidentPriorityEnum.P4,
}


class IncidentService:
    """Service for ITIL incident management operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========================================================================
    # ITIL PRACTICE: INCIDENT LOGGING
    # ========================================================================

    async def create_incident(
        self,
        incident_data: IncidentCreate,
        tenant_id: int,
        user_id: int,
        user_email: str
    ) -> Incident:
        """
        Create a new incident (ITIL: Incident Logging).
        
        Auto-calculates priority based on Impact × Urgency matrix.
        Assigns SLA targets based on priority.
        Creates audit log entry.
        """
        # Calculate priority from impact × urgency
        priority = self._calculate_priority(incident_data.impact, incident_data.urgency)
        
        # Get SLA targets
        sla = SLA_TARGETS[priority]
        
        # Generate incident ID
        incident_id = await self._generate_incident_id()
        
        # Create incident
        incident = Incident(
            incident_id=incident_id,
            tenant_id=tenant_id,
            title=incident_data.title,
            description=incident_data.description,
            category=incident_data.category,
            priority=priority,
            status=IncidentStatusEnum.NEW,
            impact=incident_data.impact,
            urgency=incident_data.urgency,
            affected_service=incident_data.affected_service,
            affected_users=incident_data.affected_users,
            source=incident_data.source or "manual",
            source_event_id=incident_data.source_event_id,
            detection_time=datetime.now(timezone.utc),
            sla_response_target=sla["response_minutes"],
            sla_resolution_target=sla["resolution_hours"],
            created_by=user_id
        )
        
        self.db.add(incident)
        await self.db.flush()
        
        # Create audit log
        await self._create_audit_log(
            incident_id=incident.id,
            user_id=user_id,
            user_email=user_email,
            action="created",
            notes=f"Incident created with priority {priority.value}"
        )
        
        await self.db.commit()
        await self.db.refresh(incident)
        
        return incident

    # ========================================================================
    # ITIL PRACTICE: CATEGORIZATION & PRIORITIZATION
    # ========================================================================

    def _calculate_priority(self, impact: ImpactEnum, urgency: UrgencyEnum) -> IncidentPriorityEnum:
        """Calculate priority using ITIL Impact × Urgency matrix."""
        return PRIORITY_MATRIX.get((impact, urgency), IncidentPriorityEnum.P4)

    # ========================================================================
    # ITIL PRACTICE: ASSIGNMENT & ESCALATION
    # ========================================================================

    async def assign_incident(
        self,
        incident_id: int,
        assigned_to: Optional[int],
        assigned_team: Optional[str],
        user_id: int,
        user_email: str,
        notes: Optional[str] = None
    ) -> Incident:
        """
        Assign incident to user/team (ITIL: Assignment).
        
        Updates status to ASSIGNED if currently NEW.
        Records response time if first assignment.
        """
        incident = await self._get_incident_by_id(incident_id)
        
        # Update assignment
        old_assigned_to = incident.assigned_to
        old_assigned_team = incident.assigned_team
        
        incident.assigned_to = assigned_to
        incident.assigned_team = assigned_team
        
        # Update status if NEW
        if incident.status == IncidentStatusEnum.NEW:
            incident.status = IncidentStatusEnum.ASSIGNED
            
            # Record response time (first assignment)
            if not incident.response_time:
                incident.response_time = datetime.now(timezone.utc)
        
        # Create audit log
        await self._create_audit_log(
            incident_id=incident.id,
            user_id=user_id,
            user_email=user_email,
            action="assigned",
            field_changed="assigned_to/assigned_team",
            old_value=f"{old_assigned_to}/{old_assigned_team}",
            new_value=f"{assigned_to}/{assigned_team}",
            notes=notes
        )
        
        await self.db.commit()
        await self.db.refresh(incident)
        
        return incident

    # ========================================================================
    # ITIL PRACTICE: RESOLUTION & RECOVERY
    # ========================================================================

    async def resolve_incident(
        self,
        incident_id: int,
        resolution_notes: str,
        root_cause: Optional[str],
        user_id: int,
        user_email: str
    ) -> Incident:
        """
        Mark incident as resolved (ITIL: Resolution).
        
        Records resolution time.
        Updates status to RESOLVED.
        """
        incident = await self._get_incident_by_id(incident_id)
        
        incident.status = IncidentStatusEnum.RESOLVED
        incident.resolution_notes = resolution_notes
        incident.root_cause = root_cause
        incident.resolution_time = datetime.now(timezone.utc)
        
        # Create audit log
        await self._create_audit_log(
            incident_id=incident.id,
            user_id=user_id,
            user_email=user_email,
            action="resolved",
            field_changed="status",
            old_value=IncidentStatusEnum.IN_PROGRESS.value,
            new_value=IncidentStatusEnum.RESOLVED.value,
            notes=resolution_notes[:500]  # Truncate for audit log
        )
        
        await self.db.commit()
        await self.db.refresh(incident)
        
        return incident

    # ========================================================================
    # ITIL PRACTICE: INCIDENT CLOSURE
    # ========================================================================

    async def close_incident(
        self,
        incident_id: int,
        user_id: int,
        user_email: str,
        closure_notes: Optional[str] = None
    ) -> Incident:
        """
        Close incident (ITIL: Closure).
        
        Validates incident is resolved.
        Records closure time.
        Generates post-mortem.
        """
        incident = await self._get_incident_by_id(incident_id)
        
        # Validate incident is resolved
        if incident.status != IncidentStatusEnum.RESOLVED:
            raise ValueError("Incident must be resolved before closing")
        
        incident.status = IncidentStatusEnum.CLOSED
        incident.closure_time = datetime.now(timezone.utc)
        
        # Generate post-mortem
        incident.post_mortem = await self._generate_post_mortem(incident)
        
        # Create audit log
        await self._create_audit_log(
            incident_id=incident.id,
            user_id=user_id,
            user_email=user_email,
            action="closed",
            field_changed="status",
            old_value=IncidentStatusEnum.RESOLVED.value,
            new_value=IncidentStatusEnum.CLOSED.value,
            notes=closure_notes
        )
        
        await self.db.commit()
        await self.db.refresh(incident)
        
        return incident

    # ========================================================================
    # QUERY OPERATIONS
    # ========================================================================

    async def get_incident(self, incident_id: int, include_audit: bool = False) -> Incident:
        """Get incident by ID with optional audit logs."""
        query = select(Incident).where(
            and_(
                Incident.id == incident_id,
                Incident.is_deleted == False
            )
        )
        
        if include_audit:
            query = query.options(
                selectinload(Incident.audit_logs),
                selectinload(Incident.attachments)
            )
        
        result = await self.db.execute(query)
        incident = result.scalar_one_or_none()
        
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        
        return incident

    async def list_incidents(
        self,
        tenant_id: int,
        filters: IncidentFilters
    ) -> tuple[List[Incident], int]:
        """List incidents with filtering and pagination."""
        # Base query
        query = select(Incident).where(
            and_(
                Incident.tenant_id == tenant_id,
                Incident.is_deleted == False
            )
        )
        
        # Apply filters
        if filters.status:
            query = query.where(Incident.status.in_(filters.status))
        
        if filters.priority:
            query = query.where(Incident.priority.in_(filters.priority))
        
        if filters.category:
            query = query.where(Incident.category.in_(filters.category))
        
        if filters.assigned_team:
            query = query.where(Incident.assigned_team == filters.assigned_team)
        
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Incident.title.ilike(search_term),
                    Incident.description.ilike(search_term),
                    Incident.incident_id.ilike(search_term)
                )
            )
        
        if filters.date_from:
            query = query.where(Incident.created_at >= filters.date_from)
        
        if filters.date_to:
            query = query.where(Incident.created_at <= filters.date_to)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting
        sort_column = getattr(Incident, filters.sort_by, Incident.created_at)
        if filters.sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)
        
        # Execute
        result = await self.db.execute(query)
        incidents = result.scalars().all()
        
        return list(incidents), total

    async def get_statistics(self, tenant_id: int) -> IncidentStats:
        """Get incident statistics for dashboard."""
        # Base query
        base_query = select(Incident).where(
            and_(
                Incident.tenant_id == tenant_id,
                Incident.is_deleted == False
            )
        )
        
        # Total incidents
        total_result = await self.db.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total_incidents = total_result.scalar()
        
        # Open incidents (not closed)
        open_result = await self.db.execute(
            select(func.count()).select_from(
                base_query.where(Incident.status != IncidentStatusEnum.CLOSED).subquery()
            )
        )
        open_incidents = open_result.scalar()
        
        # Critical incidents (P1 + P2)
        critical_result = await self.db.execute(
            select(func.count()).select_from(
                base_query.where(
                    Incident.priority.in_([IncidentPriorityEnum.P1, IncidentPriorityEnum.P2])
                ).subquery()
            )
        )
        critical_incidents = critical_result.scalar()
        
        # Count by status
        status_counts = {}
        for status in IncidentStatusEnum:
            count_result = await self.db.execute(
                select(func.count()).select_from(
                    base_query.where(Incident.status == status).subquery()
                )
            )
            status_counts[status.value] = count_result.scalar()
        
        # Count by priority
        priority_counts = {}
        for priority in IncidentPriorityEnum:
            count_result = await self.db.execute(
                select(func.count()).select_from(
                    base_query.where(Incident.priority == priority).subquery()
                )
            )
            priority_counts[priority.value] = count_result.scalar()
        
        # Count by category
        category_counts = {}
        for category in IncidentCategoryEnum:
            count_result = await self.db.execute(
                select(func.count()).select_from(
                    base_query.where(Incident.category == category).subquery()
                )
            )
            category_counts[category.value] = count_result.scalar()
        
        # Average resolution time (in hours)
        avg_resolution_result = await self.db.execute(
            select(func.avg(
                func.extract('epoch', Incident.resolution_time - Incident.detection_time) / 3600
            )).select_from(
                base_query.where(Incident.resolution_time.isnot(None)).subquery()
            )
        )
        avg_resolution_time = avg_resolution_result.scalar()
        
        return IncidentStats(
            total_incidents=total_incidents,
            open_incidents=open_incidents,
            critical_incidents=critical_incidents,
            avg_resolution_time_hours=round(avg_resolution_time, 2) if avg_resolution_time else None,
            sla_compliance_rate=None,  # TODO: Calculate SLA compliance
            new_count=status_counts.get("new", 0),
            assigned_count=status_counts.get("assigned", 0),
            in_progress_count=status_counts.get("in_progress", 0),
            resolved_count=status_counts.get("resolved", 0),
            closed_count=status_counts.get("closed", 0),
            p1_count=priority_counts.get("P1", 0),
            p2_count=priority_counts.get("P2", 0),
            p3_count=priority_counts.get("P3", 0),
            p4_count=priority_counts.get("P4", 0),
            category_breakdown=category_counts
        )

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    async def _get_incident_by_id(self, incident_id: int) -> Incident:
        """Get incident by ID (internal use)."""
        result = await self.db.execute(
            select(Incident).where(
                and_(
                    Incident.id == incident_id,
                    Incident.is_deleted == False
                )
            )
        )
        incident = result.scalar_one_or_none()
        
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        
        return incident

    async def _generate_incident_id(self) -> str:
        """Generate unique incident ID (format: INC-YYYYMMDD-XXXXX)."""
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        
        # Get count of incidents created today
        result = await self.db.execute(
            select(func.count()).where(
                Incident.incident_id.like(f"INC-{today}-%")
            )
        )
        count = result.scalar()
        
        # Generate ID
        sequence = str(count + 1).zfill(5)
        return f"INC-{today}-{sequence}"

    async def _create_audit_log(
        self,
        incident_id: int,
        user_id: int,
        user_email: str,
        action: str,
        field_changed: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        notes: Optional[str] = None
    ):
        """Create audit log entry."""
        audit_log = IncidentAuditLog(
            incident_id=incident_id,
            user_id=user_id,
            user_email=user_email,
            action=action,
            field_changed=field_changed,
            old_value=old_value,
            new_value=new_value,
            notes=notes
        )
        self.db.add(audit_log)

    async def _generate_post_mortem(self, incident: Incident) -> Dict[str, Any]:
        """Generate post-mortem report."""
        detection_time = incident.detection_time
        resolution_time = incident.resolution_time or datetime.now(timezone.utc)
        
        duration_hours = (resolution_time - detection_time).total_seconds() / 3600
        
        return {
            "incident_id": incident.incident_id,
            "title": incident.title,
            "category": incident.category.value,
            "priority": incident.priority.value,
            "detection_time": detection_time.isoformat(),
            "resolution_time": resolution_time.isoformat(),
            "duration_hours": round(duration_hours, 2),
            "affected_service": incident.affected_service,
            "affected_users": incident.affected_users,
            "root_cause": incident.root_cause,
            "resolution_notes": incident.resolution_notes,
            "sla_met": duration_hours <= incident.sla_resolution_target if incident.sla_resolution_target else None
        }
