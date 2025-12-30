"""
Cortex API Router

REST API endpoints for the Cortex Decision Engine.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from datetime import datetime

from app.database import get_db
from app.config import get_settings
from app.services.cortex_engine import CortexDecisionEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/cortex", tags=["Cortex Decision Engine"])


# Request/Response Models

class EventSubmission(BaseModel):
    """Event submission request"""
    event_type: str = Field(..., description="Event type: syscall, network, memory, file")
    source: str = Field(..., description="Source: guardian_alpha, guardian_beta")
    data: dict = Field(..., description="Event data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "syscall",
                "source": "guardian_alpha",
                "data": {
                    "syscall": "execve",
                    "process_path": "/tmp/suspicious",
                    "user": "attacker",
                    "uid": 1000,
                    "pid": 12345
                }
            }
        }


class DecisionResponse(BaseModel):
    """Decision response"""
    decision_id: int
    decision_type: str
    confidence: float
    patterns_detected: list[str]
    reasoning: str
    processing_time_ms: float
    
    class Config:
        from_attributes = True


# Endpoints

@router.post("/events", response_model=DecisionResponse, status_code=status.HTTP_201_CREATED)
async def submit_event(
    event: EventSubmission,
    x_sentinel_token: str = Header(None, alias="X-Sentinel-Token"),
    db: AsyncSession = Depends(get_db)
):
    """
    Envía un evento de seguridad para análisis.
    
    Requiere un token de seguridad válido en la cabecera X-Sentinel-Token
    para mitigar ataques de inyección de telemetría (AIOpsDoom).
    """
    settings = get_settings()
    if x_sentinel_token != settings.internal_telemetry_token:
        logger.warning(f"🚨 Intento de inyección de telemetría rechazado (Token inválido)")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized telemetry source"
        )
    """
    Submit a security event for analysis
    
    The Cortex Engine will:
    1. Detect security patterns
    2. Calculate confidence score
    3. Make a decision (allow/block/escalate)
    4. Escalate to Guardian Gamma if uncertain
    """
    try:
        engine = CortexDecisionEngine(db)
        
        # Merge event data
        event_data = event.data.copy()
        event_data["event_type"] = event.event_type
        event_data["source"] = event.source
        
        # Process event
        decision = await engine.process_event(event_data)
        
        return DecisionResponse(
            decision_id=decision.id,
            decision_type=decision.decision_type,
            confidence=decision.confidence,
            patterns_detected=decision.patterns_detected or [],
            reasoning=decision.reasoning or "",
            processing_time_ms=decision.processing_time_ms or 0.0
        )
        
    except Exception as e:
        logger.error(f"Error processing event: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process event: {str(e)}"
        )


@router.get("/decisions")
async def get_decisions(
    limit: int = 100,
    decision_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get recent decisions"""
    engine = CortexDecisionEngine(db)
    decisions = await engine.get_recent_decisions(limit=limit, decision_type=decision_type)
    
    return {
        "count": len(decisions),
        "decisions": [
            {
                "id": d.id,
                "decision_type": d.decision_type,
                "confidence": d.confidence,
                "patterns": d.patterns_detected or [],
                "created_at": d.created_at.isoformat() if d.created_at else None
            }
            for d in decisions
        ]
    }


@router.get("/patterns")
async def get_patterns(db: AsyncSession = Depends(get_db)):
    """Get all security patterns"""
    from sqlalchemy import select
    from app.models.security_pattern import SecurityPattern
    
    result = await db.execute(select(SecurityPattern))
    patterns = result.scalars().all()
    
    return {
        "count": len(patterns),
        "patterns": [
            {
                "name": p.name,
                "display_name": p.display_name,
                "severity": p.severity,
                "weight": p.weight,
                "enabled": p.enabled,
                "detection_count": p.detection_count
            }
            for p in patterns
        ]
    }


@router.get("/stats")
async def get_stats(
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """Get Cortex Engine statistics"""
    engine = CortexDecisionEngine(db)
    stats = await engine.get_statistics(hours=hours)
    return stats


logger.info("✅ Cortex API router initialized")
