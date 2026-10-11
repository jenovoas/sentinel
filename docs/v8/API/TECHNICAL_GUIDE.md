# Sentinel Cortex™ - Guía Técnica Completa

**Documentación para Desarrolladores**

**Última actualización:** Diciembre 2025  
**Versión:** 2.0 - Cortex Edition  
**Audiencia:** Desarrolladores, Arquitectos, DevOps

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Arquitectura General](#arquitectura-general)
3. [Componentes Principales](#componentes-principales)
4. [Stack Tecnológico](#stack-tecnológico)
5. [Estructura del Proyecto](#estructura-del-proyecto)
6. [Guía de Desarrollo](#guía-de-desarrollo)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Documentación de Referencia](#documentación-de-referencia)

---

## Introducción

### ¿Qué es Sentinel Cortex™?

Sentinel Cortex™ es el **primer sistema operativo vivo de seguridad** - un sistema de seguridad cognitiva auto-regenerativo que combina:

- **Cortex Engine**: Cerebro central con decision engine multi-factor
- 🚨 **Guardian-Alpha™**: Policía de intrusiones (syscall, memory, network)
- 🔒 **Guardian-Beta™**: Policía de integridad (backup, config, certs)

### Diferencia Clave vs Otros Sistemas

```
Sistemas Tradicionales:
Logs → Dashboard → Human Decision → Manual Action

Sentinel Cortex™:
Logs → Sanitization → Multi-Factor Correlation → Auto-Action → Auto-Healing
      (Claim 1)      (Claim 2)                    (Claim 3)
```

### Principios de Diseño

1. **Auto-vigilancia**: Dos componentes independientes que se monitorean mutuamente
2. **Modo Sombra**: Observan pero no ejecutan sin aprobación del Cortex
3. **Auto-regeneración**: Sistema se cura automáticamente ante corrupción
4. **Zero Trust**: Nunca confiar en una sola fuente de datos
5. **Inmutabilidad**: Logs y decisiones son inmutables (audit trail)

---

## 🏗 Arquitectura General

### Vista de Alto Nivel

```
┌─────────────────────────────────────────────────────────┐
│                    SENTINEL CORTEX™                      │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         CORTEX ENGINE (Rust)                   │    │
│  │  ┌──────────────────────────────────────────┐  │    │
│  │  │ Event Correlator                         │  │    │
│  │  │ Confidence Calculator (Bayesian)         │  │    │
│  │  │ Action Planner (N8N orchestrator)        │  │    │
│  │  │ Audit Logger (immutable)                 │  │    │
│  │  └──────────────────────────────────────────┘  │    │
│  └────────────┬──────────────────────┬────────────┘    │
│               │                      │                  │
│       ┌───────▼────────┐    ┌───────▼────────┐        │
│       │ GUARDIAN-ALPHA │    │ GUARDIAN-BETA  │        │
│       │   (Rust+eBPF)  │    │     (Rust)     │        │
│       │                │    │                │        │
│       │ • Syscall      │    │ • Backup       │        │
│       │ • Memory       │    │ • Config       │        │
│       │ • Network      │    │ • Certs        │        │
│       │ • Shadow Mode  │    │ • Shadow Mode  │        │
│       └────────────────┘    └────────────────┘        │
│               │                      │                  │
│               └──────────┬───────────┘                  │
│                          │                              │
│                   Mutual Surveillance                   │
│                   Auto-Regeneration                     │
└─────────────────────────────────────────────────────────┘
```

### Flujo de Datos

```
1. INGESTION (Múltiples fuentes)
   ├─ Prometheus (métricas)
   ├─ Loki (logs)
   ├─ PostgreSQL (eventos estructurados)
   ├─ Auditd (syscalls)
   └─ Docker (container events)

2. SANITIZATION (Claim 1)
   ├─ Pattern matching (40+ patrones)
   ├─ Schema validation
   ├─ Command injection detection
   └─ Output: Logs limpios

3. CORRELATION (Claim 2)
   ├─ Multi-source aggregation
   ├─ Temporal correlation (5 min window)
   ├─ Confidence scoring (Bayesian)
   └─ Output: DetectedPattern con confidence

4. DECISION (Cortex)
   ├─ Threshold check (confidence > 0.7)
   ├─ Context awareness (admin ops, DR mode)
   ├─ Guardian validation (ambos confirman)
   └─ Output: Action plan

5. EXECUTION (N8N)
   ├─ Playbook selection
   ├─ Action execution
   ├─ Rollback plan
   └─ Audit logging

6. REGENERATION (Claim 3)
   ├─ Detect corruption
   ├─ Restore from immutable backup
   ├─ Validate integrity
   └─ Resume operation
```

---

## 🔧 Componentes Principales

### 1. Cortex Engine (`sentinel-cortex/`)

**Lenguaje:** Rust  
**Responsabilidad:** Cerebro central, decision engine

#### Módulos

```rust
sentinel-cortex/
├── src/
│   ├── main.rs              // Entry point, main loop
│   ├── models/
│   │   ├── event.rs         // Event, EventSource, Severity, EventType
│   │   └── mod.rs
│   ├── collectors/
│   │   ├── prometheus.rs    // Prometheus collector (CPU, memory)
│   │   └── mod.rs
│   ├── engine/
│   │   ├── patterns.rs      // Pattern detector (credential stuffing, etc)
│   │   └── mod.rs
│   └── actions/
│       ├── n8n_client.rs    // N8N webhook client
│       └── mod.rs
├── Cargo.toml               // Dependencies
└── Dockerfile               // Container image
```

#### Modelos de Datos

```rust
// Event: Evento normalizado de cualquier fuente
pub struct Event {
    pub id: String,
    pub source: EventSource,      // Prometheus, Loki, Auditd, etc
    pub timestamp: DateTime<Utc>,
    pub severity: Severity,       // Low, Medium, High, Critical
    pub event_type: EventType,    // CpuSpike, FailedLogin, etc
    pub metadata: serde_json::Value,
}

// DetectedPattern: Patrón de ataque detectado
pub struct DetectedPattern {
    pub name: String,
    pub confidence: f32,          // 0.0 - 1.0
    pub severity: Severity,
    pub events: Vec<Event>,
    pub recommended_action: String,
    pub playbook: String,         // Nombre del playbook N8N
}
```

#### Patrones Implementados

**Patrón 1: Credential Stuffing**

```rust
// Detecta: 50+ failed logins + successful login desde nueva IP
if failed_logins > 50 && new_ip_login {
    confidence: 0.95
    playbook: "intrusion_lockdown"
}
```

**Patrón 2: Resource Exhaustion**

```rust
// Detecta: Memory leak + CPU spike simultáneos
if has_memory_leak && has_cpu_spike {
    confidence: 0.85
    playbook: "auto_remediation"
}
```

**Pendientes (Week 4):**

- Patrón 3: Data Exfiltration
- Patrón 4: DDoS Detection
- Patrón 5: Disk Full

#### Main Loop

```rust
// Loop principal: Collect → Detect → Act (cada 30 segundos)
loop {
    // 1. Collect events from Prometheus
    let events = prometheus.collect().await?;

    // 2. Detect patterns
    let patterns = detector.detect(&events);

    // 3. Trigger playbooks (si confidence > 0.7)
    for pattern in patterns {
        if pattern.confidence > 0.7 {
            n8n.trigger_playbook(&pattern).await?;
        }
    }

    tokio::time::sleep(Duration::from_secs(30)).await;
}
```

---

### 2. Guardian-Alpha™ (Intrusion Detection)

**Lenguaje:** Rust + eBPF  
**Responsabilidad:** Detectar intrusiones en tiempo real

#### Componentes (Planificado - Weeks 5-6)

```rust
guardian-alpha/
├── src/
│   ├── main.rs              // Entry point
│   ├── syscall/
│   │   ├── tracer.rs        // eBPF syscall tracer
│   │   └── patterns.rs      // Suspicious syscall patterns
│   ├── memory/
│   │   ├── scanner.rs       // /proc/*/maps analyzer
│   │   └── shellcode.rs     // RWX page detection
│   ├── network/
│   │   ├── sniffer.rs       // Packet capture (libpcap)
│   │   └── c2_detector.rs   // C&C pattern matching
│   └── crypto/
│       ├── channel.rs       // X25519 + ChaCha20-Poly1305
│       └── mod.rs
└── Cargo.toml
```

#### Señales Monitoreadas

```
1. SYSCALLS (eBPF)
   ├─ execve() - Ejecución de programas
   ├─ ptrace() - Inyección de código
   ├─ open() - Acceso a archivos críticos
   ├─ chmod/chown - Cambios de permisos
   └─ socket() - Conexiones de red

2. MEMORY (procfs)
   ├─ RWX pages (shellcode)
   ├─ Unknown libraries
   ├─ Heap/stack anomalies
   └─ Memory injection

3. NETWORK (libpcap)
   ├─ Conexiones a IPs no whitelist
   ├─ C&C patterns
   ├─ Data exfiltration (large transfers)
   └─ Lateral movement

4. FILES (inotify)
   ├─ Cambios en /usr/bin
   ├─ Cambios en /etc
   ├─ Cambios en source code
   └─ Container image tampering
```

#### Modo Sombra (Shadow Mode)

```rust
// Guardian-Alpha NO ejecuta acciones directamente
// Solo reporta al Cortex
pub async fn patrol(&self) -> SecurityEvent {
    loop {
        let events = self.detect_intrusion_signals().await;

        for event in events {
            // NO actúa directamente, reporta al Cortex
            self.send_to_cortex(event).await;

            // Pero ESTÁ LISTO para actuar si Cortex da orden
            if event.severity == CRITICAL {
                self.prepare_lockdown_plan().await;
                self.pre_calculate_rollback().await;
            }
        }
    }
}
```

---

### 3. Guardian-Beta™ (Integrity Assurance)

**Lenguaje:** Rust  
**Responsabilidad:** Validar integridad de datos, backups, certs

#### Componentes (Planificado - Weeks 7-8)

```rust
guardian-beta/
├── src/
│   ├── main.rs              // Entry point
│   ├── backup/
│   │   ├── validator.rs     // SHA-3 checksum validation
│   │   └── restore.rs       // PITR restore capability
│   ├── config/
│   │   ├── auditor.rs       // BLAKE3 hashing
│   │   └── git_diff.rs      // Git-based change tracking
│   ├── certs/
│   │   ├── manager.rs       // Certificate expiry checker
│   │   └── ocsp.rs          // OCSP validation
│   ├── crypto/
│   │   ├── storage.rs       // AES-256-GCM encryption
│   │   └── kdf.rs           // HKDF key derivation
│   └── healing/
│       ├── detector.rs      // Corruption detection
│       └── regenerator.rs   // Auto-healing logic
└── Cargo.toml
```

#### Chequeos Realizados

```
1. BACKUP INTEGRITY
   ├─ SHA-3 hashes de todos los backups
   ├─ Prueba de restauración (¿puedo recuperar?)
   ├─ Fecha de último backup válido
   ├─ RPO/RTO compliance
   └─ Redundancia geográfica

2. CONFIG INTEGRITY
   ├─ Git diffs en /etc (qué cambió)
   ├─ BLAKE3 signature validation
   ├─ Comparación contra baseline
   ├─ Cambios no autorizados
   └─ Secrets management

3. CERTIFICATE VALIDITY
   ├─ Fecha de expiración (30-day warning)
   ├─ OCSP responder (revocación)
   ├─ Chain validation
   ├─ Hostname/SAN matching
   └─ Key strength (>= 2048 bits)

4. PERMISSION MODEL
   ├─ RBAC policy compliance
   ├─ Principio de menor privilegio
   ├─ Admin accounts monitoreados
   ├─ Sudo logs auditados
   └─ Service account permissions

5. DATA CONSISTENCY
   ├─ Database replication lag
   ├─ Idempotency checks
   ├─ Lost+found analysis
   ├─ Filesystem corruption (fsck)
   └─ Deduplicación
```

#### Auto-Healing

```rust
// Guardian-Beta puede auto-regenerar el sistema
pub async fn heal_system(&self, corruption: CorruptionReport) {
    match corruption.type {
        CorruptionType::DataCorruption => {
            // Restaurar DB desde PITR
            self.restore_to_point_in_time(corruption.timestamp).await;
        }
        CorruptionType::ConfigDrift => {
            // Revertir a versión buena conocida
            self.restore_config_from_git(corruption.file).await;
        }
        CorruptionType::CertificateExpiry => {
            // Rotar cert automáticamente
            self.rotate_certificate(corruption.cert_path).await;
        }
        CorruptionType::PermissionDrift => {
            // Restaurar permisos RBAC
            self.restore_permissions_policy(corruption.affected_resource).await;
        }
    }

    // Siempre notificar al Cortex
    self.notify_cortex("System healed").await;
}
```

---

## 💻 Stack Tecnológico

### Backend (Cortex + Guardians)

```toml
# Rust (Performance + Safety)
[dependencies]
tokio = "1"                    # Async runtime
axum = "0.7"                   # Web framework
reqwest = "0.11"               # HTTP client
serde = "1.0"                  # Serialization
chrono = "0.4"                 # Time handling
uuid = "1.6"                   # UUID generation
tracing = "0.1"                # Logging
anyhow = "1.0"                 # Error handling

# Database
sqlx = "0.7"                   # PostgreSQL client
redis = "0.24"                 # Redis client

# Crypto (QSC™)
ring = "0.17"                  # AES-256-GCM, HKDF
sha3 = "0.10"                  # SHA-3
blake3 = "1.5"                 # BLAKE3 (fast hashing)
rustls = "0.21"                # TLS/Certificates
sodiumoxide = "0.2"            # X25519 + ChaCha20
pqcrypto = "0.16"              # Post-quantum (Kyber-1024)

# eBPF (Guardian-Alpha)
libbpf-rs = "0.21"             # eBPF bindings
procfs = "0.15"                # /proc filesystem
nix = "0.27"                   # Unix syscalls
pcap = "1.1"                   # Packet capture
```

### ML Baseline (Python)

```python
# Anomaly Detection
scikit-learn==1.3.0            # Isolation Forest
numpy==1.24.0                  # Numerical computing
pandas==2.0.0                  # Data manipulation

# API
fastapi==0.104.0               # REST API
uvicorn==0.24.0                # ASGI server
pydantic==2.0.0                # Data validation
```

### Infrastructure

```yaml
# Observability Stack
- Prometheus: Métricas (time-series)
- Loki: Logs (agregación)
- Grafana: Dashboards (visualización)
- Alertmanager: Alertas

# Databases
- PostgreSQL 15: Datos estructurados (HA con Patroni)
- Redis 7: Cache + pub/sub (HA con Sentinel)

# Automation
- N8N: Workflow orchestration
- Ansible: Configuration management

# Containers
- Docker: Containerization
- Docker Compose: Local orchestration
```

---

## 📁 Estructura del Proyecto

```
sentinel/
├── backend/                    # Backend Python (API, backup system)
│   ├── app/
│   │   ├── api/               # REST API endpoints
│   │   ├── core/              # Core business logic
│   │   ├── db/                # Database models
│   │   └── services/          # Services (backup, monitoring)
│   ├── tests/                 # Unit tests
│   └── requirements.txt
│
├── sentinel-cortex/           # Cortex Engine (Rust)
│   ├── src/
│   │   ├── main.rs           # Entry point
│   │   ├── models/           # Data models
│   │   ├── collectors/       # Event collectors
│   │   ├── engine/           # Pattern detection
│   │   └── actions/          # Action executors
│   ├── Cargo.toml
│   └── Dockerfile
│
├── guardian-alpha/            # Guardian-Alpha (Rust+eBPF) [Planificado]
│   ├── src/
│   │   ├── syscall/          # Syscall monitoring
│   │   ├── memory/           # Memory forensics
│   │   ├── network/          # Network analysis
│   │   └── crypto/           # Encrypted channels
│   └── Cargo.toml
│
├── guardian-beta/             # Guardian-Beta (Rust) [Planificado]
│   ├── src/
│   │   ├── backup/           # Backup validation
│   │   ├── config/           # Config auditing
│   │   ├── certs/            # Certificate management
│   │   ├── crypto/           # Encrypted storage
│   │   └── healing/          # Auto-healing
│   └── Cargo.toml
│
├── ml-baseline/               # ML Baseline (Python) [Planificado]
│   ├── src/
│   │   ├── models/           # ML models
│   │   ├── features/         # Feature extraction
│   │   └── api/              # FastAPI endpoints
│   └── requirements.txt
│
├── frontend/                  # Frontend (React + TypeScript)
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Pages
│   │   └── services/         # API clients
│   └── package.json
│
├── docs/                      # Documentación
│   ├── MASTER_EXECUTION_PLAN.md
│   ├── QSC_TECHNICAL_ARCHITECTURE.md
│   ├── SENTINEL_CORTEX_EXECUTIVE_SUMMARY.md
│   ├── SENTINEL_CORTEX_PITCH_DECK.md
│   ├── PATENT_STRATEGY_SUMMARY.md
│   └── [60+ archivos más]
│
├── docker/                    # Docker configurations
│   ├── prometheus/
│   ├── loki/
│   ├── grafana/
│   └── postgres/
│
├── n8n/                       # N8N workflows
│   └── workflows/            # Playbooks (JSON)
│
├── scripts/                   # Utility scripts
│   ├── setup.sh
│   ├── deploy.sh
│   └── backup.sh
│
├── docker-compose.yml         # Main compose file
├── Makefile                   # Build automation
└── README.md                  # This file
```

---

## Guía de Desarrollo

### Setup Inicial

```bash
# 1. Clonar repositorio
git clone https://github.com/jenovoas/sentinel.git
cd sentinel

# 2. Instalar dependencias Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup default stable

# 3. Instalar dependencias Python
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 5. Levantar stack de infraestructura
docker-compose up -d prometheus loki grafana postgres redis

# 6. Compilar Cortex Engine
cd sentinel-cortex
cargo build --release
```

### Desarrollo Local

#### Cortex Engine

```bash
# Compilar
cd sentinel-cortex
cargo build

# Ejecutar tests
cargo test

# Ejecutar con logs debug
RUST_LOG=debug cargo run

# Ejecutar en modo watch (auto-reload)
cargo install cargo-watch
cargo watch -x run
```

#### Backend Python

```bash
# Activar virtualenv
source .venv/bin/activate

# Ejecutar servidor de desarrollo
cd backend
uvicorn app.main:app --reload --port 8000

# Ejecutar tests
pytest tests/ -v

# Linting
black app/
flake8 app/
mypy app/
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Variables de Entorno

```bash
# Cortex Engine
PROMETHEUS_URL=http://localhost:9090
N8N_URL=http://localhost:5678
RUST_LOG=info

# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/sentinel
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key

# ML Baseline (futuro)
ML_API_URL=http://localhost:8001
MODEL_PATH=/models/isolation_forest.pkl
```

---

## 🧪 Testing

### Unit Tests (Rust)

```rust
// sentinel-cortex/src/engine/patterns.rs
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_credential_stuffing_detection() {
        let detector = PatternDetector::new();

        // Crear eventos de prueba
        let events = vec![
            Event { event_type: EventType::FailedLogin, .. },
            // ... 50 más
            Event { event_type: EventType::SuccessfulLoginNewIP, .. },
        ];

        let patterns = detector.detect(&events);

        assert_eq!(patterns.len(), 1);
        assert_eq!(patterns[0].name, "Credential Stuffing Attack");
        assert!(patterns[0].confidence > 0.9);
    }
}
```

```bash
# Ejecutar todos los tests
cargo test

# Ejecutar con coverage
cargo install cargo-tarpaulin
cargo tarpaulin --out Html
```

### Integration Tests

```rust
// sentinel-cortex/tests/integration_test.rs
#[tokio::test]
async fn test_end_to_end_flow() {
    // 1. Setup mock Prometheus
    let mock_server = MockServer::start().await;

    // 2. Inject malicious events
    mock_server.mock_cpu_spike(0.95).await;
    mock_server.mock_memory_leak(0.05).await;

    // 3. Run Cortex
    let cortex = CortexEngine::new(mock_server.url());
    let patterns = cortex.run_once().await.unwrap();

    // 4. Assert pattern detected
    assert_eq!(patterns.len(), 1);
    assert_eq!(patterns[0].playbook, "auto_remediation");
}
```

### Performance Tests

```bash
# Benchmark de pattern detection
cargo bench

# Load testing (10K events/sec)
cd tests/load
./run_load_test.sh
```

---

## 🚢 Deployment

### Docker Compose (Desarrollo)

```bash
# Levantar todo el stack
docker-compose up -d

# Ver logs
docker-compose logs -f sentinel-cortex

# Rebuild después de cambios
docker-compose up -d --build sentinel-cortex
```

### Production (Kubernetes) [Futuro]

```yaml
# k8s/cortex-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sentinel-cortex
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sentinel-cortex
  template:
    metadata:
      labels:
        app: sentinel-cortex
    spec:
      containers:
        - name: cortex
          image: sentinel/cortex:latest
          env:
            - name: PROMETHEUS_URL
              value: "http://prometheus:9090"
          resources:
            requests:
              memory: "256Mi"
              cpu: "500m"
            limits:
              memory: "512Mi"
              cpu: "1000m"
```

---

## 📚 Documentación de Referencia

### Para Inversores

1. **SENTINEL_CORTEX_EXECUTIVE_SUMMARY.md** - One-pager investor-ready
2. **SENTINEL_CORTEX_PITCH_DECK.md** - Pitch deck completo (15 slides)
3. **PATENT_STRATEGY_SUMMARY.md** - Estrategia de patentes
4. **CORTEX_NARRATIVA_COMPLETA.md** - Narrativa estratégica completa

### Para Arquitectos

1. **QSC_TECHNICAL_ARCHITECTURE.md** - Arquitectura QSC detallada
2. **CORTEX_DOS_NERVIOS.md** - Arquitectura de Dos Nervios
3. **NEURAL_ARCHITECTURE.md** - Arquitectura neural completa
4. **CLAIM_2_DECISION_ENGINE_GUIDE.md** - Guía del Decision Engine

### Para Desarrolladores

1. **MASTER_EXECUTION_PLAN.md** - Plan de ejecución 21 semanas
2. **COMPLETE_ROADMAP_QSC.md** - Roadmap con QSC integration
3. **Este archivo** - Guía técnica completa

### Para Product Managers

1. **SUPERPODERES_CAJA_SEGURA.md** - Diferenciación competitiva
2. **INVESTOR_CONCEPTS_GUIDE.md** - Conceptos para inversores
3. **BRAND_GUIDE.md** - Guía de marca

---

## Roadmap de Desarrollo

### ✅ Completado (Weeks 1-4)

- [x] Telemetry Sanitization (Claim 1)
- [x] Event models (Event, DetectedPattern)
- [x] Prometheus collector (CPU, memory)
- [x] Pattern detector (2 patterns)
- [x] N8N client
- [x] Main correlation loop

### 🚧 En Progreso (Weeks 5-8)

- [ ] Guardian-Alpha™ implementation
  - [ ] eBPF syscall tracer
  - [ ] Memory scanner
  - [ ] Network packet analyzer
  - [ ] Encrypted channel (X25519+ChaCha20)

- [ ] Guardian-Beta™ implementation
  - [ ] Backup validator (SHA-3)
  - [ ] Config auditor (BLAKE3)
  - [ ] Certificate manager
  - [ ] Encrypted storage (AES-256-GCM)

### 📅 Planificado (Weeks 9-21)

- [ ] Data Collection (Weeks 9-13)
- [ ] ML Baseline (Weeks 14-18)
- [ ] Validation (Weeks 19-20)
- [ ] Patent Filing (Week 21)

---

## 🤝 Contribuir

### Estándares de Código

**Rust:**

```rust
// ✅ BUENO: Comentarios claros en español
/// Detecta patrones de credential stuffing
///
/// # Argumentos
/// * `events` - Lista de eventos a analizar
///
/// # Retorna
/// * `Option<DetectedPattern>` - Patrón detectado o None
fn detect_credential_stuffing(&self, events: &[Event]) -> Option<DetectedPattern> {
    // Contar failed logins
    let failed_logins = events.iter()
        .filter(|e| e.event_type == EventType::FailedLogin)
        .count();

    // Verificar login desde nueva IP
    let new_ip_login = events.iter()
        .any(|e| e.event_type == EventType::SuccessfulLoginNewIP);

    // Si ambas condiciones se cumplen, es credential stuffing
    if failed_logins > 50 && new_ip_login {
        Some(DetectedPattern {
            name: "Credential Stuffing Attack".to_string(),
            confidence: 0.95,
            // ... resto de campos
        })
    } else {
        None
    }
}
```

**Python:**

```python
# ✅ BUENO: Type hints + docstrings
def extract_features(events: List[Event]) -> np.ndarray:
    """
    Extrae features numéricas de eventos para ML.

    Args:
        events: Lista de eventos a procesar

    Returns:
        Array numpy con features normalizadas (0-1)

    Ejemplo:
        >>> events = [Event(...), Event(...)]
        >>> features = extract_features(events)
        >>> features.shape
        (2, 10)
    """
    features = []
    for event in events:
        # Extraer timestamp como unix epoch
        timestamp = event.timestamp.timestamp()

        # Severity como número (0-3)
        severity = SEVERITY_MAP[event.severity]

        features.append([timestamp, severity, ...])

    return np.array(features)
```

### Git Workflow

```bash
# 1. Crear branch desde main
git checkout main
git pull origin main
git checkout -b feature/guardian-alpha-syscall

# 2. Hacer cambios con commits descriptivos
git add src/syscall/tracer.rs
git commit -m "feat(guardian-alpha): Implementar eBPF syscall tracer

- Monitorea execve, ptrace, open, chmod
- Filtra patrones sospechosos
- Envía eventos a Cortex via channel

Refs: #123"

# 3. Push y crear PR
git push origin feature/guardian-alpha-syscall
# Crear PR en GitHub

# 4. Code review y merge
# Después de aprobación, squash merge a main
```

### Convenciones de Commits

```
feat(scope): Descripción corta

Descripción larga opcional con:
- Bullet points de cambios
- Referencias a issues (#123)
- Breaking changes si aplica

Tipos: feat, fix, docs, style, refactor, test, chore
Scopes: cortex, guardian-alpha, guardian-beta, ml-baseline, docs
```

---

## 📞 Contacto y Soporte

**Email:** jaime@sentinel.dev  
**Documentación:** `/docs/` directory  
**Issues:** GitHub Issues  
**Slack:** #sentinel-dev (interno)

---

## 📄 Licencia

Propietario - Sentinel Security Inc.  
Todos los derechos reservados.

---

**Documento:** Guía Técnica Completa  
**Audiencia:** Desarrolladores, Arquitectos, DevOps  
**Última actualización:** Diciembre 2025  
**Versión:** 2.0 - Cortex Edition
