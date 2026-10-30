---
title: Auditoría del despliegue Sentinel multi-nodo
fecha: 2026-10-30
estado: aplicación_operativa_con_brecha_qhc
alcance: Fenix, Kingu, publicación Sentinel y n8n
---

# Auditoría del despliegue Sentinel multi-nodo — 2026-10-30

## Dictamen

La aplicación web distribuida Kingu↔Fenix está sirviendo por HTTPS y sus servicios principales están saludables. La auditoría encontró y corrigió una omisión real: Fenix ejecutaba Cortex `da843a84`, anterior al commit que integra `CrystalRuntime`. Se publicó la imagen `sentinel-cortex:e096eaa9` y se recreó únicamente Cortex.

El despliegue completo de Cortex **sigue incompleto**: no existe el socket QHC `/run/soma/qhc.sock`; los logs muestran QHC desconectado y el *dead man switch* enclava el scheduler después de 30 segundos. El proceso continúa `healthy`, por lo que el healthcheck por sí solo oculta esta brecha. No se instaló ni inició QHC, y no se activó Guardian/eBPF.

## Evidencia de estado

Verificación directa por SSH a Fenix y Kingu entre 04:08 y 04:21 UTC:

- Repositorio Fenix: rama `main`, SHA `e096eaa9`, árbol limpio y sincronizado con `origin/main`.
- Kingu: `sentinel-frontend.service` activo/habilitado; release `/opt/sentinel/frontend/releases/96043b54`; listener de Node en `127.0.0.1:3001`. No hay cambios en frontend entre `96043b54` y el checkout actual.
- HTTPS público: Sentinel `/login` 200, certificado Let's Encrypt con SAN correcto y validación TLS normal exitosa; HTTP redirige 301 a HTTPS. n8n `/healthz` 200 y su `showSetupOnFirstLoad` es `false`.
- Fenix: FastAPI `sentinel-backend:253a3a47`, PostgreSQL, Redis, Cortex y n8n reportan `healthy`. Alembic está en `20261029_user_timestamp_defaults (head)`.
- Desde Kingu: FastAPI `/api/v1/health` 200, Cortex `/health` 200, n8n `/healthz` 200 y `/api/auth/me` sin sesión 401. WebSocket de Cortex sin bearer 401. No se usaron credenciales humanas; login autenticado y handshake WebSocket autenticado siguen sin verificación independiente.
- Firewall: `SENTINEL-DOCKER-USER` permite TCP 8000, 8001 y 5678 de Fenix solo desde `10.88.0.2` por `wg0`, y descarta esos puertos desde otros orígenes. Las sondas desde Hercules y Ocean expiraron; desde Kingu a la IP pública de Fenix, 8000/8001/5432/6379/5678 resultaron cerrados o filtrados.
- Guardian/eBPF Sentinel: `sentinel-ebpf.service` está inactivo/no instalado; no se encontraron programas ni mapas Guardian/Sentinel en bpffs. No se adjuntó ningún programa ni se activó enforcement.
- PostgreSQL de Sentinel tiene `NetworkSettings.Ports={}`. El listener `10.88.0.1:5432` pertenece a `laespiguita-db`, no al contenedor Sentinel. Redis Sentinel tampoco publica puerto de host.
- `nginx -t` es exitoso; emite una advertencia previa de valor TLSv1.3 duplicado en el vhost `pinguinoseguro`, que no se modificó. La respuesta Sentinel no presenta HSTS, CSP, X-Frame-Options, X-Content-Type-Options ni Referrer-Policy; queda como hardening pendiente.

## Corrección aplicada a Cortex

- Imagen anterior: `sentinel-cortex:da843a84` (conservada para rollback).
- Código nuevo: el commit `a15328d6` integra `CrystalRuntime`, sus inyecciones de seguridad/observabilidad y el endpoint autenticado `/api/v1/crystal_runtime/status`.
- Se construyó en Fenix desde el checkout limpio `e096eaa9`: `./scripts/build-sentinel-cortex-image.sh sentinel-cortex:e096eaa9`.
- Docker image ID: `sha256:ad1eee42eee4038764254fb1d79aa6a6c4e5f9911f6d1ba5368e114b78341071`.
- Se fijó `SENTINEL_CORTEX_IMAGE=sentinel-cortex:e096eaa9` en `/etc/sentinel/backend.env`; sus permisos se confirmaron `root:docker 0640`, sin mostrar secretos.
- Se añadió el volumen persistente `sentinel_crystal_state` montado en `/var/lib/sentinel/crystal-state`, con UID/GID del usuario del contenedor. A las 04:20:49 UTC contenía `crystal-runtime-67951.json.gz` (399.667 bytes).
- Compose valida con `config --quiet`. Se ejecutó solo `docker compose ... up -d --no-build --no-deps cortex`; Postgres, Redis, FastAPI, n8n, Kingu, Nginx, DNS y firewall no se reiniciaron ni cambiaron.
- El contenedor Cortex quedó `healthy`, con `SENTINEL_CRYSTAL_RUNTIME=1`; ambos buffers SHM (`me60os_lattice` y `me60os_lattice_b`) tienen 13.046.592 bytes y el ring de semillas 32.832 bytes. El endpoint de estado responde 401 sin sesión, lo que confirma middleware de autenticación, pero sus métricas internas requieren consulta autenticada.
- El build completó, con cuatro warnings de constantes DTC SHM no usadas (`DTC_CLOCK_SHM`, `_BYTES`, `_MAGIC`, `_VERSION`). No se encontró lector/escritor de `me60os_dtc_clock` en `me-60os-core` o `sentinel-cortex`; no se afirma que el tick DTC se comparta entre procesos.

## Brecha QHC y efecto real

- `sentinel-qhc-agent.service` no está instalado (systemd devuelve `not-found`); el binario compilado existe en el checkout, pero no está en `/home/jnovoas/.local/bin/qhc_agent`. `/run/soma` existe vacío y `/run/soma/qhc.sock` está ausente.
- Logs de Cortex: `qhc.connected=false`, `stale=true`, error `No such file or directory`; los *pulse checks* de ticks 17, 34, 51, 68 y 85 reportan `Valid=false`, `Coherence=false`, `QHC=false`.
- A los 30 segundos el `QuantumScheduler` registra `DEAD MAN SWITCH ACTIVATED - PILOT ABSENT`. El código enclava `is_emergency_shutdown=true` y deja de procesar ticks/tareas del scheduler; **no termina el proceso Cortex**, que por eso sigue pasando el healthcheck.
- El cliente QHC actual registra un heartbeat de piloto cuando obtiene snapshot QHC. Iniciar ese agente sin validar si ese heartbeat puede sustituir la presencia del operador podría falsear el criterio de seguridad; no se hizo. El alcance de QHC/MycNet/daemons requiere decisión operativa antes de activar esa señal.

## Cambios en Git

- `1651a877 docs(deploy): define standard multi-node procedure`
- `e096eaa9 fix(deploy): persist Cortex crystal runtime state`
- Procedimiento: [`PROCEDIMIENTO_DESPLIEGUE_MULTINODO.md`](PROCEDIMIENTO_DESPLIEGUE_MULTINODO.md)

## Rollback del único servicio cambiado

La imagen previa sigue disponible. Si la nueva versión presenta una regresión, cambiar solo `SENTINEL_CORTEX_IMAGE` en `/etc/sentinel/backend.env` a `sentinel-cortex:da843a84` y recrear `cortex` con `--no-deps`. Conservar `sentinel_crystal_state`; no ejecutar `down`, eliminar volúmenes ni revertir DB. El tag `sentinel-cortex:preflight-20261029b` también permanece local.

## Pendientes antes de aceptar el despliegue integral

1. Definir si el objetivo es la aplicación Kingu↔Fenix o si incluye QHC/MycNet/daemons. Si incluye QHC, decidir qué fuente válida satisface el dead man switch y validar QHC en una sesión autorizada; no simular heartbeat.
2. Validar `/api/v1/crystal_runtime/status` y `/api/v1/qhc/status` mediante sesión real, además de login y WebSocket autenticados, sin compartir credenciales por chat/log.
3. Decidir si el contrato multi-nodo requiere publicar el tick DTC por SHM; hoy los símbolos están declarados pero no implementados.
4. Definir si se corrigen los headers TLS de Sentinel. La advertencia TLS duplicada pertenece a otro vhost y requiere cambio separado.
5. La comprobación de backups/restauración no formó parte de este cambio de Cortex; validarla antes de una futura migración o cambio de datos.

**Estado operativo registrado:** front y APIs accesibles; contenedores core saludables; Cortex nuevo y persistente desplegado; autenticación humana y QHC no verificados/pendientes; no se declara aún «despliegue integral Sentinel completado».
