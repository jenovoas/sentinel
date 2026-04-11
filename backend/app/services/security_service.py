import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monitoring import SecurityAlert, SeverityLevel
from app.schemas.security import SecurityAlertCreate, SecurityAlertUpdate

logger = logging.getLogger(__name__)

class SecurityService:
    @staticmethod
    async def get_security_alerts(
        db: AsyncSession,
        limit: int = 100,
        severity: Optional[SeverityLevel] = None,
        is_investigated: Optional[bool] = None,
        hours: Optional[int] = None
    ) -> List[SecurityAlert]:
        """
        Fetch security alerts from the database with optional filtering.
        """
        query = select(SecurityAlert)

        filters = []
        if severity:
            filters.append(SecurityAlert.severity == severity)
        if is_investigated is not None:
            filters.append(SecurityAlert.is_investigated == is_investigated)
        if hours:
            since = datetime.utcnow() - timedelta(hours=hours)
            filters.append(SecurityAlert.detected_at >= since)

        if filters:
            query = query.where(and_(*filters))

        query = query.order_by(desc(SecurityAlert.detected_at)).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create_security_alert(
        db: AsyncSession,
        alert_in: SecurityAlertCreate
    ) -> SecurityAlert:
        """
        Create a new security alert record.
        """
        alert = SecurityAlert(
            alert_type=alert_in.alert_type,
            severity=alert_in.severity,
            title=alert_in.title,
            description=alert_in.description,
            port=alert_in.port,
            protocol=alert_in.protocol,
            remote_ip=alert_in.remote_ip,
            local_process=alert_in.local_process,
            context_data=alert_in.context_data
        )

        db.add(alert)
        await db.flush()
        return alert

    @staticmethod
    async def update_security_alert(
        db: AsyncSession,
        alert_id: str,
        alert_update: SecurityAlertUpdate
    ) -> Optional[SecurityAlert]:
        """
        Update an existing security alert.
        """
        query = select(SecurityAlert).where(SecurityAlert.id == alert_id)
        result = await db.execute(query)
        alert = result.scalar_one_or_none()

        if not alert:
            return None

        if alert_update.is_investigated is not None:
            alert.is_investigated = alert_update.is_investigated
        if alert_update.investigation_notes is not None:
            alert.investigation_notes = alert_update.investigation_notes

        await db.flush()
        return alert
