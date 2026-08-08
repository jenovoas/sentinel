#  Stack de Observabilidad Profesional - Implementado

## ✅ Lo que acabamos de implementar

### 1. **Prometheus + Node Exporter** 
Stack completo de métricas de sistema:
- ✅ CPU, memoria, disco, red, procesos
- ✅ Retención: 90 días o 10GB
- ✅ Scraping cada 15 segundos
- ✅ Alertas configuradas (8 reglas)
- ✅ Exportador de métricas del host

### 2. **Loki + Promtail**
Agregación de logs centralizada:
- ✅ Captura logs de systemd/journald
- ✅ Captura logs de Docker containers
- ✅ Retención: 30 días
- ✅ Parsing automático por nivel
- ✅ Labels para queries avanzadas

### 3. **Grafana**
Visualización unificada:
- ✅ 2 dashboards pre-configurados
- ✅ Datasources auto-configurados
- ✅ Queries listas para usar
- ✅ Graficos interactivos

### 4. **Estructura Modular**
```
observability/
├── prometheus/         # Métricas
│   ├── prometheus.yml  # Config principal
│   └── rules/
│       └── alerts.yml  # 8 alertas configuradas
├── loki/              # Logs
│   └── loki-config.yml
├── promtail/          # Collector
│   └── promtail-config.yml
└── grafana/
    └── provisioning/
        ├── datasources/  # Auto-config
        └── dashboards/   # Pre-built
```

##  Cómo Usarlo

### Iniciar todo:
```bash
./observability-start.sh
```

### Acceder:
- **Grafana**: http://localhost:3001 (admin / sentinel2024)
- **Prometheus**: http://localhost:9090
- **Loki**: http://localhost:3100

### Ver dashboards:
1. Abre Grafana: http://localhost:3001
2. Login: admin / sentinel2024
3. Menu → Dashboards → Sentinel folder
4. Selecciona:
   - "Host Metrics Overview" para métricas
   - "System Logs" para logs

## 📊 Dashboards Incluidos

### 1. Host Metrics Overview
- **CPU Usage** - Gráfico en tiempo real con threshold
- **Memory Usage** - Uso de RAM con alertas
- **Network Traffic** - Bytes/s TX/RX por interfaz
- **Disk I/O** - Read/Write operations
- **Filesystem Usage** - Tabla con % usado por partición
- **Load Average** - Carga del sistema
- **Uptime** - Tiempo encendido

### 2. System Logs
- **Log Levels** - Distribución por severidad
- **Errors Over Time** - Tasa de errores/seg
- **Critical Logs** - Logs críticos en tiempo real
- **Logs by Unit** - Top 10 servicios
- **Live Stream** - Stream de todos los logs

## 🔔 Alertas Configuradas

| Alerta | Condición | Severidad |
|--------|-----------|-----------|
| HighCPUUsage | >80% por 5min | Warning |
| CriticalCPUUsage | >95% por 2min | Critical |
| HighMemoryUsage | >85% por 5min | Warning |
| CriticalMemoryUsage | >95% por 2min | Critical |
| DiskSpaceLow | >80% por 10min | Warning |
| DiskSpaceCritical | >95% por 5min | Critical |
| ServiceDown | Up=0 por 1min | Critical |
| HighAPILatency | P95 >1s por 5min | Warning |

##  Queries Útiles

### PromQL (Métricas)

**CPU total:**
```promql
100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**Memoria libre:**
```promql
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100
```

**Tráfico de red:**
```promql
rate(node_network_receive_bytes_total[5m])
```

### LogQL (Logs)

**Errores últimas 24h:**
```logql
{job="systemd-journal", level="error"}
```

**Rate de errores:**
```logql
rate({job="systemd-journal", level="error"}[5m])
```

**Logs de servicio específico:**
```logql
{job="systemd-journal", unit="nginx.service"}
```

## 💡 Ventajas vs CSV

| Característica | CSV Antiguo | Prometheus + Loki |
|----------------|-------------|-------------------|
| **Queries** | Lento, manual | Rápido, SQL-like |
| **Visualización** | Básica | Profesional |
| **Alerting** | Manual | Automático |
| **Retención** | Ilimitado (crece) | Configurable + compresión |
| **Escalabilidad** | Limitada | Alta |
| **Búsquedas** | grep manual | Indexado + labels |
| **Graficos** | Chart.js custom | Grafana nativo |
| **Correlación** | Difícil | Métricas + logs juntos |

## 🔄 Comparación con CSV Actual

**Lo que mantuvimos:**
- ✅ Scripts de captura en host-metrics/ siguen funcionando
- ✅ CSV como respaldo temporal
- ✅ API endpoints de Next.js siguen activos
- ✅ Dashboards de analytics siguen funcionando

**Lo nuevo:**
-  Prometheus scrapes Node Exporter directamente del host
-  Promtail captura journald en tiempo real
-  Todo centralizado en Grafana
-  Alerting automático
-  Retención inteligente
-  Queries mucho más rápidas

## 📝 Notas Importantes

### Recursos del Sistema
El stack consume aproximadamente:
- **CPU**: ~5-10% en idle
- **RAM**: ~500MB-1GB total
- **Disco**: Depende de retención (configurado 90d métricas, 30d logs)

### Compatibilidad
- ✅ Los scripts CSV siguen funcionando
- ✅ El dashboard de analytics sigue funcionando
- ✅ APIs de Next.js siguen activas
- ✅ Puedes usar ambos sistemas en paralelo

### Modo ligero para dev (ahorrar recursos)
Para sesiones de desarrollo donde no necesitas toda la observabilidad ni n8n:

1) Levantar solo core app:
```bash
docker-compose up -d backend frontend nginx redis postgres
```

2) Apagar observabilidad y automatización cuando no se usan:
```bash
docker-compose stop grafana prometheus loki promtail node-exporter n8n
```

3) Rehabilitar observabilidad/n8n bajo demanda:
```bash
docker-compose up -d grafana prometheus loki promtail node-exporter n8n
```

Tip: Si prefieres automatizar, crea un `docker-compose.override.yml` con profiles `observability` y `automation`, y arranca con `COMPOSE_PROFILES=observability,automation docker-compose up -d` solo cuando lo necesites.

### Migración Completa
Cuando estés listo para deprecar CSV:
1. Verificar que Grafana tiene todo lo que necesitas
2. Deshabilitar cron jobs de CSV
3. Archivar datos CSV históricos
4. Eliminar dependencia de /api/host-metrics en frontend

## 🎓 Recursos de Aprendizaje

- [Prometheus Docs](https://prometheus.io/docs/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)
- [Loki Docs](https://grafana.com/docs/loki/)
- [LogQL Guide](https://grafana.com/docs/loki/latest/logql/)
- [Grafana Tutorials](https://grafana.com/tutorials/)

## 🐛 Troubleshooting

**Prometheus no scrapes métricas:**
- Verificar targets en http://localhost:9090/targets
- Revisar logs: `docker-compose logs prometheus`

**Loki no recibe logs:**
- Verificar Promtail: `docker-compose logs promtail`
- Verificar journald: `journalctl -n 10`

**Grafana muestra "No data":**
- Verificar datasources en Settings → Data Sources
- Test connection
- Verificar range de tiempo en dashboard

---

**Estado**: ✅ Completamente funcional
**Versión**: 1.0.0
**Última actualización**: 2025-12-13
