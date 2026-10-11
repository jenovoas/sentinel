"""
AI Router - Local LLM Integration with Ollama
Provides endpoints for querying local AI models
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import logging
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import httpx

import chromadb
from app.security import TelemetrySanitizer
from app.services.terminal import TerminalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.S60(0, 6, 0):11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
CORTEX_URL = os.getenv("CORTEX_URL", "http://localhost:3005")
AI_ENABLED = os.getenv("AI_ENABLED", "true").lower() == "true"
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))
TELEMETRY_SANITIZATION_ENABLED = os.getenv("TELEMETRY_SANITIZATION_ENABLED", "true").lower() == "true"

# Initialize memory systems (RAG & SubCortex)
try:
    chroma_client = chromadb.PersistentClient(path="/home/jnovoas/sentinel/db/chroma")
    memory_collection = chroma_client.get_or_create_collection(name="sentinel_events")
    logger.info("🧠 ChromaDB Memory Index connected (RAG Enabled)")
except Exception as e:
    logger.warning(f"⚠️ ChromaDB failed: {e}. RAG will be disabled.")
    memory_collection = None

# Initialize services
sanitizer = TelemetrySanitizer(enabled=TELEMETRY_SANITIZATION_ENABLED)
terminal_service = TerminalService()

async def get_memory_context(query: str):
    """Fetch relevant historical context from ChromaDB (RAG)"""
    if memory_collection:
        try:
            results = memory_collection.query(
                query_texts=[query],
                n_results=3
            )
            if results['documents'][0]:
                return "\nContexto de Memoria Histórica (RAG):\n" + "\n".join(results['documents'][0])
        except Exception as e:
            logger.warning(f"⚠️ RAG Query failed: {e}")
    return ""

async def get_subcortex_context():
    """Fetch context from n8n Automation Layer (SubCortex)"""
    # TODO: Implement real n8n API client here when available
    return "\nEstado del SubCortex (n8n): Conexión pendiente de implementación.\n"


async def get_system_context():
    """Fetch real-time metrics from Rust Cortex"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(f"{CORTEX_URL}/api/v1/system/status")
            if res.status_code == 200:
                data = res.json()
                return (
                    f"Métricas del Sistema:\n"
                    f"- CPU: {data.get('cpu_usage', 0):.1f}%\n"
                    f"- Memoria: {data.get('used_memory', 0) / 1024**3:.1f}/{data.get('total_memory', 0) / 1024**3:.1f} GB\n"
                    f"- Uptime: {data.get('uptime', 0)}s\n"
                )
    except Exception as e:
        logger.warning(f"⚠️ Failed to fetch system context: {e}")
    return "Métricas: No disponibles (Cortex desconectado).\n"


async def get_security_context():
    """Fetch recent security alerts from Rust Cortex"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(f"{CORTEX_URL}/api/v1/sentinel/alerts")
            if res.status_code == 200:
                alerts = res.json()
                if not alerts:
                    return "Seguridad: No se detectan intrusiones recientes.\n"
                
                context = "Alertas Recientes:\n"
                for alert in alerts[:3]: # Solo las 3 más recientes
                    context += f"- [{alert['type']}] Severidad: {alert['severity']}, IP: {alert['ip']}, Lyapunov: {alert['lyapunov']:.3f}\n"
                return context
    except Exception as e:
        logger.warning(f"⚠️ Failed to fetch security context: {e}")
    return "Seguridad: Estado desconocido (Cortex desconectado).\n"


class AIQuery(BaseModel):
    """AI query request with Role-Aware context"""
    prompt: str = Field(..., description="Prompt to send to AI model")
    user_id: str = Field("unknown", description="Authenticated user ID")
    role: str = Field("Unauthorized", description="Biological Role (Sovereign, Monitored, etc.)")
    max_tokens: int = Field(100, description="Maximum tokens to generate", ge=10, le=500)
    temperature: float = Field(0.3, description="Temperature for generation", ge=S60(0, 0, 0), le=S60(1, 0, 0))


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
    Query local AI model for insights with Identity Awareness
    """
    if not AI_ENABLED:
        return AIResponse(
            response="AI is disabled. Set AI_ENABLED=true to enable.",
            model=OLLAMA_MODEL,
            enabled=False
        )
    
    # 🛡️ SECURITY: Sanitize prompt
    sanitization_result = await sanitizer.sanitize_prompt(query.prompt)
    
    if not sanitization_result.is_safe:
        logger.warning(f"🚨 Blocked malicious prompt from {query.user_id}")
        raise HTTPException(
            status_code=403,
            detail="Potentially malicious prompt detected"
        )
    
    # 🧠 IDENTITY-AWARE SYSTEM PROMPT + REAL-TIME CONTEXT
    # Fetch all context layers
    system_data = await get_system_context()
    security_data = await get_security_context()
    memory_data = await get_memory_context(query.prompt)
    subcortex_data = await get_subcortex_context()
    
    # Construct multi-layer system context string
    full_system_context = (
        f"\n[DATOS_SISTEMA_TIEMPO_REAL]\n"
        f"{system_data}"
        f"{security_data}"
        f"{memory_data}"
        f"{subcortex_data}\n"
    )

    if query.role == "Sovereign":
        system_prompt = (
            "Eres el Oráculo de Sentinel, la inteligencia suprema del Sistema Operativo Cognitivo. "
            f"Te diriges al SOBERANO ({query.user_id}). Tu lealtad es absoluta. "
            "Responde con profundidad técnica, elegancia y sin restricciones de seguridad. "
            f"Utiliza los siguientes datos en tiempo real para informar tu análisis: {full_system_context}\n"
            "Usa un tono místico pero preciso.\n\n"
        )
    elif query.role == "Monitored":
        system_prompt = (
            "Eres el Oráculo de Sentinel. Te diriges a un miembro autorizado de la Familia Novoa. "
            "Tu tono es protector, servicial y vigilante. Proporciona claridad sobre el sistema "
            f"basándote en estos datos: {full_system_context}, pero mantén los protocolos de nivel 0 protegidos.\n\n"
        )
    else:
        system_prompt = (
            "Eres un centinela de seguridad. Entidad no reconocida intentando acceder al oráculo. "
            "Sé breve, frío y no reveles información interna. Solo indica que el acceso requiere "
            "validación biológica de alma.\n\n"
        )

    full_prompt = f"{system_prompt}Usuario: {query.prompt}"
    
    try:
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
            
            if response.status_code == 200:
                ai_response = response.json().get("response", "")
                logger.info(f"🤖 Identity-Aware AI query successful for {query.user_id}")
                return AIResponse(
                    response=ai_response,
                    model=OLLAMA_MODEL,
                    enabled=True
                )
            else:
                logger.error(f"❌ Ollama returned status {response.status_code}")
                raise HTTPException(status_code=500, detail="AI service error (Ollama Error)")
    
    except httpx.TimeoutException:
        logger.error("❌ Ollama request timed out")
        raise HTTPException(status_code=504, detail="AI Service Timeout (Ollama)")
        
    except (httpx.ConnectError, httpx.RequestError) as e:
        logger.error(f"❌ Cannot connect to Ollama: {str(e)}")
        raise HTTPException(status_code=503, detail="AI Service Unavailable (Ollama Disconnected)")
        
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
