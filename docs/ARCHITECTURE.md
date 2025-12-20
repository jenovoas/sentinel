# 🏗️ Sentinel Architecture

**Version**: 1.0.0  
**Last Updated**: December 14, 2025  
**Architecture Style**: Microservices with Event-Driven Components

---

## 🎯 Overview

Sentinel is a **production-ready multi-tenant SaaS platform** that combines:
- **Core Application** - FastAPI backend + Next.js frontend
- **AI Engine** - Local LLM with GPU acceleration (Ollama)
- **Observability Stack** - Prometheus, Loki, Grafana
- **Automation** - n8n workflow engine
- **Security** - Auditd watchdog + multi-layer hardening

---

## 🏛️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                │
│                     (Web Browser / Mobile App)                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         NGINX PROXY                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Rate Limiting│  │ TLS 1.3      │  │ Security     │              │
│  │ (100 req/s)  │  │ Termination  │  │ Headers      │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└────────────────────────────┬────────────────────────────────────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   FRONTEND      │ │    BACKEND      │ │   AUTOMATION    │
│   (Next.js)     │ │   (FastAPI)     │ │     (n8n)       │
│   Port 3000     │ │   Port 8000     │ │   Port 5678     │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   ▲
         │                   │                   │ Webhook (JSON)
         │         ┌─────────┼─────────┐         │
         │         │         │         │         │
         ▼         ▼         ▼         ▼         │
┌─────────────────────────────────────────────────────────┐   ┌───────────────┐
│                   DATA LAYER                            │   │  BCI ENGINE   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │   │  (Rust)       │
│  │  PostgreSQL  │  │    Redis     │  │   Ollama AI  │   │   │  - Rubato     │
│  │  (Database)  │  │   (Cache)    │  │   (LLM)      │   │   │  - ndarray    │
│  │  Port 5432   │  │  Port 6379   │  │  Port 11434  │   │◀──┤  - CereStim   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │   │  Port 9000    │
└─────────────────────────────────────────────────────────┘   └───────▲───────┘
                             │                                        │
                             ▼                                        │ Raw Signal
┌─────────────────────────────────────────────────────────┐   ┌───────┴───────┐
│                OBSERVABILITY LAYER                       │   │  NEURAL DATA  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │   │ (Simulated)   │
│  │  Prometheus  │  │     Loki     │  │   Grafana    │   │   │ - Neuralink   │
│  │  (Metrics)   │  │    (Logs)    │  │ (Dashboards) │   │   │ - GigaScience │
│  │  Port 9090   │  │  Port 3100   │  │  Port 3001   │   │   │ - OpenNeuro   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │   └───────────────┘
└─────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                  SECURITY LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Auditd     │  │   Seccomp    │  │   AppArmor   │   │
│  │  Watchdog    │  │   Profiles   │  │   Profiles   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 🧩 Component Details

### 1. Core Application

#### Frontend (Next.js 14)
- **Technology**: React 18, TypeScript, Tailwind CSS
- **Architecture**: App Router with server-side rendering
- **Features**:
  - Responsive dashboard
  - Real-time analytics visualization
  - Multi-tenant UI
  - Dark mode support
- **API Communication**: REST API via fetch
- **State Management**: React hooks + Context API

#### Backend (FastAPI)
- **Technology**: Python 3.11, FastAPI 0.104, SQLAlchemy 2.0
- **Architecture**: Async-first with asyncpg driver
- **Features**:
  - RESTful API (OpenAPI/Swagger docs)
  - JWT authentication
  - RBAC authorization
  - Multi-tenant with RLS
  - Prometheus metrics endpoint
- **Database**: PostgreSQL 16 with Row-Level Security
- **Cache**: Redis 7 for session and query caching
- **Performance**: 
  - P95 latency: <100ms
  - Throughput: 1000+ req/s
  - Concurrent users: 150+

#### Document Vault Module (Seguridad Zero-Knowledge)
- **Tecnología**: AES-256-GCM + Argon2id
- **Arquitectura**: Cifrado del lado del cliente (o servidor con aislamiento estricto) para documentos sensibles.
- **Flujo**:
  - **Cifrado**: Clave derivada de Master Password (nunca almacenada).
  - **Integridad**: Verificación SHA-256 de cada archivo.
  - **Storage**: Blobs cifrados en disco, metadatos en DB.

#### Nginx Reverse Proxy
- **Purpose**: Load balancing, TLS termination, rate limiting
- **Features**:
  - Rate limiting (100 req/s per IP)
  - Security headers (CSP, HSTS, X-Frame-Options)
  - TLS 1.3 only
  - Request buffering
  - Gzip compression

---

### 2. AI Engine (Ollama)

#### Local LLM Inference
- **Model**: phi3:mini (1.3B parameters)
- **Hardware**: NVIDIA GTX 1050 (3GB VRAM)
- **Performance**:
  - First query: 7-10s (model loading)
  - Subsequent: 1-2s (cached in VRAM)
  - GPU utilization: 85-95% during inference
  - VRAM usage: 2GB / 3GB

#### AI Capabilities
- **Anomaly Analysis**: Automatic explanation of detected anomalies
- **Query Endpoint**: General-purpose AI queries
- **Context-Aware**: Uses system metrics for better insights
- **Privacy-First**: All processing on-premises, no external API calls

#### Integration Points
- **Backend API**: `/api/v1/ai/*` endpoints
- **Anomaly Detector**: Enriches anomalies with AI explanations
- **n8n Workflows**: AI-powered report generation
- **Future**: Predictive analytics, automated incident response

---

### 3. Observability Stack

#### Prometheus (Metrics)
- **Purpose**: Time-series metrics database
- **Scrape Targets**:
  - Backend API (`/metrics`)
  - Node Exporter (host metrics)
  - PostgreSQL Exporter (database metrics)
  - Redis Exporter (cache metrics)
  - Prometheus itself (self-monitoring)
- **Retention**: 90 days
- **Storage**: ~1.2GB for 8,000 time series
- **Alert Rules**: 8 configured (CPU, memory, disk, latency)

#### Loki (Logs)
- **Purpose**: Log aggregation and querying
- **Sources**:
  - Systemd journal (via Promtail)
  - Docker containers (via Promtail)
  - Application logs
- **Retention**: 30 days
- **Storage**: ~850MB (8:1 compression)
- **Query Language**: LogQL (similar to PromQL)

#### Promtail (Log Collector)
- **Purpose**: Collect and ship logs to Loki
- **Features**:
  - Systemd journal integration
  - Docker log collection
  - Label extraction
  - Log parsing and filtering

#### Grafana (Visualization)
- **Purpose**: Dashboards and alerting
- **Pre-configured Dashboards**:
  - Host Metrics (CPU, memory, disk, network)
  - System Logs (searchable log viewer)
- **Data Sources**:
  - Prometheus (metrics)
  - Loki (logs)
  - TestData (development)
- **Features**:
  - Auto-provisioning
  - Alert visualization
  - Custom dashboards

---

### 4. Automation (n8n)

#### Workflow Engine
- **Purpose**: Automated workflows and integrations
- **Features**:
  - Visual workflow builder
  - 300+ integrations
  - Webhook support
  - Scheduled execution
  - Error handling and retries

#### Pre-configured Workflows (6)
1. **Daily SLO Report** - 9 AM daily
   - Fetches 24h statistics
   - Generates report
   - Sends to Slack

2. **High CPU Alert** - Every 5 minutes
   - Checks CPU usage
   - Alerts if >80%
   - Includes context

3. **Anomaly Detector** - Every 15 minutes
   - Fetches critical anomalies
   - Sends detailed report
   - Links to Grafana

4. **Database Health Check** - Every 6 hours
   - Checks connections, locks, size
   - Reports health status
   - Alerts on issues

5. **Weekly Summary** - Mondays 10 AM
   - 7-day statistics
   - Trend analysis
   - Executive summary

6. **Memory Warning** - Every 10 minutes
   - Checks memory usage
   - Alerts if >85%
   - Severity levels

#### Integration Points
- **Slack**: Notifications and alerts
- **Backend API**: Data fetching
- **Grafana**: Dashboard links
- **AI Engine**: Report enrichment (future)

### 5. TruthSync (Verificación de Veracidad)

#### Arquitectura Dual-Container
TruthSync implementa un diseño híbrido para equilibrar precisión y latencia:

**A. Truth Core (Contenedor Pesado)**
- **Rol**: Fuente de la Verdad y Análisis Profundo.
- **Componentes**:
  - **Base de Datos**: PostgreSQL con hechos verificados.
  - **Motor**: Rust + Python ML para inferencia compleja.
- **Latencia**: ~50-100ms.

**B. TruthSync Edge (Contenedor Contenidos)**
- **Rol**: Caché Predictiva y Filtrado Rápido.
- **Componentes**:
  - **Caché**: In-Memory (Rust) para respuestas <1ms.
  - **Proxy**: Intercepta consultas DNS/HTTP.
- **Latencia**: <1ms (Cache Hit).

#### Flujo de Datos
1. **Consulta**: Usuario navega o consulta.
2. **Edge Check**: TruthSync Edge verifica caché.
3. **Miss**: Si no está, consulta a Truth Core (gRPC).
4. **Learning**: El Core actualiza sus modelos basado en feedback.

---

### 6. Neural Interface (Experimental Research Module)

#### BCI Ingestion Engine
- **Purpose**: Real-time bio-signal processing and event detection
- **Status**: **Research Prototype** (Not in production)
- **Technology**: Rust (Tokio, Rubato, ndarray)
- **Features**:
  - **High-Performance**: Handles >30k samples/sec
  - **Signal Processing**: Bandpass filtering, Spike detection
  - **Event Dispatch**: Webhook payloads to n8n
  - **Simulation Mode**: Replays .mat/.wav files as live streams
- **Integration**:
  - **Input**: Raw neural data (Neuralink/Blackrock formats)
  - **Output**: JSON Events to n8n Webhook
  - **Mocking**: Implements CereStim API traits for hardware compatibility

---

### 6. Security Layer

#### Auditd Watchdog
- **Purpose**: Real-time exploit detection
- **Monitored Syscalls**:
  - `execve` - Process execution
  - `ptrace` - Process debugging
  - `open` - File access
  - `chmod` - Permission changes
  - `connect` - Network connections
- **Detection Patterns**:
  - Privilege escalation
  - Unauthorized debugging
  - Suspicious file access
  - Unexpected network activity
- **Response**:
  - Automated alerts via n8n
  - Service restart
  - Process termination
  - Audit log

#### Container Hardening (5 Layers)
1. **Seccomp Profiles** - Syscall filtering (~60 allowed)
2. **AppArmor Profiles** - Mandatory Access Control
3. **Read-Only Filesystem** - Immutable containers
4. **Capability Dropping** - Remove unnecessary privileges
5. **User Namespace Remapping** - Non-root execution

#### Kernel Hardening
- **sysctl Tuning**: 30+ security settings
  - Network hardening (SYN cookies, reverse path filtering)
  - Kernel protection (ASLR, BPF hardening, ptrace restrictions)
  - Memory protection (NULL pointer dereference prevention)
  - Filesystem protection (hardlink/symlink protection)

#### Multi-Tenancy Security
- **Database-Level RLS**: True data isolation
- **JWT Authentication**: Secure token-based auth
- **RBAC**: Role-based access control
- **Audit Logging**: All actions logged

---

## 🔄 Data Flow

### 1. User Request Flow

```
User → Nginx → Frontend → Backend → Database
                                  ↓
                                Cache (Redis)
                                  ↓
                            Response ← User
```

### 2. Metrics Collection Flow

```
Application → Prometheus Exporter → Prometheus
Host System → Node Exporter → Prometheus
Database → PostgreSQL Exporter → Prometheus
                                  ↓
                            Grafana Dashboard
```

### 3. Log Collection Flow

```
Application Logs → Promtail → Loki → Grafana
Systemd Journal → Promtail → Loki → Grafana
Docker Logs → Promtail → Loki → Grafana
```

### 4. AI Query Flow

```
User → Backend → Ollama AI → GPU Inference
                    ↓
              AI Response → Backend → User
```

### 5. Automation Flow

```
Schedule/Event → n8n → Backend API → Data
                  ↓
            Slack/Email ← Notification
```

### 6. Security Event Flow

```
Kernel Syscall → Auditd → Watchdog → Pattern Match
                                        ↓
                                  n8n Alert → Slack
                                        ↓
                                Auto-remediation
```

---

## 📊 Service Inventory

### Core Services (7)
| Service | Technology | Port | Purpose |
|---------|-----------|------|---------|
| postgres | PostgreSQL 16 | 5432 | Multi-tenant database |
| redis | Redis 7 | 6379 | Cache & message broker |
| backend | FastAPI | 8000 | REST API |
| celery_worker | Celery | - | Async tasks |
| celery_beat | Celery | - | Task scheduling |
| frontend | Next.js 14 | 3000 | Web UI |
| nginx | Nginx | 80/443 | Reverse proxy |

### Observability Services (7)
| Service | Technology | Port | Purpose |
|---------|-----------|------|---------|
| prometheus | Prometheus | 9090 | Metrics database |
| loki | Loki | 3100 | Log aggregation |
| promtail | Promtail | 9080 | Log collector |
| grafana | Grafana | 3001 | Visualization |
| node-exporter | Node Exporter | 9100 | Host metrics |
| postgres-exporter | PG Exporter | 9187 | DB metrics |
| redis-exporter | Redis Exporter | 9121 | Cache metrics |

### AI & Automation Services (5)
| Service | Technology | Port | Purpose |
|---------|-----------|------|---------|
| ollama | Ollama | 11434 | LLM inference |
| ollama-init | Ollama | - | Model downloader |
| n8n | n8n | 5678 | Workflow automation |
| n8n-loader | Custom | - | Workflow loader |
| bci-engine | Rust | 9000 | BCI signal ingestion |

**Total**: 19 services

---

## 🔧 Technology Stack

### Backend
- **Language**: Python 3.11
- **Framework**: FastAPI 0.104
- **ORM**: SQLAlchemy 2.0 (async)
- **Database Driver**: asyncpg (3-5x faster than psycopg2)
- **Validation**: Pydantic 2.5
- **Task Queue**: Celery 5.3
- **HTTP Client**: httpx (async)

### Frontend
- **Language**: TypeScript
- **Framework**: Next.js 14
- **UI Library**: React 18
- **Styling**: Tailwind CSS
- **State**: React hooks

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Proxy**: Nginx
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Metrics**: Prometheus
- **Logs**: Loki
- **Dashboards**: Grafana
- **Automation**: n8n
- **AI**: Ollama (phi3:mini)

---

## 📈 Performance Characteristics

### API Performance
- **Latency**: P95 <100ms (without AI)
- **Throughput**: 1000+ req/s
- **Concurrent Users**: 150+

### AI Performance
- **First Query**: 7-10s (model loading)
- **Subsequent**: 1-2s (GPU cached)
- **VRAM Usage**: 2GB / 3GB

### Database Performance
- **Simple Query**: 2-5ms
- **Join Query**: 8-12ms
- **Aggregation**: 15-25ms
- **RLS Overhead**: +3-5ms

### Observability Performance
- **Metrics Ingestion**: 500-800 samples/s
- **Log Ingestion**: 100-200 logs/s
- **Dashboard Load**: 1.5-2s

---

## 🔒 Security Features

### Application Security
- JWT authentication with refresh tokens
- RBAC with custom roles
- Input validation (Pydantic)
- SQL injection protection (ORM)
- XSS protection (CSP headers)
- CSRF protection (SameSite cookies)

### Infrastructure Security
- TLS 1.3 only
- Rate limiting (100 req/s)
- Security headers (HSTS, CSP, X-Frame-Options)
- Container isolation (seccomp, AppArmor)
- Kernel hardening (sysctl)
- Exploit detection (auditd watchdog)

### Data Security
- Database-level RLS (multi-tenancy)
- Encrypted connections (TLS)
- Password hashing (bcrypt)
- Token encryption (HS256)
- Audit logging (all actions)

---

## 📦 Deployment

### Requirements
- **Minimum**: 4 cores, 8GB RAM, 20GB disk
- **Recommended**: 8 cores, 16GB RAM, 100GB disk
- **GPU**: 2GB+ VRAM (optional, for AI)

### One-Command Deployment
```bash
./startup.sh
```

### Manual Deployment
```bash
docker-compose up -d
```

### Services Start Order
1. Core infrastructure (postgres, redis)
2. Backend services (backend, celery)
3. Frontend (frontend, nginx)
4. Observability (prometheus, loki, grafana)
5. Automation (n8n)
6. AI (ollama)

---

## 🚀 Scaling Strategy

### Horizontal Scaling
- **Backend**: Load balancer + multiple instances
- **Celery Workers**: Add more workers
- **Frontend**: CDN + replicas
- **Database**: Read replicas (PostgreSQL streaming)
- **Redis**: Cluster mode with sharding

### Vertical Scaling
- **Backend RAM**: 512MB → 2GB → 4GB
- **Database RAM**: 512MB → 4GB → 16GB
- **Redis RAM**: 512MB → 2GB → 8GB
- **Ollama RAM**: 2GB → 4GB → 8GB

---

## 🔮 Future Enhancements

### Phase 4: Advanced Features
- Multi-model AI support
- AI model fine-tuning
- Predictive analytics
- Custom dashboard builder
- Mobile app

### Phase 5: Enterprise
- SSO integration
- Advanced RBAC
- Multi-region deployment
- High availability
- Disaster recovery

### Phase 6: Compliance
- SOC 2 Type II
- GDPR tools
- HIPAA compliance
- PCI DSS compliance
- Automated reporting

---

## 📚 Documentation

- **[README](../README.md)** - Project overview
- **[CHANGELOG](../CHANGELOG.md)** - Version history
- **[Performance](PERFORMANCE.md)** - Benchmarks and metrics
- **[Security](SECURITY.md)** - Security architecture
- **[Observability](../OBSERVABILITY-STATUS.md)** - Monitoring stack
- **[n8n Workflows](../n8n/README.md)** - Automation guide

---

**Architecture Version**: 1.0.0  
**Last Review**: December 14, 2025  
**Next Review**: January 14, 2026
