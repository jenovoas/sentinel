"""
AI Router - Local LLM Integration with Ollama
Provides endpoints for querying local AI models
"""

import logging
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import httpx

from app.security import TelemetrySanitizer

logger = logging.getLogger(__name__)

router = APIRouter(tags=["AI"])

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")
AI_ENABLED = os.getenv("AI_ENABLED", "true").lower() == "true"
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))
TELEMETRY_SANITIZATION_ENABLED = os.getenv("TELEMETRY_SANITIZATION_ENABLED", "true").lower() == "true"

# Initialize telemetry sanitizer
sanitizer = TelemetrySanitizer(enabled=TELEMETRY_SANITIZATION_ENABLED)


class AIQuery(BaseModel):
    """AI query request"""
    prompt: str = Field(..., description="Prompt to send to AI model")
    max_tokens: int = Field(100, description="Maximum tokens to generate", ge=10, le=500)
    temperature: float = Field(0.3, description="Temperature for generation", ge=0.0, le=1.0)


class AIResponse(BaseModel):
    """AI query response"""
    response: str
    model: str
    enabled: bool


class AIHealth(BaseModel):
    """AI service health status"""
    status: str
    enabled: bool
    url: str
    model: str
    models_available: list = []


@router.post("/query", response_model=AIResponse)
async def query_ai(query: AIQuery):
    """
    Query local AI model for insights
    
    Example:
        POST /api/v1/ai/query
        {
            "prompt": "Explica qué es una anomalía de CPU",
            "max_tokens": 100,
            "temperature": 0.3
        }
    """
    if not AI_ENABLED:
        return AIResponse(
            response="AI is disabled. Set AI_ENABLED=true to enable.",
            model=OLLAMA_MODEL,
            enabled=False
        )
    
    # 🛡️ SECURITY: Sanitize prompt to prevent adversarial injection
    sanitization_result = await sanitizer.sanitize_prompt(query.prompt)
    
    if not sanitization_result.is_safe:
        logger.warning(
            f"🚨 Blocked malicious prompt: {query.prompt[:100]}...",
            extra={
                "blocked_patterns": sanitization_result.blocked_patterns,
                "confidence": sanitization_result.confidence
            }
        )
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Potentially malicious prompt detected",
                "blocked_patterns": sanitization_result.blocked_patterns,
                "message": "Your prompt contains patterns that could be harmful. Please rephrase."
            }
        )
    
    logger.info(f"✅ Prompt sanitization passed: {query.prompt[:50]}...")
    
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": query.prompt,
                    "num_predict": query.max_tokens,
                    "temperature": query.temperature,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                ai_response = response.json().get("response", "")
                logger.info(f"🤖 AI query successful: {query.prompt[:50]}...")
                return AIResponse(
                    response=ai_response,
                    model=OLLAMA_MODEL,
                    enabled=True
                )
            else:
                logger.error(f"❌ Ollama returned status {response.status_code}")
                raise HTTPException(
                    status_code=500,
                    detail=f"AI service returned status {response.status_code}"
                )
    
    except httpx.TimeoutException:
        logger.error("❌ Ollama request timed out")
        raise HTTPException(status_code=504, detail="AI service timeout")
    except httpx.ConnectError:
        logger.error("❌ Cannot connect to Ollama")
        raise HTTPException(status_code=503, detail="AI service unavailable")
    except Exception as e:
        logger.error(f"❌ AI query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=AIHealth)
async def ai_health():
    """
    Check AI service health and available models
    
    Returns:
        AI service status and list of available models
    """
    if not AI_ENABLED:
        return AIHealth(
            status="disabled",
            enabled=False,
            url=OLLAMA_URL,
            model=OLLAMA_MODEL,
            models_available=[]
        )
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            
            if response.status_code == 200:
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]
                logger.info(f"✅ AI service healthy, {len(models)} models available")
                return AIHealth(
                    status="healthy",
                    enabled=True,
                    url=OLLAMA_URL,
                    model=OLLAMA_MODEL,
                    models_available=models
                )
            else:
                return AIHealth(
                    status="unhealthy",
                    enabled=True,
                    url=OLLAMA_URL,
                    model=OLLAMA_MODEL,
                    models_available=[]
                )
    
    except Exception as e:
        logger.warning(f"⚠️ AI health check failed: {e}")
        return AIHealth(
            status="unhealthy",
            enabled=True,
            url=OLLAMA_URL,
            model=OLLAMA_MODEL,
            models_available=[]
        )


@router.post("/analyze-anomaly")
async def analyze_anomaly(
    title: str,
    description: str,
    metric_value: float,
    threshold_value: float
):
    """
    Get AI analysis of an anomaly
    
    Args:
        title: Anomaly title
        description: Anomaly description
        metric_value: Actual metric value
        threshold_value: Threshold that was exceeded
    
    Returns:
        AI-generated explanation and recommendations
    """
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI is disabled")
    
    prompt = f"""Analiza esta anomalía del sistema y proporciona:
1. Explicación breve (1-2 líneas)
2. Posibles causas (máximo 3)
3. Recomendación de acción

Anomalía: {title}
Descripción: {description}
Valor actual: {metric_value}
Umbral: {threshold_value}

Responde en español, máximo 100 palabras."""
    
    try:
        query = AIQuery(prompt=prompt, max_tokens=150, temperature=0.3)
        result = await query_ai(query)
        return {
            "analysis": result.response,
            "model": result.model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
