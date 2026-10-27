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
- `/etc/conf.d/sentinel-cortex`: `SENTINEL_JWT_SECRET` debe ser idéntica a
  `SECRET_KEY` de `/opt/sentinel/.env`; `SENTINEL_JWT_ISSUER=sentinel-auth`,
  `SENTINEL_JWT_AUDIENCE=sentinel-cortex` y
  `SENTINEL_WS_ALLOWED_ORIGINS=https://sentinel.pinguinoseguro.cl`. La clave debe
  ser aleatoria y tener al menos 32 bytes. El Origin debe ser exacto, sin
  comodines. Nunca guardar secretos en Git.
- `/opt/sentinel/.env`: `POSTGRES_PASSWORD`, `REDIS_PASSWORD`, `GF_ADMIN_*`,
  `SECRET_KEY`. Deriva con el volumen PG = auth FATAL (ver TODO 2026-10-21).

## Migraciones de identidad

La app de identidad no migra la base de datos al arrancar. Tras revisar y
respaldar la base destino, aplicar explícitamente el baseline/adopción segura:

```sh
docker compose -p sentinel-alpine -f docker-compose.fenix.yml \\
  --profile db-migrate run --rm sentinel-auth-migrate
```

El paso falla si el esquema no coincide con un estado conocido. No ejecutarlo
contra la base Fénix sin validar primero el respaldo y la migración.

## Primer superusuario (solo si no existe)

Después de migrar y con `sentinel-auth` en ejecución, el primer `is_superuser`
se aprovisiona fuera de línea; no hay registro público ni credenciales
predeterminadas. El comando solicita slug, identidad y contraseña de forma
interactiva, y aborta si ya existe un superusuario:

```sh
docker compose -p sentinel-alpine -f docker-compose.fenix.yml \\
  exec -it sentinel-auth python -m app.bootstrap_admin
```

Usarlo solo contra una base respaldada y revisada. No ejecuté este comando ni
ninguna migración contra la base real de Fénix.

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
