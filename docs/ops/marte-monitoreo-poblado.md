# T7. Poblado de monitoreo y métricas en Marte — `agente:obs`

> Prerrequisito blando: T0 (AD único). Independiente de T1–T4 salvo §4 (tenant views).
> Estado base verificado 2026-10-30: 6 contenedores `Up` en marte (alloy, grafana, prometheus, mimir, loki, node-exporter). Disco 38%, RAM 9G. Prometheus SIN puerto publicado (solo red `sentinel_marte_observability`) — acceso vía Alloy o exec, no directo.

## 1. Hallazgos previos (no repetir diagnóstico)

- Prometheus TSDB compacta y hace checkpoint OK (logs 21:00 UTC).
- Grafana `Up 16h`, `ALLOW_SIGN_UP=false`, anónimo deshabilitado ✅. **Fallo**: `GF_SECURITY_ADMIN_PASSWORD` en texto claro visible en `docker inspect` — rotar a fichero `__FILE` o secrets en este task.
- :3000 y :3100 escuchan en `10.88.0.6` (solo WG ✅, nada público).
- Exporters en fenix: verificar qué escucha (`:9100` node, `:9187` postgres, `:9182`? redis, `:5678` n8n metrics). Alloy ya corre en marte como colector.

## 2. Poblado por capas (orden)

1. **Infra base**: node-exporter en fenix, kingu, hercules, ocean (si falta alguno) → scrape Prometheus vía Alloy o directo por WG. Etiqueta `node=` + `rol=` (backend/frontend/dns/obs).
2. **Servicios Sentinel**: FastAPI `/metrics`, Cortex `/metrics`, postgres-exporter, redis-exporter, n8n metricas. Jobs separados por servicio, `tenant="platform"` por defecto.
3. **Logs**: Promtail en cada nodo → Loki marte, etiquetas `node`, `service`, luego `tenant` (§4). Retención 90d (diseño vault `TELEMETRIA_Y_RESILIENCIA`).
4. **Tenant views**: cuando T1 exista (OUs + grupos SP-*): carpeta Grafana por tenant, datasource Loki/Prometheus filtrado por etiqueta `tenant`, rol Viewer. Sin tenant = sin carpeta.
5. **Alertas**: Alertmanager o Mimir ruler: caídas (up==0), disco >85%, Cortex `QHC=false` / dead-man-switch, cert TLS <15d. Ruta: n8n → WhatsApp/Telegram (capa 5 AIOps, vault `ARQUITECTURA_SEGURIDAD_SENTINEL`).

## 3. Prohibiciones

- Nada de monitoreo expuesto a internet: todo por `10.88.0.0/24`. Grafana embebido en portal por BFF (nunca iframe público directo).
- Secretos (admin grafana, tokens) en ficheros `0600` o secrets de compose, jamás en `Env` plano.
- `sudo -n` en remoto; marte por puerto 4222; un cambio = commit + vault.

## 4. Criterios de aceptación

- Dashboard "Plataforma": 4 nodos + servicios core con `up==1`, latencia WG, disco/RAM.
- Dashboard por tenant piloto: solo sus métricas/logs (test: usuario tenant-A no ve datos de tenant-B).
- Alerta de prueba extremo a extremo (p. ej. detener exporter piloto → alerta en n8n).
- Password admin grafana rotado y fuera de `docker inspect`.
