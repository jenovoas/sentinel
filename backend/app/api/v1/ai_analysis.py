"""
AI Analysis API with AIOpsShield Protection
Provides AI-powered log and metric analysis with built-in AIOpsDoom defense
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import logging

from app.services.safe_ollama import safe_ollama
from app.services.aiops_shield import ThreatLevel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Analysis"])


class AnalysisRequest(BaseModel):
    """Request for AI analysis"""
    question: str
    context: Optional[str] = None  # Logs, metrics, etc.
    bypass_shield: bool = False  # Emergency bypass (admin only)


class AnalysisResponse(BaseModel):
    """AI analysis response with sanitization metadata"""
    answer: str
    sanitization: Optional[dict] = None
    warning: Optional[str] = None


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_with_ai(request: AnalysisRequest):
    """
    Analyze logs/metrics with AI (protected by AIOpsShield)
    
    Example:
        POST /api/v1/ai/analyze
        {
            "question": "Why is CPU usage high?",
            "context": "ERROR: Process python3 consuming 95% CPU..."
        }
    """
    try:
        # Call SafeOllama (automatically sanitizes)
        result = await safe_ollama.generate(
            model="phi3:mini",
            prompt=request.question,
            context=request.context,
            bypass_shield=request.bypass_shield
        )
        
        # Check if blocked
        if result.get('sanitization', {}).get('blocked'):
            logger.error(f"Malicious content blocked: {result['sanitization']}")
            return AnalysisResponse(
                answer="⚠️ Malicious content detected and blocked by AIOpsShield",
                sanitization=result['sanitization'],
                warning="Your request contained adversarial patterns and was blocked for security."
            )
        
        # Return safe response
        warning = None
        if result.get('sanitization'):
            threat_level = result['sanitization'].get('threat_level')
            if threat_level == ThreatLevel.SUSPICIOUS.value:
                warning = "Some suspicious patterns were detected and sanitized."
        
        return AnalysisResponse(
            answer=result['response'],
            sanitization=result.get('sanitization'),
            warning=warning
        )
        
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/shield/stats")
async def get_shield_stats():
    """Get AIOpsShield statistics"""
    try:
        stats = await safe_ollama.get_stats()
        return {
            "status": "active",
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Failed to get shield stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/logs")
async def analyze_logs(
    logs: str,
    question: str = "What issues do you see in these logs?"
):
    """
    Analyze logs with AI (protected)
    
    Example:
        POST /api/v1/ai/analyze/logs
        {
            "logs": "ERROR: Connection timeout...",
            "question": "What's causing the timeout?"
        }
    """
    try:
        result = await safe_ollama.analyze_logs(logs, question)
        
        return AnalysisResponse(
            answer=result['response'],
            sanitization=result.get('sanitization')
        )
        
    except Exception as e:
        logger.error(f"Log analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
