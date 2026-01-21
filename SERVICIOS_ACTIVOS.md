# 🚀 Servicios Activos de Sentinel

**Última actualización**: 14 de Diciembre, 2025  
**Estado**: 🟢 12/12 servicios funcionando

---

## 📋 Servicios Principales

### 1. Frontend (Next.js)
- **URL**: http://localhost:3000
- **Descripción**: Aplicación web principal
- **Puerto**: 3000
- **Estado**: ✅ Activo

### 2. Backend API (FastAPI)
- **URL**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc
- **Puerto**: 8000
- **Estado**: ✅ Healthy
- **Endpoints principales**:
  - `/api/v1/health` - Health check
  - `/api/v1/analytics/*` - Analytics y métricas
  - `/api/v1/users/*` - Gestión de usuarios
  - `/api/v1/tenants/*` - Gestión de tenants

---

## 🗄️ Bases de Datos y Cache

### 3. PostgreSQL
- **Host**: localhost:5432
- **Database**: sentinel_db
- **Usuario**: sentinel_user
- **Password**: sentinel_password
- **Estado**: ✅ Healthy
- **Conexión**:
  ```bash
  docker-compose exec postgres psql -U sentinel_user -d sentinel_db
  ```

### 4. Redis
- **Host**: localhost:6379
- **Descripción**: Cache y message broker
- **Estado**: ✅ Healthy
- **Conexión**:
  ```bash
  docker-compose exec redis redis-cli
  ```

---

## 📊 Observabilidad (Monitoring Stack)

### 5. Grafana
- **URL**: http://localhost:3001
- **Usuario**: admin
- **Password**: REDACTED_PASSWORD
- **Puerto**: 3001
- **Estado**: ✅ Activo
- **Dashboards disponibles**:
  - Host Metrics Overview
  - System Logs
  - SLO & Error Budget

### 6. Prometheus
- **URL**: http://localhost:9090
- **Descripción**: Métricas time-series
- **Puerto**: 9090
- **Estado**: ✅ Activo
- **Endpoints útiles**:
  - `/targets` - Estado de targets
  - `/alerts` - Alertas activas
  - `/graph` - Query interface

### 7. Loki
- **URL**: http://localhost:3100
- **Descripción**: Agregación de logs
- **Puerto**: 3100
- **Estado**: ✅ Activo
- **API**: http://localhost:3100/ready

### 8. Node Exporter
- **URL**: http://localhost:9100
- **Descripción**: Métricas del host (CPU, memoria, disco, red)
- **Puerto**: 9100
- **Estado**: ✅ Activo
- **Métricas**: http://localhost:9100/metrics

### 9. PostgreSQL Exporter
- **URL**: http://localhost:9187
- **Descripción**: Métricas de PostgreSQL
- **Puerto**: 9187
- **Estado**: ✅ Activo
- **Métricas**: http://localhost:9187/metrics

### 10. Redis Exporter
- **URL**: http://localhost:9121
- **Descripción**: Métricas de Redis
- **Puerto**: 9121
- **Estado**: ✅ Activo
- **Métricas**: http://localhost:9121/metrics

---

## 🤖 Automatización

### 11. n8n
- **URL**: http://localhost:5678
- **Usuario**: admin
- **Password**: REDACTED_PASSWORD
- **Puerto**: 5678
- **Estado**: ✅ Healthy
- **Descripción**: Workflow automation platform
- **Uso**: Crear workflows para reportes automáticos, alertas, integraciones

---

## 🔀 Proxy y Load Balancer

### 12. Nginx
- **HTTP**: http://localhost:80
- **HTTPS**: https://localhost:443
- **Puerto HTTP**: 80
- **Puerto HTTPS**: 443
- **Estado**: ✅ Healthy
- **Descripción**: Reverse proxy con rate limiting

---

## 🔧 Servicios en Background

### Celery Worker
- **Descripción**: Procesamiento asíncrono de tareas
- **Estado**: ✅ Activo
- **Tareas**:
  - Recolección de métricas (cada 15s)
  - Limpieza de datos antiguos (diario)
  - Health checks (cada 60s)

### Celery Beat
- **Descripción**: Scheduler de tareas periódicas
- **Estado**: ✅ Activo
- **Schedule**:
  - `collect-metrics`: cada 15 segundos
  - `cleanup-old-metrics`: diario a medianoche
  - `cleanup-old-audit-logs`: diario a las 2 AM
  - `health-check`: cada 60 segundos

### Promtail
- **Puerto**: 9080
- **Descripción**: Collector de logs para Loki
- **Estado**: ✅ Activo
- **Fuentes**: journald, Docker containers

---

## 📝 Comandos Útiles

### Ver estado de todos los servicios
```bash
docker-compose ps
```

### Ver logs de un servicio específico
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f grafana
```

### Reiniciar un servicio
```bash
docker-compose restart backend
docker-compose restart prometheus
```

### Acceder a un contenedor
```bash
docker-compose exec backend bash
docker-compose exec postgres psql -U sentinel_user -d sentinel_db
docker-compose exec redis redis-cli
```

### Verificar métricas desde la API
```bash
# Métricas recientes
curl http://localhost:8000/api/v1/analytics/metrics/recent | jq

# Estadísticas de las últimas 24 horas
curl "http://localhost:8000/api/v1/analytics/statistics?hours=24" | jq

# Anomalías detectadas
curl "http://localhost:8000/api/v1/analytics/anomalies?hours=24" | jq
```

---

## 🎯 Accesos Rápidos (Copiar y Pegar)

```
Frontend:           http://localhost:3000
API Backend:        http://localhost:8000
API Docs:           http://localhost:8000/docs
Grafana:            http://localhost:3001  (admin / REDACTED_PASSWORD)
Prometheus:         http://localhost:9090
n8n:                http://localhost:5678  (admin / REDACTED_PASSWORD)
PostgreSQL:         localhost:5432         (sentinel_user / sentinel_password)
Redis:              localhost:6379
```

---

## 📊 Resumen de Puertos

| Puerto | Servicio | Acceso |
|--------|----------|--------|
| 3000 | Frontend | Web UI |
| 3001 | Grafana | Dashboards |
| 3100 | Loki | Logs API |
| 5432 | PostgreSQL | Database |
| 5678 | n8n | Automation |
| 6379 | Redis | Cache |
| 8000 | Backend | REST API |
| 9090 | Prometheus | Metrics |
| 9100 | Node Exporter | Host metrics |
| 9121 | Redis Exporter | Redis metrics |
| 9187 | PostgreSQL Exporter | DB metrics |
| 80 | Nginx HTTP | Proxy |
| 443 | Nginx HTTPS | Proxy SSL |

---

## 🔐 Credenciales

### Grafana
- Usuario: `admin`
- Password: `REDACTED_PASSWORD`

### n8n
- Usuario: `admin`
- Password: `REDACTED_PASSWORD`

### PostgreSQL
- Usuario: `sentinel_user`
- Password: `sentinel_password`
- Database: `sentinel_db`

### Redis
- Sin password (localhost only)

---

## ✅ Verificación Rápida

Para verificar que todo está funcionando:

```bash
# 1. Ver estado de servicios
docker-compose ps

# 2. Probar API
curl http://localhost:8000/api/v1/health

# 3. Probar Prometheus
curl http://localhost:9090/-/healthy

# 4. Probar Loki
curl http://localhost:3100/ready

# 5. Ver métricas recientes
curl http://localhost:8000/api/v1/analytics/metrics/recent | jq '.count'
```

---

**Nota**: Todos los servicios están configurados para reinicio automático en caso de fallo.
