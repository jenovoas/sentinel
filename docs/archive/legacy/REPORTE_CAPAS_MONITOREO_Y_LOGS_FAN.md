# 📊 Configuración de las Capas de Monitoreo, Métricas y Logs en Producción (Fan 10.88.0.1)
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor:** Fan (`10.88.0.1`)  
> **Grafana:** `http://10.88.0.1:3001`  
> **Loki API:** `http://10.88.0.1:3100`  
> **Prometheus-Cortex Metrics:** `http://10.88.0.1:8000/metrics`  
> **Fecha:** 29 de Julio, 2026

---

## 🔬 1. Configuración de Ingesta de Logs con Promtail y Loki

1. **Promtail Daemon (`/etc/sentinel/promtail.yaml`)**:
   - Ingesta directa del **Journald de Systemd** (`/var/log/journal`) capturando en tiempo real los 6 daemons (`sentinel-cortex`, `gamma-watchdog`, `qhc-agent`, `pai-neural`, `vid-agent`, `hex-daemon`).
   - Ingesta de archivos de traza eBPF y logs de Sentinel (`/var/log/sentinel/*.log`).
   - Tenant Header de Seguridad: `X-Scope-OrgID: sentinel`.

2. **Verificación de Ingesta en Loki (`http://127.0.0.1:3100`)**:
   - Consulta ejecutada con éxito: `{job="sentinel_file_logs"}` retornando interceptaciones Ring-0 en tiempo real (`FloatDetector`, `bpf_trace_printk`).

---

## 📈 2. Dashboard Provisionado en Grafana (`http://10.88.0.1:3001`)

**Nombre:** `Sentinel Cortex - Bio-Resonance & Telemetry`  
**URL:** `/d/acvw5b/sentinel-cortex-bio-resonance-and-telemetry`

### 4 Paneles Principales de Estudio y Benchmarking:

| Panel # | Título | Tipo | Expresión / Fuente | Propósito |
|---------|--------|------|--------------------|-----------|
| **Panel 1** | `Physical CPU Thermal Noise Celsius` | Gauge | `sentinel_cpu_temperature_celsius` | Mide la temperatura real de la CPU inyectada como ruido térmico a la Lattice. |
| **Panel 2** | `LiquidLattice Memory 3x3 Retention Score EXP-009` | Gauge | `sentinel_liquid_lattice_retention_score` | Mide la retención de estado sexagesimal S60 (retención objetivo $\ge 0.72$). |
| **Panel 3** | `Total Raw Energy in Lattice` | Stat | `sentinel_lattice_total_energy` | Energía total acoplada en la matriz de memoria resonante. |
| **Panel 4** | `Live Ring-0 eBPF Interceptions & Systemd Logs` | Logs Panel | `{job="sentinel_file_logs"}` (Loki) | Visualizador de logs e intercepciones eBPF en vivo sincronizado con las pruebas de estrés. |
