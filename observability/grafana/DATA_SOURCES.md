# Grafana Data Sources - Configuración Actualizada

**Fecha**: 14 de Diciembre, 2025  
**Data Sources Activos**: 3  
**Estado**: ✅ Configurados correctamente

---

## 📊 Data Sources Disponibles

### 1. ✅ Prometheus (Default)
- **Tipo**: prometheus
- **URL**: http://prometheus:9090
- **UID**: `prometheus`
- **Descripción**: Base de datos principal de métricas time-series
- **Mejoras aplicadas**:
  - ✅ Intervalo de scraping: 15 segundos
  - ✅ Timeout de queries: 60 segundos
  - ✅ HTTP Method: POST (para queries largas)
  - ✅ No editable (protegido)

**Métricas disponibles a través de Prometheus**:
- Node Exporter (job: `node-exporter`)
- PostgreSQL Exporter (job: `postgres`)
- Redis Exporter (job: `redis`)
- Backend API (job: `backend`)
- Prometheus self-monitoring (job: `prometheus`)

### 2. ✅ Loki
- **Tipo**: loki
- **URL**: http://loki:3100
- **UID**: `loki`
- **Descripción**: Sistema de agregación de logs
- **Mejoras aplicadas**:
  - ✅ Max lines: 1000
  - ✅ Timeout: 60 segundos
  - ✅ No editable (protegido)

**Logs disponibles**:
- Journald (systemd logs)
- Docker containers
- Niveles: critical, error, warning, info, debug

### 3. ✅ TestData
- **Tipo**: testdata
- **UID**: `testdata`
- **Descripción**: Fuente de datos de prueba para desarrollo de dashboards
- **Uso**: Crear y probar dashboards sin datos reales

---

## 🎯 Cómo Acceder a Métricas de Exporters

### Importante: Arquitectura Correcta

Los exporters (PostgreSQL, Redis, Node) **NO son data sources separados**. Todos están configurados como **targets de Prometheus** y sus métricas se consultan a través del data source de Prometheus.

### Consultar Métricas de PostgreSQL

```promql
# Conexiones activas
pg_stat_database_numbackends{datname="sentinel_db"}

# Tamaño de la base de datos
pg_database_size_bytes{datname="sentinel_db"}

# Queries por segundo
rate(pg_stat_database_xact_commit{datname="sentinel_db"}[5m])

# Cache hit ratio
pg_stat_database_blks_hit / (pg_stat_database_blks_hit + pg_stat_database_blks_read)
```

### Consultar Métricas de Redis

```promql
# Comandos por segundo
rate(redis_commands_processed_total[5m])

# Hit ratio
redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total)

# Memoria usada
redis_memory_used_bytes

# Clientes conectados
redis_connected_clients
```

### Consultar Métricas de Node Exporter

```promql
# CPU usage
100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memoria disponible
node_memory_MemAvailable_bytes

# Disco I/O
rate(node_disk_read_bytes_total[5m])

# Network TX
rate(node_network_transmit_bytes_total{device="eth0"}[5m])
```

---

## 🔍 Verificar Targets en Prometheus

Para ver todos los exporters que Prometheus está scrapeando:

1. Ve a http://localhost:9090/targets
2. Deberías ver:
   - ✅ prometheus (localhost:9090)
   - ✅ node-exporter (node-exporter:9100)
   - ✅ postgres (postgres-exporter:9187)
   - ✅ redis (redis-exporter:9121)
   - ✅ backend (backend:8000)

### Verificar vía API

```bash
# Ver todos los targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health, lastScrape: .lastScrape}'

# Ver métricas de PostgreSQL
curl -s http://localhost:9090/api/v1/query?query=pg_up | jq

# Ver métricas de Redis
curl -s http://localhost:9090/api/v1/query?query=redis_up | jq

# Ver métricas de Node
curl -s http://localhost:9090/api/v1/query?query=node_uname_info | jq
```

---

## 📈 Crear Dashboards con Múltiples Exporters

### Ejemplo: Dashboard de Base de Datos

```json
{
  "panels": [
    {
      "title": "PostgreSQL Connections",
      "targets": [
        {
          "datasource": "Prometheus",
          "expr": "pg_stat_database_numbackends{datname=\"sentinel_db\"}"
        }
      ]
    },
    {
      "title": "Redis Hit Ratio",
      "targets": [
        {
          "datasource": "Prometheus",
          "expr": "redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total)"
        }
      ]
    }
  ]
}
```

---

## 🚀 Data Source Adicional (Opcional)

### Sentinel API JSON Datasource

Si quieres consultar directamente la API de Sentinel (sin pasar por Prometheus):

1. **Instalar plugin**:
```bash
docker-compose exec grafana grafana cli plugins install marcusolsson-json-datasource
docker-compose restart grafana
```

2. **Descomentar en datasources.yml**:
```yaml
- name: Sentinel API
  type: marcusolsson-json-datasource
  uid: sentinel-api
  access: proxy
  url: http://backend:8000
  isDefault: false
  jsonData:
    timeout: 60
  editable: false
```

3. **Reiniciar Grafana**:
```bash
docker-compose restart grafana
```

---

## ✅ Resumen de Cambios

### Antes
- Prometheus (básico)
- Loki (básico)

### Después
- ✅ Prometheus (mejorado con timeout, httpMethod POST)
- ✅ Loki (mejorado con maxLines, timeout)
- ✅ TestData (nuevo, para desarrollo)
- ✅ Todos los exporters accesibles vía Prometheus

### Métricas Disponibles

| Fuente | Job Name | Puerto | Métricas |
|--------|----------|--------|----------|
| Node Exporter | `node-exporter` | 9100 | CPU, memoria, disco, red |
| PostgreSQL | `postgres` | 9187 | Conexiones, queries, locks |
| Redis | `redis` | 9121 | Comandos, hit ratio, memoria |
| Backend | `backend` | 8000 | API metrics (futuro) |
| Prometheus | `prometheus` | 9090 | Self-monitoring |

---

## 🎯 Próximos Pasos

1. **Importar dashboards pre-hechos**:
   - PostgreSQL Dashboard (ID: 9628)
   - Redis Dashboard (ID: 763)
   - Node Exporter Full (ID: 1860)

2. **Crear dashboards custom**:
   - Combinar métricas de múltiples exporters
   - Correlacionar logs con métricas
   - Crear alertas específicas

3. **Instrumentar backend**:
   - Agregar endpoint `/metrics` en FastAPI
   - Usar `prometheus_client` library
   - Exponer métricas custom de aplicación

---

## 📞 Verificación Final

```bash
# Ver data sources en Grafana
curl -s http://localhost:3001/api/datasources -u admin:darkfenix | jq -r '.[] | "\(.name) - \(.type)"'

# Debería mostrar:
# Loki - loki
# Prometheus - prometheus
# TestData - testdata

# Ver targets en Prometheus
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'

# Debería mostrar: 5 (prometheus, node-exporter, postgres, redis, backend)
```

---

**Estado**: 🟢 Configuración correcta y optimizada  
**Arquitectura**: Prometheus como agregador central de todos los exporters  
**Próxima acción**: Importar dashboards pre-hechos para PostgreSQL y Redis
