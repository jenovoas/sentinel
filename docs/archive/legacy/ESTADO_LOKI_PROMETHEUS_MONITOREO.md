# 🔍 Estado Actual y Diagnóstico de Loki y Prometheus en Fan (`10.88.0.1`)

> **Servidor:** Fan (`10.88.0.1`)  
> **Loki API:** `http://10.88.0.1:3100`  
> **Loki Version:** 3.4.3 (Contenedor Podman `sentinel-loki`)  
> **Tenant ID (Header):** `X-Scope-OrgID: sentinel`  
> **Promtail:** Ingestador activo en Podman (`sentinel_systemd` + `sentinel_file_logs`)  
> **Fecha:** 29 de Julio, 2026

---

## 🔬 Diagnóstico Técnico del Estado de Loki: 🟢 100% OPERATIVO

Ejecutamos consultas API en vivo hacia Loki en Fan para verificar la presencia de streams e índices:

1. **Salud de Loki (`GET /ready`)**: `ready` (OK).
2. **Jobs Activos Ingeridos (`GET /loki/api/v1/label/job/values`)**:
   - `sentinel_file_logs` (Logs de trazas eBPF y archivos `/var/log/sentinel/*.log`).
   - `sentinel_systemd` (Logs directos del Journald de Linux).
3. **Unidades Systemd Ingeridas (`GET /loki/api/v1/label/unit/values`)**:
   - `sentinel-cortex.service`
   - `sentinel-gamma-watchdog.service`
   - `sentinel-hex-daemon.service`
   - `sentinel-qhc-agent.service`
   - `sentinel-vid-agent.service`
   - `sentinel-ebpf-forwarder.service`
   - `sentinel-pai-neural.service`

---

## 📊 ¿Cómo Graficar y Analizar los Logs en Grafana?

En Grafana (`http://10.88.0.1:3001`), Loki está registrado con el **OrgID / Header**: `X-Scope-OrgID: sentinel`.

### Consultas LogQL Recomendadas para Pruebas:
- **Trazas eBPF de Syscalls**:
  ```logql
  {job="sentinel_file_logs", filename="/var/log/sentinel/ebpf_trace.log"}
  ```
- **Logs de Errores o Anomalías en Servicios Sentinel**:
  ```logql
  {job="sentinel_systemd", unit=~"sentinel.*"} |= "ERROR"
  ```
- **Conteo de Eventos eBPF por Segundo (Tasa de Intercepción)**:
  ```logql
  rate({job="sentinel_file_logs", filename="/var/log/sentinel/ebpf_trace.log"}[1m])
  ```

