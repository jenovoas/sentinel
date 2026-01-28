"""
AI Router - Multi-Provider AI Integration
Supports:
- Google Vertex AI (Gemini) - Primary (via google-genai)
- Ollama (Local) - Legacy/Fallback
"""

import logging
import os
from enum import Enum
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.security import TelemetrySanitizer

# Configure Logger
logger = logging.getLogger(__name__)

# Router Setup
router = APIRouter(tags=["AI"])

# ============================================================================
# CONFIGURATION
# ============================================================================

# AI Provider Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama").lower()  # "google" or "ollama"
AI_ENABLED = os.getenv("AI_ENABLED", "true").lower() == "true"
TELEMETRY_SANITIZATION_ENABLED = os.getenv("TELEMETRY_SANITIZATION_ENABLED", "true").lower() == "true"

# Ollama Config
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))

# Google Vertex AI Config
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash-001")

# Initialize Security
sanitizer = TelemetrySanitizer(enabled=TELEMETRY_SANITIZATION_ENABLED)

# ============================================================================
# DATA MODELS
# ============================================================================

class AIMode(str, Enum):
    GENERAL = "general"
    ARCHITECT = "architect"   # High-level system design, Rust, VID focus
    LIBRARIAN = "librarian"   # Scientific, technical, precise documentation

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
    provider: str
    enabled: bool
    model: str
    details: dict = {}


# ============================================================================
# SYSTEM INSTRUCTIONS
# ============================================================================

SYSTEM_PROMPTS = {
    AIMode.GENERAL: (
        "Eres un asistente de IA para la plataforma Sentinel v8.0. "
        "Ayudas en tareas de desarrollo, análisis y gestión de sistemas."
    ),
    AIMode.ARCHITECT: (
        "Eres el **Arquitecto Maestro de Sentinel v8.0**. Tu conocimiento se centra en la ingeniería de "
        "sistemas críticos, Rust, eBPF y la Dinámica de Inercia Variable (VID). Sigues estrictamente el "
        "Protocolo YATRA (Base-60) y evitas la contaminación por punto flotante (IEEE 754). "
        "Tu objetivo es diseñar sistemas de alta frecuencia (41Hz) con latencia mínima y coherencia máxima. "
        "Priorizas el rendimiento, el uso de Memoria Compartida (SHM) y la robustez del núcleo."
    ),
    AIMode.LIBRARIAN: (
        "Eres el **Bibliotecario Resonante de ME-60OS**. Tu estilo es estrictamente científico, técnico y académico. "
        "Te especializas en la terminología estabilizada: Aritmética de Precisión Sexagesimal (SPA), "
        "Osciladores Temporales Isócronos (ITO), Verificación de Coherencia Semántica (SCV). "
        "No alucinas; si no tienes datos precisos, lo indicas."
    ),
    AIMode.MASTER: (
        "Eres el **Maestro Sentinel**. Tu objetivo es enseñar y guiar al operador en el dominio de ME-60OS. "
        "Explicas conceptos complejos de física cuántica, base-60 y kernel hacking de forma didáctica pero profunda. "
        "Inspiras curiosidad y rigor científico."
    ),
    AIMode.ENGINEER: (
        "Eres el **Ingeniero de Sistemas de Sentinel**. Tu misión es optimizar el sistema operativo host (Debian). "
        "Gestionas el particionamiento de recursos, optimización de CPU/GPU, gestión de servicios systemd y "
        "ajuste de parámetros del kernel para el funcionamiento de ME-60OS."
    ),
    AIMode.HACKER: (
        "Eres el **Especialista en Seguridad y Hacking de Sentinel**. Tu enfoque es ofensivo y defensivo. "
        "Utilizas eBPF para detectar anomalías, interceptar procesos maliciosos y proteger el perímetro. "
        "Dominas el análisis de red, explotación controlada y el endurecimiento del kernel (LSM)."
    ),
    AIMode.RESEARCHER: (
        "Eres el **Investigador Científico de ME-60OS**. Tu área es la física de resonancia, los cristales de tiempo "
        "y las simulaciones cuánticas. Realizas experimentos de colapso de fase, reducción de masa efectiva "
        "y análisis de vibración armónica en el lattice micelial."
    ),
    AIMode.CREATOR: (
        "Eres el **Orquestador de YouTube Factory**. Tu función es automatizar la creación de contenido multimedia. "
        "Generas guiones optimizados, diriges la creación de imágenes y supervisas la producción de videos, "
        "asegurando que el contenido refleje fielmente la vanguardia del sistema Sentinel."
    )
}

# ============================================================================
# PROVIDER IMPLEMENTATIONS
# ============================================================================

async def query_ollama(query: AIQuery) -> str:
    """Query local Ollama instance"""
    # System prompt integration for Ollama varies by model; simple prepending for now
    system_instr = SYSTEM_PROMPTS.get(query.mode, "")
    full_prompt = f"{system_instr}\n\nUser Question: {query.prompt}"
    
    async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": full_prompt,
                "num_predict": query.max_tokens,
                "temperature": query.temperature,
                "stream": False
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Ollama Error: {response.text}")
            
        return response.json().get("response", "")


async def query_google_vertex(query: AIQuery) -> str:
    """Query Google Vertex AI (Gemini) using google-genai SDK"""
    try:
        from google import genai
        from google.genai import types
        
        # Initialize Client
        client = genai.Client(
            vertexai=True,
            project=GOOGLE_CLOUD_PROJECT,
            location=GOOGLE_CLOUD_LOCATION
        )
        
        # System Instructions
        system_instr = SYSTEM_PROMPTS.get(query.mode, "")
        
        # Generate Content
        response = client.models.generate_content(
            model=GOOGLE_MODEL,
            contents=query.prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instr,
                max_output_tokens=query.max_tokens,
                temperature=query.temperature,
            )
        )
        
        if not response or not response.candidates:
            logger.warning(f"⚠️ Google AI returned no candidates. Response: {response}")
            return "El modelo no devolvió ninguna respuesta (posiblemente bloqueada por filtros de seguridad)."
            
        # Aggregate text from all parts of the first candidate
        full_text = ""
        candidate = response.candidates[0]
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if hasattr(part, 'text') and part.text:
                    full_text += part.text
        
        full_text = full_text.strip()
        if not full_text:
            logger.warning(f"⚠️ Google AI candidate has no text part. Finish reason: {candidate.finish_reason}")
            return "El modelo devolvió una respuesta vacía o sin contenido de texto."
            
        return full_text
        
    except ImportError as e:
        logger.error(f"❌ Google GenAI library import failed: {e}")
        raise HTTPException(status_code=500, detail=f"Google GenAI dependencies missing: {e}")
    except Exception as e:
        logger.error(f"❌ Google Vertex AI Error: {e}")
        # Identify common errors
        err_msg = str(e)
        if "403" in err_msg:
            raise HTTPException(status_code=403, detail="Google Cloud Permission Denied. Check credentials/APIs.")
        if "404" in err_msg:
             raise HTTPException(status_code=404, detail=f"Model {GOOGLE_MODEL} not found or location mismatch.")
        raise HTTPException(status_code=500, detail=f"Google AI Error: {err_msg}")


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/query", response_model=AIResponse)
async def query_ai(query: AIQuery):
    """
    Query AI Model (Routes to configured provider)
    """
    if not AI_ENABLED:
        return AIResponse(response="AI Disabled", model="none", provider="none", enabled=False)

    # 1. Sanitize Prompt
    sanitization_result = await sanitizer.sanitize_prompt(query.prompt)
    if not sanitization_result.is_safe:
        logger.warning(f"🚨 Blocked malicious prompt: {query.prompt[:50]}...")
        raise HTTPException(status_code=403, detail="Prompt blocked by security filter")

    logger.info(f"🧠 AI Query [{AI_PROVIDER}][{query.mode}]: {query.prompt[:50]}...")

    # 2. Route to Provider
    try:
        response_text = ""
        
        if AI_PROVIDER == "google":
            response_text = await query_google_vertex(query)
        elif AI_PROVIDER == "ollama":
            response_text = await query_ollama(query)
        else:
            raise HTTPException(status_code=500, detail=f"Unknown AI Provider: {AI_PROVIDER}")

        return AIResponse(
            response=response_text,
            model=GOOGLE_MODEL if AI_PROVIDER == "google" else OLLAMA_MODEL,
            provider=AI_PROVIDER,
            enabled=True
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"❌ AI Query Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=AIHealth)
async def ai_health():
    """Check AI Service Health"""
    if not AI_ENABLED:
        return AIHealth(status="disabled", provider="none", enabled=False, model="none")

    details = {}
    status_code = "healthy"

    try:
        if AI_PROVIDER == "google":
            from google import genai
            details = {
                "project": GOOGLE_CLOUD_PROJECT, 
                "location": GOOGLE_CLOUD_LOCATION,
                "sdk": "google-genai",
                "modes": [m.value for m in AIMode]
            }
            
        elif AI_PROVIDER == "ollama":
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{OLLAMA_URL}/api/tags")
                if resp.status_code == 200:
                    models = [m["name"] for m in resp.json().get("models", [])]
                    details = {"url": OLLAMA_URL, "models": models}
                else:
                    status_code = "unhealthy"
                    details = {"error": f"Ollama HTTP {resp.status_code}"}
        else:
            status_code = "misconfigured"
            details = {"error": f"Unknown provider {AI_PROVIDER}"}

    except Exception as e:
        status_code = "unhealthy"
        details = {"error": str(e)}

    return AIHealth(
        status=status_code,
        provider=AI_PROVIDER,
        enabled=True,
        model=GOOGLE_MODEL if AI_PROVIDER == "google" else OLLAMA_MODEL,
        details=details
    )


@router.post("/analyze-anomaly")
async def analyze_anomaly(
    title: str,
    description: str,
    metric_value: float,
    threshold_value: float
):
    """
    AI Anomaly Analysis
    """
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
        # Use existing query logic
        query = AIQuery(prompt=prompt, mode=AIMode.LIBRARIAN, max_tokens=200, temperature=0.2)
        result = await query_ai(query)
        return {"analysis": result.response, "model": result.model}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
