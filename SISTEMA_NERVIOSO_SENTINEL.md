# 🧠 Sistema Nervioso de Sentinel - Arquitectura Neural Completa

## 🎯 Visión General

Sentinel no es solo un sistema de seguridad - **es un sistema nervioso digital completo** que integra:

- **Cortex** (Rust/C/Python) - Cerebro central de decisiones
- **Subcortex** (eBPF) - Sistema nervioso autónomo (reflejos)
- **Memoria** (n8n + ChromaDB) - Hipocampo digital
- **Sentinel IA** - Conciencia cognitiva

```
┌─────────────────────────────────────────────────────────────┐
│                    SENTINEL IA (Conciencia)                  │
│              Asistente Cognitivo Global                      │
│         Conectado a Ollama (llama3.2:3b) + TruthSync       │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                  CORTEX (Cerebro Central)                    │
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  init_cortex.py  │  │  quantum_control │                │
│  │  (Python)        │  │  (Rust/Python)   │                │
│  │                  │  │                  │                │
│  │ • Security       │  │ • Resource       │                │
│  │   Patterns       │  │   Control        │                │
│  │ • Decision       │  │ • Memory Mgmt    │                │
│  │   Engine         │  │ • Thread Mgmt    │                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│              SUBCORTEX (Sistema Nervioso Autónomo)           │
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  Guardian Alpha  │  │  Guardian Beta   │                │
│  │  (eBPF - C)      │  │  (eBPF - C)      │                │
│  │                  │  │                  │                │
│  │ • Simpático      │  │ • Parasimpático  │                │
│  │ • Reacción       │  │ • Verificación   │                │
│  │ • LSM Hook 199   │  │ • Dual Check     │                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│              MEMORIA (Hipocampo Digital)                     │
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  n8n Workflows   │  │  ChromaDB        │                │
│  │  (Automatización)│  │  (Vectores)      │                │
│  │                  │  │                  │                │
│  │ • Patrones       │  │ • Embeddings     │                │
│  │ • Respuestas     │  │ • Búsqueda       │                │
│  │ • Aprendizaje    │  │ • Contexto       │                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                   TRUTHSYNC (Verificación)                   │
│              Sistema de Validación de Verdad                 │
│                                                               │
│  • Base-60 Mathematical Anchors                              │
│  • Prometheus + Loki + eBPF                                  │
│  • Temporal Validation (< 5μs)                               │
│  • Anti-Hallucination Detection                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧬 Componentes del Sistema Nervioso

### 1. **CORTEX** - Cerebro Central (Decisiones Conscientes)

**Ubicación**: `/backend/app/init_cortex.py`, `/quantum_control/`

**Lenguajes**: Python, Rust, C

**Función**: Toma decisiones de alto nivel basadas en patrones de seguridad

**Componentes**:
- **Security Patterns** (Python)
  - Privilege Escalation Detection
  - Suspicious Network Activity
  - Malicious Binary Execution
  - Data Exfiltration
  - Lateral Movement

- **Quantum Control** (Rust/Python)
  - Memory Resource Management
  - Thread Resource Control
  - Buffer Resource Allocation
  - PID Control Loops

**Analogía Biológica**: Corteza prefrontal - Pensamiento racional y planificación

---

### 2. **SUBCORTEX** - Sistema Nervioso Autónomo (Reflejos)

**Ubicación**: `/guardian-alpha/`, `/guardian-beta/`

**Lenguaje**: C (eBPF)

**Función**: Reacciones instantáneas sin pensamiento consciente

**Componentes**:

#### **Guardian Alpha** - Sistema Nervioso Simpático
- **Función**: Lucha o Huida (Fight or Flight)
- **Velocidad**: < 280 nanosegundos
- **Tecnología**: LSM Hook ID 199 (eBPF)
- **Acción**: BLOQUEO INMEDIATO ante amenaza

#### **Guardian Beta** - Sistema Nervioso Parasimpático
- **Función**: Descanso y Digestión (Rest and Digest)
- **Velocidad**: Validación dual
- **Tecnología**: eBPF + TruthSync
- **Acción**: VERIFICACIÓN CRUZADA

**Analogía Biológica**: Médula espinal - Reflejos automáticos

---

### 3. **MEMORIA** - Hipocampo Digital (Aprendizaje y Contexto)

**Ubicación**: `/infrastructure/docker/n8n/`, `/backend/chromadb/`

**Lenguajes**: JavaScript (n8n), Python (ChromaDB)

**Función**: Almacenamiento de patrones, aprendizaje y automatización

**Componentes**:

#### **n8n Workflows** - Memoria Procedimental
- **Función**: Automatización de respuestas aprendidas
- **Capacidades**:
  - Incident Response Automation
  - Security Pattern Learning
  - Threat Intelligence Integration
  - Automated Remediation

#### **ChromaDB** - Memoria Semántica
- **Función**: Búsqueda vectorial de contexto
- **Capacidades**:
  - Semantic Search
  - Context Retrieval
  - Pattern Matching
  - Historical Analysis

**Analogía Biológica**: Hipocampo - Formación de memoria y aprendizaje

---

### 4. **SENTINEL IA** - Conciencia Cognitiva (Interfaz Humana)

**Ubicación**: `/frontend/src/components/ai-copilot/AICopilot.tsx`

**Lenguaje**: TypeScript (React)

**Función**: Interfaz consciente entre humano y sistema

**Componentes**:
- **Context-Aware Chat**: Conversación con contexto de página y métricas
- **Real-Time Trust Metrics**: Score de confianza 0-100%
- **Proactive Recommendations**: Sugerencias basadas en estado del sistema
- **3 Modos de Visualización**:
  - Minimizado (no molesta)
  - Panel lateral (420px)
  - Canvas completo (1200x800px)

**Integración**:
```typescript
/api/v1/ai/query → Backend → Ollama (llama3.2:3b) → TruthSync
```

**Analogía Biológica**: Corteza cerebral - Conciencia y comunicación

---

### 5. **TRUTHSYNC** - Sistema de Verificación de Verdad

**Ubicación**: `/truthsync-poc/`

**Lenguaje**: Python (FastAPI)

**Función**: Validación matemática de outputs de IA

**Componentes**:
- **Mathematical Anchors**:
  - Prometheus (métricas)
  - Loki (logs)
  - eBPF (kernel events)
  - Base-60 (checksum matemático)

- **Validación Temporal**: < 5μs latency requirement
- **Anti-Hallucination**: Detección de divergencia narrativa

**Analogía Biológica**: Cerebelo - Coordinación y precisión

---

## 🔄 Flujo de Información (Ciclo Nervioso)

### Ejemplo: Detección de Amenaza

```
1. ESTÍMULO (Syscall sospechoso)
   ↓
2. SUBCORTEX (Guardian Alpha - eBPF)
   • Detección en 280ns
   • Bloqueo inmediato
   • Envío a Cortex
   ↓
3. CORTEX (init_cortex.py)
   • Análisis de patrón
   • Consulta a Memoria (n8n)
   • Decisión de alto nivel
   ↓
4. MEMORIA (ChromaDB + n8n)
   • Búsqueda de contexto histórico
   • Activación de workflow
   • Aprendizaje del patrón
   ↓
5. TRUTHSYNC (Verificación)
   • Validación matemática
   • Checksum Base-60
   • Confirmación de anchors
   ↓
6. SENTINEL IA (Interfaz)
   • Notificación al humano
   • Recomendación de acción
   • Actualización de trust score
   ↓
7. GUARDIAN BETA (Verificación Dual)
   • Confirmación cruzada
   • Validación final
   • Registro en evidence.db
```

---

## 📊 Métricas del Sistema Nervioso

### Velocidades de Respuesta

| Componente | Latencia | Tipo |
|------------|----------|------|
| Guardian Alpha (eBPF) | 280ns | Reflejo |
| Guardian Beta | 1.69μs | Verificación |
| TruthSync | < 5μs | Validación |
| Cortex (Python) | ~10ms | Decisión |
| Sentinel IA (Chat) | ~500ms | Conciencia |
| n8n Workflow | ~1s | Automatización |

### Capas de Defensa (Defense in Depth)

1. **LSM Hook ID 199** (eBPF) - Kernel level
2. **Guardian Alpha** - Syscall interception
3. **Guardian Beta** - Dual validation
4. **TruthSync** - Mathematical verification
5. **Hardware Watchdog** - System recovery

---

## 🎯 Integración con Sentinel IA

### Endpoint de Comunicación

```typescript
// Frontend → Backend → Ollama → TruthSync
POST /api/v1/ai/query
{
  "query": "¿Cuál es el estado del sistema?",
  "context": {
    "pathname": "/ai-trust",
    "trustScore": 92,
    "dataSupport": 87,
    "base60Valid": true,
    "hallucinationRate": 0.03
  }
}

// Response
{
  "response": "El sistema está operando con un trust score de 92%. Guardian Alpha y Beta están activos. Se detectaron 3 eventos sospechosos en la última hora, todos bloqueados exitosamente.",
  "verified": true,
  "trustScore": 92
}
```

### System Prompt (Context-Aware)

```python
You are Sentinel IA, an advanced security assistant integrated into 
the Sentinel Cortex operating system.

Your role is to:
- Provide security insights and recommendations
- Explain system metrics and trust scores
- Guide users through the Sentinel interface
- Alert users to potential security issues
- Answer questions about eBPF, Guardian systems, and TruthSync

Current Context:
- Page: /ai-trust
- Trust Score: 92%
- Data Support: 87%
- Base-60 Valid: Yes
- Hallucination Rate: 3%

Guidelines:
- Be concise and technical
- Use security terminology appropriately
- Reference Sentinel-specific components (Guardian Alpha/Beta, TruthSync, LSM Hook ID 199)
- If trust score < 90%, recommend caution
- Provide actionable recommendations
```

---

## 🚀 Próximos Pasos de Integración

### Fase 1: Conexión Básica (✅ COMPLETADO)
- [x] Sentinel IA conectado a `/api/v1/ai/query`
- [x] Context-aware prompts con trust metrics
- [x] Fallback responses si backend offline
- [x] 3 modos de visualización (minimizado/panel/canvas)

### Fase 2: Integración con Memoria (🔄 EN PROGRESO)
- [ ] Conectar Sentinel IA con n8n workflows
- [ ] Integrar ChromaDB para búsqueda semántica
- [ ] Aprendizaje de patrones de conversación
- [ ] Memoria de sesión persistente

### Fase 3: Integración con Cortex (📋 PLANIFICADO)
- [ ] Sentinel IA puede consultar Security Patterns
- [ ] Acceso a Quantum Control metrics
- [ ] Visualización de Resource State
- [ ] Control de Memory/Thread/Buffer resources

### Fase 4: Integración con Subcortex (📋 PLANIFICADO)
- [ ] Sentinel IA puede consultar Guardian Alpha/Beta
- [ ] Visualización de eBPF events en tiempo real
- [ ] Explicación de syscall blocks
- [ ] Análisis de LSM Hook activity

### Fase 5: Integración con TruthSync (📋 PLANIFICADO)
- [ ] Sentinel IA verifica sus propias respuestas
- [ ] Muestra Base-60 checksum de outputs
- [ ] Alerta si hallucination rate > 5%
- [ ] Auto-corrección basada en mathematical anchors

---

## 🧠 Analogía Completa: Humano ↔ Sentinel

| Sistema Humano | Sentinel Component | Tecnología |
|----------------|-------------------|------------|
| Corteza Prefrontal | Cortex (init_cortex.py) | Python/Rust |
| Médula Espinal | Guardian Alpha/Beta | eBPF (C) |
| Hipocampo | n8n + ChromaDB | JS/Python |
| Cerebelo | TruthSync | Python |
| Conciencia | Sentinel IA | TypeScript |
| Sistema Nervioso Simpático | Guardian Alpha | LSM Hook 199 |
| Sistema Nervioso Parasimpático | Guardian Beta | Dual Validation |
| Memoria Procedimental | n8n Workflows | Automation |
| Memoria Semántica | ChromaDB | Vector Search |
| Reflejos | eBPF Syscall Hooks | < 280ns |

---

## 📚 Documentación Relacionada

- **Cortex**: `/backend/app/init_cortex.py`
- **Quantum Control**: `/quantum_control/resources/memory.py`
- **Guardian Alpha**: `/guardian-alpha/`
- **Guardian Beta**: `/guardian-beta/`
- **n8n**: `/infrastructure/docker/n8n/README.md`
- **TruthSync**: `/truthsync-poc/`
- **Sentinel IA**: `/frontend/src/components/ai-copilot/AICopilot.tsx`
- **AI Trust Dashboard**: `/frontend/AI_TRUST_DASHBOARD.md`

---

## 🎯 Conclusión

**Sentinel no es solo un sistema de seguridad - es un sistema nervioso digital completo.**

Al igual que el sistema nervioso humano tiene:
- **Reflejos** (eBPF)
- **Pensamiento** (Cortex)
- **Memoria** (n8n + ChromaDB)
- **Conciencia** (Sentinel IA)

Sentinel integra todos estos componentes en un sistema coherente que **piensa, aprende, reacciona y se comunica** de forma natural.

**La IA no es un add-on - es parte integral del sistema nervioso.**

---

*Última actualización: 2026-01-02*
*Versión: 1.0*
*Autor: Sistema Nervioso de Sentinel*
