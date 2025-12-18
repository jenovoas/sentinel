# 📐 TruthSync - UML Diagrams & Visual Architecture

**Purpose**: Professional diagrams for stakeholder communication and technical understanding

---

## 🎯 DIAGRAM INDEX

1. [System Architecture Diagram](#1-system-architecture)
2. [Component Diagram](#2-component-diagram)
3. [Sequence Diagram - Happy Path](#3-sequence-diagram-happy-path)
4. [Sequence Diagram - Cache Hit](#4-sequence-diagram-cache-hit)
5. [Class Diagram - Core Components](#5-class-diagram)
6. [Deployment Diagram](#6-deployment-diagram)
7. [Data Flow Diagram](#7-data-flow-diagram)

---

## 1. SYSTEM ARCHITECTURE

```mermaid
graph TB
    subgraph "Client Layer"
        API[API Gateway<br/>FastAPI/Flask]
        WEB[Web Interface]
    end
    
    subgraph "Python Orchestration Layer"
        ENGINE[TruthSync Engine<br/>Python Wrapper]
        ML[Sentinel ML<br/>Integration]
        OBS[Observability<br/>Prometheus/Grafana]
    end
    
    subgraph "Shared Memory Layer"
        IB1[Input Buffer 1]
        IB2[Input Buffer 2]
        IB3[Input Buffer 3]
        IB4[Input Buffer 4]
        OB1[Output Buffer 1]
        OB2[Output Buffer 2]
        OB3[Output Buffer 3]
        OB4[Output Buffer 4]
    end
    
    subgraph "Rust Processing Core"
        CACHE[Predictive Cache<br/>LRU + Aho-Corasick]
        EXTRACT[Claim Extractor<br/>Parallel Processing]
        VERIFY[Self-Verifier<br/>Adaptive Learning]
    end
    
    subgraph "Monitoring Stack"
        PROM[Prometheus]
        GRAF[Grafana]
        LOKI[Loki]
    end
    
    API --> ENGINE
    WEB --> ENGINE
    ENGINE --> IB1
    ENGINE --> IB2
    ENGINE --> IB3
    ENGINE --> IB4
    
    IB1 --> CACHE
    IB2 --> CACHE
    IB3 --> CACHE
    IB4 --> CACHE
    
    CACHE --> EXTRACT
    EXTRACT --> VERIFY
    
    VERIFY --> OB1
    VERIFY --> OB2
    VERIFY --> OB3
    VERIFY --> OB4
    
    OB1 --> ENGINE
    OB2 --> ENGINE
    OB3 --> ENGINE
    OB4 --> ENGINE
    
    ENGINE --> ML
    ENGINE --> OBS
    OBS --> PROM
    PROM --> GRAF
    ENGINE --> LOKI
    
    style CACHE fill:#90EE90
    style EXTRACT fill:#87CEEB
    style VERIFY fill:#FFB6C1
    style ENGINE fill:#FFD700
```

---

## 2. COMPONENT DIAGRAM

```mermaid
graph LR
    subgraph "TruthSync System"
        subgraph "Python Components"
            PY_ENGINE[TruthSync Engine]
            PY_ML[ML Connector]
            PY_METRICS[Metrics Collector]
        end
        
        subgraph "Rust Components"
            RS_BUFFER[Buffer Manager]
            RS_CACHE[Predictive Cache]
            RS_EXTRACT[Claim Extractor]
            RS_VERIFY[Verifier]
        end
        
        subgraph "Shared Memory"
            SHM[Sub-Buffers<br/>4x Input, 4x Output]
        end
    end
    
    subgraph "External Systems"
        SENTINEL[Sentinel ML]
        PROMETHEUS[Prometheus]
        GRAFANA[Grafana]
    end
    
    PY_ENGINE -->|writes| SHM
    SHM -->|reads| RS_BUFFER
    RS_BUFFER --> RS_CACHE
    RS_CACHE --> RS_EXTRACT
    RS_EXTRACT --> RS_VERIFY
    RS_VERIFY -->|writes| SHM
    SHM -->|reads| PY_ENGINE
    
    PY_ENGINE --> PY_ML
    PY_ML --> SENTINEL
    
    PY_ENGINE --> PY_METRICS
    PY_METRICS --> PROMETHEUS
    PROMETHEUS --> GRAFANA
```

---

## 3. SEQUENCE DIAGRAM - HAPPY PATH

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Engine as TruthSync Engine
    participant Buffer as Sub-Buffer
    participant Cache as Predictive Cache
    participant Extractor as Claim Extractor
    participant Verifier as Self-Verifier
    participant ML as Sentinel ML
    participant Metrics as Prometheus
    
    Client->>API: POST /verify {"text": "..."}
    API->>Engine: process(text)
    
    Engine->>Buffer: write_input(text)
    Note over Buffer: Round-robin to Buffer 1
    
    Buffer->>Cache: check(hash(text))
    Cache-->>Buffer: MISS
    
    Buffer->>Extractor: extract_claims(text)
    Note over Extractor: Aho-Corasick matching<br/>Parallel processing
    
    Extractor->>Verifier: verify(claims, confidence)
    Note over Verifier: Record prediction<br/>Calculate accuracy
    
    Verifier->>Buffer: write_output(claims)
    Buffer->>Engine: read_output()
    
    Engine->>Cache: update(hash, claims, confidence)
    Engine->>ML: send_features(text, claims, confidence)
    Engine->>Metrics: record_metrics(duration, accuracy)
    
    Engine->>API: return {claims, confidence}
    API->>Client: 200 OK {claims: [...]}
```

---

## 4. SEQUENCE DIAGRAM - CACHE HIT

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Engine as TruthSync Engine
    participant Buffer as Sub-Buffer
    participant Cache as Predictive Cache
    participant Metrics as Prometheus
    
    Client->>API: POST /verify {"text": "..."}
    API->>Engine: process(text)
    
    Engine->>Buffer: write_input(text)
    Buffer->>Cache: check(hash(text))
    
    Note over Cache: Cache HIT!<br/>Return immediately
    Cache-->>Buffer: claims (cached)
    
    Buffer->>Engine: return cached_claims
    
    Note over Engine: Skip Rust processing<br/>~1μs total latency
    
    Engine->>Metrics: record_cache_hit()
    Engine->>API: return {claims, confidence}
    API->>Client: 200 OK {claims: [...]}
    
    Note over Client,Metrics: Total time: ~5μs<br/>(vs ~20μs for full processing)
```

---

## 5. CLASS DIAGRAM

```mermaid
classDiagram
    class TruthSyncEngine {
        +SubBufferManager buffers
        +MLConnector ml
        +MetricsCollector metrics
        +process(text) Result
        +process_batch(texts[]) Results
    }
    
    class SubBufferManager {
        +SharedBuffer[] input_buffers
        +SharedBuffer[] output_buffers
        +PredictiveCache cache
        +write_input(text) u64
        +read_output() Result
        +cache_stats() Stats
    }
    
    class SharedBuffer {
        +Shmem shmem
        +usize capacity
        +write(msg_type, data) Result
        +read() Result
    }
    
    class PredictiveCache {
        +HashMap cache
        +ClaimPredictor predictor
        +get(key) Option
        +put(key, claims, confidence)
        +predict_claims(text) f32
        +stats() CacheStats
    }
    
    class ClaimPredictor {
        +AhoCorasick factual_matcher
        +AhoCorasick opinion_matcher
        +predict_claim_likelihood(text) f32
        +learn(text, had_claims)
    }
    
    class ClaimExtractor {
        +extract(text) Vec~String~
        +is_verifiable(sentence) bool
    }
    
    class TruthSyncVerifier {
        +HashMap predictions
        +u64 total_predictions
        +u64 correct_predictions
        +record_prediction(key, likelihood)
        +verify(key, had_claims) VerificationResult
        +accuracy() f32
    }
    
    class SentinelMLConnector {
        +extract_features(text, claims) Features
        +send_training_data(features)
        +get_adaptive_threshold() f32
        +detect_anomalies() Dict
    }
    
    class IntegrityMonitor {
        +TruthSyncMetrics metrics
        +Logger logger
        +record_claim_processing()
        +record_prediction()
        +update_cache_stats()
    }
    
    TruthSyncEngine --> SubBufferManager
    TruthSyncEngine --> SentinelMLConnector
    TruthSyncEngine --> IntegrityMonitor
    
    SubBufferManager --> SharedBuffer
    SubBufferManager --> PredictiveCache
    
    PredictiveCache --> ClaimPredictor
    
    SharedBuffer ..> ClaimExtractor : reads from
    ClaimExtractor ..> TruthSyncVerifier : verified by
```

---

## 6. DEPLOYMENT DIAGRAM

```mermaid
graph TB
    subgraph "Production Environment"
        subgraph "Container: TruthSync"
            RUST[Rust Core<br/>libtruthsync_core.so]
            PYTHON[Python Engine<br/>truthsync.py]
            SHM[Shared Memory<br/>8 buffers]
        end
        
        subgraph "Container: Monitoring"
            PROM[Prometheus<br/>:9090]
            GRAF[Grafana<br/>:3000]
            LOKI[Loki<br/>:3100]
        end
        
        subgraph "Container: Sentinel ML"
            ML[ML Pipeline<br/>:8000]
        end
    end
    
    subgraph "External"
        CLIENT[Clients<br/>API Requests]
    end
    
    CLIENT -->|HTTPS| PYTHON
    PYTHON <-->|mmap| SHM
    RUST <-->|mmap| SHM
    PYTHON -->|HTTP| PROM
    PYTHON -->|HTTP| LOKI
    PYTHON -->|HTTP| ML
    PROM -->|Query| GRAF
    
    style RUST fill:#FFA500
    style PYTHON fill:#4169E1
    style SHM fill:#32CD32
```

---

## 7. DATA FLOW DIAGRAM

```mermaid
flowchart TD
    START([Client Request]) --> HASH{Calculate Hash}
    HASH --> CACHE_CHECK{Cache Check}
    
    CACHE_CHECK -->|HIT| CACHE_RETURN[Return Cached<br/>~5μs]
    CACHE_CHECK -->|MISS| BUFFER_WRITE[Write to Input Buffer<br/>~1μs]
    
    BUFFER_WRITE --> PREDICT{Predict Likelihood}
    PREDICT -->|High| PROCESS[Process with Rust<br/>~15μs]
    PREDICT -->|Low| SKIP[Skip Processing]
    
    PROCESS --> EXTRACT[Aho-Corasick Extract<br/>~8μs]
    EXTRACT --> VERIFY[Self-Verify<br/>~1μs]
    VERIFY --> BUFFER_READ[Write to Output Buffer<br/>~1μs]
    
    BUFFER_READ --> UPDATE_CACHE[Update Cache]
    UPDATE_CACHE --> SEND_ML[Send to Sentinel ML]
    SEND_ML --> METRICS[Record Metrics]
    
    CACHE_RETURN --> METRICS
    SKIP --> METRICS
    
    METRICS --> END([Return to Client])
    
    style CACHE_RETURN fill:#90EE90
    style PROCESS fill:#FFB6C1
    style METRICS fill:#87CEEB
```

---

## 📊 PERFORMANCE VISUALIZATION

```mermaid
gantt
    title TruthSync Processing Timeline (Cache Miss)
    dateFormat X
    axisFormat %Lμs
    
    section Python
    API Receive           :0, 1
    Buffer Write          :1, 2
    Buffer Read           :18, 19
    Response Send         :19, 20
    
    section Shared Memory
    Input Buffer          :2, 3
    Output Buffer         :17, 18
    
    section Rust
    Cache Check           :3, 5
    Aho-Corasick Match    :5, 13
    Verification          :13, 14
    Cache Update          :14, 15
    Buffer Write          :15, 17
```

---

## 🎓 EXPLANATION FOR STAKEHOLDERS

### Why This Architecture Works

**1. Hybrid Design**
- Python handles high-level logic (easy to modify)
- Rust handles heavy computation (10-500x faster)
- Best of both worlds

**2. Zero-Copy Buffers**
- Shared memory = no data copying
- ~2μs overhead (negligible)
- Enables true parallelism

**3. Predictive Caching**
- AI predicts which content needs processing
- 80%+ cache hit rate expected
- 5x speedup from caching alone

**4. Self-Verification**
- System validates its own predictions
- Adapts thresholds automatically
- Improves over time

**5. Sentinel Integration**
- Feeds existing ML pipeline
- Leverages proven infrastructure
- No new systems needed

### Key Metrics

| Metric | Value | Meaning |
|--------|-------|---------|
| Cache Hit Rate | 80%+ | Most requests served instantly |
| Processing Time | <20μs | 50x faster than Python |
| Accuracy | >85% | High-quality predictions |
| Throughput | 500k/sec | Handles massive scale |

---

**These diagrams can be imported into:**
- Draw.io / Lucidchart (Mermaid export)
- PlantUML (convert syntax)
- Microsoft Visio (import Mermaid)
- Confluence / Notion (native Mermaid support)
