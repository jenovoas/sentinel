# Sentinel High Availability - Quick Start Guide

**Status**: Phase 1 Implementation  
**Last Updated**: December 15, 2025

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- Docker & Docker Compose installed
- At least 4GB RAM available
- 20GB disk space

### Step 1: Start HA Stack

```bash
# Start etcd, PostgreSQL primary, replica, and HAProxy
docker-compose -f docker-compose-ha.yml up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose -f docker-compose-ha.yml ps
```

### Step 2: Verify Cluster Health

```bash
# Check Patroni cluster status
docker exec sentinel-postgres-primary patronictl -c /etc/patroni/patroni.yml list

# Expected output:
# + Cluster: sentinel-cluster (7234567890123456789) -----+----+-----------+
# | Member            | Host            | Role    | State   | TL | Lag in MB |
# +-------------------+-----------------+---------+---------+----+-----------+
# | postgres-primary  | postgres-primary| Leader  | running |  1 |           |
# | postgres-replica  | postgres-replica| Replica | running |  1 |         0 |
# +-------------------+-----------------+---------+---------+----+-----------+
```

### Step 3: Test Replication

```bash
# Insert test data on primary
docker exec -it sentinel-postgres-primary psql -U sentinel -d sentinel -c \
    "CREATE TABLE ha_test (id serial, created_at timestamp default now());"

docker exec -it sentinel-postgres-primary psql -U sentinel -d sentinel -c \
    "INSERT INTO ha_test DEFAULT VALUES;"

# Verify on replica
docker exec -it sentinel-postgres-replica psql -U sentinel -d sentinel -c \
    "SELECT * FROM ha_test;"

# Should show the inserted row
```

### Step 4: Setup Automated Backups

```bash
# Make scripts executable
chmod +x scripts/backup-postgres.sh
chmod +x scripts/restore-postgres.sh

# Test manual backup
./scripts/backup-postgres.sh

# Add to crontab (every 6 hours)
crontab -e
# Add line:
0 */6 * * * /home/jnovoas/sentinel/scripts/backup-postgres.sh >> /var/log/sentinel-backup.log 2>&1
```

---

## 🔧 Configuration

### Connection Strings

```bash
# Primary (Read-Write)
postgresql://sentinel:darkfenix@localhost:5432/sentinel

# Replica (Read-Only)
postgresql://sentinel:darkfenix@localhost:5433/sentinel
```

### HAProxy Stats

Access at: http://localhost:7000

Shows:
- Primary/Replica status
- Connection counts
- Health check results

---

## 🧪 Testing Failover

### Simulate Primary Failure

```bash
# Stop primary node
docker stop sentinel-postgres-primary

# Watch Patroni promote replica (< 30 seconds)
watch -n 1 'docker exec sentinel-postgres-replica patronictl -c /etc/patroni/patroni.yml list'

# Replica should become Leader
# Applications automatically reconnect to new primary via HAProxy
```

### Restore Primary

```bash
# Start primary again
docker start sentinel-postgres-primary

# It will rejoin as replica
# Manual failback if desired:
docker exec sentinel-postgres-primary patronictl -c /etc/patroni/patroni.yml switchover
```

---

## 📊 Monitoring

### Check Replication Lag

```bash
# On primary
docker exec sentinel-postgres-primary psql -U sentinel -c \
    "SELECT client_addr, state, sync_state, replay_lag FROM pg_stat_replication;"
```

### Check Cluster Health

```bash
# Patroni status
docker exec sentinel-postgres-primary patronictl -c /etc/patroni/patroni.yml list

# etcd health
docker exec sentinel-etcd etcdctl endpoint health
```

---

## 🔄 Backup & Restore

### Manual Backup

```bash
./scripts/backup-postgres.sh
```

Backups stored in: `/var/backups/sentinel/postgres/`

### Restore from Backup

```bash
./scripts/restore-postgres.sh /var/backups/sentinel/postgres/sentinel_backup_YYYYMMDD_HHMMSS.sql.gz
```

---

## 🚨 Troubleshooting

### Replica Not Syncing

```bash
# Check replication status
docker logs sentinel-postgres-replica

# Verify replication user
docker exec sentinel-postgres-primary psql -U sentinel -c \
    "SELECT * FROM pg_stat_replication;"

# Rebuild replica if needed
docker-compose -f docker-compose-ha.yml stop postgres-replica
docker volume rm sentinel_postgres_replica_data
docker-compose -f docker-compose-ha.yml up -d postgres-replica
```

### Split-Brain Prevention

Patroni uses etcd for distributed consensus. As long as etcd quorum is maintained, split-brain cannot occur.

### Connection Issues

```bash
# Check HAProxy status
curl http://localhost:7000

# Test direct connection to primary
docker exec sentinel-postgres-primary pg_isready -U ${POSTGRES_USER:-sentinel} -d ${POSTGRES_DB:-sentinel}

# Test direct connection to replica
docker exec sentinel-postgres-replica pg_isready -U ${POSTGRES_USER:-sentinel} -d ${POSTGRES_DB:-sentinel}
```

---

## 📈 Next Steps

### Phase 2: Full HA (Recommended)

1. **Deploy Cloud Standby**
   - Spin up identical stack on cloud VPS
   - Configure VPN between on-premise and cloud
   - Set up DNS failover

2. **Add Monitoring**
   - Prometheus metrics for Patroni
   - Grafana dashboard for replication lag
   - Alerts for failover events

3. **Implement Keepalived**
   - Virtual IP for automatic failover
   - VRRP for network-level HA

### Phase 3: Pi-hole HA

1. Deploy 3 Pi-hole instances
2. Configure Gravity Sync
3. Update client DHCP with all 3 DNS servers

---

## 📚 Resources

- [Patroni Documentation](https://patroni.readthedocs.io/)
- [PostgreSQL Replication](https://www.postgresql.org/docs/current/warm-standby.html)
- [HAProxy Configuration](http://www.haproxy.org/)
- [etcd Documentation](https://etcd.io/docs/)

---

## ✅ Success Criteria

Your HA setup is working when:

- [ ] Replica shows 0 lag in `patronictl list`
- [ ] Test data inserted on primary appears on replica
- [ ] Simulated primary failure triggers automatic promotion
- [ ] HAProxy stats show both nodes healthy
- [ ] Automated backups run successfully
- [ ] Restore test completes without errors

---

**Questions?** Check logs: `docker-compose -f docker-compose-ha.yml logs -f`
