# 📊 Configuración de Persistencia y Monitoreo Continuo del Verificador (`sentinel-verifier`)
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor Target:** Fan (`10.88.0.1`)  
> **Servicio Systemd:** `sentinel-verifier.service` (`User=root`)  
> **Archivo Log de Persistencia:** `/var/log/sentinel/sentinel_verifier.log`  
> **Promtail / Loki Job:** `sentinel_file_logs`  
> **Grafana Master URL:** `http://10.88.0.1:3001/d/a5s799/securepenguin-e28094-monitoreo`  
> **Fecha:** 29 de Julio, 2026

---

## 🔬 1. Servicio Systemd y Guardado de Logs en Tiempo Real

Configuramos y habilitamos el daemon de sistema `sentinel-verifier.service` ejecutándose como `root` con la bandera `--watch 15 --json`:

```ini
[Unit]
Description=Sentinel System Invariant Verifier Service
After=multi-user.target sentinel-cortex.service

[Service]
Type=simple
User=root
ExecStart=/home/jnovoas/.local/bin/sentinel-verifier --watch 15 --json
StandardOutput=append:/var/log/sentinel/sentinel_verifier.log
StandardError=append:/var/log/sentinel/sentinel_verifier.err
Restart=always
RestartSec=5
```

### Muestra de Log Persistido (`/var/log/sentinel/sentinel_verifier.log`):
```json
{"timestamp_unix":1785353785,"host":"fan","total":10,"ok":9,"fail":1,"skip":0,"results":[{"id":"lsm_progs","status":"OK"},{"id":"cortex_events_ringbuf","status":"OK"},{"id":"bpf_pins","status":"OK"},{"id":"cortex_segv","status":"FAIL"},{"id":"watchdog_alive","status":"OK"},{"id":"sentinel_status_http","status":"OK"},{"id":"health_http","status":"OK"},{"id":"sentinel_services","status":"OK"},{"id":"ebpf_trace_log","status":"OK"},{"id":"lattice_metrics","status":"OK"}]}
```

---

## 📈 2. Integración al Master Dashboard de Grafana (Versión 7)

Actualizamos el Dashboard Principal de Grafana (`http://10.88.0.1:3001`):

- **Panel 12 — `Automated Invariant Verifier Logs (sentinel-verifier JSON Stream)`**:
  Visualizador en vivo alimentado por Loki que muestra cada reporte de 10 invariantes ejecutado automáticamente cada 15 segundos.
