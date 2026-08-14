# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
"""
AI Router - Google Vertex AI Integration
Provider:
- Google Vertex AI (Gemini) - Primary (via google-genai)
"""

import logging
import os
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.core.prompts import AIMode, SYSTEM_PROMPTS
from app.security import TelemetrySanitizer, get_current_user

# Configure Logger
logger = logging.getLogger(__name__)

# Router Setup
router = APIRouter(prefix="/api/v1/ai", tags=["AI"])

# ============================================================================
# CONFIGURATION
# ============================================================================

# AI Provider Configuration
AI_ENABLED = os.getenv("AI_ENABLED", "true").lower() == "true"
TELEMETRY_SANITIZATION_ENABLED = os.getenv("TELEMETRY_SANITIZATION_ENABLED", "true").lower() == "true"

# Google Vertex AI Config
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.5-pro")

# Initialize Security
sanitizer = TelemetrySanitizer(enabled=TELEMETRY_SANITIZATION_ENABLED)

# ============================================================================
# DATA MODELS
# ============================================================================

class AIQuery(BaseModel):
    """AI query request"""
    prompt: str = Field(..., description="Prompt to send to AI model")
    mode: AIMode = Field(AIMode.GENERAL, description="Persona mode for the AI")
    max_tokens: int = Field(1024, description="Maximum tokens to generate", ge=10, le=8192)
    temperature: float = Field(0.4, description="Temperature for generation", ge=0.0, le=1.0)
    

class AIResponse(BaseModel):
    """AI query response"""
    response: str
    model: str
    provider: str
    enabled: bool


class AIHealth(BaseModel):
    """AI service health status"""
    status: str
    enabled: bool
    model: str
    details: dict = {}

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/query", response_model=AIResponse)
async def query_ai(query: AIQuery, current_user = Depends(get_current_user)):
    """
    Query Google Vertex AI Model
    """
    if not AI_ENABLED:
        return AIResponse(response="AI is disabled in configuration.", model="none", provider="google", enabled=False)

    sanitization_result = await sanitizer.sanitize_prompt(query.prompt)
    if not sanitization_result.is_safe:
        logger.warning(f"🚨 Blocked malicious prompt: {query.prompt[:50]}...")
        raise HTTPException(status_code=403, detail="Prompt blocked by security filter")

    logger.info(f"🧠 AI Query [google][{query.mode}]: {query.prompt[:50]}...")

    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel, GenerationConfig

        vertexai.init(
            project=GOOGLE_CLOUD_PROJECT,
            location=GOOGLE_CLOUD_LOCATION
        )

        system_instr = SYSTEM_PROMPTS.get(query.mode, "")

        model = GenerativeModel(
            model_name=GOOGLE_MODEL,
            system_instruction=system_instr
        )

        generation_config = GenerationConfig(
            max_output_tokens=query.max_tokens,
            temperature=query.temperature,
        )

        response = await model.generate_content_async(
            query.prompt,
            generation_config=generation_config
        )

        response_text = response.text

        return AIResponse(
            response=response_text,
            model=GOOGLE_MODEL,
            provider="google",
            enabled=True
        )

    except ImportError as e:
        logger.error(f"❌ Google Cloud AI Platform library import failed: {e}")
        raise HTTPException(status_code=500, detail="Dependencias de 'google-cloud-aiplatform' no encontradas. Ejecute 'pip install google-cloud-aiplatform'.")
    except Exception as e:
        logger.error(f"❌ Google Vertex AI Error: {e}")
        err_msg = str(e)
        if "403" in err_msg:
            raise HTTPException(status_code=403, detail="Google Cloud Permission Denied. Check credentials/APIs.")
        if "404" in err_msg:
             raise HTTPException(status_code=404, detail=f"Model {GOOGLE_MODEL} not found or location mismatch.")
        raise HTTPException(status_code=500, detail=f"Google AI Error: {err_msg}")


@router.get("/health", response_model=AIHealth)
async def ai_health():
    """Check AI Service Health"""
    if not AI_ENABLED:
        return AIHealth(status="disabled", enabled=False, model="none")

    details = {}
    status_code = "healthy"

    try:
        # This is a configuration check, not a live connection test.
        if not GOOGLE_CLOUD_PROJECT:
            raise ValueError("GOOGLE_CLOUD_PROJECT is not set")

        status_code = "healthy"
        details = {
            "project": GOOGLE_CLOUD_PROJECT,
            "location": GOOGLE_CLOUD_LOCATION,
            "model_configured": GOOGLE_MODEL,
            "sdk": "google-cloud-aiplatform",
        }

    except Exception as e:
        status_code = "unhealthy"
        details = {"error": str(e)}

    return AIHealth(
        status=status_code,
        enabled=True,
        model=GOOGLE_MODEL,
        details=details
    )
