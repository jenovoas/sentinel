# Sentinel High Availability & Disaster Recovery Architecture

**Document Version**: 1.0  
**Last Updated**: December 15, 2025  
**Status**: Design Phase  
**Priority**: CRITICAL for Production

---

## 🚨 Problem Statement

### Current Architecture Risk: Single Point of Failure (SPOF)

**Critical Issue**: Sentinel currently runs as a single instance. If it fails:
- ❌ Complete loss of monitoring visibility
- ❌ Security alerts stop flowing
- ❌ AI analysis unavailable
- ❌ Automation workflows halt
- ❌ **Client networks may lose DNS filtering** (if Pi-hole is centralized)

**Business Impact**:
- Revenue loss during downtime
- SLA violations
- Security blind spots
- Client trust damage
- Potential data loss

---

## 🎯 High Availability Requirements

### RPO/RTO Targets

| Component | RPO (Data Loss) | RTO (Recovery Time) | Availability Target |
|-----------|----------------|---------------------|---------------------|
| Sentinel Control Plane | 5 minutes | 2 minutes | 99.95% (4.38h/year) |
| PostgreSQL Database | 1 minute | 1 minute | 99.99% (52.6m/year) |
| DNS Filtering | 0 seconds | 0 seconds | 99.99% (always-on) |
| Metrics Collection | 15 seconds | 30 seconds | 99.9% (8.77h/year) |
| AI Services | 5 minutes | 5 minutes | 99.5% (43.8h/year) |

### Failure Scenarios to Handle

1. **Hardware Failure**: Server dies completely
2. **Network Partition**: Loss of connectivity
3. **Software Crash**: Application bug/OOM
4. **Data Corruption**: Database issues
5. **Region Failure**: Entire datacenter down
6. **Human Error**: Accidental deletion/misconfiguration

---

## 🏗️ Proposed HA Architecture

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Networks                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Client A │  │ Client B │  │ Client C │                  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
│       │             │             │                          │
└───────┼─────────────┼─────────────┼──────────────────────────┘
        │             │             │
        ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              Load Balancer / DNS Failover                    │
│         (HAProxy / Keepalived / Cloud LB)                    │
│              VIP: sentinel.yourdomain.com                    │
└───────┬─────────────────────────────────┬───────────────────┘
        │                                 │
        ▼                                 ▼
┌──────────────────┐            ┌──────────────────┐
│  Sentinel Node 1 │            │  Sentinel Node 2 │
│   (On-Premise)   │◄──────────►│   (Cloud/Colo)   │
│                  │  Heartbeat │                  │
│  - Frontend      │            │  - Frontend      │
│  - Backend       │            │  - Backend       │
│  - Prometheus    │            │  - Prometheus    │
│  - Grafana       │            │  - Grafana       │
│  - Loki          │            │  - Loki          │
│  - Redis         │            │  - Redis         │
└────────┬─────────┘            └────────┬─────────┘
         │                                │
         ▼                                ▼
┌─────────────────────────────────────────────────────────────┐
│           PostgreSQL HA Cluster (Patroni/Stolon)            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Primary  │◄─┤ Standby  │◄─┤ Standby  │                  │
│  │  (RW)    │  │  (RO)    │  │  (RO)    │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│       Streaming Replication + Automatic Failover            │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│              Shared Storage / Backup System                  │
│  - S3/MinIO for metrics/logs (15 day retention)             │
│  - Automated backups every 6 hours                           │
│  - Point-in-time recovery enabled                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│         DNS Filtering Layer (Independent HA)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Pi-hole 1│  │ Pi-hole 2│  │ Pi-hole 3│                  │
│  │ Primary  │  │ Secondary│  │ Tertiary │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│  Config sync via Gravity Sync / Ansible                     │
│  Clients use all 3 DNS servers (DHCP config)                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Component-by-Component HA Design

### 1. Sentinel Control Plane (Frontend + Backend)

#### Option A: Active-Passive (Simpler, Recommended for Start)

**Setup**:
```yaml
# docker-compose-ha.yml
version: '3.8'

services:
  # Node 1 (Primary)
  sentinel-primary:
    image: sentinel:latest
    environment:
      - NODE_ROLE=primary
      - FAILOVER_PEER=sentinel-secondary
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
    
  # Node 2 (Standby)
  sentinel-secondary:
    image: sentinel:latest
    environment:
      - NODE_ROLE=standby
      - FAILOVER_PEER=sentinel-primary
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
```

**Failover Mechanism**:
- **Keepalived**: Virtual IP (VIP) floats between nodes
- **Health checks**: Every 10 seconds
- **Automatic failover**: < 30 seconds
- **Manual failback**: After primary recovery

**Pros**:
- ✅ Simple to implement
- ✅ Clear primary/secondary roles
- ✅ No split-brain issues
- ✅ Lower resource usage

**Cons**:
- ❌ Standby node idle (wasted resources)
- ❌ Brief downtime during failover

#### Option B: Active-Active (More Complex, Better Utilization)

**Setup**:
- Load balancer distributes traffic across both nodes
- Both nodes actively serve requests
- Session affinity via Redis (shared state)
- Requires stateless application design

**Pros**:
- ✅ Better resource utilization
- ✅ Zero downtime failover
- ✅ Horizontal scalability

**Cons**:
- ❌ More complex configuration
- ❌ Requires shared session store
- ❌ Potential race conditions

**Recommendation**: Start with **Active-Passive**, migrate to Active-Active later.

---

### 2. PostgreSQL Database

#### Recommended: Patroni + etcd/Consul

**Architecture**:
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ PostgreSQL 1 │     │ PostgreSQL 2 │     │ PostgreSQL 3 │
│  (Primary)   │────►│  (Replica)   │────►│  (Replica)   │
│   RW         │     │   RO         │     │   RO         │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            ▼
                    ┌──────────────┐
                    │ Patroni DCS  │
                    │ (etcd/Consul)│
                    └──────────────┘
```

**Features**:
- **Streaming Replication**: Real-time data sync
- **Automatic Failover**: < 30 seconds
- **Read Replicas**: Offload read queries
- **Point-in-Time Recovery**: Restore to any moment
- **Connection Pooling**: PgBouncer for efficiency

**Configuration**:
```yaml
# patroni.yml
scope: sentinel-cluster
namespace: /db/
name: postgres1

restapi:
  listen: 0.0.0.0:8008
  connect_address: postgres1:8008

etcd:
  hosts: etcd1:2379,etcd2:2379,etcd3:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
    postgresql:
      use_pg_rewind: true
      parameters:
        max_connections: 200
        shared_buffers: 2GB
        effective_cache_size: 6GB
        wal_level: replica
        max_wal_senders: 10
        max_replication_slots: 10
        hot_standby: on

postgresql:
  listen: 0.0.0.0:5432
  connect_address: postgres1:5432
  data_dir: /var/lib/postgresql/14/main
  bin_dir: /usr/lib/postgresql/14/bin
  authentication:
    replication:
      username: replicator
      password: ${REPLICATION_PASSWORD}
    superuser:
      username: postgres
      password: ${POSTGRES_PASSWORD}
```

**Backup Strategy**:
```bash
# Automated backups with pgBackRest
pgbackrest --stanza=sentinel backup --type=full  # Daily
pgbackrest --stanza=sentinel backup --type=incr  # Every 6 hours
pgbackrest --stanza=sentinel backup --type=diff  # Hourly

# Retention policy
full-retention=7      # Keep 7 full backups
diff-retention=4      # Keep 4 differential backups
```

**Alternative**: Managed Database Services
- **AWS RDS PostgreSQL**: Multi-AZ, automated backups
- **Google Cloud SQL**: HA configuration, point-in-time recovery
- **Azure Database**: Zone-redundant, auto-failover

**Pros of Managed**:
- ✅ Zero maintenance
- ✅ Proven reliability
- ✅ Automatic backups
- ✅ Easy scaling

**Cons of Managed**:
- ❌ Higher cost
- ❌ Vendor lock-in
- ❌ Less control

---

### 3. Redis (Session Store / Cache)

#### Recommended: Redis Sentinel

**Architecture**:
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Redis 1     │     │  Redis 2     │     │  Redis 3     │
│  (Master)    │────►│  (Replica)   │────►│  (Replica)   │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            ▼
                    ┌──────────────┐
                    │Redis Sentinel│
                    │  (Quorum 2)  │
                    └──────────────┘
```

**Features**:
- Automatic master failover
- Client-side discovery
- Quorum-based decision making

**Configuration**:
```conf
# sentinel.conf
sentinel monitor sentinel-redis redis1 6379 2
sentinel down-after-milliseconds sentinel-redis 5000
sentinel parallel-syncs sentinel-redis 1
sentinel failover-timeout sentinel-redis 10000
```

**Alternative**: Redis Cluster (for horizontal scaling)

---

### 4. Prometheus + Grafana

#### Strategy: Federation + Remote Storage

**Architecture**:
```
┌──────────────┐     ┌──────────────┐
│ Prometheus 1 │     │ Prometheus 2 │
│  (Node 1)    │     │  (Node 2)    │
└──────┬───────┘     └──────┬───────┘
       │                    │
       └────────────────────┘
                ▼
        ┌──────────────┐
        │ Thanos/Cortex│
        │ (Long-term)  │
        └──────┬───────┘
               ▼
        ┌──────────────┐
        │  S3/MinIO    │
        │  (Storage)   │
        └──────────────┘
```

**Features**:
- **Thanos**: Global query view, long-term storage
- **Deduplication**: Merge metrics from multiple Prometheus
- **Downsampling**: Reduce storage for old data
- **Unlimited retention**: S3-backed storage

**Grafana HA**:
- Shared PostgreSQL for dashboards/users
- Session store in Redis
- Multiple Grafana instances behind load balancer

---

### 5. DNS Filtering (Pi-hole / AdGuard)

#### Critical: Independent HA (Survives Sentinel Failure)

**Architecture**:
```
Client DHCP Configuration:
  Primary DNS:   192.168.1.10 (Pi-hole 1)
  Secondary DNS: 192.168.1.11 (Pi-hole 2)
  Tertiary DNS:  192.168.1.12 (Pi-hole 3)
```

**Sync Mechanism**:
```bash
# Gravity Sync - Automated config sync
# Runs every 15 minutes via cron

# /etc/gravity-sync/gravity-sync.conf
REMOTE_HOST='pihole2.local'
REMOTE_USER='pihole'
SYNC_FREQUENCY='15'
```

**Key Points**:
- ✅ **Autonomous Operation**: Works without Sentinel
- ✅ **Config Sync**: Gravity Sync or Ansible
- ✅ **Client Failover**: Automatic via DNS fallback
- ✅ **Monitoring**: Sentinel monitors but doesn't control

**Sentinel Integration**:
- Monitors Pi-hole health
- Sends alerts if Pi-hole down
- Provides analytics dashboard
- **Does NOT** control DNS resolution

---

## 🔄 Disaster Recovery Plan

### Scenario 1: Primary Sentinel Node Failure

**Detection**: < 30 seconds (health check failure)

**Automatic Actions**:
1. Keepalived detects primary down
2. VIP floats to secondary node
3. Secondary becomes active
4. Clients reconnect automatically

**Manual Actions**:
1. Investigate primary failure
2. Fix and restart primary
3. Verify replication sync
4. Plan failback window

**Recovery Time**: 2-5 minutes

---

### Scenario 2: Database Corruption

**Detection**: Immediate (query errors)

**Automatic Actions**:
1. Patroni promotes standby to primary
2. Applications reconnect to new primary
3. Failed node removed from cluster

**Manual Actions**:
1. Restore corrupted node from backup
2. Re-sync with primary
3. Add back to cluster

**Recovery Time**: 1-2 minutes (failover) + 30-60 minutes (rebuild)

---

### Scenario 3: Complete Site Failure (On-Premise)

**Detection**: < 1 minute (site unreachable)

**Automatic Actions**:
1. DNS failover to cloud instance
2. Cloud instance becomes primary
3. Clients redirect to cloud

**Manual Actions**:
1. Assess on-premise damage
2. Restore from cloud backups
3. Rebuild on-premise infrastructure
4. Sync data back

**Recovery Time**: 5-10 minutes (failover) + hours/days (rebuild)

---

### Scenario 4: Human Error (Accidental Deletion)

**Detection**: Immediate (user report)

**Manual Actions**:
1. Identify deletion timestamp
2. Restore from point-in-time backup
3. Verify data integrity
4. Resume operations

**Recovery Time**: 15-30 minutes

---

## 📊 Monitoring & Alerting for HA

### Health Checks

```yaml
# Health check endpoints
/health                    # Overall system health
/health/database          # PostgreSQL connection
/health/redis             # Redis connection
/health/prometheus        # Metrics collection
/health/ollama            # AI service
/health/pihole            # DNS filtering
```

### Critical Alerts

| Alert | Threshold | Action |
|-------|-----------|--------|
| Node Down | 3 failed health checks | Auto-failover + PagerDuty |
| Database Lag | > 10 seconds | Alert ops team |
| Disk Space | > 85% | Alert + auto-cleanup |
| Memory Usage | > 90% | Alert + investigate |
| Replication Broken | Any lag increase | Immediate alert |
| Backup Failed | Any failure | Immediate alert |

---

## 💰 Cost Analysis

### Option 1: Self-Hosted HA (On-Premise + Cloud)

**Infrastructure**:
- On-Premise Server: $3,000 (one-time)
- Cloud VPS (4 vCPU, 16GB): $80/month
- S3 Storage (500GB): $12/month
- **Total**: $3,000 + $92/month

**Pros**: Full control, lower long-term cost  
**Cons**: Maintenance overhead, requires expertise

---

### Option 2: Hybrid (Managed DB + Self-Hosted App)

**Infrastructure**:
- On-Premise Server: $3,000 (one-time)
- Cloud VPS: $80/month
- AWS RDS PostgreSQL (Multi-AZ): $150/month
- S3 Storage: $12/month
- **Total**: $3,000 + $242/month

**Pros**: Less DB maintenance, proven reliability  
**Cons**: Higher monthly cost, vendor lock-in

---

### Option 3: Kubernetes Cluster (Advanced)

**Infrastructure**:
- 3-node K8s cluster (on-prem): $9,000 (one-time)
- Or managed K8s (GKE/EKS): $300/month
- Managed DB: $150/month
- S3 Storage: $12/month
- **Total**: $9,000 + $162/month OR $462/month

**Pros**: Auto-scaling, container orchestration, industry standard  
**Cons**: Complexity, learning curve, overkill for small deployments

---

## 🎯 Recommended Implementation Roadmap

### Phase 1: Foundation (Month 1-2)

**Priority: CRITICAL**

- [ ] Implement PostgreSQL replication (Patroni)
- [ ] Set up automated backups (pgBackRest)
- [ ] Configure Redis Sentinel
- [ ] Deploy secondary Sentinel node (cloud)
- [ ] Implement health check endpoints
- [ ] Set up basic monitoring alerts

**Deliverable**: Basic HA with manual failover

---

### Phase 2: Automation (Month 3)

**Priority: HIGH**

- [ ] Configure Keepalived for VIP failover
- [ ] Implement automatic failover scripts
- [ ] Set up Prometheus federation
- [ ] Deploy Thanos for long-term storage
- [ ] Create DR runbooks
- [ ] Test failover scenarios

**Deliverable**: Automatic failover < 2 minutes

---

### Phase 3: DNS HA (Month 4)

**Priority: HIGH**

- [ ] Deploy 3 Pi-hole instances
- [ ] Configure Gravity Sync
- [ ] Update client DHCP configs
- [ ] Implement Pi-hole monitoring
- [ ] Test DNS failover

**Deliverable**: DNS filtering survives Sentinel failure

---

### Phase 4: Optimization (Month 5-6)

**Priority: MEDIUM**

- [ ] Migrate to Active-Active (if needed)
- [ ] Implement auto-scaling
- [ ] Optimize backup retention
- [ ] Conduct DR drills
- [ ] Document all procedures
- [ ] Train team on HA operations

**Deliverable**: Production-ready HA system

---

## 📝 Operational Procedures

### Daily Operations

```bash
# Check cluster health
patronictl -c /etc/patroni/patroni.yml list

# Verify replication lag
psql -h localhost -U postgres -c "SELECT * FROM pg_stat_replication;"

# Check Redis Sentinel status
redis-cli -p 26379 SENTINEL masters

# Verify backups
pgbackrest --stanza=sentinel info
```

### Monthly DR Drill

1. Simulate primary node failure
2. Verify automatic failover
3. Test backup restoration
4. Document any issues
5. Update runbooks

---

## 🚀 Quick Start: Minimal HA Setup

For immediate improvement (can be done in 1 week):

```bash
# 1. Add PostgreSQL streaming replication
docker-compose -f docker-compose-ha.yml up -d postgres-replica

# 2. Configure automated backups
crontab -e
0 */6 * * * /usr/local/bin/backup-sentinel.sh

# 3. Deploy cloud standby
# Use same docker-compose on cloud VPS
# Point to same PostgreSQL primary

# 4. Set up DNS failover
# Add cloud IP as secondary in DNS
```

**Result**: Basic HA in 1 week, survives single node failure

---

## 📚 References

- [PostgreSQL HA with Patroni](https://patroni.readthedocs.io/)
- [Redis Sentinel Documentation](https://redis.io/topics/sentinel)
- [Prometheus Federation](https://prometheus.io/docs/prometheus/latest/federation/)
- [Thanos Documentation](https://thanos.io/tip/thanos/getting-started.md/)
- [Keepalived User Guide](https://www.keepalived.org/manpage.html)
- [Pi-hole HA Setup](https://docs.pi-hole.net/guides/dns/unbound/)

---

## ✅ Success Criteria

System is production-ready when:

- [ ] Can survive any single component failure
- [ ] RTO < 2 minutes for control plane
- [ ] RPO < 5 minutes for all data
- [ ] DNS filtering works independently
- [ ] Automated backups tested and verified
- [ ] DR drills passed successfully
- [ ] Team trained on failover procedures
- [ ] Monitoring alerts configured
- [ ] Runbooks documented and accessible

---

**Next Steps**: Review this plan, prioritize based on budget/timeline, and start with Phase 1.
