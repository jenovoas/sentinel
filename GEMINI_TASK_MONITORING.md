# GEMINI_TASK: Plan de Integración de Monitoreo Fenix (Nodo Único) 🛡️🛰️

## CONTEXTO DE PRODUCCIÓN (FENIX)

Infraestructura Fenix Sovereignty — **Nodo Único**:

| Nodo | IP VPN (wg0) | Acceso SSH | Rol |
| :--- | :--- | :--- | :--- |
| **Fenix** | `10.100.0.1` | `ssh -p 4222 jnovoas@10.10.10.8` | Orquestador Ring 0, DNS Master, Proxy, App Host |

> [!IMPORTANT]
> Los nodos `sentinel`, `kingu`, `centurion` e `ifenix` pertenecían a la fase de pruebas y ya no existen en el entorno productivo. Todo el stack de monitoreo reside en **Fenix**.

## STACK DE MONITOREO (PODMAN)

Todos los servicios corren bajo **Podman Rootless** en Fenix:

- **Prometheus** (Métricas) → `sentinel-net`:9090
- **Grafana** (Visualización) → `sentinel-net`:3000
- **Loki** (Logs) → `sentinel-net`:3100
- **Node Exporter** (Host Metrics) → `localhost`:9100
- **Promtail** (Log Collector) → `localhost`:9080

---

## FASE 1: Métricas del Host (Fenix)

### 1.1 Node Exporter

Desplegado localmente para monitorear CPU, RAM y Disco de Fenix:

```bash
podman run -d \
  --name node-exporter \
  --restart unless-stopped \
  --net host \
  --pid host \
  -v /:/host:ro,rslave \
  quay.io/prometheus/node-exporter:latest \
  --path.rootfs=/host
```

### 1.2 Configuración Prometheus

Añadir target local en `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'fenix-host'
    static_configs:
      - targets: ['localhost:9100']
        labels:
          instance: 'fenix'
          env: 'prod'
```

---

## FASE 2: Recolección de Logs (Promtail)

Promtail recolecta logs de `journald` y de los contenedores para enviarlos a Loki:

```bash
podman run -d \
  --name promtail \
  --restart unless-stopped \
  -v /var/log/journal:/var/log/journal:ro \
  -v /run/log/journal:/run/log/journal:ro \
  -v /etc/machine-id:/etc/machine-id:ro \
  -v ./config/promtail.yml:/etc/promtail/config.yml:ro \
  --cap-add CAP_DAC_READ_SEARCH \
  grafana/promtail:latest \
  -config.file=/etc/promtail/config.yml
```

---

## FASE 3: Monitoreo de Servicios Ring 0

### 3.1 Sentinel Cortex (Rust)

Métricas nativas de la orquestación S60 y ciclo de 17s.
- Target: `sentinel-cortex:8000/metrics`

### 3.2 Infraestructura (Postgres / Redis)

- **Postgres Exporter**: Métricas de base de datos `sentinel_db`.
- **Redis Exporter**: Métricas de caché y latencia.

### 3.3 Traefik Gateway

Métricas de ruteo global y estado de certificados TLS del nodo Fenix.

---

## FASE 4: Dashboards Críticos

1. **Fenix Sovereign Guard**: Estado vital del nodo (System Load, I/O, Error Rate).
2. **Ring 0 Operations**: Tiempos de respuesta de Cortex y salud del motor Base-60.
3. **Infrastructure Health**: Estado del ruteo y certificados TLS.

---

## REGLAS DE ORO OPERATIVAS

- **NUNCA USAR DOCKER**: Usar siempre `podman` y `podman-compose`.
- **SEGURIDAD**: Acceso a servicios de monitoreo protegidos por el middleware `monitor-auth` (htpasswd).
- **CONECTIVIDAD**: Uso prioritario de la red `proxy` para exposición y `sentinel_internal` para backend.

**YATRA. Truth Resonates.**
