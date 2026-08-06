# Changelog
All notable changes to the Sentinel project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added (sesión 2026-08-05 — bitácora)
- **Migración Py→Rust del núcleo me-60os-core** (runtime 100% Rust, S60 determinista):
  - `celestial.rs` — mecánica orbital Kepler (SVector3 + elementos keplerianos) validada vs vis-viva (Bong Wie). 4 tests.
  - `numerical_control.rs` — interpolador DDA determinista (SovereignDDA). 4 tests.
  - `dsp.rs` — S60DSP multiplicador hardware 64×64→128-bit con traps de overflow. 7 tests.
  - `dual_lane.rs` — DualLaneRouter (seguridad WAL fsync + observabilidad con backpressure). 8 tests.
  - `orbital_ascent.rs` — **MUSEO**: ascenso orbital acoplado a cristal + lattice (drag/gravedad/thrust/Merkabah/MHD). Dejado como estudio del error de perspectiva (función aislada vs sistema vivo). 6 tests.
- **Cotejo de fórmulas contra papers primarios** (Agent Reach / Jina Reader → vault):
  - MHD: Muir & Nikiforakis 2022 (arXiv:2207.09857) confirma reducción de drag Cd 0.4→0.15. Nuestro SPA > float64.
  - Kepler/SPA y superradiancia (Dicke N²) validados. Merkabah-rígido/ZPE etiquetados como hipótesis.
  - Notas en `PersonalVault/Fisica/` (kepler_orbital_s60_cotejo, ascento_orbital_acoplado, verificacion_formulas_papers).
- **3 skills de conocimiento Sentinel** (portables/compartibles en `docs/skills/`, versionadas en git):
  - `sentinel-knowledge-layer` (CAPA 1: Agent Reach + vault + git como licencia + flujo de cotejo).
  - `sentinel-comprehension` (CAPA 2: por qué del sistema — pentaresonancia no-2D, cristal 41.77Hz/68 ticks, gap ahorra energía, Merkabah asintótico, levitación de datos = canal de fase en RAM).
  - `sentinel-s60-stack` (CAPA 3: build/verify + PITFALL pentaresonancia ya implementada + módulo aislado = museo).
- **Arquitectura fonónica-hidrodinámica documentada**: memoria resonante (EXP-001), líquida (EXP-009, retención 72% vs 44% ECC), sparse (EXP-014, 99.9% ahorro RAM) + BufferCascade OU-kernel + truthsync + mycnet acoplado al cristal (crystal_tick 41.77Hz).

### Fixed
- Hook `code-review-graph` (13 repos): editable apuntaba a `/tmp/code-review-graph` muerto (ModuleNotFoundError en cada commit). Reparado reinstalando 2.3.7 desde PyPI (`--user`).
- `sentinel-cortex/Cargo.toml`: conflicto de versiones `tower` (0.4 vs axum 0.7 → tower 0.5.3) que rompía tests handler. Fijado `tower = "0.5"` + `use tower::ServiceExt`. 26 tests handler OK.

### Changed
- Python legacy: `EA_NASIR_MASTER_FORMULA.py` eliminado; `MASTER_FORMULA.py` nuevo (autoría J. Novoa). `.continue/config.json` y `ebpf/reload_guardian.sh` ajustados.
- 13 repos (sentinel, vault, me-60os, micellia, sentinel_media, ONG_Impacta, mycnet, pinguinoseguro_web, laespiguita, portfolio, iwardrobe, diepo-parra, sentinel_cubepath) commiteados y pusheados (mapa de agentes + trabajo de sesión).

### Pending (urgente — ver `todo`)
- Integrar `BufferCascade` (OU-kernel) en `truthsync-core` como buffer en línea/cascada **por nodo** (truthsync hoy solo filtra claims, no encola/predice por nodo).
- Verificar bombeo 2T adaptativo con PID (EXP-001) en Rust vs `quantum/time_crystal_memory.py`.
- Separar memoria/propagación en `isochronous_oscillator.rs` (estilo Zhang&Wang 2025 fonónico).
- Re-acoplar `orbital_ascent.rs` (museo) a `LiquidLattice` en vez de `ResonantMatrix` simple.

---

### Added
- `OptomechanicalSystem::calculate_visibility()` — quantum interference visibility (S60 pure, no floats)
- 3 new tests for `calculate_visibility`: max coherent, anti-correlated, zero total
- 1 new linearity test for `calculate_visibility` (intermediate V ≈ 0.5)
- `AGENTS.md` and `CLAUDE.md` project instructions

### Fixed
- Resolved 15 compilation warnings in `sentinel-cortex`
- Removed unused imports (`sha3::Digest`, `BiometricVerifier`, `S60Error`, `mpsc`)
- Removed dead code (`BiometricVerifier`, `soul_verifier_s60_production` usage in main)
- Fixed `mut` redundancy and unused variable warnings across handlers

### Changed
- `sentinel_status_handler` and `truth_claim_handler` visibility reduced from `pub` to `pub(crate)`
- `calculate_coupling` parameter renamed (`mem` → `_mem`) to suppress unused warning
- `semantic_shell.rs` cleaned up redundant `rustyline` imports

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

**For detailed changes, see the [commit history](https://github.com/jenovoas/sentinel/commits/main).**
