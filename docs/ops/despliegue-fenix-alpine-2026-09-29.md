# Despliegue Sentinel en Fenix Alpine — 2026-09-29

Estado actual: **nodo único**. Fenix concentra DNS, web, correo y Sentinel
hasta terminar este servidor e instalar el segundo. No contratar datacenter
ni levantar un segundo nodo mientras tanto. Kingu y WireGuard no forman
parte de este arranque; el segundo servidor se decide cuando Fenix esté listo.

Rama: `alpine_fenix`. Solo esa. Prohibido crear otra. Prohibido usar `main`.

## Nodo

| Campo | Valor |
|---|---|
| Host | `fenix` |
| Sistema | Alpine Linux, kernel `6.18.40-0-virt` |
| IP pública | `172.233.24.102` |
| Init | OpenRC |
| Contenedores | Docker Compose, proyecto `sentinel-alpine` |
| TLS | Nginx del host, Let's Encrypt |
| Checkout operativo | `/opt/sentinel` |

## Arranque

Daemons nativos, scripts en `openrc/`:

- `sentinel-ebpf-load` carga LSM, XDP y TC.
- `sentinel-cortex` escucha en `127.0.0.1:8000`.
- `sentinel-verifier`, `sentinel-qhc-agent`, `sentinel-ebpf-forwarder`.
- `sentinel-pai-neural`, `sentinel-hex-daemon`, `sentinel-adm-agent`, `sentinel-vid-agent`.
- `sentinel-audit-watchdog`, `sentinel-process-memory`.
- `sentinel-stack` levanta Compose desde `/opt/sentinel`.

```bash
rc-service sentinel-stack start
rc-service sentinel-cortex status
docker compose -p sentinel-alpine -f docker-compose.fenix.yml ps
```

Compose (`docker-compose.fenix.yml`): postgres, redis, frontend, prometheus,
node-exporter, postgres-exporter, redis-exporter, grafana, loki, promtail,
alertmanager, n8n, neural-guard. Cortex no va en el contenedor: corre nativo
y Nginx hace de proxy.

## Qué cambió respecto de systemd

- `journalctl` / `systemctl` del verifier pasaron a OpenRC y archivos de log.
- Promtail lee syslog, no `systemd-journal`.
- PyO3 es opcional. El SHM POSIX no depende de Python.
- eBPF se carga con `bpftool`. Scripts: `ebpf/install_ebpf_deps_alpine.sh`,
  `ebpf/populate_whitelist_alpine.sh`.
- El tick térmico usa una sola amplitud PAI-60 (`thermal_amplitude`). No hay
  rama `inject(i64)` ni `SENTINEL_PAI_CONVERT`.

## Límites conocidos al cierre del 2026-09-30

- SOMA compila y no tiene servicio OpenRC. No entra en el arranque.
- `neural-guard` corre en Compose. El motor de correlación sigue parcial.
- QHC expone `/run/soma/qhc.sock`. Falta caracterizar el damping del cristal
  en la ruta viva de Cortex: el default sigue siendo `1/120`.
- La fase del oscilador no se envuelve módulo 360°.
