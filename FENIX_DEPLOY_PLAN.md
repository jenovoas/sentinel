# 🚀 FENIX DEPLOY PLAN — Stack Unificado Sentinel+ME-60OS

**Última actualización**: 2026-03-18  
**Estado**: FASE AUDITORÍA — depurando configs antes de levantar nada

---

## MISIÓN

Unificar Sentinel + ME-60OS en un producto único y desplegarlo en **fenix**  
(Rocky Linux 9, GCloud, Podman rootless, CPU-only, sin GPU).  
Servidor crítico único. Failover se implementa DESPUÉS de tener el stack estable.

**REGLA**: Depurar TODOS los configs antes de `podman-compose up`. Levantar servicio por servicio.

---

## BUGS ENCONTRADOS EN AUDITORÍA INICIAL

### BUG-01 — `docker/postgres/init.sql` línea 78: password dev hardcodeada

```sql
CREATE ROLE sentinel_app LOGIN PASSWORD 'sentinel_password';  -- ← DEV PASSWORD
```

**Fix**: Usar `${POSTGRES_PASSWORD}` o eliminar el rol (sentinel_user del .env ya tiene permisos)

### BUG-02 — `backend/Dockerfile.worker`: dependencias WiFi de laptop

```dockerfile
RUN apt-get install -y network-manager wireless-tools  -- ← INÚTIL en GCloud
```

**Fix**: Eliminar esas dos líneas

### BUG-03 — `docker-compose.fenix.yml`: `celery_worker` = backend Python legacy

El worker Celery usa FastAPI/Python. **Decisión pendiente**: ¿permanece en stack de fenix o se reemplaza con worker Rust?

### BUG-04 — `docker-compose.fenix.yml`: `cortex` tiene labels Traefik pero NO expone HTTP

`sentinel-cortex/main.rs` es daemon puro (loop 17s/68s). No hay servidor en puerto 8000.  
Traefik y Prometheus apuntan a un endpoint que no existe.  
**Decisión pendiente**: ¿añadir HTTP mínimo (Axum) al cortex, o limpiar las labels?

### BUG-05 — `prometheus.fenix.yml`: job `sentinel-cortex` → `cortex:8000` no existe

Derivado de BUG-04. Prometheus fallará al conectar.

### BUG-06 — `prometheus.fenix.yml`: scraping `node-exporter:9100`, `postgres-exporter:9187`, `redis-exporter:9121`

Estos servicios NO están en `docker-compose.fenix.yml`. Prometheus tendrá targets caídos.  
**Fix**: Añadir los exporters al compose O eliminar sus jobs del prometheus.fenix.yml

### BUG-07 — `.env`: variable `GF_ADMIN_PASSWORD` vs compose usa `GF_ADMIN_PASSWORD`

Verificar que los nombres coinciden exactamente. ✅ Parece OK pero confirmar al levantar Grafana.

---

## ORDEN DE REPARACIÓN

### Paso 0 — Decisiones de arquitectura (BLOQUEANTES) — PENDIENTE USUARIO

- [x] BUG-03: ¿Celery worker Python permanece o se elimina? -> Eliminado
- [x] BUG-04: ¿cortex expone HTTP (Axum /health + /metrics) o limpiamos labels Traefik? -> Limpiado, e implementado contenedor Nginx ultraligero

### Paso 1 — Fixes seguros (sin decisión)

- [x] BUG-01: fix `init.sql` (password dev hardcodeada)
- [x] BUG-02: fix `Dockerfile.worker` (eliminar wireless-tools/network-manager)
- [x] BUG-06: añadir exporters al compose o limpiar prometheus.fenix.yml

### Paso 2 — Verificar pre-condiciones en fenix

- [x] `podman network ls` → confirmar red `proxy` existe (creada)
- [x] `podman volume ls` → confirmar volúmenes `postgres_data`, `redis_data`, `prometheus_data`, `grafana_data` (creados)

### Paso 3 — Deploy iterativo (uno por uno)

1. [x] `podman-compose -f docker-compose.fenix.yml up -d postgres` → verificar healthcheck (init.sql corregido y aplicado)
2. [x] `podman-compose -f docker-compose.fenix.yml up -d redis` → `redis-cli PING` (redis limpio funcionando)
3. [x] `podman-compose -f docker-compose.fenix.yml up -d cortex` → logs (binario nativo Inyectado exitosamente, loop 17s activo)
4. [x] `podman-compose -f docker-compose.fenix.yml up -d prometheus grafana web-server node-exporter postgres-exporter redis-exporter` → logs (stack completo levantado)

---

## REGLAS DE OPERACIÓN

- **NO levantar nada** hasta completar Paso 0 y Paso 1
- **Backup obligatorio** antes de cualquier cambio: `.backups/<archivo>.backup.YYYYMMDD_HHMMSS.bak`
- **Podman, no Docker** — Rocky Linux 9, rootless
- **NO floats** en código Rust/Python central (Protocolo YATRA)
