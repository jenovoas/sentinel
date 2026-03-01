# GEMINI_TASK: Plan de Integración de Monitoreo SecurePenguin

## CONTEXTO DEL SISTEMA

Infraestructura SecurePenguin — 4 nodos GCP + laptop:

| Nodo       | IP VPN      | IP GCP       | Rol                                    |
|------------|-------------|--------------|----------------------------------------|
| sentinel   | 10.10.10.2  | 34.176.43.117| Plataforma central (Prometheus+Grafana+Loki+n8n) |
| kingu      | 10.10.10.7  | (dynamic)    | WireGuard hub, PowerDNS slave, Traefik |
| centurion  | 10.10.10.6  | (dynamic)    | Guacamole, servidores legacy           |
| fenix      | 10.10.10.8  | 34.176.228.224| DNS master, Traefik principal, n8n    |
| ifenix     | 10.10.10.9  | (laptop)     | Nodo secundario sincronizado           |

**Stack de monitoreo en sentinel (ya desplegado en Podman):**
- Prometheus → puerto 9090
- Grafana → puerto 3001 (admin/REDACTED_PASSWORD)
- Loki → puerto 3100
- Promtail → recolector de logs local
- Node Exporter → puerto 9100 (solo sentinel)
- n8n → puerto 5678 (workflows de automatización)

**Servicios en sentinel (docker-compose.yml):**
- sentinel-backend (FastAPI, puerto 8000)
- sentinel-frontend (Next.js, puerto 3000)
- sentinel-postgres (PostgreSQL, puerto 5432, BD: sentinel_db)
- sentinel-redis (Redis, puerto 6379)
- sentinel-n8n (n8n, puerto 5678)
- sentinel-grafana, sentinel-prometheus, sentinel-loki, sentinel-promtail
- sentinel-node-exporter (puerto 9100)
- sentinel-guacd, sentinel-guacamole (puerto 8090)
- qhc-agent.service, adm-agent.service, vid-agent.service (ME-60OS, systemd)

---

## OBJETIVO

Conectar TODOS los servicios y nodos monitoreables al stack Prometheus+Grafana+Loki en sentinel.
Resultado final: **panel único de observabilidad** que muestra estado de toda la infraestructura.

---

## FASE 1: Node Exporter en todos los nodos (métricas host)

### 1.1 Desplegar Node Exporter como contenedor Podman en cada nodo externo

Para cada nodo: **fenix (10.10.10.8)**, **kingu (10.10.10.7)**, **centurion (10.10.10.6)**:

```bash
# Ejecutar en cada nodo via SSH
podman run -d \
  --name node-exporter \
  --restart unless-stopped \
  --net host \
  --pid host \
  -v /:/host:ro,rslave \
  quay.io/prometheus/node-exporter:latest \
  --path.rootfs=/host
```

Verificar que puerto 9100 está accesible desde sentinel:
```bash
# Desde sentinel:
curl http://10.10.10.8:9100/metrics | head -5  # fenix
curl http://10.10.10.7:9100/metrics | head -5  # kingu
curl http://10.10.10.6:9100/metrics | head -5  # centurion
```

**Abrir puerto 9100 si hay firewall:** verificar nftables/iptables en cada nodo.

### 1.2 Agregar targets en prometheus.yml de sentinel

Archivo: `/home/jnovoas/Dev/sentinel/observability/prometheus/prometheus.yml`

Agregar al final de `scrape_configs`:
```yaml
  - job_name: 'node-exporter-fenix'
    static_configs:
      - targets: ['10.10.10.8:9100']
        labels:
          service: 'host-metrics'
          instance: 'fenix'
          role: 'traefik-dns-master'

  - job_name: 'node-exporter-kingu'
    static_configs:
      - targets: ['10.10.10.7:9100']
        labels:
          service: 'host-metrics'
          instance: 'kingu'
          role: 'wireguard-hub-dns'

  - job_name: 'node-exporter-centurion'
    static_configs:
      - targets: ['10.10.10.6:9100']
        labels:
          service: 'host-metrics'
          instance: 'centurion'
          role: 'guacamole-legacy'
```

Recargar Prometheus: `curl -X POST http://localhost:9090/-/reload`

---

## FASE 2: Promtail en todos los nodos (logs centralizados)

### 2.1 Config Promtail para nodos externos

Crear `/home/jnovoas/Dev/sentinel/observability/promtail/promtail-fenix.yml`:
```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions-fenix.yaml

clients:
  - url: http://10.10.10.2:3100/loki/api/v1/push

scrape_configs:
  - job_name: systemd-journal
    journal:
      max_age: 12h
      labels:
        job: systemd-journal
        host: fenix
    relabel_configs:
      - source_labels: ['__journal__systemd_unit']
        target_label: unit
      - source_labels: ['__journal_priority_keyword']
        target_label: level

  - job_name: traefik-logs
    static_configs:
      - targets: [localhost]
        labels:
          job: traefik
          host: fenix
          __path__: /var/log/traefik/*.log
```

Desplegar con Podman en fenix:
```bash
podman run -d \
  --name promtail \
  --restart unless-stopped \
  -v /var/log/journal:/var/log/journal:ro \
  -v /run/log/journal:/run/log/journal:ro \
  -v /etc/machine-id:/etc/machine-id:ro \
  -v /home/jnovoas/promtail-config.yml:/etc/promtail/config.yml:ro \
  --cap-add CAP_DAC_READ_SEARCH \
  grafana/promtail:latest \
  -config.file=/etc/promtail/config.yml
```

Repetir con config equivalente para **kingu** y **centurion** (cambiar `host:` label).

---

## FASE 3: Métricas de servicios específicos

### 3.1 Traefik metrics (fenix)

Traefik tiene endpoint de métricas nativo. En el archivo de configuración de Traefik en fenix:

```yaml
# traefik.yml o como static config
metrics:
  prometheus:
    addEntryPointsLabels: true
    addRoutersLabels: true
    addServicesLabels: true
    entryPoint: metrics

entryPoints:
  metrics:
    address: ":8082"
```

Agregar en prometheus.yml:
```yaml
  - job_name: 'traefik-fenix'
    static_configs:
      - targets: ['10.10.10.8:8082']
        labels:
          service: 'traefik'
          instance: 'fenix'
```

### 3.2 PowerDNS metrics (centurion + kingu como slaves)

Habilitar API de PowerDNS en `/etc/powerdns/pdns.conf` de centurion:
```ini
webserver=yes
webserver-port=8081
webserver-allow-from=10.10.10.0/24
api=yes
api-key=securepenguin_pdns_api_2026
```

Desplegar `powerdns-exporter`:
```bash
# En centurion:
podman run -d \
  --name pdns-exporter \
  -p 9120:9120 \
  --restart unless-stopped \
  ledgr/powerdns-exporter \
  -api-url=http://localhost:8081/api/v1 \
  -api-key=securepenguin_pdns_api_2026
```

Agregar en prometheus.yml:
```yaml
  - job_name: 'powerdns-centurion'
    static_configs:
      - targets: ['10.10.10.6:9120']
        labels:
          service: 'powerdns'
          instance: 'centurion'
          role: 'master'
```

### 3.3 WireGuard metrics (kingu — hub principal)

```bash
# En kingu:
podman run -d \
  --name wg-exporter \
  -p 9586:9586 \
  --restart unless-stopped \
  --cap-add NET_ADMIN \
  --privileged \
  mindflavor/prometheus-wireguard-exporter
```

Agregar en prometheus.yml:
```yaml
  - job_name: 'wireguard-kingu'
    static_configs:
      - targets: ['10.10.10.7:9586']
        labels:
          service: 'wireguard'
          instance: 'kingu'
```

### 3.4 PostgreSQL exporter (sentinel)

Ya debería estar en compose. Verificar en `docker-compose.yml`:
```yaml
  postgres-exporter:
    image: quay.io/prometheuscommunity/postgres-exporter:latest
    container_name: sentinel-postgres-exporter
    environment:
      DATA_SOURCE_NAME: "postgresql://sentinel_user:sentinel_password@sentinel-postgres:5432/sentinel_db?sslmode=disable"
    ports:
      - "9187:9187"
    networks:
      - sentinel_network
    restart: unless-stopped
```

### 3.5 Redis exporter (sentinel)

```yaml
  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: sentinel-redis-exporter
    environment:
      REDIS_ADDR: "redis://sentinel-redis:6379"
    ports:
      - "9121:9121"
    networks:
      - sentinel_network
    restart: unless-stopped
```

### 3.6 ME-60OS agents metrics (qhc/adm/vid — sentinel)

Los agentes ME-60OS emiten métricas. Verificar si exponen endpoint Prometheus o hay que leerlas del journal:

```yaml
  - job_name: 'me60os-qhc'
    static_configs:
      - targets: ['localhost:9200']  # verificar puerto real
        labels:
          service: 'me60os-qhc'
          instance: 'sentinel'

  - job_name: 'me60os-adm'
    static_configs:
      - targets: ['localhost:9201']
        labels:
          service: 'me60os-adm'
          instance: 'sentinel'
```

Si no hay endpoints: recolectar via Promtail desde journald con label `unit: qhc-agent.service`.

### 3.7 Blackbox exporter (SSL + endpoints HTTP)

Para monitorear que los servicios expuestos externamente responden y tienen SSL válido:

```yaml
  blackbox-exporter:
    image: quay.io/prometheus/blackbox-exporter:latest
    container_name: sentinel-blackbox
    ports:
      - "9115:9115"
    networks:
      - sentinel_network
    restart: unless-stopped
```

Targets en prometheus.yml:
```yaml
  - job_name: 'blackbox-http'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
          - https://pinguinoseguro.cl
          - https://n8n.pinguinoseguro.cl
          - https://grafana.pinguinoseguro.cl
          - https://sentinel.pinguinoseguro.cl
          - https://sentinel-api.pinguinoseguro.cl
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: sentinel-blackbox:9115
```

---

## FASE 4: Dashboards Grafana

### 4.1 Dashboard: Infraestructura Global SecurePenguin

Crear JSON en `/home/jnovoas/Dev/sentinel/observability/grafana/provisioning/dashboards/`:

Paneles requeridos:
- **Mapa de nodos**: estado UP/DOWN de fenix, kingu, centurion, sentinel (via blackbox)
- **CPU/RAM/Disk** por nodo (via node-exporter, separado por instance label)
- **WireGuard peers**: latencia y bytes transferidos por peer (kingu)
- **Traefik**: requests/s, errores, latencia por servicio (fenix)
- **PowerDNS**: queries/s, cache hit rate (centurion)
- **PostgreSQL**: conexiones activas, queries/s, tamaño BD (sentinel)
- **Redis**: memoria usada, operaciones/s, keys (sentinel)
- **SSL Certificates**: días hasta expiración (blackbox)

### 4.2 Dashboard: ME-60OS Agents (Base-60)

Paneles:
- **QHC Phase**: ciclo YHWH 10-5-6-5 actual (del journal o métricas)
- **ADM Coherence**: TQ promedio de mesh batman-adv (objetivo: >0.7)
- **VID Thermal**: acciones cooling/contracting en ventana 60s
- **Audit Cortex Bridge**: eventos por segundo, YHWH-17 throttle rate

### 4.3 Dashboard: Logs Centralizados

Mejoras al dashboard System Logs existente:
- Filtro por nodo (fenix/kingu/centurion/sentinel)
- Filtro por servicio/unit
- Alertas de errores críticos
- Logs de Guardian-Alpha LSM (eventos de bloqueo)

---

## FASE 5: Alertmanager + n8n workflows

### 5.1 Alertmanager

Agregar al docker-compose.yml:
```yaml
  alertmanager:
    image: quay.io/prometheus/alertmanager:latest
    container_name: sentinel-alertmanager
    volumes:
      - ./observability/alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml
    ports:
      - "9093:9093"
    networks:
      - sentinel_network
    restart: unless-stopped
```

Configurar alertmanager.yml para enviar a n8n webhook:
```yaml
route:
  receiver: 'n8n-webhook'
receivers:
  - name: 'n8n-webhook'
    webhook_configs:
      - url: 'http://sentinel-n8n:5678/webhook/alertmanager'
```

### 5.2 Reglas de alerta en Prometheus

Archivo: `/home/jnovoas/Dev/sentinel/observability/prometheus/rules/alerts.yml`

Agregar reglas:
```yaml
groups:
  - name: infrastructure
    rules:
      - alert: NodeDown
        expr: up{job=~"node-exporter.*"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Nodo {{ $labels.instance }} caído"

      - alert: HighCPU
        expr: 100 - (avg by(instance)(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 85
        for: 5m
        labels:
          severity: warning

      - alert: DiskAlmostFull
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.1
        for: 5m
        labels:
          severity: critical

      - alert: SSLExpiraSoon
        expr: (probe_ssl_earliest_cert_expiry - time()) / 86400 < 14
        labels:
          severity: warning
        annotations:
          summary: "SSL de {{ $labels.instance }} expira en menos de 14 días"

      - alert: ME60OSAdmCoherenciaLow
        expr: me60os_adm_coherence < 0.5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Coherencia mesh MycNet por debajo de 0.5"
```

### 5.3 Workflows n8n

Crear/importar workflows en n8n (puerto 5678):

**Workflow 1: Alert Handler**
- Trigger: Webhook `/webhook/alertmanager`
- Acción: Parsear alerta → formatear mensaje → enviar a canal de notificación

**Workflow 2: Health Check Scheduled**
- Trigger: Cron cada 5 minutos
- Acción: HTTP GET a cada servicio expuesto, guardar estado en BD, alertar si falla

**Workflow 3: Auto-remediation**
- Trigger: Webhook de alerta "NodeDown" para servicios Podman
- Acción: SSH al nodo → `podman restart <servicio>` → confirmar recuperación

---

## FASE 6: Conexión Traefik → servicios sentinel

Actualmente Traefik en fenix no tiene rutas para los nuevos servicios en sentinel.

### 6.1 Rutas a agregar en Traefik (fenix)

Servicios sentinel accesibles via HTTPS:
```
grafana.pinguinoseguro.cl → sentinel:3001
sentinel.pinguinoseguro.cl → sentinel:3000
sentinel-api.pinguinoseguro.cl → sentinel:8000
n8n.pinguinoseguro.cl → sentinel:5678  (ya existente en centurion, migrar)
guacamole.pinguinoseguro.cl → sentinel:8090
prometheus.pinguinoseguro.cl → sentinel:9090 (con auth básica)
alertmanager.pinguinoseguro.cl → sentinel:9093 (con auth básica)
```

Verificar config actual de Traefik en fenix:
```bash
ssh -p 4222 jnovoas@10.10.10.8 "ls ~/traefik/ || ls /etc/traefik/"
```

---

## ORDEN DE EJECUCIÓN RECOMENDADO

```
PRIORIDAD 1 (esta sesión):
[1] SSH sentinel recuperado → verificar servicios Podman activos
[2] Node Exporter en fenix (el más crítico)
[3] prometheus.yml: añadir targets externos
[4] Blackbox exporter: monitorear URLs externas

PRIORIDAD 2 (siguiente sesión):
[5] Node Exporter en kingu y centurion
[6] Promtail en fenix y kingu
[7] PowerDNS exporter en centurion
[8] WireGuard exporter en kingu

PRIORIDAD 3 (cuando servicios estables):
[9] Postgres + Redis exporters en sentinel
[10] Dashboards Grafana completos
[11] Alertmanager + n8n workflows
[12] Traefik routes para todos los subdominios

PRIORIDAD 4 (investigación):
[13] ME-60OS metrics endpoint (¿expone Prometheus?)
[14] Guardian-Alpha LSM metrics
[15] batman-adv / MycNet observabilidad
```

---

## ENTREGABLES QUE GEMINI DEBE PRODUCIR

Para cada fase, Gemini debe:

1. **Verificar** que el target/servicio es accesible desde sentinel
2. **Editar** el archivo de configuración correspondiente
3. **Recargar** el servicio (Prometheus reload, Podman restart)
4. **Confirmar** que los datos aparecen en Prometheus/Grafana
5. **Reportar** en formato estándar:

```
RESULTADO [GEMINI] [MON-NNN]:
- Estado: COMPLETADO | PARCIAL | FALLIDO
- Acciones realizadas: <lista>
- Issues: <errores>
- Recomendación: <siguiente paso>
```

---

## NOTAS CRÍTICAS PARA GEMINI

- Siempre validar variables antes de usar en rutas de archivos
- NO docker en sentinel — solo `podman` y `podman-compose`
- El compose de sentinel está en: `~/Dev/sentinel/docker-compose.yml`
- Prometheus config: `~/Dev/sentinel/observability/prometheus/prometheus.yml`
- Grafana dashboards: `~/Dev/sentinel/observability/grafana/provisioning/dashboards/`
- Reload Prometheus sin restart: `curl -X POST http://10.10.10.2:9090/-/reload`
- SSH a nodos: `ssh -p 4222 jnovoas@10.10.10.X`
- Contenedor Promtail necesita `CAP_DAC_READ_SEARCH` para leer journald
