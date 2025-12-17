# SENTINEL AI SECURITY - CONTEXTO TÉCNICO COMPLETO
## Arquitectura Multi-Layer con Datos de Desempeño (Diciembre 2025)

**Documento de Referencia Técnica para Análisis Profundo**

---

## 1. ARQUITECTURA PROPUESTA: MULTI-LAYER AI SECURITY

### Layer 1: Input Sanitization ✅
**Componente existente:** `TelemetrySanitizer`
- Detecta prompt injection
- Sanitiza inputs maliciosos
- Bloquea jailbreak attempts

### Layer 2: Source Verification (NUEVO)
**Componente:** `SourceVerifier`

```python
class SourceVerifier:
    def __init__(self):
        self.trusted_sources = [
            "internal_docs", 
            "mitre_attack", 
            "cve_database", 
            "company_policies"
        ]
        self.verification_cache = {}
    
    async def verify_source(self, source_url: str, content: str) -> VerificationResult:
        """
        Verifica integridad de fuente antes de usar.
        
        Checks:
        1. Source whitelist (trusted domains)
        2. Content hash (SHA-256 para detect tampering)
        3. Digital signature (para critical sources)
        4. Freshness validation (timestamp)
        """
        # Implementation...
```

**Checks implementados:**
- Source whitelist (trusted domains)
- Content hash (detect tampering)
- Digital signature (critical sources)
- Freshness validation

---

### Layer 3: RIG Implementation (Retrieval-Interleaved Generation)

**Diferencias clave RIG vs RAG:**
- **RAG tradicional**: Single retrieval → Generate
- **RIG**: Multiple interleaved retrieve-generate cycles
- **Ventaja RIG**: Identifica gaps durante generación y re-consulta

```python
class RIGService:
    async def generate_with_verification(self, query: str, context: str) -> RIGResponse:
        # Step 1: Preliminary generation con placeholders [SOURCE_X]
        preliminary = await self.llm.generate(prompt_with_citation_format)
        
        # Step 2: Extract claims y verify cada uno
        claims = self._extract_claims(preliminary)
        verified_claims = []
        
        for claim in claims:
            sources = await self.vector_db.search(claim.text)
            verified_sources = await self._verify_each_source(sources)
            if verified_sources:
                verified_claims.append({
                    'claim': claim, 
                    'sources': verified_sources
                })
        
        # Step 3: Refine response con SOLO verified claims
        final_response = await self.llm.generate(verified_claims_only)
        return RIGResponse(
            text=final_response, 
            verified_sources=verified_claims
        )
```

---

### Layer 4: Safety Layers (SPPFT)

**Paper base:** "Safety Layers in Aligned LLMs" (ICLR 2025)

**Concepto:**
- Capas medias del LLM (layers 10-15 en modelos 70B) mantienen alineación de seguridad
- Durante fine-tuning: congelar estas capas preserva safety sin degradar performance

```python
class SafetyLayerProtection:
    def __init__(self, model):
        self.model = model
        self.safety_layers = [10, 11, 12, 13, 14, 15]  # Capas críticas
    
    def freeze_safety_layers(self):
        for layer_idx in self.safety_layers:
            layer = self.model.layers[layer_idx]
            for param in layer.parameters():
                param.requires_grad = False
    
    def fine_tune_safe(self, training_data):
        self.freeze_safety_layers()
        optimizer = torch.optim.AdamW(
            filter(lambda p: p.requires_grad, self.model.parameters()),
            lr=1e-5
        )
        # Training loop solo entrena non-safety layers
```

---

### Layer 5: Runtime Monitoring

```python
class LLMSecurityMonitor:
    async def monitor_interaction(
        self, 
        input_text: str, 
        output_text: str, 
        context: dict
    ) -> SecurityAlert:
        alerts = []
        
        if self._detect_injection(input_text):
            alerts.append(SecurityAlert(
                type="PROMPT_INJECTION", 
                severity="HIGH"
            ))
        
        if pii := self._detect_pii(output_text):
            alerts.append(SecurityAlert(
                type="PII_LEAKAGE", 
                severity="CRITICAL"
            ))
        
        if self._detect_jailbreak(input_text, output_text):
            alerts.append(SecurityAlert(
                type="JAILBREAK_ATTEMPT", 
                severity="CRITICAL"
            ))
        
        if not self._verify_factuality(output_text, context):
            alerts.append(SecurityAlert(
                type="HALLUCINATION", 
                severity="MEDIUM"
            ))
        
        return SecurityAlertCollection(alerts)
```

---

## 2. AMENAZAS (OWASP LLM TOP 10 2025)

### Ranking Actualizado:
1. **LLM01: Prompt Injection** (mantiene #1)
2. LLM02: Insecure Output Handling
3. **LLM03: Supply Chain** (↑ de #5 → #3)
4. LLM04: Data and Model Poisoning
5. LLM05: Insecure Plugin Design
6. LLM06: Excessive Agency
7. **LLM07: System Prompt Leakage** (NUEVO 2025)
8. LLM08: Vector and Embedding Weaknesses
9. LLM09: Misinformation
10. **LLM10: Unbounded Consumption** (NUEVO 2025)

### Amenazas Específicas SIEM:
- **Data poisoning**: Manipular training data o threat intelligence
- **Source manipulation**: Comprometer CVE databases, threat feeds
- **Cognitive attacks**: Explotar confianza en LLM outputs
- **Supply chain**: CloudBorne, CloudJacking en modelo lifecycle

---

## 3. DATOS DE DESEMPEÑO

### 3.1 vLLM vs Ollama (RedHat Benchmarks, Agosto 2025)

| Métrica | vLLM | Ollama | Ventaja vLLM |
|---------|------|--------|--------------|
| **TTFT** | 50-200ms | 200-8000ms | **5-10x más rápido** |
| **TPS** | 150-300 | 30-80 | **4-10x throughput** |
| **ITL** | 10-80ms | 5-15ms | Ollama mejor (pero queue wait) |
| **RPS** | 20-50 | 3-8 | **6x más requests** |

**Trade-off clave:**
- vLLM: Optimiza throughput (más requests totales)
- Ollama: Optimiza experiencia individual (baja ITL, alta queue)

**Fuente**: https://developers.redhat.com/articles/2025/08/08/ollama-vs-vllm-deep-dive-performance-benchmarking

---

### 3.2 Llama 3.1 70B Benchmarks

**Artificial Analysis (promedio providers):**
- Output speed: **61.1 tokens/second**
- TTFT: **0.38s (380ms)**
- Context window: 130k tokens
- Price: $0.72 per 1M tokens (input/output)

**vLLM con Llama 3.1 70B (optimizado):**
- TTFT: **<1s** (con tuning adecuado)
- TPOT: ~130ms
- ITL: ~120ms

**Oracle Cloud benchmarks:**
- Batch size 1: TTFT ~400ms
- Batch size 8: TTFT ~1200ms

**Fuentes:**
- https://artificialanalysis.ai/models/llama-3-1-instruct-70b
- https://github.com/vllm-project/vllm/issues/7567
- https://docs.oracle.com/en-us/iaas/Content/generative-ai/benchmark-meta-llama-3-1-70b-instruct.htm

---

### 3.3 RAG Pipeline Performance

**Latency SLA típico:**
- Target: **2-3 segundos end-to-end**
- Retrieval: 50-200ms
- Generation: 1-2s
- **Critical**: No exceder 3s (user tolerance)

**Componente breakdown:**
- Vector search (pgvector): 9.81s promedio
- Vector search (Redis cached): **<1ms**
- Vector search (ChromaDB): 23.08s promedio
- Embedding generation: 10-50ms
- LLM generation (70B): 1-2s

**Metrics clave:**
- **Recall@k**: % documentos relevantes en top-k
- **Precision@k**: % top-k realmente relevantes
- **MRR**: Posición promedio primer doc relevante
- **Citation Precision**: % citas correctamente atribuidas
- **Faithfulness**: Respuesta grounded en data
- **Answer Relevancy**: Alineación con query

**Percentiles críticos:**
- P50 (median): experiencia típica
- P95: experiencia "mala" (5% usuarios)
- P99: worst-case acceptable

**Fuentes:**
- https://www.braintrust.dev/articles/rag-evaluation-metrics
- https://neptune.ai/blog/evaluating-rag-pipelines

---

### 3.4 RIG vs RAG Performance

**Trade-off fundamental:**
- **RAG**: Más rápido (1 retrieval), menos preciso
- **RIG**: Más lento (múltiples retrievals), más preciso

**Estimaciones latency:**
- 2-cycle RIG: **+40-60% vs RAG**
- 5-cycle RIG: **+150-200% vs RAG**
- Benefit: Reducción significativa alucinaciones

**DataGemma results (Google, Sept 2024):**
- RIG reduce alucinaciones vs RAG
- Mejor trazabilidad de fuentes
- Ideal para high-stakes decisions (SIEM)

**Fuente**: https://blog.google/technology/ai/google-datagemma-ai-llm/

---

## 4. INFRAESTRUCTURA Y COSTOS

### 4.1 NVIDIA Triton Inference Server

**Features clave:**
- **Dynamic Batching**: 4-10x throughput improvement
- **Concurrent Model Execution**: múltiples instancias paralelo
- **Model Ensemble**: orquesta pipelines multi-modelo
- **Zero-downtime updates**

**Performance:**
- MLPerf Inference v4.1: Triton = bare-metal (no overhead)
- Llama 2 70B con 8x H200: idéntico vs código manual

```protobuf
name: "llama_70b"
backend: "tensorrt"
max_batch_size: 8

dynamic_batching {
  preferred_batch_size: [ 4, 8 ]
  max_queue_delay_microseconds: 100
}

instance_group [{
  count: 2
  kind: KIND_GPU
  gpus: [ 0, 1 ]
}]
```

**Fuente**: https://docs.nvidia.com/deeplearning/triton-inference-server/

---

### 4.2 Perplexity Architecture (Referencia)

**Stack:**
- NVIDIA H100 GPUs en pods
- Disaggregated serving (prefill vs decode separado)
- NVIDIA Triton Inference Server
- TensorRT-LLM para optimización

**Métricas producción (Junio 2025):**
- **1.4 billion queries/mes**
- 30 million queries/día
- 20% MoM growth

**Optimizaciones:**
- Disaggregated serving: +40% throughput
- Dynamic batching
- Context-minimization (seguridad)

**Fuente**: https://developer.nvidia.com/blog/spotlight-perplexity-ai-serves-400-million-search-queries-a-month-using-nvidia-inference-stack/

---

### 4.3 Costos Reales (Diciembre 2025)

**Hardware compra:**
- 1x H100 80GB: ~$25,000 USD
- 8x H100 setup: ~$250,000 USD

**Cloud alquiler/hora:**

| Provider | H100 80GB | H200 141GB |
|----------|-----------|------------|
| Hyperbolic | $1.49/h | $2.15/h |
| RunPod | $2.39/h | N/A |
| AWS | $3.90/h | N/A |
| Azure | $6.98/h | $6.00/h |

**Alternativas económicas:**
- **RTX 4090 24GB**: $1,600 one-time
- Break-even vs cloud: **67 días** uso 24/7
- Spot instances: 60-90% descuento

**Estimación Sentinel (SOC típico):**
```
Workload diario:
- 10,000 classifications (7B local): $0
- 1,000 embeddings (CPU): $0
- 100 investigaciones (70B cloud batch): $3/día
- 10 incident response (70B on-demand): $1/día

Total: $4/día = $120/mes
vs alternativa todo cloud: $1,170/mes
```

**Fuentes:**
- https://intuitionlabs.ai/articles/h100-rental-prices-cloud-comparison
- https://www.thundercompute.com/blog/nvidia-h100-pricing

---

### 4.4 vLLM vs Triton

**Ventajas vLLM:**
- Open-source, gratis
- Performance similar/superior para LLMs
- **PagedAttention**: 60% menos memoria GPU
- Continuous batching: mejor throughput
- Más simple configurar

**Benchmark:**
- 7B models: vLLM = 95% performance TensorRT
- 13B models: vLLM = 92% performance TensorRT
- 34B models: vLLM = 88% performance TensorRT

**Cuándo usar:**
- **Triton**: Multi-framework, enterprise features
- **vLLM**: LLM específicamente, startups, simplicidad

---

## 5. ARQUITECTURA OPTIMIZADA SENTINEL

### 5.1 Stack Híbrido (Costo-Efectivo)

```
┌─────────────────────────────────────────┐
│ Tier 1: Local (GRATIS)                  │
│ - Threat classification (Llama 7B)      │
│ - Embeddings (all-MiniLM-L6-v2, CPU)    │
│ - Fast queries (<100ms target)          │
│ Hardware: 1x RTX 4090 24GB              │
│ Costo mensual: $0                       │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Tier 2: Cloud Batch (BARATO)            │
│ - Deep analysis (Llama 70B)             │
│ - Batch processing nocturno             │
│ - Investigaciones complejas             │
│ Provider: Hyperbolic H100 $1.49/hora    │
│ Costo: 2h/día = $89/mes                 │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Tier 3: On-Demand (EMERGENCIAS)         │
│ - Incident response crítico             │
│ - <10 queries/mes                       │
│ Provider: AWS/Azure                     │
│ Costo: ~$40/mes                         │
└─────────────────────────────────────────┘

COSTO TOTAL: ~$130 USD/mes
```

---

### 5.2 Pipeline RIG Optimizado con SLAs

```python
class RIGPerformanceOptimizer:
    """
    3 niveles de latencia según urgencia:
    - Critical: <200ms (cached + pre-computed)
    - Standard: <500ms (2-cycle RIG max)
    - Deep: <2s (5-cycle RIG con verificación completa)
    """
    
    async def optimized_rig_retrieval(
        self, 
        query: str,
        priority: str = "standard"
    ) -> RIGResponse:
        
        # Level 1: Cache check (sub-1ms)
        if cached := await self.cache.get(query):
            return cached
        
        # Level 2: Priority routing
        if priority == "critical":
            # Single-shot RAG para velocidad
            response = await self._fast_rag(query)
            assert response.ttft < 0.2  # 200ms SLA
            
        elif priority == "standard":
            # 2-cycle RIG optimizado
            response = await self._standard_rig(query)
            assert response.ttft < 0.5  # 500ms SLA
            
        else:  # priority == "deep"
            # Full RIG con verificación
            response = await self._deep_rig(query)
            assert response.ttft < 2.0  # 2s SLA
        
        await self.cache.set(query, response, ttl=3600)
        return response
```

---

### 5.3 Optimizaciones Clave

**1. Pre-computation de Amenazas Comunes:**
```python
COMMON_QUERIES = [
    "lateral movement indicators",
    "privilege escalation patterns",
    "data exfiltration IOCs"
]

# Pre-compute embeddings + results
for query in COMMON_QUERIES:
    embedding = compute_embedding(query)
    results = vector_db.search(embedding, top_k=10)
    cache.set(query, results, ttl=86400)  # 24h TTL
```

**2. Hot/Cold Storage Tiers:**
```
Hot (Redis): CVEs recientes, amenazas activas (<1ms)
Warm (pgvector): MITRE ATT&CK, playbooks (10-20ms)
Cold (S3): Historical logs, archived (200-500ms)
```

**3. Dynamic Batching con vLLM:**
```python
vllm_engine = vLLM(
    model="meta-llama/Llama-3.1-8B-Instruct",
    max_num_batched_tokens=8192,  # Batch size dinámico
    gpu_memory_utilization=0.9
)
```

**4. Prompt Caching:**
```python
# Cachear prefijos comunes (75% savings)
SYSTEM_PROMPT = """You are Sentinel SIEM..."""  # 5000 tokens
# Primera llamada: paga 5000 tokens input
# Siguientes: solo paga tokens variable (query)
```

---

## 6. HERRAMIENTAS Y FRAMEWORKS

### 6.1 Ragas (RAG Assessment)
```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision
)

results = evaluate(
    dataset=test_dataset,
    metrics=[faithfulness, answer_relevancy, context_precision]
)
```

### 6.2 Guardrails AI
```python
from guardrails import Guard

guard = Guard.from_string(
    validators=[
        "no-pii",
        "no-toxic-language",
        "factual-consistency"
    ]
)

validated_output = guard.validate(llm_output)
```

### 6.3 OWASP CycloneDX (SBOM)
```python
from cyclonedx.model import bom

# Generate Software Bill of Materials
sbom = bom.Bom()
# Track: data sources, models, code dependencies
```

---

## 7. MÉTRICAS DE ÉXITO

### 7.1 Latency Targets (P95)

| Query Type | Target P95 | Strategy |
|------------|------------|----------|
| Critical | <250ms | Cache + local 7B |
| Standard | <600ms | 2-cycle RIG |
| Deep | <2.5s | 5-cycle RIG |

### 7.2 Throughput Targets
- Sustained: **200+ QPS** (Standard workload)
- Complex: **30-50 QPS** (Deep analysis)
- Cache hit rate: **>70%** (pre-warm nocturno)

### 7.3 Quality Metrics

**RAG/RIG Pipeline:**
- Faithfulness score: >0.85
- Answer relevancy: >0.80
- Context precision: >0.75
- Citation accuracy: >0.90

**Security:**
- Prompt injection detection: >95% recall
- PII leakage: 0 false negatives (critical)
- Hallucination rate: <5%

---

## 8. DIFERENCIADOR COMPETITIVO

### Propuesta de Valor Única:
> "Sentinel es el primer SIEM con **verificación de fuentes certificada en tiempo real** para IA. Mientras competidores confían ciegamente en LLMs, Sentinel implementa RIG con audit trail completo, cumpliendo OWASP Top 10 LLM 2025 y normativas bancarias."

### Casos de Uso Inmediato:
1. **Threat Intelligence Verificado**: Cada alerta cita fuentes con hash validation
2. **Compliance Automatizado**: Trazabilidad completa (EU AI Act, DORA)
3. **Incident Response**: Playbooks sin alucinaciones

### Ventajas vs Competidores:
- **Splunk/QRadar**: No tienen source verification nativa
- **Microsoft Sentinel**: LLM integration básica sin RIG
- **SIEM tradicionales**: Alert fatigue sin IA

---

## 9. ROADMAP IMPLEMENTACIÓN

### Fase 1 (Inmediata):
- Integrar Ragas metrics para validar RAG pipeline
- Implementar SourceVerifier con CycloneDX SBOM
- Deploy input guardrails (TelemetrySanitizer enhancement)

### Fase 2 (Q1 2026):
- Implementar RIG con 2-cycle optimization
- Fine-tuning con SPPFT (safety layers frozen)
- Runtime monitoring con PII/jailbreak detection

### Fase 3 (Q2 2026):
- Certificación OWASP LLM Top 10 2025
- Integration threat intelligence feeds verificados
- Red teaming automatizado

---

## ÁREAS CRÍTICAS PARA ANÁLISIS

**Preguntas clave:**
1. ¿Es realista <500ms para 2-cycle RIG dado benchmarks?
2. ¿Stack híbrido (local + cloud) balancea costo vs performance?
3. ¿Safety layers preservan seguridad durante fine-tuning?
4. ¿Qué componente es bottleneck más probable en producción?
5. ¿Cómo escala 100 → 10,000 queries/día?

---

## REFERENCIAS COMPLETAS

### Papers:
- "Safety Layers in Aligned LLMs" (ICLR 2025)
- "Design Patterns for Securing LLM Agents" (arXiv, Junio 2025)
- "Ground Every Sentence: Improving RAG with Interleaved Generation" (2024)
- DataGemma: Google's RIG implementation (Sept 2024)
- OWASP LLM Top 10 2025

### Benchmarks:
- RedHat vLLM vs Ollama (Agosto 2025)
- Artificial Analysis LLM Leaderboard
- Oracle Cloud Llama 3.1 70B Benchmarks
- NVIDIA MLPerf Inference v4.1

### Herramientas:
- NVIDIA Triton Inference Server
- vLLM Documentation
- Ragas Framework
- Guardrails AI
- OWASP CycloneDX

---

**Status**: 🟢 **READY FOR DEEP TECHNICAL ANALYSIS**

**Objetivo**: Evaluar viabilidad técnica, identificar bottlenecks, proponer optimizaciones, validar SLAs alcanzables.
