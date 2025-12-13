# Sentinel Operational Dashboard - Maintenance Guide

## System Status ✅

### Current Status (13 Dec 2025)
- **All containers**: Running & Healthy
- **Backend (FastAPI)**: ✅ Healthy - Responsive API
- **Frontend (Next.js)**: ✅ Running - Auto-compiling fast refresh
- **Database (PostgreSQL)**: ✅ Healthy - All migrations applied
- **Redis**: ✅ Healthy - Cache layer operational
- **Celery**: ✅ Running - Task scheduler active

### Performance Metrics
- Dashboard API response time: ~200ms (concurrent)
- Frontend compilation time: ~250-300ms (hot reload)
- Throughput: ~5 req/sec under concurrent load
- All endpoints returning 200 status

## Quick Health Check

```bash
# One-liner to verify everything is running
docker-compose ps && curl -s http://localhost:8000/api/v1/health | jq '.status'
```

Expected output:
```
healthy
database: true
redis: true
celery: true
```

## Dashboard Features

### Available Metrics
- **CPU**: Real-time usage with 15min history
- **Memory**: RAM utilization with trend graph
- **GPU**: Detection & temperature monitoring (if available)
- **Network**: Upload/download traffic visualization
- **Database**: Connections, locks, query monitoring
- **Repository**: Git activity tracking
- **Automatic Issues**: CPU/Memory/Connection threshold alerts

### Interactive Features
- Click any circular metric to open historic graph (btop-style)
- 60-sample history (~15 minutes at 15s refresh rate)
- Auto-updating every 15 seconds
- Dark terminal aesthetic with smooth animations

## Common Issues & Solutions

### Issue: Dashboard shows "0%" for all metrics
**Cause**: API still warming up or metrics collection delayed
**Solution**: Wait 30 seconds and refresh browser. Backend needs first collection cycle.

### Issue: GPU shows "No detectada"
**Cause**: No GPU available (expected on CPU-only systems)
**Solution**: Normal behavior. GPU card not installed or drivers missing.

### Issue: Network traffic always "0%"
**Cause**: Network interfaces not accessible or calculation issue
**Solution**: Check host network stack. Usually recovers after API restart.

### Issue: Cannot connect to http://localhost:3000
**Cause**: Frontend not compiled or port conflict
**Solution**: 
```bash
docker-compose logs frontend | grep -E "error|Error"
# If stuck, rebuild:
docker-compose build frontend
docker-compose restart frontend
```

### Issue: Dashboard API returns 500 errors
**Cause**: Database connection, GPU utils missing, or monitoring service crash
**Solution**:
```bash
# Check backend logs
docker-compose logs backend --tail=50

# If GPU errors, that's OK (gracefully handled)
# If DB connection error, verify postgres is running:
docker-compose exec postgres psql -U sentinel_user -d sentinel_db -c "SELECT 1"
```

## Maintenance Tasks

### Daily
- ✅ Automated: Dashboard auto-refreshes every 15s
- Monitor DB connections (shown in dashboard)
- Check for any persistent error messages

### Weekly
- Review git activity in dashboard repo section
- Archive old logs if needed:
  ```bash
  docker-compose exec backend sh -c "find logs/ -mtime +7 -delete"
  ```

### Monthly
- Run DB maintenance during low-traffic periods
- Check disk space usage
- Review and rotate backups

## Deployment Commands

```bash
# Start all services
docker-compose up -d

# Restart specific service (e.g., backend)
docker-compose restart backend

# Rebuild and restart
docker-compose build backend && docker-compose up -d backend

# View live logs
docker-compose logs -f backend

# Full system restart
docker-compose down && docker-compose up -d

# Clean old containers/images (WARNING: destructive)
docker system prune -a
```

## Database

### Current Schema
- Migrations applied: 2 (initial + Organization/Roles)
- Tables: tenants, organizations, users, audit_logs, etc.
- UUID primary keys (PostgreSQL native)
- SQLAlchemy 2.0 ORM

### Check DB Health
```bash
# Connect to database
docker-compose exec postgres psql -U sentinel_user -d sentinel_db

# Quick queries
SELECT count(*) FROM users;
SELECT count(*) FROM organizations;
SELECT * FROM alembic_version;
```

## Monitoring Best Practices

1. **Dashboard as Early Warning**: Watch CPU/Memory trends before they spike
2. **Historical Graphs**: Click metrics to see 15-min trends
3. **Auto-Alerts**: System highlights CPU >80%, Memory >80%, Connections >50
4. **Git Tracking**: Monitor repo activity for deployment issues
5. **Database Queries**: Review active queries tab for long-running operations

## Performance Tuning

### Reduce API Refresh Rate (for slower networks)
Edit `frontend/src/app/dash-op/page.tsx`:
```tsx
const API_REFRESH_MS = 30000; // Change from 15000ms (15s) to 30000ms (30s)
```

### Increase History Size
Edit `frontend/src/app/dash-op/page.tsx`:
```tsx
const HISTORY_SIZE = 120; // Change from 60 to 120 samples (~30min)
```

## Troubleshooting Checklist

- [ ] All containers show "Up" and "healthy"?
- [ ] API health endpoint returns `status: healthy`?
- [ ] Frontend loading at http://localhost:3000/dash-op?
- [ ] Metrics updating every 15 seconds?
- [ ] Can click circular stats to open graphs?
- [ ] No errors in `docker-compose logs`?
- [ ] Database connection shows in health check?

## Support

For issues not covered here:
1. Check logs: `docker-compose logs backend`
2. Verify containers: `docker-compose ps`
3. Restart service: `docker-compose restart backend`
4. Full rebuild: `docker-compose build && docker-compose up -d`

## Version Info

- FastAPI: 0.104
- Next.js: 14
- PostgreSQL: 16
- SQLAlchemy: 2.0
- psutil: 5.9+
- Redis: 7
- Celery: 5.3

---
**Last Updated**: 13 Dec 2025
**Status**: Production Ready ✅
