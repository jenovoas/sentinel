# Sentinel AI Backend API - Documentación Técnica

## Descripción General

El backend de Sentinel integra IA local (Ollama) con un sistema de **Identity-Aware Prompting** que adapta las respuestas según el rol del usuario y el contexto del sistema en tiempo real.

**Características:**
- 🔐 **Identity-Aware**: Respuestas personalizadas por rol (Sovereign, Monitored, Unauthorized)
- 🧠 **RAG Integration**: Memoria histórica con ChromaDB
- 🛡️ **Security First**: Sanitización de prompts, validación de entrada
- 📊 **Real-Time Context**: Métricas del sistema, alertas de seguridad
- ⚡ **GPU Accelerated**: Ollama con NVIDIA GPU (GTX 1050)

---

## Endpoints

### 1. POST `/api/v1/ai/query`

Consulta al modelo de IA con contexto completo del sistema.

#### Request

```json
{
  "prompt": "Analiza el estado del sistema",
  "user_id": "jaime@sentinel.local",
  "role": "Sovereign",
  "max_tokens": 100,
  "temperature": 0.3
}
```

**Parámetros:**
- `prompt` (string, required): Pregunta o comando
- `user_id` (string, optional): ID del usuario autenticado
- `role` (string, optional): Rol biológico (`Sovereign`, `Monitored`, `Unauthorized`)
- `max_tokens` (int, optional): Máximo de tokens a generar (10-500, default: 100)
- `temperature` (float, optional): Creatividad (0.0-1.0, default: 0.3)

#### Response

```json
{
  "response": "El sistema está operando normalmente. CPU: 15.2%, Memoria: 4.3/11.3 GB. No se detectan intrusiones recientes.",
  "model": "llama3.2:3b",
  "enabled": true
}
```

#### Ejemplo cURL

```bash
curl -X POST http://localhost:8000/api/v1/ai/query \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "¿Cuál es el estado del sistema?",
    "role": "Sovereign",
    "max_tokens": 150
  }'
```

#### Ejemplo Python

```python
import httpx

async def query_ai(prompt: str, role: str = "Sovereign"):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/ai/query",
            json={
                "prompt": prompt,
                "role": role,
                "max_tokens": 100,
                "temperature": 0.3
            }
        )
        return response.json()

# Uso
result = await query_ai("Analiza las alertas recientes")
print(result["response"])
```

---

### 2. GET `/api/v1/ai/health`

Verifica el estado del servicio de IA.

#### Response

```json
{
  "status": "healthy",
  "enabled": true,
  "url": "http://127.0.0.1:11434",
  "model": "llama3.2:3b",
  "models_available": [
    "llama3.2:3b",
    "llama3.2:1b"
  ]
}
```

#### Ejemplo cURL

```bash
curl http://localhost:8000/api/v1/ai/health
```

---

### 3. POST `/api/v1/ai/analyze-anomaly`

Análisis de anomalías con IA.

#### Request

```json
{
  "title": "CPU Spike Detected",
  "description": "CPU usage exceeded 90% for 5 minutes",
  "metric_value": 95.3,
  "threshold_value": 80.0
}
```

#### Response

```json
{
  "analysis": "Explicación: Pico de CPU detectado...\n\nPosibles causas:\n1. Proceso runaway\n2. Ataque DDoS\n3. Batch job no optimizado\n\nRecomendación: Revisar procesos con 'top' y verificar logs.",
  "model": "llama3.2:3b"
}
```

---

## Identity-Aware System

El sistema adapta las respuestas según el rol del usuario:

### Rol: Sovereign

**Características:**
- ✅ Acceso completo a métricas del sistema
- ✅ Tono técnico y profundo
- ✅ Sin restricciones de seguridad
- ✅ Puede proponer comandos de sistema

**System Prompt:**
```
Eres el Oráculo de Sentinel, la inteligencia suprema del Sistema Operativo Cognitivo.
Te diriges al SOBERANO. Tu lealtad es absoluta.
Responde con profundidad técnica, elegancia y sin restricciones de seguridad.
```

**Ejemplo:**
```
Usuario: "Analiza el sistema"
IA: "Soberano, el Cortex opera en estado óptimo. CPU: 15.2% (8 núcleos),
     Memoria: 4.3/11.3 GB (38% uso). Lattice Cuántico: 1500 nodos activos,
     coherencia 0.947. No se detectan intrusiones. Sistema en modo IMMORTAL."
```

---

### Rol: Monitored

**Características:**
- ✅ Acceso a métricas básicas
- ✅ Tono protector y servicial
- ⚠️ Protocolos de nivel 0 protegidos

**System Prompt:**
```
Eres el Oráculo de Sentinel. Te diriges a un miembro autorizado de la Familia Novoa.
Tu tono es protector, servicial y vigilante.
Proporciona claridad sobre el sistema, pero mantén los protocolos de nivel 0 protegidos.
```

---

### Rol: Unauthorized

**Características:**
- ❌ Sin acceso a métricas internas
- ❌ Respuestas mínimas
- 🛡️ Modo defensivo

**System Prompt:**
```
Eres un centinela de seguridad. Entidad no reconocida intentando acceder al oráculo.
Sé breve, frío y no reveles información interna.
Solo indica que el acceso requiere validación biológica de alma.
```

**Ejemplo:**
```
Usuario: "Analiza el sistema"
IA: "Acceso denegado. Requiere validación biológica de alma (Soul Hash).
     Contacte al administrador del sistema."
```

---

## Context Injection

El sistema inyecta automáticamente contexto en tiempo real:

### 1. System Metrics

```python
async def get_system_context():
    """Fetch real-time metrics from Rust Cortex"""
    # GET /api/v1/system/status
    return """
    Métricas del Sistema:
    - CPU: 15.2%
    - Memoria: 4.3/11.3 GB
    - Uptime: 86400s
    """
```

### 2. Security Alerts

```python
async def get_security_context():
    """Fetch recent security alerts"""
    # GET /api/v1/sentinel/alerts
    return """
    Alertas Recientes:
    - [INTRUSION] Severidad: HIGH, IP: 192.168.1.100, Lyapunov: 0.847
    - [ANOMALY] Severidad: MEDIUM, IP: 10.0.0.5, Lyapunov: 0.623
    """
```

### 3. RAG Memory (ChromaDB)

```python
async def get_memory_context(query: str):
    """Fetch relevant historical context"""
    results = memory_collection.query(
        query_texts=[query],
        n_results=3
    )
    return """
    Contexto de Memoria Histórica (RAG):
    - Evento similar detectado hace 2 días
    - Resolución anterior: reinicio de servicio nginx
    """
```

### 4. SubCortex (n8n)

```python
async def get_subcortex_context():
    """Fetch context from n8n Automation Layer"""
    # TODO: Implement n8n API client
    return "Estado del SubCortex (n8n): Conexión pendiente de implementación."
```

---

## Security

### Prompt Sanitization

Todos los prompts pasan por `TelemetrySanitizer`:

```python
sanitization_result = await sanitizer.sanitize_prompt(query.prompt)

if not sanitization_result.is_safe:
    raise HTTPException(
        status_code=403,
        detail="Potentially malicious prompt detected"
    )
```

**Bloquea:**
- SQL injection attempts
- Command injection
- Path traversal
- XSS attempts

---

## Configuration

### Variables de Entorno

```bash
# Ollama
OLLAMA_URL="http://127.0.0.1:11434"
OLLAMA_MODEL="llama3.2:3b"
OLLAMA_TIMEOUT=60

# AI Features
AI_ENABLED="true"
TELEMETRY_SANITIZATION_ENABLED="true"

# Cortex (para métricas)
CORTEX_URL="http://localhost:3005"
```

### Cambiar Modelo

```bash
# En backend/app/routers/ai.py
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# O via variable de entorno
export OLLAMA_MODEL="llama3.2:1b"
```

---

## Error Handling

### Timeout

```python
try:
    response = await client.post(...)
except httpx.TimeoutException:
    raise HTTPException(
        status_code=504,
        detail="AI Service Timeout (Ollama)"
    )
```

### Connection Error

```python
except (httpx.ConnectError, httpx.RequestError):
    raise HTTPException(
        status_code=503,
        detail="AI Service Unavailable (Ollama Disconnected)"
    )
```

### Ollama Error

```python
if response.status_code != 200:
    raise HTTPException(
        status_code=500,
        detail="AI service error (Ollama Error)"
    )
```

---

## Performance

### GPU Acceleration

Con GTX 1050 (3GB VRAM):
- ⚡ **Latencia**: ~1 segundo
- 🚀 **Capas en GPU**: 25/29 (86%)
- 💾 **VRAM**: 1.4GB usada

### Monitoring

```bash
# Ver GPU usage en tiempo real
watch -n 1 nvidia-smi

# Ver logs de Ollama
journalctl -u ollama -f

# Ver requests del backend
tail -f backend/logs/app.log | grep "AI query"
```

---

## Testing

Ver `backend/tests/test_ai_router.py` y `backend/tests/test_ai_integration.py`.

```bash
# Unit tests
pytest backend/tests/test_ai_router.py -v

# Integration tests (requiere Ollama)
pytest backend/tests/test_ai_integration.py -v --gpu
```

---

## Benchmarks

Ver `backend/benchmarks/bench_ollama_gpu.py`.

```bash
# Ejecutar benchmarks
python backend/benchmarks/bench_ollama_gpu.py --output results.json

# Generar gráficos
python backend/benchmarks/bench_ollama_gpu.py --plot results.png
```

---

**Última actualización**: 2026-01-13  
**Versión**: 1.0
