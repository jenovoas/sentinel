"""
API Endpoint for AIOpsShield Integration with n8n

Provides sanitization endpoint for n8n workflow to create "Air Gap" before LLM.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging

from app.security.telemetry_sanitizer import TelemetrySanitizer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/security", tags=["security"])

# Global sanitizer instance
sanitizer = TelemetrySanitizer(enabled=True)


class SanitizeRequest(BaseModel):
    """Request to sanitize a prompt"""
    prompt: str


class SanitizeResponse(BaseModel):
    """Response from sanitization"""
    is_safe: bool
    sanitized_prompt: Optional[str] = None
    blocked_patterns: List[str] = []
    threat_level: str = "none"  # none, low, medium, high, critical


@router.post("/sanitize", response_model=SanitizeResponse)
async def sanitize_prompt(request: SanitizeRequest):
    """
    Sanitize a prompt before sending to LLM
    
    This is the CRITICAL "Air Gap" that prevents AIOpsDoom attacks.
    
    Flow:
    1. n8n receives log
    2. n8n calls this endpoint
    3. If safe → continue to Ollama
    4. If unsafe → block and alert
    
    Args:
        request: Prompt to sanitize
        
    Returns:
        Sanitization result with safety status
    """
    try:
        # Sanitize the prompt
        result = await sanitizer.sanitize_prompt(request.prompt)
        
        # Determine threat level
        threat_level = "none"
        if not result.is_safe:
            num_patterns = len(result.blocked_patterns)
            if num_patterns >= 5:
                threat_level = "critical"
            elif num_patterns >= 3:
                threat_level = "high"
            elif num_patterns >= 2:
                threat_level = "medium"
            else:
                threat_level = "low"
        
        # Log if blocked
        if not result.is_safe:
            logger.warning(
                f"AIOpsDoom attack blocked: {num_patterns} patterns detected\n"
                f"Patterns: {result.blocked_patterns}\n"
                f"Threat Level: {threat_level}"
            )
        
        return SanitizeResponse(
            is_safe=result.is_safe,
            sanitized_prompt=result.sanitized_prompt if result.is_safe else None,
            blocked_patterns=result.blocked_patterns,
            threat_level=threat_level
        )
    
    except Exception as e:
        logger.error(f"Sanitization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sanitization error: {str(e)}")


@router.post("/alerts/aiops-attack")
async def alert_aiops_attack(
    threat_type: str,
    blocked_patterns: List[str],
    original_log: str,
    timestamp: str
):
    """
    Receive alert from n8n about AIOpsDoom attack
    
    This endpoint is called when n8n detects an unsafe log.
    
    Args:
        threat_type: Type of threat (e.g., "AIOpsDoom")
        blocked_patterns: List of patterns that were blocked
        original_log: The original malicious log
        timestamp: When the attack was detected
    """
    logger.critical(
        f"AIOpsDoom ATTACK DETECTED\n"
        f"Type: {threat_type}\n"
        f"Patterns: {blocked_patterns}\n"
        f"Timestamp: {timestamp}\n"
        f"Original Log: {original_log[:200]}..."
    )
    
    # TODO: Send to PagerDuty/Slack/etc
    # TODO: Store in forensic database
    # TODO: Update threat intelligence
    
    return {
        "status": "alert_received",
        "threat_type": threat_type,
        "patterns_count": len(blocked_patterns),
        "timestamp": timestamp
    }


@router.post("/aiops/decision")
async def execute_aiops_decision(
    llm_response: dict,
    original_log: str,
    decision_context: dict
):
    """
    Execute decision from LLM after sanitization
    
    This endpoint receives the LLM's decision and executes it.
    
    Args:
        llm_response: Response from Ollama
        original_log: The original (sanitized) log
        decision_context: Context about the decision
    """
    logger.info(
        f"Executing AI decision\n"
        f"Sanitized: {decision_context.get('sanitized', False)}\n"
        f"Timestamp: {decision_context.get('timestamp')}"
    )
    
    # TODO: Parse LLM response
    # TODO: Execute decision (e.g., scale, alert, remediate)
    # TODO: Log to audit trail
    
    return {
        "status": "decision_executed",
        "sanitized": decision_context.get("sanitized", False),
        "timestamp": decision_context.get("timestamp")
    }
