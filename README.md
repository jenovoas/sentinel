# 🛡️ Sentinel - Enterprise Observability & Security Platform

**Modern observability platform with AI-powered insights and kernel-level security monitoring**

Sentinel combines traditional observability (metrics, logs, traces) with **defense-in-depth security** that operates at the Linux kernel level. Unlike tools that only monitor application-layer events, Sentinel provides real-time exploit detection through auditd syscall monitoring.

---

## 🔒 **What Makes Sentinel Different**

### Kernel-Level Security Monitoring (Auditd Watchdog)

> **"Defense-in-depth security that operates below the application layer"**

Sentinel monitors critical Linux syscalls (`execve`, `open`, `ptrace`, `chmod`) at the **kernel level** using auditd. This provides:

- ✅ **Real-time exploit detection** - Catches privilege escalation attempts before they reach your application
- ✅ **Suspicious execution monitoring** - Detects unauthorized process execution and code injection
- ✅ **File access auditing** - Tracks sensitive file access patterns
- ✅ **AI-powered analysis** - Automatic threat assessment and recommendations

**Why this matters**: Most observability tools (Grafana, Datadog, New Relic) focus on application metrics and logs. Sentinel goes deeper, monitoring at the kernel level where exploits actually happen.

**Enterprise value**: This is the same level of security monitoring typically requiring specialized security products or significant manual configuration. Sentinel provides it out-of-the-box.

---

[![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue)](docs/)
[![AI](https://img.shields.io/badge/AI-Ollama%20%2B%20GPU-green)](docs/AI_INTEGRATION_COMPLETE.md)
[![Observability](https://img.shields.io/badge/Observability-Prometheus%20%2B%20Loki-orange)](OBSERVABILITY-STATUS.md)
[![Automation](https://img.shields.io/badge/Automation-n8n-purple)](n8n/README.md)

---

## 🚀 Quick Start

### One-Command Startup

```bash
./startup.sh
```

This script will:
1. ✅ Start all 18 services in the correct order
2. ✅ Wait for health checks
3. ✅ Download AI models (first run only)
4. ✅ Display access points and status

### Manual Startup

```bash
docker-compose up -d
```

Services start in ~2-3 minutes.

---

## 🌐 Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | - |
| **API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Grafana** | http://localhost:3001 | admin / REDACTED_PASSWORD |
| **Prometheus** | http://localhost:9090 | - |
| **n8n Automation** | http://localhost:5678 | admin / REDACTED_PASSWORD |
| **Ollama AI** | http://localhost:11434 | - |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         SENTINEL PLATFORM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Frontend   │  │   Backend    │  │  Automation  │          │
│  │  (Next.js)   │◄─┤  (FastAPI)   │◄─┤    (n8n)     │          │
│  │  Port 3000   │  │  Port 8000   │  │  Port 5678   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘          │
│         │                 │                                      │
│         │                 │                                      │
│  ┌──────▼─────────────────▼──────┐  ┌──────────────┐           │
│  │         Nginx Proxy           │  │   AI Engine  │           │
│  │  (Rate Limit + Security)      │  │   (Ollama)   │           │
│  │         Port 80/443            │  │  Port 11434  │           │
│  └───────────────────────────────┘  └──────┬───────┘           │
│                                             │                    │
│  ┌──────────────┐  ┌──────────────┐       │  ┌──────────────┐ │
│  │  PostgreSQL  │  │    Redis     │       └──┤  phi3:mini   │ │
│  │  (Database)  │  │   (Cache)    │          │   (Model)    │ │
│  │  Port 5432   │  │  Port 6379   │          └──────────────┘ │
│  └──────┬───────┘  └──────┬───────┘                            │
│         │                 │                                     │
│  ┌──────▼─────────────────▼──────────────────────────┐         │
│  │              Celery Workers                        │         │
│  │  (Async Tasks + Scheduled Jobs)                   │         │
│  └────────────────────────────────────────────────────┘         │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                    OBSERVABILITY STACK                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Prometheus  │  │     Loki     │  │   Grafana    │          │
│  │  (Metrics)   │  │    (Logs)    │  │ (Dashboards) │          │
│  │  Port 9090   │  │  Port 3100   │  │  Port 3001   │          │
│  └──────▲───────┘  └──────▲───────┘  └──────────────┘          │
│         │                 │                                      │
│  ┌──────┴───────┬─────────┴─────────┬──────────────┐           │
│  │ Node Exporter│   Promtail        │  Exporters   │           │
│  │ (Host)       │   (Logs)          │  (PG/Redis)  │           │
│  └──────────────┴───────────────────┴──────────────┘           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Services (18 Total)

### Core Application (7 services)

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| **postgres** | postgres:16-alpine | 5432 | Multi-tenant database with RLS |
| **redis** | redis:7-alpine | 6379 | Cache layer & message broker |
| **backend** | Custom (Python 3.11) | 8000 | FastAPI REST API |
| **celery_worker** | Custom (Python 3.11) | - | Async task processing |
| **celery_beat** | Custom (Python 3.11) | - | Task scheduling |
| **frontend** | Custom (Node 20) | 3000 | Next.js web application |
| **nginx** | nginx:alpine | 80/443 | Reverse proxy & rate limiting |

### Observability Stack (6 services)

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| **prometheus** | prom/prometheus | 9090 | Metrics database & queries |
| **loki** | grafana/loki | 3100 | Log aggregation system |
| **promtail** | grafana/promtail | 9080 | Log collector agent |
| **grafana** | grafana/grafana | 3001 | Visualization & dashboards |
| **node-exporter** | prom/node-exporter | 9100 | Host system metrics |
| **postgres-exporter** | prometheuscommunity/postgres-exporter | 9187 | PostgreSQL metrics |
| **redis-exporter** | oliver006/redis_exporter | 9121 | Redis metrics |

### AI Stack (2 services)

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| **ollama** | ollama/ollama:latest | 11434 | Local LLM inference (GPU) |
| **ollama-init** | ollama/ollama:latest | - | Model downloader (one-time) |

**GPU Support**: NVIDIA GTX 1050 (3GB VRAM, CUDA 6.1)  
**Model**: phi3:mini (1.3B parameters, 2.2GB)  
**Performance**: 7-10s first query, ~1-2s subsequent

### Automation (3 services)

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| **n8n** | n8nio/n8n | 5678 | Workflow automation |
| **n8n-loader** | Custom | - | Workflow loader (one-time) |

**Workflows**: 6 pre-configured (SLO reports, alerts, health checks)

---

## 🔑 Key Features

### 🏢 Multi-Tenancy
- Row-Level Security (RLS) in PostgreSQL
- Tenant isolation at database level
- Automatic tenant context in all queries

### 🤖 AI Integration
- Local LLM with GPU acceleration
- 3 AI endpoints: `/query`, `/health`, `/analyze-anomaly`
- Automatic anomaly explanation
- Privacy-first (no data leaves your server)

### 📊 Observability
- **Metrics**: Prometheus + 3 exporters (host, PostgreSQL, Redis)
- **Logs**: Loki + Promtail (systemd + Docker logs)
- **Dashboards**: 2 pre-configured Grafana dashboards
- **Alerts**: 8 automated alerts (CPU, memory, disk, latency)
- **SLOs**: Uptime 99.9%, Error Rate <1%, Latency P95 <1s

### 🔄 Automation
- **n8n Workflows**:
  - Daily SLO Report (9 AM)
  - High CPU Alert (every 5 min, >80%)
  - Memory Warning (every 10 min, >85%)
  - Anomaly Detector (every 15 min)
  - Database Health Check (every 6 hours)
  - Weekly Summary (Mondays 10 AM)

### 🔒 Security
- Auditd watchdog for exploit detection
- Security alerts via n8n
- Rate limiting in Nginx
- HTTPS ready (certificates required)

### ⚡ Performance
- Async-first architecture (asyncpg, httpx)
- Connection pooling
- Redis caching
- Celery for background tasks
- GPU-accelerated AI inference

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104
- **ORM**: SQLAlchemy 2.0 (async)
- **Database Driver**: asyncpg (3-5x faster than psycopg2)
- **Validation**: Pydantic 2.5
- **Task Queue**: Celery 5.3
- **AI Client**: httpx (async)

### Frontend
- **Framework**: Next.js 14
- **UI**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **State**: React hooks
- **API Client**: Fetch API

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

## 📂 Project Structure

```
sentinel/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database setup
│   │   ├── models/            # SQLAlchemy models
│   │   ├── routers/           # API endpoints
│   │   │   ├── ai.py          # AI integration endpoints
│   │   │   ├── analytics.py  # Analytics & anomalies
│   │   │   └── ...
│   │   ├── services/          # Business logic
│   │   │   └── anomaly_detector.py  # Anomaly detection
│   │   └── tasks/             # Celery tasks
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/               # App Router pages
│   │   ├── components/        # React components
│   │   └── lib/               # Utilities
│   └── package.json
│
├── observability/              # Observability stack
│   ├── prometheus/
│   │   ├── prometheus.yml     # Scrape config
│   │   └── rules/alerts.yml   # Alert rules
│   ├── loki/
│   │   └── loki-config.yml
│   ├── promtail/
│   │   └── promtail-config.yml
│   └── grafana/
│       └── provisioning/      # Auto-provisioned dashboards
│
├── n8n/                        # Automation workflows
│   ├── workflows/             # 6 pre-configured workflows
│   └── WORKFLOWS_GUIDE.md
│
├── docs/                       # Documentation
│   ├── AI_INTEGRATION_COMPLETE.md
│   ├── INSTALL_GPU.md
│   └── OLLAMA_GPU_SETUP.md
│
├── docker-compose.yml          # Service orchestration
├── startup.sh                  # One-command startup
├── .env.example                # Environment template
└── README.md                   # This file
```

---

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://sentinel_user:REDACTED_PASSWORD@postgres:5432/sentinel_db

# Redis
REDIS_URL=redis://redis:6379/0

# Backend
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
FASTAPI_ENV=development

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# Grafana
GRAFANA_USER=admin
GRAFANA_PASSWORD=REDACTED_PASSWORD

# n8n
N8N_USER=admin
N8N_PASSWORD=REDACTED_PASSWORD

# Ollama AI
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=phi3:mini
AI_ENABLED=true
```

### GPU Configuration (Optional)

If you have an NVIDIA GPU:

1. Install NVIDIA Container Toolkit:
   ```bash
   # See docs/INSTALL_GPU.md for detailed instructions
   sudo pacman -S nvidia-container-toolkit  # Arch Linux
   sudo nvidia-ctk runtime configure --runtime=docker
   sudo systemctl restart docker
   ```

2. GPU support is already enabled in `docker-compose.yml`

3. Verify GPU access:
   ```bash
   docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi
   ```

---

## 📖 Documentation

- **[AI Integration](docs/AI_INTEGRATION_COMPLETE.md)** - Complete AI setup guide
- **[GPU Setup](docs/INSTALL_GPU.md)** - Quick GPU installation
- **[Observability](OBSERVABILITY-STATUS.md)** - Metrics, logs, dashboards
- **[n8n Workflows](n8n/WORKFLOWS_GUIDE.md)** - Automation guide
- **[Architecture](ARCHITECTURE.md)** - SOLID principles & design
- **[Analytics](PHASE_2_ANALYTICS.md)** - Anomaly detection details
- **[Services](SERVICIOS_ACTIVOS.md)** - All active services list

---

## 🔧 Common Commands

### Service Management

```bash
# Start all services
./startup.sh

# Start specific service
docker-compose up -d SERVICE_NAME

# Stop all services
docker-compose down

# Restart service
docker-compose restart SERVICE_NAME

# View logs
docker-compose logs -f SERVICE_NAME

# View all service status
docker-compose ps
```

### Database

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U sentinel_user -d sentinel_db

# Run migrations
docker-compose exec backend alembic upgrade head

# Create migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### AI

```bash
# Test AI endpoint
curl -X POST http://localhost:8000/api/v1/ai/query \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Explain CPU anomaly","max_tokens":50}'

# Check AI health
curl http://localhost:8000/api/v1/ai/health | jq

# Download additional model
docker-compose exec ollama ollama pull llama3.2:1b
```

### Monitoring

```bash
# View Prometheus targets
open http://localhost:9090/targets

# View Grafana dashboards
open http://localhost:3001

# Check metrics
curl http://localhost:8000/metrics
```

---

## 🚨 Troubleshooting

### Services Not Starting

```bash
# Check Docker
docker info

# Check logs
docker-compose logs SERVICE_NAME

# Rebuild service
docker-compose build SERVICE_NAME
docker-compose up -d SERVICE_NAME
```

### Database Connection Issues

```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres pg_isready -U sentinel_user

# Reset database (⚠️ destroys data)
docker-compose down -v
docker-compose up -d postgres
```

### AI Not Working

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# View Ollama logs
docker-compose logs ollama

# Restart Ollama
docker-compose restart ollama

# Re-download model
docker-compose exec ollama ollama pull phi3:mini
```

### High Resource Usage

```bash
# Check resource usage
docker stats

# Limit Ollama memory (edit docker-compose.yml)
# Add under ollama service:
#   deploy:
#     resources:
#       limits:
#         memory: 4G
```

---

## 📊 Performance Benchmarks

### API Performance
- **Latency**: P95 < 100ms (without AI)
- **Throughput**: 1000+ req/s
- **Concurrent Users**: 100+

### AI Performance
- **First Query**: 7-10s (model loading)
- **Subsequent**: 1-2s (with GPU)
- **CPU Only**: 3-5s

### Database
- **Connection Pool**: 20 connections
- **Query Cache**: Redis (TTL 5min)
- **RLS Overhead**: <5ms

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

---

## 📄 License

This project is proprietary software.

---

## 🙏 Acknowledgments

- **FastAPI** - Modern async web framework
- **Next.js** - React framework
- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **Ollama** - Local LLM inference
- **n8n** - Workflow automation

---

**Built with ❤️ by the Sentinel Team**
