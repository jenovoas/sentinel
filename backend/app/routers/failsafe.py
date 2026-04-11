"""
Fail-Safe Security Layer - Event Router

Sends events to N8N playbooks when primary systems fail to respond.
Acts as the bridge between Sentinel and automated remediation.

Events are queued and sent to N8N webhooks with proper authentication.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any
from datetime import datetime, UTC
import httpx
import os
import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.failsafe_service import track_execution, update_execution, get_failsafe_stats

router = APIRouter(prefix="/api/v1/failsafe", tags=["fail-safe"])
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

N8N_BASE_URL = os.getenv("N8N_BASE_URL", "http://n8n:5678")
N8N_WEBHOOK_TOKEN = os.getenv("N8N_WEBHOOK_TOKEN", "")

# ============================================================================
# MODELS
# ============================================================================

class FailSafeEvent(BaseModel):
    """Event to trigger fail-safe playbook"""
    playbook: Literal[
        "backup_recovery",
        "intrusion_lockdown", 
        "health_failsafe",
        "integrity_check",
        "offboarding",
        "auto_remediation"
    ]
    severity: Literal["low", "medium", "high", "critical"]
    context: Dict[str, Any] = Field(..., description="Event-specific context")
    triggered_by: str = Field(..., description="What triggered this (e.g., 'backup_failed')")
    wait_time_minutes: int = Field(default=10, description="How long to wait before triggering")


class PlaybookStatus(BaseModel):
    """Status of a playbook execution"""
    playbook: str
    status: Literal["idle", "waiting", "triggered", "success", "failed"]
    last_run: Optional[str] = None
    last_outcome: Optional[str] = None
    execution_count: int = 0
    success_rate: float = 0.0


# ============================================================================
# PLAYBOOK WEBHOOKS
# ============================================================================

PLAYBOOK_WEBHOOKS = {
    "backup_recovery": f"{N8N_BASE_URL}/webhook/failsafe/backup-recovery",
    "intrusion_lockdown": f"{N8N_BASE_URL}/webhook/failsafe/intrusion-lockdown",
    "health_failsafe": f"{N8N_BASE_URL}/webhook/failsafe/health-failsafe",
    "integrity_check": f"{N8N_BASE_URL}/webhook/failsafe/integrity-check",
    "offboarding": f"{N8N_BASE_URL}/webhook/failsafe/offboarding",
    "auto_remediation": f"{N8N_BASE_URL}/webhook/failsafe/auto-remediation",
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def send_to_n8n(playbook: str, event_data: Dict[str, Any], execution_id: uuid.UUID) -> bool:
    """
    Send event to N8N webhook
    
    Args:
        playbook: Playbook name
        event_data: Event context and metadata
        execution_id: ID of the execution record in database
        
    Returns:
        True if successful, False otherwise
    """
    webhook_url = PLAYBOOK_WEBHOOKS.get(playbook)
    
    if not webhook_url:
        logger.error(f"Unknown playbook: {playbook}")
        return False
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                webhook_url,
                json={
                    **event_data,
                    "execution_id": str(execution_id),
                    "timestamp": datetime.now(UTC).isoformat(),
                    "source": "sentinel",
                },
                headers={
                    "Authorization": f"Bearer {N8N_WEBHOOK_TOKEN}",
                    "Content-Type": "application/json",
                }
            )
            
            if response.status_code == 200:
                logger.info(f"✓ Sent event to {playbook} playbook")
                return True
            else:
                logger.error(f"✗ N8N webhook failed: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"✗ Error sending to N8N: {e}")
        return False


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/trigger")
async def trigger_failsafe(
    event: FailSafeEvent,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger a fail-safe playbook
    
    This endpoint is called by Sentinel when:
    - An alert is not acknowledged in time
    - A critical event needs automated response
    - Primary systems fail to respond
    
    The event is queued and sent to N8N after the specified wait time.
    """
    try:
        # 1. Log the trigger
        logger.warning(
            f"🛡️ Fail-safe triggered: {event.playbook} "
            f"(severity: {event.severity}, wait: {event.wait_time_minutes}m)"
        )
        
        # 2. Track in database
        execution = await track_execution(
            db=db,
            playbook=event.playbook,
            triggered_by=event.triggered_by,
            severity=event.severity,
            context_data=event.context
        )

        # In production, you'd queue this with Redis/Celery
        # For now, send immediately in background
        background_tasks.add_task(
            send_to_n8n,
            event.playbook,
            {
                "playbook": event.playbook,
                "severity": event.severity,
                "context": event.context,
                "triggered_by": event.triggered_by,
                "wait_time_minutes": event.wait_time_minutes,
            },
            execution.id
        )
        
        return {
            "status": "queued",
            "execution_id": str(execution.id),
            "playbook": event.playbook,
            "message": f"Fail-safe playbook '{event.playbook}' queued for execution",
            "wait_time_minutes": event.wait_time_minutes,
        }
        
    except Exception as e:
        logger.error(f"Error triggering fail-safe: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger fail-safe: {str(e)}"
        )


@router.get("/status")
async def get_failsafe_status(db: AsyncSession = Depends(get_db)):
    """
    Get fail-safe layer status
    
    Returns:
        - Active playbooks
        - Recent executions
        - Success rates
    """
    try:
        stats = await get_failsafe_stats(db)
        return stats
    except Exception as e:
        logger.error(f"Error getting fail-safe status: {e}")
        # Fallback to some default structure if DB fails, but with real error logging
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch fail-safe status: {str(e)}"
        )


@router.post("/execution/{execution_id}/update")
async def update_execution_status(
    execution_id: uuid.UUID,
    status: Literal["success", "failed", "triggered", "waiting"],
    outcome: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Update the status of a fail-safe execution
    
    This is typically called by N8N after a playbook completes.
    """
    try:
        execution = await update_execution(db, execution_id, status, outcome)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")

        return {"status": "updated", "execution_id": str(execution_id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/playbooks")
async def list_playbooks():
    """
    List all available fail-safe playbooks
    
    Returns:
        List of playbooks with descriptions
    """
    return {
        "playbooks": [
            {
                "id": "backup_recovery",
                "name": "Backup Recovery",
                "description": "Retry failed backups with verification and multi-channel notification",
                "trigger": "Backup fails + no acknowledge in 15 minutes",
                "actions": ["Retry backup", "Verify integrity", "Notify team", "Create ticket"],
            },
            {
                "id": "intrusion_lockdown",
                "name": "Intrusion Lockdown",
                "description": "Automatically block malicious IPs and lock compromised accounts",
                "trigger": "Critical security event + no response in 10 minutes",
                "actions": ["Block IP", "Lock account", "Revoke sessions", "Notify security"],
            },
            {
                "id": "health_failsafe",
                "name": "Health Failsafe",
                "description": "Auto-restart failed services and switch to standby nodes",
                "trigger": "Health check fails + no response in 5 minutes",
                "actions": ["Verify failure", "Restart service", "Monitor recovery", "Escalate"],
            },
            {
                "id": "integrity_check",
                "name": "Backup Integrity Check",
                "description": "Daily validation of backup integrity and RPO compliance",
                "trigger": "Scheduled daily at 2 AM",
                "actions": ["Verify checksums", "Check RPO", "Test restore", "Generate report"],
            },
            {
                "id": "offboarding",
                "name": "Secure Offboarding",
                "description": "Complete access revocation for departing users",
                "trigger": "User marked for offboarding + no completion in 2 hours",
                "actions": ["Disable account", "Revoke keys", "Remove groups", "Audit trail"],
            },
            {
                "id": "auto_remediation",
                "name": "Anomaly Auto-Remediation",
                "description": "Automatically fix detected anomalies (CPU, memory, disk)",
                "trigger": "AI detects anomaly + confidence > 95% + no response in 5 min",
                "actions": ["Verify anomaly", "Identify cause", "Apply fix", "Monitor impact"],
            },
        ]
    }


@router.get("/health")
async def health_check():
    """Health check for fail-safe layer"""
    return {
        "status": "healthy",
        "n8n_configured": bool(N8N_WEBHOOK_TOKEN),
        "playbooks_available": len(PLAYBOOK_WEBHOOKS),
    }
