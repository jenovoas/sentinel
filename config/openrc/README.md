# OpenRC de fénix (configuración del host, versionada)

Mononodo Alpine/OpenRC. Esta carpeta espeja `/etc` del host para
reproducibilidad. Fuente de verdad del ESTADO: `TODO.md` + `rc-status`.

## Contenido
- `init.d/sentinel-*`: 17 servicios (copia de `/etc/init.d`). Sin secretos
  (verificado con grep). Servicios nuevos de esta serie: `sentinel-gamma-watchdog`,
  `sentinel-ringbuf-forwarder` (con `start_pre` que re-pinea mapas eBPF).
- `sysctl.d/99-docker-forward.conf`: `net.ipv4.ip_forward=1` (Docker lo exige).

## NO versionado (secretos del host)
- `/etc/conf.d/sentinel-*`: credenciales (`DATABASE_URL` con password de
  `pinguino_orchestrator`, `ORCHESTRATOR_SERVICE_SECRET`, etc.). Permisos
  0600/0640. Respaldar fuera del repo.
- `/opt/sentinel/.env`: `POSTGRES_PASSWORD`, `REDIS_PASSWORD`, `GF_ADMIN_*`,
  `SECRET_KEY`. Deriva con el volumen PG = auth FATAL (ver TODO 2026-10-21).

## Aplicar en host nuevo
```sh
sudo cp config/openrc/init.d/sentinel-* /etc/init.d/
sudo chmod +x /etc/init.d/sentinel-*
sudo cp config/openrc/sysctl.d/*.conf /etc/sysctl.d/
sudo sysctl --system
for s in docker sentinel-stack sentinel-ebpf-load sentinel-ringbuf-forwarder \
         sentinel-gamma-watchdog sentinel-cortex sentinel-qhc-agent \
         sentinel-verifier sentinel-audit-watchdog sentinel-process-memory \
         sentinel-deployment-orchestrator; do
    sudo rc-update add $s default
done
# Crear /etc/conf.d/sentinel-* y /opt/sentinel/.env DESDE el respaldo de secretos.
```
