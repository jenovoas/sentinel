# Sentinel - Multi-Tenant SaaS Platform

A production-ready, fully-containerized multi-tenant SaaS platform built with FastAPI, Next.js, PostgreSQL, and async task processing.

## Quick Start

```bash
cd /home/jnovoas/sentinel
docker-compose up -d
```

Services start in ~2-3 minutes:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001 (admin / REDACTED_PASSWORD)
- **Prometheus**: http://localhost:9090
- **n8n Automation**: http://localhost:5678 (admin / REDACTED_PASSWORD)
- **Database**: localhost:5432
- **Cache**: localhost:6379

## Architecture

### Services (12 total)

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| **PostgreSQL** | postgres:16-alpine | 5432 | Multi-tenant database with RLS |
| **Redis** | redis:7-alpine | 6379 | Cache layer & message broker |
| **FastAPI Backend** | Custom (Python 3.11) | 8000 | REST API |
| **Celery Worker** | Custom (Python 3.11) | - | Async task processing |
| **Celery Beat** | Custom (Python 3.11) | - | Task scheduling |
| **Next.js Frontend** | Custom (Node 20) | 3000 | Web application |
| **Nginx** | nginx:alpine | 80/443 | Reverse proxy & rate limiting |
| **Prometheus** | prom/prometheus | 9090 | Metrics database & queries |
| **Loki** | grafana/loki | 3100 | Log aggregation system |
| **Promtail** | grafana/promtail | 9080 | Log collector agent |
| **Node Exporter** | prom/node-exporter | 9100 | Host system metrics |
| **Grafana** | grafana/grafana | 3001 | Visualization & dashboards |
| **n8n** | n8n | 5678 | Workflow automation & reports |

### Key Technologies

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Database**: PostgreSQL 16 with Row-Level Security (RLS)
- **Async**: Celery with Redis broker
- **Proxy**: Nginx with rate limiting and security headers
- **Observability**: Prometheus + Loki + Grafana stack

## Project Structure

```
sentinel/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database setup
│   │   ├── celery_app.py        # Celery configuration
│   │   ├── logging_config.py    # Logging setup
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routers/             # API route handlers
│   │   ├── services/            # Business logic
│   │   └── tasks/               # Celery async tasks
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile               # Production image
│   ├── Dockerfile.worker        # Celery worker image
│   └── Dockerfile.beat          # Celery Beat image
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router
│   │   ├── components/          # React components
│   │   ├── lib/                 # Utilities & helpers
│   │   └── store/               # State management
│   ├── package.json             # Node dependencies
│   ├── Dockerfile               # Production image
│   └── Dockerfile.dev           # Development image
├── docker/
│   ├── postgres/init.sql        # Database schema & RLS
│   ├── nginx/nginx.conf         # Reverse proxy config
│   └── redis/                   # Redis configuration
├── docker-compose.yml           # Service orchestration
├── .env                         # Environment variables
└── Makefile                     # Useful commands
```

## Configuration

All configuration via environment variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://sentinel_user:sentinel_password@postgres:5432/sentinel_db
# For local Postgres on host:
# DATABASE_URL=postgresql+asyncpg://sentinel_user:sentinel_password@localhost:5432/sentinel_db

# Redis
REDIS_URL=redis://redis:6379/0

# FastAPI
SECRET_KEY=your-secret-key-min-32-chars    # Change in production!
FASTAPI_ENV=development
LOG_LEVEL=INFO

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# Grafana Observability
GRAFANA_USER=admin
GRAFANA_PASSWORD=sentinel2024    # Change in production!
```

After bringing up services, run migrations before first use:

```bash
make up          # start stack
make db-migrate  # apply Alembic migrations in backend container
```

## 📊 Observability Stack

Sentinel includes a professional observability stack with Prometheus, Loki, and Grafana.

### Quick Start Observability

```bash
./observability-start.sh
```

Then access **Grafana** at http://localhost:3001 (admin / sentinel2024)

### What's Included

- ✅ **Real-time metrics**: CPU, memory, disk, network from your host
- ✅ **System logs**: Captured from journald and Docker containers
- ✅ **Pre-built dashboards**: Host metrics + system logs
- ✅ **Alerting**: 8 pre-configured alert rules
- ✅ **90-day retention**: Metrics stored for 3 months
- ✅ **30-day log retention**: Automatic cleanup

### Dashboards

1. **Host Metrics Overview** - CPU, memory, disk, network, filesystem usage
2. **System Logs** - Error rates, log streams, severity distribution

For complete documentation see [OBSERVABILITY.md](./OBSERVABILITY.md)

### Auditd Watchdog (Host Security)

#### Setup inicial:
```bash
sudo ./host-metrics/auditd_setup.sh   # instala auditd, habilita servicio y carga reglas base
```

#### Reglas disponibles:

**Base (siempre activas):**
- `exec-watchdog`: monitorea syscall `execve` (ejecuciones de procesos)
- `file-watchdog`: monitorea `open` fallidos
- `ptrace-watchdog`: monitorea `ptrace` (debug/injection)

Cargar persistentemente:
```bash
sudo ./host-metrics/install_auditd_rules.sh install
```

**Extra (opcional, lab avanzado):**
- `etc-change`: cambios en `/etc` (permisos/propietario)
- `shadow-access`: intentos fallidos de acceso a `/etc/shadow`
- `passwd-access`: intentos fallidos de acceso a `/etc/passwd`
- `tmp-exec`: execuciones desde `/tmp` y `/var/tmp`
- `kmod-change`: carga/descarga de módulos del kernel

Activar reglas extra:
```bash
sudo ./host-metrics/install_auditd_rules_extra.sh install
```

Desactivar:
```bash
sudo ./host-metrics/install_auditd_rules_extra.sh remove
```

#### Watchdog daemon:

Ejecuta watchdog como servicio systemd (monitorea logs y reinicia auditd si detecta patrones):
```bash
sudo ./observability/node-exporter/install_process_collector.sh
```

Ver logs: `journalctl -u audit-watchdog -f`

#### Métricas de procesos (Top memoria):

Daemon automático que captura consumo de memoria por proceso:
```bash
sudo ./observability/node-exporter/install_process_collector.sh
```

Ve a Grafana → "Sentinel - Host Metrics Overview" → panel "Top 10 Procesos por Memoria" (abajo).

## API Endpoints

### Health & Status
- `GET /` - Root endpoint
- `GET /api/v1/health` - Health check

### Users (Multi-tenant)
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/` - List users
- `GET /api/v1/users/{user_id}` - Get user
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Tenants
- `POST /api/v1/tenants/` - Create tenant
- `GET /api/v1/tenants/` - List tenants
- `GET /api/v1/tenants/{tenant_id}` - Get tenant
- `PUT /api/v1/tenants/{tenant_id}` - Update tenant
- `DELETE /api/v1/tenants/{tenant_id}` - Delete tenant

See full documentation at `/docs` when running.

## Key Features

### Multi-Tenancy
- PostgreSQL Row-Level Security (RLS) for automatic tenant isolation
- Every user belongs to exactly one tenant
- Queries automatically filtered by tenant_id

### Security
- JWT authentication framework ready to implement
- Password hashing with bcrypt (configured)
- CORS for cross-origin requests
- Rate limiting at Nginx level (3 tiers)
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)

### Performance
- Async/await with FastAPI
- Redis caching layer
- Connection pooling with automatic recycling
- Celery for background tasks
- Celery Beat for scheduled tasks

### Operations
- Health check endpoints
- Structured logging with log rotation
- Docker health checks for all services
- Automatic container restart policies
- Volume persistence for data

---

## 🤖 Automation with n8n

Sentinel includes **n8n** for workflow automation and reporting.

### Access

- **URL**: http://localhost:5678
- **User**: admin
- **Password**: REDACTED_PASSWORD

### Pre-Built Workflows

1. **Daily SLO Report**: Sends Slack with availability, burn rate, error budget
2. **Burn Rate Alert**: Triggers when 2h burn rate > 30x
3. **Health Check**: Pings services every 15 minutes

### Integration Options

**Slack** (Recommended):
1. Create Slack app with incoming webhooks
2. Add webhook URL to n8n
3. Get daily reports in Slack channel

**Email**:
- Use SMTP for notifications
- Local mailhog at http://localhost:1025 for testing
- Configure real SMTP for production

See [observability/n8n/workflows-readme.md](observability/n8n/workflows-readme.md) for setup guide.

### Quick Setup Script

```bash
# Configure n8n with Slack webhook
./observability/n8n/setup-n8n-slack.sh "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

## Useful Commands

```bash
# View status
docker-compose ps

# View logs
docker-compose logs -f [service]

# Restart service
docker-compose restart backend

# Access database
docker-compose exec postgres psql -U sentinel_user -d sentinel_db

# Backend shell
docker-compose exec backend bash

# Stop everything
docker-compose down

# Clean everything including volumes
docker-compose down -v
```

## Development

### Backend
```bash
# Install dependencies
docker-compose exec backend pip install -r requirements.txt

# Run tests (when added)
docker-compose exec backend pytest

# Format code
docker-compose exec backend black app/

# Check types
docker-compose exec backend mypy app/
```

### Frontend
```bash
# Install dependencies
docker-compose exec frontend npm install

# Build for production
docker-compose exec frontend npm run build

# Format code
docker-compose exec frontend npm run format
```

## Database Schema

The database includes:

### Tables
- **tenants**: Organizations/accounts
- **users**: User accounts with tenant association
- **audit_logs**: Event logging for compliance

### RLS Policies
- Users see only their tenant's data
- Audit logs filtered by tenant
- Extensible to additional entity tables

See `docker/postgres/init.sql` for complete schema.

## Production Deployment

### Before Deploying

**CRITICAL CHANGES**:
```bash
# Generate secure secret key
openssl rand -hex 32

# Update .env with:
SECRET_KEY=<generated-key>
FASTAPI_ENV=production
ALLOWED_ORIGINS=https://yourdomain.com

# Change database passwords
POSTGRES_PASSWORD=<secure-password>
```

### Infrastructure
1. Use managed PostgreSQL (AWS RDS, Azure Database, etc.) instead of container
2. Use managed Redis (AWS ElastiCache, Azure Cache, etc.)
3. Configure SSL/TLS certificates for HTTPS
4. Set up automated backups
5. Configure load balancing for multiple backend instances
6. Set up monitoring and alerting

### Scaling
```bash
# Scale worker processes
docker-compose up -d --scale celery_worker=5

# Use external databases
# Update DATABASE_URL and REDIS_URL in .env
```

## Troubleshooting

### Services won't start
```bash
docker-compose logs [service]
```

### Database connection errors
```bash
docker-compose exec postgres pg_isready -U sentinel_user
```

### Port already in use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Clear cache and rebuild
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Code Quality & Standards

### Backend Code Organization
- Each module has clear responsibilities
- Comprehensive docstrings following Google style
- Type hints for all functions
- Separation of concerns (routers, services, models)

### Frontend Code Organization
- Component-based architecture
- TypeScript for type safety
- Tailwind CSS for styling
- App Router for routing

### Testing
- Unit tests in progress
- Integration tests ready
- Use pytest for backend testing

### Documentation
- All functions documented
- Comments explain "why", not "what"
- Examples provided for complex functionality

---

## 🎯 SLOs & Error Budget Management

### SLO Definitions

**Sentinel follows these Service Level Objectives:**

| SLO | Target | Error Budget/Month | 
|-----|--------|-------------------|
| **Uptime** | 99.9% | 43.2 minutes downtime |
| **Error Rate** | <1% | 1 error per 100 requests |
| **Latency P95** | <1s | Max 95th percentile latency |

### Understanding Burn Rate

**Burn Rate** measures how fast you consume your error budget:

```
Burn Rate = (1 - Availability) / (1 - SLO Target)

Examples:
- Burn Rate 2h = 0.5x → Breaking SLO in ~60 days (normal)
- Burn Rate 2h = 10x → Breaking SLO in 6 days (degrading)
- Burn Rate 2h = 30x → Breaking SLO in <2 hours (CRITICAL)
```

### Alert Thresholds

Prometheus alerts are configured to fire when:

1. **🔴 Fast Burn (2h window)**: Burn Rate > 30x
   - **Action**: Page on-call immediately. Investigate outage/incident.
   - **Implication**: If not fixed in 2 hours, SLO breaks.

2. **🟡 Slow Burn (24h window)**: Burn Rate > 10x
   - **Action**: Schedule incident review within 4 hours.
   - **Implication**: If not fixed in 3 days, SLO breaks.

### Monitoring Dashboard

Access the SLO Dashboard in Grafana:
- **URL**: http://localhost:3001/d/slo-error-budget
- **Panels**:
  - 📊 Disponibilidad Mensual (pie chart)
  - 🎯 SLO Target vs Actual (99.9% goal)
  - 🔥 Burn Rate Trends (2h and 24h)
  - 💰 Error Budget Remaining (%)
  - 📈 Availability Over Time (hourly/daily/monthly)
  - ⚠️ Current Error Rate

### Prometheus Recording Rules

Pre-computed metrics for dashboards (updated every 1 minute):

```promql
# Availability metrics
slo:availability:hourly      # Last hour uptime %
slo:availability:daily       # Last day uptime %
slo:availability:monthly     # Last 30 days uptime %

# Error budget tracking
slo:error_budget:remaining   # % of budget left
slo:burnrate:2h              # Burn rate (2h window)
slo:burnrate:24h             # Burn rate (24h window)

# Error rate metrics
slo:error_rate:5m            # Error rate last 5 minutes
```

### Example Alert Queries

Check status in Prometheus:

```bash
# View current burn rate
curl http://localhost:9090/api/v1/query?query=slo:burnrate:2h

# View error budget remaining
curl http://localhost:9090/api/v1/query?query=slo:error_budget:remaining

# View monthly availability
curl http://localhost:9090/api/v1/query?query=slo:availability:monthly
```

### Recommended Actions by Error Budget

| Budget | Status | Action |
|--------|--------|--------|
| >50% | ✅ Green | Normal operations. Deploy and iterate. |
| 25-50% | 🟡 Caution | Slow burn detected. Review incidents. |
| 10-25% | 🟠 Warning | Freeze new deployments. Focus on stability. |
| <10% | 🔴 Critical | Only critical hotfixes. Prepare maintenance window. |

### Configuration (alerts.yml)

SLO rules are defined in `observability/prometheus/rules/alerts.yml`:

```yaml
# Uptime SLO: 99.9%
- alert: SLO_Uptime_BurnRateFast
  expr: (1 - avg(rate(up{job=~"fastapi|sentinel"}[2h]))) > 0.001 * 30
  # Fires if losing uptime faster than 30x budget rate

# Error Rate SLO: <1%
- alert: SLO_ErrorRate_High
  expr: sum(rate(sentinel_errors_total[5m])) / sum(rate(sentinel_requests_total[5m])) > 0.01
  # Fires if error rate exceeds 1%

# Latency SLO: P95 <1s
- alert: SLO_LatencyHigh
  expr: histogram_quantile(0.95, ...) > 1
  # Fires if P95 latency exceeds 1 second
```

### Reload SLO Rules

After updating `alerts.yml`, reload Prometheus:

```bash
docker-compose restart prometheus
```

Or use Prometheus API:
```bash
curl -X POST http://localhost:9090/-/reload
```

---

## Deployment Checklist

- [ ] Change `SECRET_KEY`
- [ ] Update `ALLOWED_ORIGINS`
- [ ] Change database passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Review RLS policies
- [ ] Test under load
- [ ] Security audit

## Support & Contributing

This is a team project. Please:

1. **Before making changes**: Create an issue describing what you'll do
2. **Code style**: Follow existing patterns and maintain comments
3. **Testing**: Add tests for new features
4. **Documentation**: Update docs alongside code changes
5. **Pull requests**: Clear description of changes and why

## License

Internal project - Sentinel Platform

---

**Last Updated**: December 13, 2024  
**Maintained by**: Development Team  
**Status**: Production Ready ✅
