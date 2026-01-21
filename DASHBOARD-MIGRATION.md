# 📊 Migración de Dashboards a Grafana

## ✅ Dashboard Operacional Creado

He creado **"Sentinel - Operational Dashboard"** con las siguientes secciones:

### Métricas del Host (Ya Disponibles)

| Panel | Métrica | Fuente | Estado |
|-------|---------|--------|--------|
| **CPU Usage** | % uso de CPU | Node Exporter | ✅ Funcionando |
| **Memory Usage** | % uso de RAM | Node Exporter | ✅ Funcionando |
| **Memory Available** | RAM disponible | Node Exporter | ✅ Funcionando |
| **System Load** | Load average 1m | Node Exporter | ✅ Funcionando |
| **Network Traffic** | TX/RX bytes/s | Node Exporter | ✅ Funcionando |
| **Disk I/O** | Read/Write bytes/s | Node Exporter | ✅ Funcionando |
| **Disk Usage** | % usado por partición | Node Exporter | ✅ Funcionando |
| **Network Connections** | TCP established | Node Exporter | ✅ Funcionando |
| **System Uptime** | Tiempo encendido | Node Exporter | ✅ Funcionando |
| **System Logs** | Errores y warnings | Promtail → Loki | ✅ Funcionando |
| **Total Processes** | Procesos activos | Node Exporter | ✅ Funcionando |
| **Filesystem Table** | Uso detallado | Node Exporter | ✅ Funcionando |

### Métricas Pendientes de Instrumentar

| Panel | Métrica | Requiere | Prioridad |
|-------|---------|----------|-----------|
| **GPU Usage** | GPU % y memoria | nvidia-smi o exporter | 🔸 Media |
| **Database Health** | Estado de PostgreSQL | PostgreSQL Exporter | 🔴 Alta |
| **DB Connections** | Active/Idle/Total | PostgreSQL Exporter | 🔴 Alta |
| **DB Queries** | Queries activas | PostgreSQL Exporter | 🟡 Media |
| **Cache Stats** | Redis stats | Redis Exporter | 🟡 Media |
| **API Requests** | Request rate | Backend instrumentation | 🔴 Alta |
| **API Latency** | Response time | Backend instrumentation | 🔴 Alta |
| **WiFi Signal** | SSID y señal | Node Exporter wifi | 🟢 Baja |

## 🚀 Cómo Ver el Nuevo Dashboard

1. Reinicia Grafana para cargar el nuevo dashboard:
   ```bash
   docker-compose restart grafana
   ```

2. Espera 10 segundos y abre:
   ```
   http://localhost:3001
   ```

3. Login: `admin` / `sentinel2024`

4. Navega a:
   ```
   Menu → Dashboards → Sentinel folder → Sentinel - Operational Dashboard
   ```

## 📈 Comparación: Next.js vs Grafana

### Lo que YA tienes en Grafana:

| Métrica Next.js | Equivalente Grafana | Panel # |
|-----------------|---------------------|---------|
| CPU % gauge | CPU Usage stat | #1 |
| Memory % gauge | Memory Usage stat | #2 |
| CPU history sparkline | CPU Usage Over Time | #5 |
| Memory history sparkline | Memory Usage Over Time | #6 |
| Network TX/RX | Network Traffic chart | #7 |
| Disk usage | Disk Usage gauge | #9 |
| Network connections | Network Connections stat | #10 |
| System logs | Recent System Logs panel | #12 |
| Filesystem table | Filesystem Usage table | #14 |

### Lo que FALTA instrumentar:

#### 1. **GPU Metrics** (Opcional)
```bash
# Si tienes NVIDIA GPU, necesitas nvidia-gpu-exporter
# Ver: https://github.com/utkuozdemir/nvidia_gpu_exporter
```

#### 2. **PostgreSQL Metrics** (IMPORTANTE)
```yaml
# Agregar a docker-compose.yml:
postgres-exporter:
  image: prometheuscommunity/postgres-exporter
  environment:
    DATA_SOURCE_NAME: "postgresql://sentinel_user:sentinel_password@postgres:5432/sentinel_db?sslmode=disable"
  ports:
    - "9187:9187"
```

#### 3. **Redis Metrics** (Útil para cache)
```yaml
# Agregar a docker-compose.yml:
redis-exporter:
  image: oliver006/redis_exporter
  environment:
    REDIS_ADDR: "redis:6379"
  ports:
    - "9121:9121"
```

#### 4. **Backend API Metrics** (MUY IMPORTANTE)
```python
# backend/app/main.py - Agregar:
from prometheus_client import Counter, Histogram, make_asgi_app

# Métricas
http_requests_total = Counter('http_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
http_request_duration = Histogram('http_request_duration_seconds', 'Request duration', ['endpoint'])

# Endpoint /metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

## 🎯 Plan de Acción Sugerido

### **Fase 1: Usa lo que ya tienes** ✅ (AHORA)
```
✅ Dashboard operacional con host metrics
✅ System logs en tiempo real
✅ 12 paneles funcionales
✅ Auto-refresh cada 10 segundos
```

### **Fase 2: Instrumenta Backend** (Próxima sesión)
1. Agregar prometheus_client a FastAPI
2. Exponer /metrics endpoint
3. Agregar PostgreSQL Exporter
4. Agregar Redis Exporter
5. Actualizar dashboard con nuevas métricas

### **Fase 3: Dashboards Avanzados** (Futuro)
1. Dashboard de API performance
2. Dashboard de Database health
3. Dashboard de Cache analytics
4. Alerting avanzado

## 📚 Para Estudiar Grafana

### **Empieza Explorando:**

1. **Tu Nuevo Dashboard**
   - Abre: http://localhost:3001
   - Explora cada panel
   - Haz zoom (click + drag en gráficos)
   - Cambia el time range (arriba derecha)

2. **Modo Edición**
   - Clic en título del panel → Edit
   - Ve la query PromQL
   - Modifica y ve resultados en tiempo real
   - Clic "Apply" para guardar

3. **Explore**
   - Menu → Explore
   - Selecciona datasource (Prometheus o Loki)
   - Prueba queries:
     ```promql
     # CPU
     node_cpu_seconds_total
     
     # Memory
     node_memory_MemTotal_bytes
     
     # Network
     node_network_receive_bytes_total
     ```

### **Tutoriales Rápidos:**

```
1. Panel basics (5min): https://grafana.com/docs/grafana/latest/panels/
2. PromQL basics (10min): https://prometheus.io/docs/prometheus/latest/querying/basics/
3. Grafana transforms (5min): https://grafana.com/docs/grafana/latest/panels/transformations/
```

## 🔄 Próximos Pasos

Cuando estés listo, te ayudo a:

1. ✅ **Instrumentar el backend** con métricas de API
2. ✅ **Agregar PostgreSQL Exporter** para DB stats
3. ✅ **Crear dashboard de Analytics** (equivalente a tu página de analytics)
4. ✅ **Configurar alertas** personalizadas
5. ✅ **Deprecar dashboards de Next.js** (cuando estés listo)

## 📝 Notas Importantes

- ✅ El dashboard se auto-refresca cada 10 segundos
- ✅ Puedes cambiar a 5s o 30s en settings (arriba derecha)
- ✅ Todas las queries son optimizadas para performance
- ✅ Los colores y thresholds están configurados (verde/amarillo/rojo)
- ✅ El dashboard es totalmente personalizable

## 🎓 Recursos

- Dashboard creado: `observability/grafana/provisioning/dashboards/json/sentinel-operational-dashboard.json`
- Documentación: `OBSERVABILITY.md`
- Health check: `./observability-health.sh`

---

**Estado**: Dashboard operacional con host metrics ✅ LISTO  
**Pendiente**: Instrumentación de backend y database  
**Siguiente**: Cuando domines este dashboard, continuamos con la instrumentación
