"""
Guardian Gamma Service - Human-in-the-Loop Decision System

This service manages critical security decisions that require human validation.
Guardian Alpha (eBPF) and Guardian Beta (Dual-Lane) can escalate decisions
to Guardian Gamma when confidence is below threshold.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
import asyncio
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import GammaDecision


class GuardianSource(str, Enum):
    """Source guardian that created the decision"""
    ALPHA = "alpha"
    BETA = "beta"


class DecisionType(str, Enum):
    """Type of decision requiring human validation"""
    BINARY_BLOCK = "binary_block"
    ANOMALY_DETECTED = "anomaly_detected"
    TELEMETRY_SUSPICIOUS = "telemetry_suspicious"
    THRESHOLD_EXCEEDED = "threshold_exceeded"


class DecisionStatus(str, Enum):
    """Status of the decision"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    TIMEOUT = "timeout"


class GuardianGammaService:
    """
    Service for managing human-in-the-loop decisions.
    
    Workflow:
    1. Guardian Alpha/Beta creates decision request
    2. Decision stored in queue with timeout
    3. Human reviews via dashboard
    4. Human approves/denies with feedback
    5. System learns from feedback
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_decision(
        self,
        guardian: GuardianSource,
        decision_type: DecisionType,
        context: Dict[str, Any],
        confidence: float,
        evidence: Optional[Dict[str, Any]] = None,
        timeout_minutes: int = 30
    ) -> int:
        """
        Create a new decision request for human validation.
        
        Args:
            guardian: Source guardian (alpha or beta)
            decision_type: Type of decision
            context: Decision context (binary path, metric, etc)
            confidence: AI confidence score (0-1)
            evidence: Supporting evidence
            timeout_minutes: Minutes before auto-deny
            
        Returns:
            Decision ID
        """
        timeout_at = datetime.utcnow() + timedelta(minutes=timeout_minutes)
        
        decision = GammaDecision(
            guardian_source=guardian.value,
            decision_type=decision_type.value,
            context=context,
            evidence=evidence or {},
            confidence=confidence,
            status=DecisionStatus.PENDING.value,
            timeout_at=timeout_at
        )
        
        self.db.add(decision)
        await self.db.commit()
        await self.db.refresh(decision)
        
        return decision.id
    
    async def get_pending_decisions(
        self,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all pending decisions ordered by priority.
        
        Priority:
        1. Low confidence (needs human judgment)
        2. Oldest first (FIFO)
        
        Returns:
            List of pending decisions
        """
        query = (
            select(GammaDecision)
            .where(GammaDecision.status == DecisionStatus.PENDING.value)
            .where(GammaDecision.timeout_at > datetime.utcnow())
            .order_by(GammaDecision.confidence.asc())  # Low confidence first
            .order_by(GammaDecision.created_at.asc())  # Then FIFO
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        decisions = result.scalars().all()
        
        return [
            {
                "id": d.id,
                "guardian": d.guardian_source,
                "type": d.decision_type,
                "context": d.context,
                "evidence": d.evidence,
                "confidence": d.confidence,
                "created_at": d.created_at.isoformat(),
                "timeout_at": d.timeout_at.isoformat()
            }
            for d in decisions
        ]
    
    async def approve_decision(
        self,
        decision_id: int,
        feedback: Optional[str] = None
    ) -> bool:
        """
        Approve a decision and provide feedback.
        
        Args:
            decision_id: Decision ID
            feedback: Human feedback for learning
            
        Returns:
            True if approved, False if not found or already decided
        """
        query = (
            update(GammaDecision)
            .where(GammaDecision.id == decision_id)
            .where(GammaDecision.status == DecisionStatus.PENDING.value)
            .values(
                status=DecisionStatus.APPROVED.value,
                human_decision="approved",
                human_feedback=feedback,
                decided_at=datetime.utcnow()
            )
        )
        
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def deny_decision(
        self,
        decision_id: int,
        feedback: Optional[str] = None
    ) -> bool:
        """
        Deny a decision and provide feedback.
        
        Args:
            decision_id: Decision ID
            feedback: Human feedback for learning
            
        Returns:
            True if denied, False if not found or already decided
        """
        query = (
            update(GammaDecision)
            .where(GammaDecision.id == decision_id)
            .where(GammaDecision.status == DecisionStatus.PENDING.value)
            .values(
                status=DecisionStatus.DENIED.value,
                human_decision="denied",
                human_feedback=feedback,
                decided_at=datetime.utcnow()
            )
        )
        
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def wait_for_decision(
        self,
        decision_id: int,
        timeout_seconds: int = 1800  # 30 minutes
    ) -> Optional[str]:
        """
        Wait for human decision (blocking).
        
        Used by Guardian Alpha/Beta to wait for human approval.
        
        Args:
            decision_id: Decision ID
            timeout_seconds: Max wait time
            
        Returns:
            "approved", "denied", or None if timeout
        """
        start_time = datetime.utcnow()
        
        while True:
            # Check if decision was made
            query = select(GammaDecision).where(GammaDecision.id == decision_id)
            result = await self.db.execute(query)
            decision = result.scalar_one_or_none()
            
            if not decision:
                return None
            
            if decision.status != DecisionStatus.PENDING.value:
                return decision.human_decision
            
            # Check timeout
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            if elapsed > timeout_seconds:
                # Auto-deny on timeout
                await self.deny_decision(decision_id, "Auto-denied: timeout")
                return "denied"
            
            # Wait before checking again
            await asyncio.sleep(1)
    
    async def cleanup_expired(self) -> int:
        """
        Mark expired decisions as timeout.
        
        Returns:
            Number of decisions marked as timeout
        """
        query = (
            update(GammaDecision)
            .where(GammaDecision.status == DecisionStatus.PENDING.value)
            .where(GammaDecision.timeout_at <= datetime.utcnow())
            .values(
                status=DecisionStatus.TIMEOUT.value,
                human_decision="timeout",
                decided_at=datetime.utcnow()
            )
        )
        
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.rowcount


async def get_gamma_service(db: AsyncSession = None) -> GuardianGammaService:
    """Get Guardian Gamma service instance"""
    if db is None:
        async for session in get_db():
            db = session
            break
    return GuardianGammaService(db)
