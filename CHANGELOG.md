# Changelog

All notable changes to the Sentinel project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [1.0.0] - 2025-12-14

### Phase 3: AI & Automation

#### Added - AI Integration
- **Ollama AI Service** with NVIDIA GPU support (GTX 1050, 3GB VRAM)
  - Local LLM inference with phi3:mini model (1.3B parameters)
  - GPU acceleration for 5-10x faster inference (1-2s vs 3-5s CPU)
  - Automatic model download on first run
- **AI Router** (`/api/v1/ai`) with 3 endpoints:
  - `POST /query` - General AI queries
  - `GET /health` - AI service status
  - `POST /analyze-anomaly` - Anomaly analysis with AI explanations
- **NVIDIA Container Toolkit** integration for Docker GPU access
- **AI-powered anomaly detection** with automatic explanations
- Comprehensive AI documentation:
  - `docs/AI_INTEGRATION_COMPLETE.md` - Full implementation guide
  - `docs/INSTALL_GPU.md` - Quick GPU setup
  - `docs/OLLAMA_GPU_SETUP.md` - Detailed configuration

#### Added - Automation (n8n)
- **6 Pre-configured n8n Workflows**:
  1. Daily SLO Report (9 AM daily)
  2. High CPU Alert (every 5 min, >80%)
  3. Anomaly Detector (every 15 min, critical only)
  4. Database Health Check (every 6 hours)
  5. Weekly Summary Report (Mondays 10 AM)
  6. Memory Warning Alert (every 10 min, >85%)
- **n8n Auto-loader** - Automatic workflow deployment
- **Slack Integration** for notifications
- Workflow documentation:
  - `n8n/README.md` - Workflow summary
  - `n8n/WORKFLOWS_GUIDE.md` - Implementation guide

#### Added - Security Hardening
- **Auditd Watchdog** for real-time exploit detection
  - Monitors syscalls: execve, ptrace, open, chmod
  - Automated response to suspicious activity
  - Integration with n8n for security alerts
- **Audit Rules** for kernel-level monitoring
- **Systemd Service** for watchdog daemon
- Security documentation:
  - `docs/SECURITY.md` - Complete security architecture
  - Auditd configuration and setup guides

#### Added - Documentation
- **Comprehensive README** with architecture diagram
- **Startup Script** (`startup.sh`) for one-command deployment
- **Performance Metrics** (`docs/PERFORMANCE.md`):
  - AI inference benchmarks
  - API latency measurements
  - Resource requirements
  - Scaling limits
- **Bilingual Documentation** (English/Spanish):
  - `docs/en/` - English documentation
  - `docs/es/` - Spanish documentation
- **Architecture Documentation** (`docs/architecture.md`)

#### Changed
- Updated `docker-compose.yml` with Ollama services
- Enhanced backend with AI integration (`httpx` dependency)
- Improved `.env.example` with AI configuration
- Reorganized documentation structure

---

### Phase 2: Analytics & Anomaly Detection

#### Added - Analytics Engine
- **Anomaly Detection Service** (`backend/app/services/anomaly_detector.py`)
  - Statistical methods: Z-score, threshold, trend analysis
  - Multi-metric monitoring: CPU, memory, network, GPU, database
  - Baseline learning phase (100 samples)
  - Configurable thresholds and sensitivity
- **Analytics API Endpoints**:
  - `GET /api/v1/analytics/metrics/recent` - Recent metrics
  - `GET /api/v1/analytics/statistics` - Statistical analysis
  - `GET /api/v1/analytics/anomalies` - Detected anomalies
  - `POST /api/v1/analytics/metrics` - Submit metrics
- **Database Models**:
  - `MetricSample` - Time-series metric storage
  - `Anomaly` - Anomaly records with severity
  - `SecurityAlert` - Security event tracking
  - `SystemReport` - Periodic system reports

#### Added - Data Collection
- **Celery Tasks** for automated data collection:
  - Metric collection (every 15 seconds)
  - Anomaly detection (every 15 seconds)
  - Data cleanup (daily)
  - Report generation (daily)
- **Host Metrics Collector** - System metrics gathering
- **PostgreSQL Exporter** - Database metrics
- **Redis Exporter** - Cache metrics

#### Added - Frontend Analytics
- **Analytics Dashboard** (`frontend/src/app/analytics/page.tsx`)
  - Real-time metrics visualization
  - Anomaly timeline
  - Statistical charts
  - Responsive design with Tailwind CSS

#### Documentation
- `PHASE_2_ANALYTICS.md` - Complete analytics architecture
- `ARCHITECTURE.md` - SOLID principles application

---

### Phase 1: Infrastructure & Observability

#### Added - Core Infrastructure
- **Multi-tenant SaaS Platform**:
  - FastAPI backend (Python 3.11, async-first)
  - Next.js frontend (React 18, TypeScript)
  - PostgreSQL 16 with Row-Level Security (RLS)
  - Redis 7 for caching and message broker
  - Nginx reverse proxy with rate limiting
- **Async Task Processing**:
  - Celery workers for background tasks
  - Celery Beat for scheduled jobs
  - Redis as broker and result backend
- **Authentication & Authorization**:
  - JWT-based authentication
  - Role-Based Access Control (RBAC)
  - Bcrypt password hashing
  - Token refresh mechanism

#### Added - Observability Stack
- **Prometheus** (port 9090):
  - Metrics collection and storage
  - 90-day retention
  - 5 scrape targets configured
  - Alert rules for critical conditions
- **Loki** (port 3100):
  - Log aggregation system
  - 30-day retention
  - Systemd and Docker log collection
- **Promtail**:
  - Log collector agent
  - Systemd journal integration
  - Docker container logs
- **Grafana** (port 3001):
  - Pre-configured dashboards (2):
    - Host Metrics Dashboard
    - System Logs Dashboard
  - Data source provisioning
  - Alert visualization
- **Exporters**:
  - Node Exporter - Host system metrics
  - PostgreSQL Exporter - Database metrics
  - Redis Exporter - Cache metrics

#### Added - Database
- **PostgreSQL 16** with features:
  - Row-Level Security (RLS) for multi-tenancy
  - Async driver (asyncpg) - 3-5x faster
  - Connection pooling
  - Automatic migrations (Alembic)
  - Full-text search with GIN indexes

#### Added - Frontend
- **Next.js 14** application:
  - App Router architecture
  - Server-side rendering
  - TypeScript for type safety
  - Tailwind CSS for styling
  - Responsive design

#### Added - Docker Infrastructure
- **18 Services** orchestrated with Docker Compose:
  - Core: postgres, redis, backend, frontend, nginx
  - Workers: celery_worker, celery_beat
  - Observability: prometheus, loki, promtail, grafana
  - Exporters: node-exporter, postgres-exporter, redis-exporter
  - Automation: n8n, n8n-loader
  - AI: ollama, ollama-init
- **Health Checks** for all services
- **Volume Management** for data persistence
- **Network Isolation** with custom bridge network

#### Documentation
- `README.md` - Project overview and quick start
- `OBSERVABILITY-STATUS.md` - Observability stack details
- `CHECKLIST.md` - Implementation checklist
- `.env.example` - Environment configuration template

---

## Version History

### [1.0.0] - 2025-12-14
- **Phase 1**: Infrastructure & Observability ✅
- **Phase 2**: Analytics & Anomaly Detection ✅
- **Phase 3**: AI & Automation ✅

---

## Roadmap

### Phase 4: Advanced Features (Planned)
- [ ] Multi-model AI support (llama3, mistral)
- [ ] AI model fine-tuning with historical data
- [ ] Advanced anomaly prediction with ML
- [ ] Automated incident response workflows
- [ ] Custom dashboard builder
- [ ] Mobile app (React Native)

### Phase 5: Enterprise Features (Planned)
- [ ] SSO integration (SAML, OAuth2)
- [ ] Advanced RBAC with custom roles
- [ ] Audit log export (SIEM integration)
- [ ] Multi-region deployment
- [ ] High availability setup
- [ ] Disaster recovery automation

### Phase 6: Compliance & Security (Planned)
- [ ] SOC 2 Type II certification
- [ ] GDPR compliance tools
- [ ] HIPAA compliance mode
- [ ] PCI DSS compliance
- [ ] Automated compliance reporting
- [ ] Security incident playbooks

---

## Contributors

- **jnovoas** - Project Lead & Development

---

## License

This project is proprietary software.

---

**For detailed changes, see the [commit history](https://github.com/jaime-novoa/sentinel/commits/main).**
