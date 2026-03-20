# Observability Stack - README

## 📊 Stack de Observabilidad Profesional

Este directorio contiene toda la configuración del stack de observabilidad para Sentinel.

### 🏗️ Arquitectura

```
Host System
    ↓
Node Exporter → Prometheus → Grafana (Métricas)
Journald → Promtail → Loki → Grafana (Logs)
```

### 🎯 Componentes

#### 1. **Prometheus** (puerto 9090)

- Base de datos de time-series para métricas
- Scraping automático cada 15 segundos
- Retención: 90 días o 10GB
- Alerting integrado

#### 2. **Node Exporter** (puerto 9100)

- Captura métricas del host Linux
- CPU, memoria, disco, red, procesos
- Acceso directo al sistema del host

#### 3. **Loki** (puerto 3100)

- Agregación de logs tipo Prometheus
- Ligero (no indexa contenido)
- Retención: 30 días
- Compresión automática

#### 4. **Promtail** (puerto 9080)

- Agente de captura de logs
- Lee journald del sistema
- Captura logs de Docker containers
- Pipeline de parsing y etiquetado

#### 5. **Grafana** (puerto 3001)

- Visualización unificada
- Dashboards pre-configurados
- Alerting visual
- Credenciales: admin / sentinel2024

### 📁 Estructura de Directorios

```
observability/
├── prometheus/
│   ├── prometheus.yml          # Config principal
│   └── rules/
│       └── alerts.yml          # Reglas de alertas
├── loki/
│   └── loki-config.yml         # Config de Loki
├── promtail/
│   └── promtail-config.yml     # Config de Promtail
└── grafana/
    └── provisioning/
        ├── datasources/
        │   └── datasources.yml # Auto-config datasources
        └── dashboards/
            ├── dashboards.yml  # Auto-import dashboards
            └── json/
                ├── host-metrics.json    # Dashboard de métricas
                └── system-logs.json     # Dashboard de logs
```

### 🚀 Uso

#### Iniciar todo el stack:

```bash
docker-compose up -d
```

#### Acceder a las interfaces:

- **Grafana**: http://localhost:3001 (admin / sentinel2024)
- **Prometheus**: http://localhost:9090
- **Loki**: http://localhost:3100
- **Node Exporter**: http://localhost:9100/metrics

#### Ver logs de un servicio:

```bash
docker-compose logs -f prometheus
docker-compose logs -f loki
docker-compose logs -f promtail
```

#### Detener el stack:

```bash
docker-compose down
```

#### Detener y limpiar datos:

```bash
docker-compose down -v  # ⚠️ Elimina todos los datos!
```

### 📊 Dashboards Pre-configurados

1. **Host Metrics Overview**
   - CPU, memoria, disco, red en tiempo real
   - Gráficos de tendencias
   - Thresholds visuales
   - Tabla de filesystems

2. **System Logs**
   - Stream en vivo de logs
   - Filtros por nivel (error, critical, warning)
   - Agrupación por servicio/unit
   - Gráficos de tasa de errores

### 🔔 Alertas Configuradas

#### Alertas de CPU:

- **HighCPUUsage**: >80% por 5min (warning)
- **CriticalCPUUsage**: >95% por 2min (critical)

#### Alertas de Memoria:

- **HighMemoryUsage**: >85% por 5min (warning)
- **CriticalMemoryUsage**: >95% por 2min (critical)

#### Alertas de Disco:

- **DiskSpaceLow**: >80% por 10min (warning)
- **DiskSpaceCritical**: >95% por 5min (critical)

#### Alertas de Servicios:

- **ServiceDown**: servicio caído por 1min (critical)
- **HighAPILatency**: P95 >1s por 5min (warning)

### 🔧 Personalización

#### Agregar nuevas alertas:

Edita `prometheus/rules/alerts.yml` y agrega reglas.

#### Crear dashboard personalizado:

1. Diseña en Grafana UI
2. Exporta como JSON
3. Guarda en `grafana/provisioning/dashboards/json/`
4. Reinicia Grafana: `docker-compose restart grafana`

#### Ajustar retención:

En `prometheus/prometheus.yml`:
```yaml
storage:
  tsdb:
    retention:
      time: 90d  # Cambiar días
      size: 10GB # Cambiar tamaño
```

En `loki/loki-config.yml`:
```yaml
limits_config:
  retention_period: 720h  # Cambiar horas
```

### 🎓 Queries Útiles (PromQL)

#### CPU Usage:

```promql
100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

#### Memory Usage:

```promql
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

#### Disk Usage:

```promql
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100
```

#### Network Traffic:

```promql
rate(node_network_receive_bytes_total[5m])
```

### 🎓 Queries Útiles (LogQL)

#### Errores en última hora:

```logql
{job="systemd-journal", level="error"} |= ""
```

#### Logs de un servicio específico:

```logql
{job="systemd-journal", unit="nginx.service"}
```

#### Rate de errores:

```logql
rate({job="systemd-journal", level="error"}[5m])
```

### 🔐 Seguridad

**⚠️ IMPORTANTE - Cambiar en producción:**

1. Cambiar password de Grafana en `.env`:
   ```bash
   GRAFANA_PASSWORD=tu_password_seguro
   ```

2. Habilitar autenticación en Prometheus (agregar nginx proxy)

3. Habilitar HTTPS con certificados

4. Configurar firewall para puertos internos

### 📈 Monitoreo del Propio Stack

El stack se auto-monitorea:
- Prometheus scrapes itself
- Métricas de Loki disponibles en Prometheus
- Métricas de Promtail disponibles

### 🐛 Troubleshooting

#### Prometheus no ve el Node Exporter:

```bash
# Verificar que Node Exporter está corriendo
curl http://localhost:9100/metrics

# Ver targets en Prometheus
# http://localhost:9090/targets
```

#### Loki no recibe logs:

```bash
# Verificar Promtail
docker-compose logs promtail

# Verificar que journald es accesible
journalctl -n 10
```

#### Grafana no muestra datos:

1. Verifica datasources: Settings → Data Sources
2. Test connection
3. Revisa queries en panel edit mode

### 📚 Recursos

- [Prometheus Docs](https://prometheus.io/docs/)
- [Loki Docs](https://grafana.com/docs/loki/)
- [Grafana Docs](https://grafana.com/docs/)
- [Node Exporter](https://github.com/prometheus/node_exporter)

### 🎯 Próximos Pasos

1. **Alertmanager**: Configurar notificaciones (email, Slack, Discord)
2. **Tempo**: Agregar distributed tracing
3. **Redis Exporter**: Monitorear Redis
4. **PostgreSQL Exporter**: Monitorear PostgreSQL
5. **Custom Metrics**: Instrumentar backend con `prometheus_client`
