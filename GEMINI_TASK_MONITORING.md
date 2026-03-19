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

## 0. Resumen Ejecutivo (Nodo Único Fenix)

**Fenix** es el único nodo de producción actual. Todos los servicios Ring 0 y de infraestructura se consolidan en este host bajo Podman.


### Arquitectura de Monitoreo

- **Node Exporter:** Métricas de hardware/SO de Fenix.
- **Promtail:** Recolección de logs de contenedores Podman.
- **Prometheus:** Agregación y almacenamiento de series temporales.
- **Neural Guard (Rust):** Motor de correlación en tiempo real (Cortex).

Métricas de ruteo global y estado de certificados TLS del nodo Fenix.

---

### 1.2 Dashboards Críticos en Grafana

1. **Fenix Infrastructure:** Salud del nodo (CPU, RAM, Disk, Load).
2. **Sentinel Core (Ring 0):** Estado del Cortex (`neural-guard`), latencia de respuesta de IA y uso de memoria S60.
3. **Pinguino Web & ERP:** Disponibilidad y latencia de servicios públicos.

---

## REGLAS DE ORO OPERATIVAS

- **NUNCA USAR DOCKER**: Usar siempre `podman` y `podman-compose`.
- **SEGURIDAD**: Acceso a servicios de monitoreo protegidos por el middleware `monitor-auth` (htpasswd).
- **CONECTIVIDAD**: Uso prioritario de la red `proxy` para exposición y `sentinel_internal` para backend.

**YATRA. Truth Resonates.**
