# Sentinel - Quick Start Guide

**Get Sentinel running in 5 minutes**

---

## Prerequisites

- Docker & Docker Compose installed
- 8GB RAM minimum (16GB recommended)
- 20GB disk space
- (Optional) NVIDIA GPU for AI acceleration

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-org/sentinel.git
cd sentinel
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work for development)
```

### 3. Start Sentinel

```bash
./startup.sh
```

This will:
- ✅ Start all 18 services
- ✅ Download AI models (first run only, ~2GB)
- ✅ Wait for health checks
- ✅ Display access URLs

**Startup time**: ~3-5 minutes (first run), ~1-2 minutes (subsequent)

---

## Access Points

Once started, access Sentinel at:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Grafana** | http://localhost:3001 | admin / admin |
| **Prometheus** | http://localhost:9090 | - |
| **n8n** | http://localhost:5678 | admin / darkfenix |

---

## Verify Installation

### 1. Check Services

```bash
docker-compose ps
```

All services should show "Up" status.

### 2. Test API

```bash
curl http://localhost:8000/health | jq
```

Should return:
```json
{
  "status": "healthy",
  "components": {
    "database": {"status": "healthy"},
    "redis": {"status": "healthy"}
  }
}
```

### 3. Test AI

```bash
curl -X POST http://localhost:8000/api/v1/ai/query \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello, how are you?","max_tokens":50}'
```

Should return AI response within 1-10 seconds.

---

## Next Steps

### Explore Dashboards

1. **Executive Dashboard**: http://localhost:3000/dashboard
   - SLOs, AI insights, security alerts

2. **AI Playground**: http://localhost:3000/ai/playground
   - Test AI queries, see performance metrics

3. **Security Dashboard**: http://localhost:3000/security/watchdog
   - Auditd events, exploit detection

4. **Metrics**: http://localhost:3000/metrics
   - Grafana dashboards (create your own)

### Configure Monitoring

1. **Open Grafana**: http://localhost:3001
2. **Add Prometheus data source**: http://prometheus:9090
3. **Create dashboards** or import from [Grafana.com](https://grafana.com/grafana/dashboards/)

### Set Up Automation

1. **Open n8n**: http://localhost:5678
2. **Explore workflows**: 6 pre-configured workflows
3. **Customize alerts**: Edit workflows to match your needs

---

## Troubleshooting

### Services not starting?

```bash
# Check logs
docker-compose logs SERVICE_NAME

# Restart specific service
docker-compose restart SERVICE_NAME

# Full restart
docker-compose down
docker-compose up -d
```

### AI not working?

```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Re-download model
docker-compose exec ollama ollama pull phi3:mini

# Restart Ollama
docker-compose restart ollama
```

### High memory usage?

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

## Production Deployment

For production deployment with High Availability:

1. **Read HA docs**: [docs/HA_REFERENCE_DESIGN.md](HA_REFERENCE_DESIGN.md)
2. **Deploy PostgreSQL HA**: `docker-compose -f docker-compose-ha.yml up -d`
3. **Deploy Redis HA**: `docker-compose -f docker-compose-redis-ha.yml up -d`
4. **Configure DNS failover**: See [docs/FAILOVER_ORCHESTRATION.md](FAILOVER_ORCHESTRATION.md)
5. **Set up monitoring**: Configure Prometheus alerts
6. **Test failover**: Run `./scripts/test-redis-failover.sh`

---

## Support

- **Documentation**: [docs/](../docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/sentinel/issues)
- **Email**: support@sentinel.dev

---

**You're all set! 🎉**

Sentinel is now monitoring your infrastructure. Check the dashboards and explore the features.
