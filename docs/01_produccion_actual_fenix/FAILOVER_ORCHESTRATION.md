# Sentinel Failover Flow - Detailed Orchestration

**Version**: 1.0  
**Date**: December 15, 2025  
**Purpose**: Concrete step-by-step failover automation

---

## 🎯 Overview

This document describes **exactly** what happens during failover:
- Who detects the failure
- Who makes decisions
- Who changes DNS/ingress
- How secrets/config sync
- What the client sees at each phase

---

## 🏗️ Architecture Components

### Detection Layer

```
┌─────────────────────────────────────────────────────────────┐
│                    HEALTH CHECK LAYER                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Route53      │  │ Cloudflare   │  │ Custom       │      │
│  │ Health Check │  │ Health Check │  │ Watchdog     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │              │
│         └─────────────────┼─────────────────┘              │
│                           │                                │
│                           ▼                                │
│              ┌────────────────────────┐                    │
│              │ Decision Engine        │                    │
│              │ (Consensus Required)   │                    │
│              └────────────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

**Components**:

1. **Route53 Health Check** (Primary)
   - URL: `https://sentinel-on-prem.yourdomain.com/health`
   - Interval: 30 seconds
   - Failure threshold: 3 (90 seconds)
   - Regions: 3 different AWS regions (consensus)

2. **Cloudflare Health Check** (Secondary)
   - Same URL
   - Interval: 30 seconds
   - Independent verification

3. **Custom Watchdog** (Tertiary)
   - Runs on cloud instance
   - Pings on-prem every 10 seconds
   - Requires 6 consecutive failures (60s)

**Decision Logic**:
```python
def should_failover():
    """
    Failover only if ALL THREE agree on-prem is down
    Prevents false positives from single source
    """
    route53_down = route53_health_check.is_unhealthy()
    cloudflare_down = cloudflare_health_check.is_unhealthy()
    watchdog_down = custom_watchdog.is_unreachable()
    
    # Require consensus
    if route53_down and cloudflare_down and watchdog_down:
        # Additional validation: Can we reach on-prem DB?
        db_reachable = check_postgres_replication()
        if not db_reachable:
            return True  # Confirmed: on-prem is down
    
    return False  # Not enough evidence, stay on primary
```

---

## 📊 Normal Operation Mode

### State: ON-PREMISE PRIMARY, CLOUD STANDBY

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENTS                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              DNS: sentinel.yourdomain.com                    │
│              A Record: <ON-PREM-IP> (TTL: 60s)              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   ON-PREMISE SITE                            │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Sentinel Backend (Active)                          │     │
│  │ - Serving requests                                 │     │
│  │ - Writing to PostgreSQL Primary                    │     │
│  │ - Publishing metrics                               │     │
│  │ - Running n8n workflows                            │     │
│  └────────────────────────────────────────────────────┘     │
│                           │                                  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │ PostgreSQL Primary (HAProxy: 5432)                 │     │
│  │ - Streaming to local replica                       │     │
│  │ - Async replication to cloud                       │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                     │
                     │ VPN Tunnel (WireGuard)
                     │ Async Replication
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     CLOUD SITE                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Sentinel Backend (Standby Active)                  │     │
│  │ - Health checks only                               │     │
│  │ - NOT serving client requests                      │     │
│  │ - Monitoring on-prem health                        │     │
│  │ - Ready to promote in < 60s                        │     │
│  └────────────────────────────────────────────────────┘     │
│                           │                                  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │ PostgreSQL Standby (HAProxy: 5432)                 │     │
│  │ - Receiving async replication from on-prem         │     │
│  │ - Lag: < 5 seconds (monitored)                     │     │
│  │ - Can be promoted to primary                       │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

**Health Check Responses**:
- On-prem `/health`: `200 OK` (every 30s)
- Cloud `/health`: `200 OK` but with `"role": "standby"`

**Metrics Published**:
```json
{
  "site": "on-premise",
  "role": "primary",
  "health": "healthy",
  "database": {
    "primary": true,
    "replication_lag_bytes": 0,
    "async_replica_lag_seconds": 2.3
  },
  "timestamp": "2025-12-15T01:35:00Z"
}
```

---

## 🚨 Failover Trigger (T+0s)

### Event: On-Premise Site Failure

**Possible Causes**:
- Hardware failure (server died)
- Network partition (ISP outage)
- Power outage (UPS depleted)
- Software crash (kernel panic)
- Natural disaster (fire, flood)

**Detection Timeline**:

```
T+0s:   On-prem goes down
T+10s:  Custom watchdog detects (first failure)
T+20s:  Custom watchdog confirms (second failure)
T+30s:  Route53 health check fails (first)
T+60s:  Route53 health check fails (second)
T+70s:  Custom watchdog confirms (6th consecutive failure)
T+90s:  Route53 health check fails (third - THRESHOLD)
T+90s:  Cloudflare health check also fails (third)
T+90s:  ⚠️ CONSENSUS REACHED - INITIATE FAILOVER
```

**Decision Engine Activates**:
```bash
# Executed on cloud instance
/usr/local/bin/sentinel-failover-orchestrator

# Logs:
[2025-12-15 01:36:30] ALERT: On-premise health check failed
[2025-12-15 01:36:30] Consensus: 3/3 health checks failed
[2025-12-15 01:36:30] Validating: Checking PostgreSQL replication
[2025-12-15 01:36:31] CONFIRMED: PostgreSQL replication stopped
[2025-12-15 01:36:31] DECISION: INITIATE FAILOVER TO CLOUD
[2025-12-15 01:36:31] Starting failover sequence...
```

---

## 🔄 Failover Sequence (T+90s to T+150s)

### Phase 1: Database Promotion (T+90s - T+110s)

**Step 1.1: Stop Async Replication** (T+90s)
```bash
# On cloud PostgreSQL
docker exec sentinel-postgres-cloud psql -U postgres -c \
    "SELECT pg_wal_replay_pause();"

# Verify no more WAL is being received
# This prevents split-brain if on-prem comes back
```

**Step 1.2: Promote Cloud PostgreSQL to Primary** (T+95s)
```bash
# Patroni handles this automatically
docker exec sentinel-postgres-cloud patronictl failover \
    --master postgres-primary \
    --candidate postgres-cloud \
    --force

# Patroni output:
# Current cluster topology
# + Cluster: sentinel-cluster -----+
# | Member         | Role    | State   |
# +----------------+---------+---------+
# | postgres-cloud | Leader  | running | ← PROMOTED
# +----------------+---------+---------+
```

**Step 1.3: Verify Database Writeable** (T+100s)
```bash
# Test write
docker exec sentinel-postgres-cloud psql -U sentinel -c \
    "INSERT INTO failover_log (event, timestamp) VALUES ('cloud_promoted', NOW());"

# Success: Database is now primary
```

**Duration**: 20 seconds  
**RPO**: < 5 seconds (async replication lag)

---

### Phase 2: Application Promotion (T+110s - T+130s)

**Step 2.1: Update Cloud Backend Configuration** (T+110s)
```bash
# Cloud backend already running, just needs to know it's primary now
docker exec sentinel-backend-cloud /usr/local/bin/promote-to-primary.sh

# promote-to-primary.sh:
#!/bin/bash
# Update role in Redis
redis-cli SET sentinel:role "primary"

# Enable request serving
redis-cli SET sentinel:accept_requests "true"

# Notify all workers
kill -USR1 $(cat /var/run/sentinel-backend.pid)
```

**Step 2.2: Start Accepting Requests** (T+115s)
```python
# Backend code (already running)
@app.middleware("http")
async def check_role(request: Request, call_next):
    role = await redis.get("sentinel:role")
    accept_requests = await redis.get("sentinel:accept_requests")
    
    if role == "standby" and accept_requests != "true":
        # Standby mode: only health checks
        if request.url.path != "/health":
            return JSONResponse(
                status_code=503,
                content={"error": "Site in standby mode"}
            )
    
    # Primary mode: serve all requests
    response = await call_next(request)
    return response
```

**Step 2.3: Verify Application Health** (T+120s)
```bash
# Test application
curl https://sentinel-cloud.yourdomain.com/health

# Response:
{
  "status": "healthy",
  "role": "primary",  # Changed from "standby"
  "database": "connected",
  "timestamp": "2025-12-15T01:37:50Z"
}
```

**Duration**: 20 seconds

---

### Phase 3: DNS/Ingress Update (T+130s - T+150s)

**Step 3.1: Update DNS Records** (T+130s)

**Option A: Route53 Automatic Failover** (Recommended)
```bash
# Already configured in Route53:
# - Primary record: on-prem IP (health check attached)
# - Failover record: cloud IP (activates on primary failure)

# Route53 automatically switches when health check fails
# No manual intervention needed!

# Verify:
aws route53 get-health-check-status --health-check-id <ID>
# Output: "Unhealthy" for on-prem
# Route53 automatically serves cloud IP now
```

**Option B: Manual DNS Update** (If not using Route53 failover)
```bash
# Update DNS via API
curl -X PATCH https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/dns_records/<RECORD_ID> \
  -H "Authorization: Bearer <API_TOKEN>" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "A",
    "name": "sentinel.yourdomain.com",
    "content": "<CLOUD-IP>",
    "ttl": 60
  }'

# Response: {"success": true}
```

**Step 3.2: Verify DNS Propagation** (T+135s)
```bash
# Check from multiple locations
dig @8.8.8.8 sentinel.yourdomain.com +short
# Should return: <CLOUD-IP>

dig @1.1.1.1 sentinel.yourdomain.com +short
# Should return: <CLOUD-IP>
```

**Step 3.3: Monitor Client Traffic** (T+140s)
```bash
# Watch HAProxy stats on cloud
curl http://sentinel-cloud.yourdomain.com:7000

# Should see:
# - Connections increasing
# - Requests being served
# - No errors
```

**Duration**: 20 seconds  
**Client Impact**: 60-120s (DNS TTL + client cache)

---

### Phase 4: Notification & Monitoring (T+150s+)

**Step 4.1: Send Alerts** (T+150s)
```python
# Automated alerts
send_pagerduty_alert(
    severity="critical",
    summary="Sentinel Failover: Cloud site now primary",
    details={
        "trigger": "On-premise site unreachable",
        "failover_time": "60 seconds",
        "data_loss": "< 5 seconds (RPO)",
        "action_required": "Investigate on-premise failure"
    }
)

send_slack_notification(
    channel="#sentinel-ops",
    message="🚨 FAILOVER COMPLETE: Cloud site is now primary. On-premise site is down. Investigate immediately."
)

send_email_notification(
    to=["ops@company.com", "cto@company.com"],
    subject="CRITICAL: Sentinel Failover to Cloud",
    body="..."
)
```

**Step 4.2: Update Status Page** (T+155s)
```bash
# Update public status page
curl -X POST https://status.yourdomain.com/api/incidents \
  -H "Authorization: Bearer <TOKEN>" \
  --data '{
    "name": "On-premise site maintenance",
    "status": "investigating",
    "message": "We are currently operating from our cloud site. Service is fully operational."
  }'
```

**Step 4.3: Enable Enhanced Monitoring** (T+160s)
```bash
# Increase scrape frequency
# Prometheus: 15s → 5s
# Logs: INFO → DEBUG

# Watch for:
# - Increased error rates
# - Latency spikes
# - Database connection issues
# - Redis failover events
```

---

## 📈 Post-Failover State

### State: CLOUD PRIMARY, ON-PREMISE DOWN

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENTS                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              DNS: sentinel.yourdomain.com                    │
│              A Record: <CLOUD-IP> (TTL: 60s)  ← CHANGED     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     CLOUD SITE                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Sentinel Backend (Active) ← NOW PRIMARY            │     │
│  │ - Serving ALL requests                             │     │
│  │ - Writing to PostgreSQL Primary                    │     │
│  │ - Publishing metrics                               │     │
│  │ - Running n8n workflows                            │     │
│  └────────────────────────────────────────────────────┘     │
│                           │                                  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │ PostgreSQL Primary (HAProxy: 5432) ← PROMOTED      │     │
│  │ - NO replication (on-prem down)                    │     │
│  │ - Accepting writes                                 │     │
│  │ - Backups to S3 every 6h                           │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                     ▲
                     │ VPN Tunnel (DOWN)
                     │
                     ✗
┌─────────────────────────────────────────────────────────────┐
│                   ON-PREMISE SITE                            │
│                      ❌ DOWN ❌                              │
└─────────────────────────────────────────────────────────────┘
```

**What Works**:
- ✅ Client access (via cloud)
- ✅ All Sentinel features
- ✅ Database writes
- ✅ Monitoring & alerting
- ✅ AI analysis (CPU-based Ollama)
- ✅ **Pi-hole DNS filtering** (autonomous!)

**What's Degraded**:
- ⚠️ No database replication (single point)
- ⚠️ Slower AI (CPU vs GPU)
- ⚠️ Higher latency (cloud vs local)

**What's Lost**:
- ❌ On-premise monitoring
- ❌ Local network insights

---

## 🔙 Failback Procedure

### When On-Premise Recovers

**Prerequisites**:
1. On-premise site is healthy
2. Network connectivity restored
3. PostgreSQL can sync from cloud
4. Team approval to failback

**Failback Timeline**:

```
T+0:    On-premise site comes back online
T+5m:   PostgreSQL syncs from cloud (catch-up)
T+10m:  Verify data integrity
T+15m:  Manual decision: Failback now or wait?
T+20m:  Execute failback (reverse of failover)
T+25m:  DNS points back to on-premise
T+30m:  Cloud returns to standby mode
```

**Failback Script**:
```bash
#!/bin/bash
# /usr/local/bin/sentinel-failback.sh

echo "Starting failback to on-premise..."

# 1. Sync cloud DB to on-premise
echo "Syncing database..."
pg_basebackup -h cloud-postgres -D /var/lib/postgresql/data -U replicator -v -P

# 2. Promote on-premise PostgreSQL
echo "Promoting on-premise PostgreSQL..."
patronictl failover --master postgres-cloud --candidate postgres-primary --force

# 3. Update DNS
echo "Updating DNS..."
aws route53 change-resource-record-sets --hosted-zone-id <ZONE_ID> --change-batch file://failback-dns.json

# 4. Demote cloud to standby
echo "Demoting cloud to standby..."
ssh cloud "docker exec sentinel-backend /usr/local/bin/demote-to-standby.sh"

# 5. Verify
echo "Verifying failback..."
curl https://sentinel.yourdomain.com/health | jq '.role'
# Should return: "primary"

echo "Failback complete!"
```

---

## 🎯 Client Experience Timeline

### What the Client Sees

**T+0s to T+90s: Normal Operation**
```
Client → DNS → On-prem → Response (200 OK)
Latency: 50ms
```

**T+90s to T+150s: Failover in Progress**
```
Client → DNS → On-prem → ❌ Timeout
Client retries...
Client → DNS (cached) → On-prem → ❌ Timeout
Client sees: "Service Unavailable" or timeout
```

**T+150s to T+210s: DNS Propagation**
```
Client → DNS (TTL expired) → Cloud → Response (200 OK)
Latency: 150ms (higher due to cloud)
Some clients still cached old DNS → timeout
```

**T+210s+: Fully Operational on Cloud**
```
All clients → DNS → Cloud → Response (200 OK)
Latency: 150ms
Service fully restored
```

**Total Client Impact**:
- Worst case: 2-3 minutes of errors
- Best case: 60-90 seconds
- **Pi-hole DNS**: ZERO impact (autonomous)

---

## 🔐 Secrets & Config Sync

### Problem: How does cloud know on-prem secrets?

**Solution: HashiCorp Vault** (Recommended)

```
┌─────────────────────────────────────────────────────────────┐
│                    HashiCorp Vault                           │
│                  (Managed Service / HA)                      │
│                                                              │
│  Secrets:                                                    │
│  - DATABASE_PASSWORD                                         │
│  - REDIS_PASSWORD                                            │
│  - API_KEYS                                                  │
│  - ENCRYPTION_KEYS                                           │
│  - OAUTH_SECRETS                                             │
└────────┬─────────────────────────────────┬──────────────────┘
         │                                 │
         │ Pull secrets on startup         │
         │                                 │
         ▼                                 ▼
┌──────────────────┐            ┌──────────────────┐
│  On-Prem Backend │            │  Cloud Backend   │
│  (Vault Agent)   │            │  (Vault Agent)   │
└──────────────────┘            └──────────────────┘
```

**Alternative: Encrypted S3**
```bash
# On-prem: Encrypt and upload secrets
gpg --encrypt --recipient sentinel@company.com secrets.env
aws s3 cp secrets.env.gpg s3://sentinel-secrets/

# Cloud: Download and decrypt on startup
aws s3 cp s3://sentinel-secrets/secrets.env.gpg .
gpg --decrypt secrets.env.gpg > /etc/sentinel/secrets.env
source /etc/sentinel/secrets.env
```

**Best Practice**:
- Secrets rotation every 90 days
- Audit log of secret access
- Separate secrets per environment

---

## 📊 Monitoring the Failover Itself

### Metrics to Track

```python
# Prometheus metrics
failover_events_total = Counter('sentinel_failover_events_total')
failover_duration_seconds = Histogram('sentinel_failover_duration_seconds')
failover_data_loss_seconds = Gauge('sentinel_failover_data_loss_seconds')

# During failover
with failover_duration_seconds.time():
    execute_failover()
    failover_events_total.inc()
    
# Calculate data loss
last_on_prem_write = get_last_write_timestamp_on_prem()
first_cloud_write = get_first_write_timestamp_cloud()
data_loss = first_cloud_write - last_on_prem_write
failover_data_loss_seconds.set(data_loss.total_seconds())
```

### Grafana Dashboard: "Failover Events"

```
Panel 1: Failover Timeline
- X-axis: Time
- Y-axis: Site (on-prem / cloud)
- Shows: Which site is primary over time

Panel 2: Failover Duration
- Average: 60s
- P95: 90s
- P99: 120s

Panel 3: Data Loss (RPO)
- Average: 2.3s
- Max: 4.8s

Panel 4: Client Impact
- Requests failed during failover
- Error rate spike
- Latency increase
```

---

## ✅ Success Criteria

Failover is successful when:

- [ ] Cloud site promoted to primary (< 60s)
- [ ] DNS updated to cloud IP (< 90s)
- [ ] Clients can access service (< 150s)
- [ ] Data loss < 5 seconds (RPO met)
- [ ] No data corruption
- [ ] All alerts sent
- [ ] Monitoring operational
- [ ] **Pi-hole DNS never interrupted**

---

## 🧪 Testing Checklist

### Monthly Failover Drill

```bash
# 1. Announce drill
echo "Failover drill starting in 5 minutes..."

# 2. Simulate on-prem failure
docker-compose -f docker-compose-on-prem.yml down

# 3. Monitor failover
watch -n 1 'curl -s https://sentinel.yourdomain.com/health | jq'

# 4. Verify cloud takeover
# - DNS points to cloud
# - Requests being served
# - Database writable
# - Metrics flowing

# 5. Restore on-prem
docker-compose -f docker-compose-on-prem.yml up -d

# 6. Failback
./scripts/failback-to-on-prem.sh

# 7. Document results
# - Failover time: ____ seconds
# - Data loss: ____ seconds
# - Issues found: ____
# - Action items: ____
```

---

## 🎯 Next Steps

1. **Implement health endpoints** (Week 2)
2. **Set up Vault for secrets** (Week 3)
3. **Deploy cloud standby** (Week 4)
4. **Configure Route53 failover** (Week 4)
5. **First failover drill** (Week 6)
6. **Automate failback** (Week 7)

---

**This is your operational playbook. Print it, test it, refine it.**
