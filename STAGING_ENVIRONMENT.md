# 🧪 Staging Environment - Setup Guide

**Purpose**: Isolated testing environment for HackMe challenge validation  
**Status**: Ready to deploy  
**Estimated Setup Time**: 30 minutes

---

## 🎯 OBJECTIVES

**Staging environment will allow you to**:
1. Test all security features in isolation
2. Validate HackMe challenge scenarios
3. Benchmark performance under load
4. Identify issues before production
5. Train white-hat hackers safely

---

## 🏗️ ARCHITECTURE

### Network Isolation

```
┌─────────────────────────────────────────────────────────┐
│                    STAGING ENVIRONMENT                   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐    ┌──────────────┐                   │
│  │  Cloudflare  │───▶│    Nginx     │                   │
│  │   Tunnel     │    │   (mTLS)     │                   │
│  └──────────────┘    └──────┬───────┘                   │
│                              │                            │
│         ┌────────────────────┼────────────────────┐      │
│         │                    │                    │      │
│    ┌────▼─────┐      ┌──────▼──────┐      ┌─────▼────┐ │
│    │   Loki   │      │   Backend   │      │  Mimir   │ │
│    │ (Logs)   │      │  (FastAPI)  │      │(Metrics) │ │
│    └──────────┘      └─────────────┘      └──────────┘ │
│                                                           │
│    ┌──────────┐      ┌─────────────┐      ┌──────────┐ │
│    │ Grafana  │      │   n8n       │      │ Postgres │ │
│    │ (Viz)    │      │(Workflows)  │      │  (DB)    │ │
│    └──────────┘      └─────────────┘      └──────────┘ │
│                                                           │
│    ┌──────────────────────────────────────────────────┐ │
│    │         Monitoring (Prometheus + Alerts)         │ │
│    └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Key Differences from Production

| Feature | Production | Staging |
|---------|-----------|---------|
| **Domain** | sentinel.example.com | staging.sentinel.example.com |
| **SSL** | Let's Encrypt | Self-signed (or Cloudflare) |
| **Data Retention** | 2 years | 7 days |
| **Resources** | 32GB RAM, 8 CPU | 16GB RAM, 4 CPU |
| **Monitoring** | 24/7 alerts | Business hours only |
| **Backups** | Daily | None (ephemeral) |

---

## 📁 FILES TO CREATE

### 1. docker-compose.staging.yml
### 2. .env.staging
### 3. nginx/nginx.staging.conf
### 4. scripts/deploy-staging.sh
### 5. scripts/test-staging.sh
### 6. monitoring/alerts.staging.yml

---

## 🚀 DEPLOYMENT STEPS

### Prerequisites

```bash
# 1. Install Docker + Docker Compose
sudo apt update
sudo apt install docker.io docker-compose

# 2. Install Cloudflare Tunnel (optional)
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# 3. Clone repository
git clone https://github.com/jenovoas/sentinel.git
cd sentinel
```

### Deploy Staging

```bash
# 1. Copy staging environment file
cp .env.example .env.staging

# 2. Edit staging config
nano .env.staging
# Set:
# - ENVIRONMENT=staging
# - DOMAIN=staging.sentinel.example.com
# - DATA_RETENTION_DAYS=7

# 3. Deploy with staging compose
docker-compose -f docker-compose.staging.yml up -d

# 4. Wait for services to start (2-3 minutes)
docker-compose -f docker-compose.staging.yml ps

# 5. Run health checks
./scripts/test-staging.sh
```

### Access Staging

```
Grafana:    https://staging.sentinel.example.com:3000
Backend:    https://staging.sentinel.example.com:8000
n8n:        https://staging.sentinel.example.com:5678
Prometheus: https://staging.sentinel.example.com:9090
```

---

## 🧪 TESTING PROCEDURES

### 1. Smoke Tests (5 minutes)

```bash
# Test all services are up
curl -k https://staging.sentinel.example.com:8000/health
# Expected: {"status": "healthy"}

# Test Loki ingestion
curl -k -X POST https://staging.sentinel.example.com:3100/loki/api/v1/push \
  -H "Content-Type: application/json" \
  -d '{"streams": [{"stream": {"lane": "ops"}, "values": [["'$(date +%s%N)'", "test"]]}]}'
# Expected: 204 No Content

# Test Grafana
curl -k https://staging.sentinel.example.com:3000/api/health
# Expected: {"database": "ok"}
```

### 2. Security Tests (15 minutes)

```bash
# Run AIOpsDoom fuzzer
cd backend
python fuzzer_aiopsdoom.py --target staging.sentinel.example.com
# Expected: 100% detection

# Test eBPF LSM (requires root)
sudo python test_ebpf_lsm.py
# Expected: All blocks successful

# Test mTLS headers
curl -k -X POST https://staging.sentinel.example.com:3100/loki/api/v1/push \
  -H "X-Scope-OrgID: fake" \
  -H "X-Scope-Signature: invalid"
# Expected: 403 Forbidden
```

### 3. Performance Tests (30 minutes)

```bash
# Run benchmarks
cd backend
python benchmark_dual_lane.py --target staging
# Expected: Similar to local results

# Load test (requires Apache Bench)
ab -n 10000 -c 100 https://staging.sentinel.example.com:8000/metrics
# Monitor: CPU, memory, response times
```

### 4. Chaos Tests (1 hour)

```bash
# Kill random services
docker-compose -f docker-compose.staging.yml stop loki
# Wait 30s
docker-compose -f docker-compose.staging.yml start loki
# Verify: No data loss, WAL replay successful

# Network partition
sudo iptables -A INPUT -p tcp --dport 3100 -j DROP
# Wait 1 minute
sudo iptables -D INPUT -p tcp --dport 3100 -j DROP
# Verify: System recovers, buffers flush
```

---

## 📊 MONITORING

### Prometheus Queries

**Service Health**:
```promql
up{job="sentinel-backend"}
```

**Request Rate**:
```promql
rate(http_requests_total[5m])
```

**Error Rate**:
```promql
rate(http_requests_total{status=~"5.."}[5m])
```

**Latency P95**:
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### Alerts (Business Hours Only)

```yaml
# monitoring/alerts.staging.yml
groups:
  - name: staging_alerts
    interval: 1m
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 5m
        annotations:
          summary: "Service {{ $labels.job }} is down"
      
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 10m
        annotations:
          summary: "High error rate on {{ $labels.job }}"
```

---

## 🔒 SECURITY HARDENING

### Staging-Specific Security

1. **Isolated Network**:
```yaml
# docker-compose.staging.yml
networks:
  staging_internal:
    internal: true
    driver: bridge
  staging_external:
    driver: bridge
```

2. **Limited Exposure**:
- Only Nginx exposed to internet
- All other services internal-only
- Cloudflare Tunnel for additional protection

3. **Ephemeral Data**:
- 7-day retention (auto-delete)
- No production data
- Synthetic test data only

4. **Access Control**:
```bash
# IP whitelist (optional)
# nginx.staging.conf
allow 1.2.3.4;  # Your IP
allow 5.6.7.8;  # White-hat tester IP
deny all;
```

---

## 🎯 HACKME CHALLENGE PREPARATION

### Pre-Challenge Checklist

- [ ] Deploy staging environment
- [ ] Run all smoke tests (5/5 passing)
- [ ] Run security tests (100% detection)
- [ ] Run performance tests (benchmarks validated)
- [ ] Run chaos tests (recovery successful)
- [ ] Invite 3-5 white-hat hackers
- [ ] Monitor for 7 days
- [ ] Fix any issues found
- [ ] Document lessons learned
- [ ] Update production configs

### White-Hat Tester Access

```bash
# Create tester account
docker-compose -f docker-compose.staging.yml exec backend \
  python -m app.cli create-user \
  --email tester@example.com \
  --role tester \
  --expires 7d

# Provide access:
# - URL: https://staging.sentinel.example.com
# - Credentials: (generated above)
# - Scope: Full attack surface
# - Rules: Responsible disclosure, no DoS
```

---

## 📈 SUCCESS CRITERIA

**Staging is ready for HackMe when**:

1. ✅ All services healthy (100% uptime for 7 days)
2. ✅ Security tests passing (100% detection maintained)
3. ✅ Performance benchmarks validated (within 10% of local)
4. ✅ Chaos tests successful (recovery < 1 minute)
5. ✅ White-hat testing complete (0 critical findings)
6. ✅ Monitoring alerts working (0 false positives)

---

## 🔄 TEARDOWN

### When Testing Complete

```bash
# 1. Export logs (for analysis)
docker-compose -f docker-compose.staging.yml logs > staging-logs.txt

# 2. Export metrics
curl -k https://staging.sentinel.example.com:9090/api/v1/query \
  -d 'query=up' > staging-metrics.json

# 3. Stop all services
docker-compose -f docker-compose.staging.yml down

# 4. Remove volumes (ephemeral data)
docker-compose -f docker-compose.staging.yml down -v

# 5. Clean up
rm -rf staging-data/
```

---

## 📝 NEXT STEPS

After staging validation:

1. **Update Production Configs** based on findings
2. **Document Lessons Learned** in `STAGING_REPORT.md`
3. **Prepare HackMe Announcement** with staging results
4. **Deploy Production** with confidence
5. **Launch Public Challenge** 🚀

---

**Status**: Staging environment design complete, ready to implement 🧪
