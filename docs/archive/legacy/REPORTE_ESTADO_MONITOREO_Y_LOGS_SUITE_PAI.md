# 📊 Reporte de Monitoreo y Guardado de Logs de la Suite PAI / ME-60OS
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor Target:** Fan (`10.88.0.1`)  
> **Servicios Auditados:**  
>   - `sentinel-pai-neural.service` (`pai_neural_daemon`)  
>   - `sentinel-hex-daemon.service` (`hex_daemon`)  
>   - `sentinel-qhc-agent.service` (`qhc_agent`)  
>   - `sentinel-vid-agent.service` (`vid_agent`)  
>   - `sentinel-adm-agent.service` (`adm_agent`)  
> **Ingestor de Logs:** Promtail / Loki 3.4 (Job `sentinel_systemd_journal`)  
> **Dashboard:** Grafana Master v7 (`http://10.88.0.1:3001`)  
> **Fecha:** 29 de Julio, 2026

---

## 📊 1. Guardado de Logs Persistentes en Disco y Systemd Journal

Todos los servicios de la suite PAI se ejecutan bajo `systemd` como daemons continuos. Sus salidas `stdout` y `stderr` son capturadas por el journald de Linux y persisten en disco:

- **PAI-Neural Daemon**:
  `sentinel-pai-neural.service` $\rightarrow$ Logs de picos SNN LIF y conexión eBPF Ring-0.
- **Hex Controller Daemon**:
  `sentinel-hex-daemon.service` $\rightarrow$ Logs de ticks de estabilización Salto 17 y rotación de clave dinámicas.
- **QHC Agent**:
  `sentinel-qhc-agent.service` $\rightarrow$ Pulso YHWH $10;5,6,5$ constante.

---

## 📈 2. Monitoreo e Ingesta en Grafana (Loki)

Promtail lee el journald de sistema en Fan (`/var/log/journal`) y transmite las trazas a Loki 3.4.

En Grafana (`http://10.88.0.1:3001`):
- Los logs se pueden consultar en vivo mediante la query LogQL:
  `{syslog_identifier=~"pai_neural_daemon|hex_daemon|qhc_agent|vid_agent"}`
