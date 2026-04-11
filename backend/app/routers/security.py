from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.monitoring import SeverityLevel
from app.schemas.security import SecurityAlertResponse, SecurityAlertCreate, SecurityAlertUpdate
from app.services.security_service import SecurityService

router = APIRouter(prefix="/api/v1/security", tags=["security"])

@router.get("/alerts", response_model=List[SecurityAlertResponse])
async def get_alerts(
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[SeverityLevel] = None,
    is_investigated: Optional[bool] = None,
    hours: Optional[int] = Query(None, ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve security alerts from the watchdog system.
    """
    alerts = await SecurityService.get_security_alerts(
        db, limit=limit, severity=severity, is_investigated=is_investigated, hours=hours
    )
    return alerts

@router.post("/alerts", response_model=SecurityAlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_in: SecurityAlertCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest a new security alert (used by watchdog scripts).
    """
    alert = await SecurityService.create_security_alert(db, alert_in)
    await db.commit()
    await db.refresh(alert)
    return alert

@router.patch("/alerts/{alert_id}", response_model=SecurityAlertResponse)
async def update_alert(
    alert_id: str,
    alert_update: SecurityAlertUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update investigation status of an alert.
    """
    alert = await SecurityService.update_security_alert(db, alert_id, alert_update)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    await db.commit()
    await db.refresh(alert)
    return alert
