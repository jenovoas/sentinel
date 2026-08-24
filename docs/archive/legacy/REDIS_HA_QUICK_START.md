# Redis High Availability - Quick Start Guide

**Status**: Phase 3 Implementation  
**Last Updated**: December 15, 2025

---

## 🚀 Quick Start (10 Minutes)

### Prerequisites

- Docker & Docker Compose installed
- Sentinel network created (`docker network create sentinel-network`)
- At least 2GB RAM available

### Step 1: Start Redis HA Stack

```bash
# Start Redis master, 2 replicas, and 3 Sentinels
docker-compose -f docker-compose-redis-ha.yml up -d

# Wait for services to be healthy (30 seconds)
docker-compose -f docker-compose-redis-ha.yml ps
```

### Step 2: Verify Cluster Health

```bash
# Check Sentinel status
docker exec sentinel-redis-sentinel-1 redis-cli -p 26379 SENTINEL master mymaster

# Expected output:
# 1) "name"
# 2) "mymaster"
# 3) "ip"
# 4) "redis-master"
# 5) "port"
# 6) "6379"
# 7) "flags"
# 8) "master"
```

### Step 3: Check Replication

```bash
# Check master
docker exec sentinel-redis-master redis-cli INFO replication

# Should show:
# role:master
# connected_slaves:2

# Check replica
docker exec sentinel-redis-replica-1 redis-cli INFO replication

# Should show:
# role:slave
# master_host:redis-master
```

### Step 4: Test Failover

```bash
# Run automated failover test
./scripts/test-redis-failover.sh

# This will:
# 1. Check current master
# 2. Write test data
# 3. Trigger failover
# 4. Verify new master
# 5. Verify data persistence
# 6. Test write to new master
```

---

## 🔧 Configuration

### Sentinel Configuration

**Key Parameters** (in `redis/sentinel-*.conf`):

```conf
# Quorum: Number of Sentinels that must agree master is down
sentinel monitor mymaster redis-master 6379 2

# How long master must be unreachable before considering it down
sentinel down-after-milliseconds mymaster 5000

# How many replicas can sync in parallel during failover
sentinel parallel-syncs mymaster 1

# Failover timeout
sentinel failover-timeout mymaster 10000
```

**Why quorum=2?**
- With 3 Sentinels, need 2 to agree
- Prevents false positives from single Sentinel failure
- Follows majority consensus (2 out of 3)

### Backend Integration

**Using Redis Sentinel Client**:

```python
from app.redis_client import get_redis_master, get_redis_slave

# For writes (always goes to master)
master = await get_redis_master()
await master.set("session:123", "user_data")

# For reads (load balanced across replicas)
slave = await get_redis_slave()
data = await slave.get("session:123")
```

**Automatic Failover**:
- Backend automatically reconnects to new master
- No code changes needed during failover
- Sentinel handles promotion transparently

---

## 🧪 Testing Scenarios

### Test 1: Normal Operation

```bash
# Write to master
docker exec sentinel-redis-master redis-cli SET test_key "hello"

# Read from replica (should replicate within milliseconds)
docker exec sentinel-redis-replica-1 redis-cli GET test_key
# Output: "hello"
```

### Test 2: Master Failure (Automatic Failover)

```bash
# Stop master
docker stop sentinel-redis-master

# Watch Sentinel promote replica (< 10 seconds)
watch -n 1 'docker exec sentinel-redis-sentinel-1 redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster'

# Verify new master is writable
NEW_MASTER=$(docker exec sentinel-redis-sentinel-1 redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster | head -1)
echo "New master: $NEW_MASTER"

# Test write to new master
if [ "$NEW_MASTER" == "redis-replica-1" ]; then
    docker exec sentinel-redis-replica-1 redis-cli SET failover_test "success"
fi
```

### Test 3: Sentinel Failure

```bash
# Stop one Sentinel
docker stop sentinel-redis-sentinel-1

# Cluster still works (2 Sentinels remaining)
docker exec sentinel-redis-sentinel-2 redis-cli -p 26379 SENTINEL master mymaster

# Quorum still met (2 out of 3)
```

### Test 4: Network Partition

```bash
# Simulate network partition (disconnect master)
docker network disconnect sentinel-network sentinel-redis-master

# Sentinels detect master down
# Promote replica to master
# Reconnect old master (becomes replica)
docker network connect sentinel-network sentinel-redis-master
```

---

## 📊 Monitoring

### Check Cluster Status

```bash
# Sentinel view of cluster
docker exec sentinel-redis-sentinel-1 redis-cli -p 26379 SENTINEL master mymaster

# Number of known Sentinels
docker exec sentinel-redis-sentinel-1 redis-cli -p 26379 SENTINEL sentinels mymaster

# Number of replicas
docker exec sentinel-redis-sentinel-1 redis-cli -p 26379 SENTINEL replicas mymaster
```

### Prometheus Metrics

```python
# Add to backend/app/routers/health.py
@router.get("/metrics")
async def prometheus_metrics():
    redis_health = await check_redis()
    
    metrics = []
    
    # Redis health
    metrics.append(f'redis_health{{mode="{redis_health.get("mode", "unknown")}"}} {1 if redis_health.get("status") == "healthy" else 0}')
    
    # Redis latency
    if "latency_ms" in redis_health:
        metrics.append(f'redis_latency_ms {redis_health["latency_ms"]}')
    
    # Cluster info (if Sentinel mode)
    if "cluster" in redis_health:
        cluster = redis_health["cluster"]
        metrics.append(f'redis_replicas_count {cluster.get("replicas_count", 0)}')
    
    return Response(content="\n".join(metrics), media_type="text/plain")
```

---

## 🚨 Troubleshooting

### Replica Not Syncing

```bash
# Check replication lag
docker exec sentinel-redis-master redis-cli INFO replication | grep lag

# Check replica logs
docker logs sentinel-redis-replica-1

# Force resync
docker exec sentinel-redis-replica-1 redis-cli REPLICAOF redis-master 6379
```

### Sentinel Not Detecting Master

```bash
# Check Sentinel logs
docker logs sentinel-redis-sentinel-1

# Verify Sentinel can reach master
docker exec sentinel-redis-sentinel-1 ping redis-master

# Reset Sentinel (last resort)
docker exec sentinel-redis-sentinel-1 redis-cli -p 26379 SENTINEL reset mymaster
```

### Split-Brain Prevention

Redis Sentinel prevents split-brain through:
1. **Quorum**: Requires majority agreement (2 out of 3)
2. **Epoch**: Incremental counter prevents old master from accepting writes
3. **Configuration Epoch**: Ensures all Sentinels agree on current master

---

## 📈 Performance Tuning

### Memory Management

```conf
# In redis master/replica config
maxmemory 512mb
maxmemory-policy allkeys-lru  # Evict least recently used keys
```

### Persistence

```conf
# AOF (Append-Only File) for durability
appendonly yes
appendfsync everysec  # Sync to disk every second

# RDB snapshots
save 900 1      # Save if 1 key changed in 15 minutes
save 300 10     # Save if 10 keys changed in 5 minutes
save 60 10000   # Save if 10000 keys changed in 1 minute
```

### Replication Performance

```conf
# Parallel syncs during failover
sentinel parallel-syncs mymaster 1  # Conservative (one at a time)
# or
sentinel parallel-syncs mymaster 2  # Faster (both replicas sync in parallel)
```

---

## ✅ Success Criteria

Redis HA is working when:

- [ ] All 3 Sentinels are healthy
- [ ] Master has 2 connected replicas
- [ ] Replication lag < 1 second
- [ ] Failover test completes successfully
- [ ] Backend can write/read through Sentinel client
- [ ] Failover time < 10 seconds
- [ ] No data loss during failover

---

## 🎯 Next Steps

### Integration with Backend

1. Update `docker-compose.yml` to use Redis HA stack
2. Set environment variable: `REDIS_MODE=sentinel`
3. Restart backend to use Sentinel client

### Production Deployment

1. Deploy Redis HA to cloud site
2. Configure cross-site replication (optional)
3. Set up monitoring alerts
4. Document runbooks

### Advanced Features

1. **Redis Cluster** (for horizontal scaling)
   - Use when single master can't handle load
   - Shards data across multiple masters

2. **Managed Redis** (for less ops overhead)
   - AWS ElastiCache
   - Google Cloud Memorystore
   - Azure Cache for Redis

---

**Questions?** Check logs: `docker-compose -f docker-compose-redis-ha.yml logs -f`
