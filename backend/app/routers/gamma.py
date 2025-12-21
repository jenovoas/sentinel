"""
Guardian Gamma API Router - Human-in-the-Loop Decisions

Endpoints for managing critical security decisions that require human validation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from app.database import get_db
from app.services.guardian_gamma import (
    GuardianGammaService,
    GuardianSource,
    DecisionType
)


router = APIRouter(prefix="/gamma", tags=["Guardian Gamma"])


# Request/Response Models

class CreateDecisionRequest(BaseModel):
    """Request to create a decision for human validation"""
    guardian: GuardianSource
    decision_type: DecisionType
    context: Dict[str, Any] = Field(..., description="Decision context")
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence score")
    evidence: Optional[Dict[str, Any]] = Field(None, description="Supporting evidence")
    timeout_minutes: int = Field(30, ge=1, le=1440, description="Timeout in minutes")


class CreateDecisionResponse(BaseModel):
    """Response after creating a decision"""
    decision_id: int
    status: str = "pending"
    timeout_at: str


class DecisionFeedback(BaseModel):
    """Feedback for a decision"""
    feedback: Optional[str] = Field(None, description="Human feedback for learning")


class PendingDecision(BaseModel):
    """Pending decision details"""
    id: int
    guardian: str
    type: str
    context: Dict[str, Any]
    evidence: Dict[str, Any]
    confidence: float
    created_at: str
    timeout_at: str


# Endpoints

@router.post("/decision", response_model=CreateDecisionResponse, status_code=status.HTTP_201_CREATED)
async def create_decision(
    request: CreateDecisionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new decision request for human validation.
    
    Used by Guardian Alpha/Beta to escalate decisions when confidence is low.
    
    Example:
        ```python
        # Guardian Alpha escalates binary block decision
        response = await client.post("/gamma/decision", json={
            "guardian": "alpha",
            "decision_type": "binary_block",
            "context": {
                "binary_path": "/tmp/suspicious",
                "hash": "abc123..."
            },
            "confidence": 0.65,
            "timeout_minutes": 30
        })
        ```
    """
    service = GuardianGammaService(db)
    
    decision_id = await service.create_decision(
        guardian=request.guardian,
        decision_type=request.decision_type,
        context=request.context,
        confidence=request.confidence,
        evidence=request.evidence,
        timeout_minutes=request.timeout_minutes
    )
    
    # Get the created decision to return timeout
    decisions = await service.get_pending_decisions(limit=1)
    decision = next((d for d in decisions if d["id"] == decision_id), None)
    
    return CreateDecisionResponse(
        decision_id=decision_id,
        timeout_at=decision["timeout_at"] if decision else ""
    )


@router.get("/pending", response_model=List[PendingDecision])
async def get_pending_decisions(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all pending decisions ordered by priority.
    
    Priority:
    1. Low confidence (needs human judgment)
    2. Oldest first (FIFO)
    
    Used by the Guardian Gamma dashboard to display pending decisions.
    """
    service = GuardianGammaService(db)
    decisions = await service.get_pending_decisions(limit=limit)
    
    return [PendingDecision(**d) for d in decisions]


@router.post("/approve/{decision_id}", status_code=status.HTTP_200_OK)
async def approve_decision(
    decision_id: int,
    feedback: DecisionFeedback,
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a decision and provide feedback.
    
    The feedback is used to train the system and improve future decisions.
    """
    service = GuardianGammaService(db)
    
    success = await service.approve_decision(
        decision_id=decision_id,
        feedback=feedback.feedback
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found or already decided"
        )
    
    return {"status": "approved", "decision_id": decision_id}


@router.post("/deny/{decision_id}", status_code=status.HTTP_200_OK)
async def deny_decision(
    decision_id: int,
    feedback: DecisionFeedback,
    db: AsyncSession = Depends(get_db)
):
    """
    Deny a decision and provide feedback.
    
    The feedback is used to train the system and improve future decisions.
    """
    service = GuardianGammaService(db)
    
    success = await service.deny_decision(
        decision_id=decision_id,
        feedback=feedback.feedback
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found or already decided"
        )
    
    return {"status": "denied", "decision_id": decision_id}


@router.post("/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_expired_decisions(
    db: AsyncSession = Depends(get_db)
):
    """
    Mark expired decisions as timeout.
    
    This endpoint should be called periodically (e.g., via cron job)
    to clean up decisions that exceeded their timeout.
    """
    service = GuardianGammaService(db)
    count = await service.cleanup_expired()
    
    return {"cleaned_up": count}
