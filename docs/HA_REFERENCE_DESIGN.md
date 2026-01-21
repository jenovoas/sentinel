# Sentinel Multi-Site HA Architecture - Reference Design

**Version**: 1.0  
**Date**: December 15, 2025  
**Status**: Design Phase - Ready for Implementation

---

## 🎯 Architecture Overview

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLIENT NETWORKS                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ Client A │  │ Client B │  │ Client C │  │ Client D │               │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘               │
└───────┼─────────────┼─────────────┼─────────────┼─────────────────────┘
        │             │             │             │
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    DNS LAYER (INDEPENDENT HA)                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                              │
│  │ Pi-hole 1│  │ Pi-hole 2│  │ Pi-hole 3│  ← Gravity Sync              │
│  │ Primary  │  │ Secondary│  │ Tertiary │  ← Autonomous operation      │
│  └──────────┘  └──────────┘  └──────────┘                              │
│  Survives Sentinel failure - Critical for network uptime                │
└───────┬─────────────────────────────────────────────────────────────────┘
        │
        │ Monitoring only (not control)
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              GLOBAL DNS FAILOVER / LOAD BALANCER                         │
│                  sentinel.yourdomain.com                                 │
│              (Route53 / Cloudflare / DNS Failover)                       │
└───────┬─────────────────────────────────────┬───────────────────────────┘
        │                                     │
        │ Primary Route                       │ Failover Route
        │ (Health check: every 30s)           │ (Activates on failure)
        │                                     │
        ▼                                     ▼
┌──────────────────────────┐        ┌──────────────────────────┐
│   ON-PREMISE SITE        │        │     CLOUD SITE           │
│   (Primary Active)       │◄──────►│   (Standby/DR)           │
│                          │  VPN   │                          │
│  ┌────────────────────┐  │        │  ┌────────────────────┐  │
│  │ Sentinel Stack     │  │        │  │ Sentinel Stack     │  │
│  │ - Frontend         │  │        │  │ - Frontend         │  │
│  │ - Backend          │  │        │  │ - Backend          │  │
│  │ - Prometheus       │  │        │  │ - Prometheus       │  │
│  │ - Grafana          │  │        │  │ - Grafana          │  │
│  │ - Loki             │  │        │  │ - Loki             │  │
│  │ - Redis Sentinel   │  │        │  │ - Redis Sentinel   │  │
│  │ - Ollama (GPU)     │  │        │  │ - Ollama (CPU)     │  │
│  └────────┬───────────┘  │        │  └────────┬───────────┘  │
│           │              │        │           │              │
│           ▼              │        │           ▼              │
│  ┌────────────────────┐  │        │  ┌────────────────────┐  │
│  │ PostgreSQL HA      │  │        │  │ PostgreSQL HA      │  │
│  │ ┌────────────────┐ │  │        │  │ ┌────────────────┐ │  │
│  │ │ Primary + Rep  │ │  │        │  │ │ Standby        │ │  │
│  │ │ (Patroni)      │ │◄─┼────────┼──┼►│ (Async Rep)    │ │  │
│  │ └────────────────┘ │  │ Async  │  │ └────────────────┘ │  │
│  │ HAProxy: 5432/5433│  │ Repl   │  │ HAProxy: 5432/5433│  │
│  └────────┬───────────┘  │        │  └────────┬───────────┘  │
│           │              │        │           │              │
│           ▼              │        │           ▼              │
│  ┌────────────────────┐  │        │  ┌────────────────────┐  │
│  │ S3/MinIO Backups   │  │        │  │ S3/MinIO Backups   │  │
│  │ Every 6 hours      │◄─┼────────┼──┼►│ Sync from primary│  │
│  └────────────────────┘  │        │  └────────────────────┘  │
│                          │        │                          │
│  Local Metrics Storage   │        │  Metrics Aggregation     │
│  15 days retention       │        │  Long-term (Thanos)      │
└──────────────────────────┘        └──────────────────────────┘
```

---

## 🔄 Operational Modes

### Mode 1: Normal Operation (Both Sites Active)

```
State: ON-PREMISE = PRIMARY, CLOUD = STANDBY

Traffic Flow:
  Clients → DNS (sentinel.yourdomain.com)
         → ON-PREMISE (primary route)
         → HAProxy → PostgreSQL Primary
         → Sentinel Backend → Response

Data Flow:
  PostgreSQL Primary (on-prem)
    ├─► Streaming Replication → PostgreSQL Replica (on-prem)
    └─► Async Replication → PostgreSQL Standby (cloud)
  
  Backups:
    On-prem → S3/MinIO → Cloud (sync every 6h)

Monitoring:
  Sentinel monitors Pi-holes (does not control)
  Prometheus scrapes all endpoints
  Grafana displays unified view
```

### Mode 2: On-Premise Failure (Cloud Takeover)

```
State: ON-PREMISE = DOWN, CLOUD = PRIMARY

Trigger: Health check fails (3 consecutive failures = 90s)

Automatic Actions:
  1. DNS failover activates (TTL 60s)
  2. Traffic routes to cloud site
  3. Cloud PostgreSQL promotes to primary (if using async rep)
  4. Cloud Sentinel becomes active
  5. Alerts sent to ops team

Client Impact:
  - DNS clients: 60-120s to switch (DNS TTL + cache)
  - Pi-hole: ZERO impact (autonomous)
  - Monitoring: Brief gap (< 2 minutes)
  - Data loss: < 5 minutes (RPO)

Manual Actions Required:
  1. Investigate on-premise failure
  2. Decide: repair or rebuild
  3. When ready: failback to on-premise
```

### Mode 3: Degraded Mode (Both Sites Down)

```
State: SENTINEL = DOWN, DNS = UP

What Still Works:
  ✅ DNS filtering (Pi-hole autonomous)
  ✅ Network connectivity
  ✅ Local services

What Stops:
  ❌ Centralized monitoring
  ❌ AI analysis
  ❌ Alerting
  ❌ Automation workflows
  ❌ Dashboard access

Recovery:
  1. Restore cloud site from backups (15-30 min)
  2. Point DNS to cloud
  3. Resume operations in degraded mode
  4. Rebuild on-premise when possible
```

---

## 📋 Component Checklist

### PostgreSQL HA Cluster

**On-Premise Cluster**:
- [x] Patroni + etcd configured
- [x] HAProxy load balancer
- [x] Streaming replication (< 1s lag)
- [x] Automated backups (every 6h)
- [x] Backup retention (7 days local)
- [ ] S3/MinIO integration for backups
- [ ] Point-in-time recovery tested
- [ ] Monitoring (Prometheus exporter)
- [ ] Alerting (replication lag > 10s)

**Cloud Cluster**:
- [ ] Identical Patroni setup
- [ ] Async replication from on-premise
- [ ] Backup sync from S3/MinIO
- [ ] Promotion procedure documented
- [ ] Tested failover scenario

**Connection Configuration**:
```yaml
# Backend environment variables
DATABASE_HOST: postgres-haproxy  # Not direct postgres!
DATABASE_PORT: 5432              # Primary (RW)
DATABASE_REPLICA_PORT: 5433      # Replica (RO) for analytics
DATABASE_USER: sentinel
DATABASE_PASSWORD: ${POSTGRES_PASSWORD}
DATABASE_NAME: sentinel
```

---

### Sentinel Application (Backend + Frontend)

**Containerization**:
- [x] Docker images built
- [x] Environment-based configuration
- [ ] Health check endpoints
- [ ] Graceful shutdown handling
- [ ] Connection retry logic
- [ ] Circuit breaker for DB
- [ ] Stateless design (session in Redis)

**Configuration Management**:
```yaml
# All config from environment/secrets
- DATABASE_URL (from HAProxy, not direct postgres)
- REDIS_URL (from Redis Sentinel)
- OLLAMA_URL
- S3_BACKUP_BUCKET
- ALERT_WEBHOOK_URL
```

**Health Check Endpoints**:
```python
# backend/app/routers/health.py
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": await check_db_connection(),
        "redis": await check_redis_connection(),
        "ollama": await check_ollama_connection(),
        "timestamp": datetime.now()
    }

@router.get("/health/ready")
async def readiness_check():
    # Only return 200 if ALL dependencies are ready
    # Used by load balancer to determine if node can serve traffic
    pass

@router.get("/health/live")
async def liveness_check():
    # Return 200 if process is alive (even if deps are down)
    # Used by orchestrator to determine if process should be restarted
    pass
```

**Deployment Checklist**:
- [ ] Health endpoints implemented
- [ ] Graceful shutdown (SIGTERM handling)
- [ ] Database connection pooling (max 20 per instance)
- [ ] Redis connection with retry
- [ ] Logging to stdout (for container logs)
- [ ] Metrics endpoint (/metrics for Prometheus)

---

### Redis HA (Session Store)

**Current State**: Single instance ❌

**Required**: Redis Sentinel

```yaml
# docker-compose-redis-ha.yml
services:
  redis-master:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    
  redis-replica-1:
    image: redis:7-alpine
    command: redis-server --replicaof redis-master 6379
    
  redis-replica-2:
    image: redis:7-alpine
    command: redis-server --replicaof redis-master 6379
    
  redis-sentinel-1:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
    
  redis-sentinel-2:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
    
  redis-sentinel-3:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
```

**Backend Integration**:
```python
# Use redis-py with Sentinel support
from redis.sentinel import Sentinel

sentinel = Sentinel([
    ('redis-sentinel-1', 26379),
    ('redis-sentinel-2', 26379),
    ('redis-sentinel-3', 26379)
], socket_timeout=0.1)

# Get master (read-write)
master = sentinel.master_for('mymaster', socket_timeout=0.1)

# Get slave (read-only)
slave = sentinel.slave_for('mymaster', socket_timeout=0.1)
```

**Checklist**:
- [ ] Redis Sentinel deployed (3 instances)
- [ ] Master + 2 replicas configured
- [ ] Backend uses Sentinel client
- [ ] Failover tested (< 10s)
- [ ] Session persistence verified

---

### DNS Filtering (Pi-hole) - CRITICAL

**Architecture**: 3 independent instances

```
Client DHCP Config:
  Primary DNS:   192.168.1.10 (Pi-hole 1)
  Secondary DNS: 192.168.1.11 (Pi-hole 2)
  Tertiary DNS:  192.168.1.12 (Pi-hole 3)
```

**Sync Mechanism**: Gravity Sync

```bash
# /etc/gravity-sync/gravity-sync.conf
REMOTE_HOST='pihole2.local'
REMOTE_USER='pihole'
SYNC_FREQUENCY='15'  # minutes

# Cron job (on Pi-hole 1)
*/15 * * * * /usr/local/bin/gravity-sync sync
```

**Sentinel Integration**:
```python
# Sentinel monitors but does NOT control
@router.get("/pihole/health")
async def check_pihole_health():
    results = []
    for pihole in PIHOLE_INSTANCES:
        try:
            response = await httpx.get(f"http://{pihole}/admin/api.php")
            results.append({
                "host": pihole,
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "queries_today": response.json().get("dns_queries_today", 0)
            })
        except Exception as e:
            results.append({"host": pihole, "status": "unreachable", "error": str(e)})
    
    return {"piholes": results, "autonomous": True}
```

**Checklist**:
- [ ] 3 Pi-hole instances deployed
- [ ] Gravity Sync configured and tested
- [ ] Client DHCP updated with all 3 DNS
- [ ] Sentinel monitoring endpoint created
- [ ] Alerts for Pi-hole failures
- [ ] **VERIFIED**: DNS works when Sentinel is down

---

### Monitoring Stack

**Prometheus Federation**:
```yaml
# On-premise Prometheus scrapes local targets
# Cloud Prometheus scrapes cloud targets
# Thanos aggregates both for global view

# prometheus-on-prem.yml
global:
  external_labels:
    site: on-premise
    
scrape_configs:
  - job_name: 'sentinel-backend'
    static_configs:
      - targets: ['backend:8000']
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-primary:9187', 'postgres-replica:9187']
  
  - job_name: 'pihole'
    static_configs:
      - targets: ['pihole1:9617', 'pihole2:9617', 'pihole3:9617']

# Remote write to Thanos (cloud)
remote_write:
  - url: http://thanos-receive.cloud:19291/api/v1/receive
```

**Grafana HA**:
```yaml
# Shared PostgreSQL for dashboards/users
# Session store in Redis
# Multiple Grafana instances behind load balancer

services:
  grafana-1:
    image: grafana/grafana:latest
    environment:
      - GF_DATABASE_TYPE=postgres
      - GF_DATABASE_HOST=postgres-haproxy:5432
      - GF_SESSION_PROVIDER=redis
      - GF_SESSION_PROVIDER_CONFIG=addr=redis-sentinel:26379
      
  grafana-2:
    image: grafana/grafana:latest
    # Same config as grafana-1
```

**Checklist**:
- [ ] Prometheus on both sites
- [ ] Thanos for global query
- [ ] Grafana HA (shared DB + Redis)
- [ ] Dashboards for HA metrics
- [ ] Alerts for failover events

---

### Network & DNS Failover

**Global DNS Configuration**:

```
# Route53 / Cloudflare Health Check
Health Check:
  - URL: https://sentinel-on-prem.yourdomain.com/health
  - Interval: 30 seconds
  - Failure threshold: 3 (90 seconds total)
  - Timeout: 10 seconds

DNS Records:
  sentinel.yourdomain.com (Primary)
    - Type: A
    - Value: <ON-PREMISE-IP>
    - TTL: 60 seconds
    - Health check: enabled
    
  sentinel.yourdomain.com (Failover)
    - Type: A
    - Value: <CLOUD-IP>
    - TTL: 60 seconds
    - Failover policy: activate on primary failure
```

**VPN Between Sites**:
```bash
# WireGuard recommended for site-to-site

# On-premise endpoint
[Interface]
Address = 10.0.0.1/24
PrivateKey = <on-prem-private-key>

[Peer]
PublicKey = <cloud-public-key>
Endpoint = <cloud-public-ip>:51820
AllowedIPs = 10.0.0.2/32

# Cloud endpoint
[Interface]
Address = 10.0.0.2/24
PrivateKey = <cloud-private-key>

[Peer]
PublicKey = <on-prem-public-key>
Endpoint = <on-prem-public-ip>:51820
AllowedIPs = 10.0.0.1/32
```

**Checklist**:
- [ ] DNS health checks configured
- [ ] Failover policy tested
- [ ] TTL optimized (60s recommended)
- [ ] VPN between sites (if using async replication)
- [ ] Firewall rules for replication traffic

---

## 🧪 Testing Procedures

### Test 1: Database Failover

```bash
# Simulate primary database failure
docker stop sentinel-postgres-primary

# Expected:
# - Patroni promotes replica (< 30s)
# - HAProxy routes to new primary
# - Backend reconnects automatically
# - Zero data loss
# - Brief connection errors (< 30s)

# Verify:
docker exec sentinel-postgres-replica patronictl list
# Should show replica as Leader

# Check backend logs:
docker logs sentinel-backend | grep -i "database"
# Should show reconnection messages

# Restore:
docker start sentinel-postgres-primary
# It will rejoin as replica
```

### Test 2: Full Site Failover

```bash
# Simulate complete on-premise failure
# (In test environment, not production!)

# 1. Stop all on-premise services
docker-compose down

# 2. Wait for DNS failover (90-120s)
# 3. Verify cloud site takes over
curl https://sentinel.yourdomain.com/health
# Should return 200 from cloud IP

# 4. Verify Pi-hole still works
nslookup google.com 192.168.1.10
# Should resolve (Pi-hole autonomous)

# 5. Check data consistency
# Login to cloud Sentinel
# Verify recent data is present (within RPO)
```

### Test 3: Backup & Restore

```bash
# 1. Create test data
docker exec sentinel-postgres-primary psql -U sentinel -c \
    "INSERT INTO test_table VALUES ('test-$(date +%s)');"

# 2. Run backup
./scripts/backup-postgres.sh

# 3. Simulate data loss
docker exec sentinel-postgres-primary psql -U sentinel -c \
    "DROP TABLE test_table;"

# 4. Restore from backup
./scripts/restore-postgres.sh /var/backups/sentinel/postgres/sentinel_backup_*.sql.gz

# 5. Verify data restored
docker exec sentinel-postgres-primary psql -U sentinel -c \
    "SELECT * FROM test_table;"
```

### Test 4: Pi-hole Autonomy

```bash
# 1. Stop Sentinel completely
docker-compose down

# 2. Verify DNS still works
nslookup google.com 192.168.1.10
nslookup google.com 192.168.1.11
nslookup google.com 192.168.1.12

# 3. Verify ad blocking still works
nslookup ads.google.com 192.168.1.10
# Should return 0.0.0.0 (blocked)

# 4. Restart Sentinel
docker-compose up -d

# 5. Verify Sentinel can monitor Pi-holes
curl http://localhost:8000/api/v1/pihole/health
```

---

## 📊 Monitoring & Alerting

### Critical Alerts

| Alert | Condition | Action | Priority |
|-------|-----------|--------|----------|
| Site Down | Health check fails 3x | Auto-failover + PagerDuty | P0 |
| Database Lag | Replication lag > 10s | Alert ops team | P1 |
| Backup Failed | Any backup failure | Immediate alert | P1 |
| Pi-hole Down | 2+ Pi-holes unreachable | Alert + investigate | P1 |
| Disk Space | > 85% on any node | Alert + cleanup | P2 |
| Memory High | > 90% for 5 min | Alert + investigate | P2 |

### Dashboards

**1. HA Overview Dashboard**:
- Site status (on-prem vs cloud)
- Active database primary
- Replication lag
- Backup status
- DNS health (all 3 Pi-holes)

**2. Failover Dashboard**:
- Failover events timeline
- RTO/RPO metrics
- Health check history
- Traffic routing (on-prem vs cloud)

**3. Component Health**:
- PostgreSQL cluster status
- Redis Sentinel status
- Prometheus federation
- Backup success rate

---

## 💰 Cost Breakdown

### On-Premise (One-time + Monthly)

| Item | Cost |
|------|------|
| Server (Dell R730, 64GB RAM) | $3,000 (one-time) |
| UPS (1500VA) | $300 (one-time) |
| Network switch | $200 (one-time) |
| **Subtotal** | **$3,500** |
| Electricity (~500W 24/7) | $50/month |
| Internet (business, static IP) | $100/month |
| **Monthly Total** | **$150/month** |

### Cloud (Monthly)

| Item | Cost |
|------|------|
| VPS (8 vCPU, 32GB RAM) | $160/month |
| Block storage (500GB SSD) | $50/month |
| S3 storage (1TB) | $23/month |
| Data transfer (500GB/month) | $45/month |
| **Monthly Total** | **$278/month** |

### Total Cost

- **Initial**: $3,500
- **Monthly**: $428/month ($150 on-prem + $278 cloud)
- **Annual**: $8,636 ($3,500 + $5,136)

### Cost Optimization Options

1. **Managed PostgreSQL** (instead of self-hosted):
   - AWS RDS Multi-AZ: $300/month
   - Saves ops time, increases reliability
   - Total: $578/month

2. **Smaller cloud instance** (standby only):
   - 4 vCPU, 16GB RAM: $80/month
   - Only promote during failover
   - Total: $348/month

3. **Hybrid approach**:
   - Managed DB + self-hosted app
   - Best of both worlds
   - Total: $480/month

---

## 🚀 Implementation Roadmap

### Week 1: Foundation
- [x] PostgreSQL HA (Patroni + etcd + HAProxy)
- [x] Backup scripts
- [ ] Test failover scenarios
- [ ] Document procedures

### Week 2: Application HA
- [ ] Implement health check endpoints
- [ ] Add graceful shutdown
- [ ] Configure connection retry logic
- [ ] Test backend with DB failover

### Week 3: Redis HA
- [ ] Deploy Redis Sentinel
- [ ] Configure backend to use Sentinel
- [ ] Test Redis failover
- [ ] Verify session persistence

### Week 4: Cloud Deployment
- [ ] Provision cloud VPS
- [ ] Deploy Sentinel stack to cloud
- [ ] Configure async replication
- [ ] Set up VPN between sites

### Week 5: DNS & Monitoring
- [ ] Deploy 3 Pi-hole instances
- [ ] Configure Gravity Sync
- [ ] Update client DHCP
- [ ] Set up DNS failover

### Week 6: Testing & Validation
- [ ] Full failover drill
- [ ] Backup/restore test
- [ ] Load testing
- [ ] Documentation review

### Week 7: Production Cutover
- [ ] Final validation
- [ ] Runbook review
- [ ] Team training
- [ ] Go live!

---

## ✅ Success Criteria

System is production-ready when:

- [ ] Can survive any single component failure
- [ ] Can survive complete site failure
- [ ] RTO < 2 minutes (database), < 5 minutes (site)
- [ ] RPO < 5 minutes
- [ ] DNS filtering works independently
- [ ] Automated backups tested and verified
- [ ] Failover drills passed (3 consecutive successes)
- [ ] Team trained on procedures
- [ ] Monitoring and alerts configured
- [ ] Runbooks documented and accessible
- [ ] Client acceptance testing passed

---

## 📚 Next Steps

1. **Review this design** with your team
2. **Prioritize components** based on risk/budget
3. **Create GitHub issues** for each checklist item
4. **Start with Week 1** (PostgreSQL HA testing)
5. **Schedule weekly reviews** to track progress

---

**Questions? Issues? Updates?**  
Document all changes in this file and keep it as the single source of truth for HA architecture.
