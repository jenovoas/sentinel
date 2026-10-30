---
title: Auditoría del despliegue Sentinel multi-nodo
fecha: 2026-10-30
estado: backend_fenix_operativo_qhc_validado_marte_pendiente
alcance: backend Fenix, frontend Kingu, QHC compartido y preparación de seguridad/monitoreo Marte
---

# Auditoría del despliegue Sentinel multi-nodo — 2026-10-30

## Dictamen

La aplicación web distribuida Kingu↔Fenix está sirviendo por HTTPS y sus servicios principales están saludables. La auditoría encontró y corrigió una omisión real: Fenix ejecutaba Cortex `da843a84`, anterior al commit que integra `CrystalRuntime`. Se publicó la imagen `sentinel-cortex:e096eaa9` y se recreó únicamente Cortex.

SOMA (`soma_orchestrator`/`soma_worker`) queda fuera: es orquestación de agentes y no se usará todavía. QHC sí es una dependencia compartida requerida por Sentinel y MyCNet; es un proceso independiente aunque su IPC viva bajo `/run/soma`.

QHC fue instalado y validado en Fenix durante esta sesión. El backend de aplicación sigue operativo; la capa distribuida de seguridad/monitoreo en Marte todavía no se desplegó. No se declara completa la red hasta que se resuelva acceso a Marte, se verifique su ruta a Fenix y se acepte la recepción remota de eventos.

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

- En la captura original (04:08–04:21 UTC), `sentinel-qhc-agent.service` no estaba instalado (systemd devolvía `not-found`); `/run/soma/qhc.sock` estaba ausente.
- Logs de Cortex: `qhc.connected=false`, `stale=true`, error `No such file or directory`; los *pulse checks* de ticks 17, 34, 51, 68 y 85 reportan `Valid=false`, `Coherence=false`, `QHC=false`.
- A los 30 segundos el `QuantumScheduler` registra `DEAD MAN SWITCH ACTIVATED - PILOT ABSENT`. El código enclava `is_emergency_shutdown=true` y deja de procesar ticks/tareas del scheduler; **no termina el proceso Cortex**, que por eso sigue pasando el healthcheck.
- A las 04:38 UTC se instaló el binario release compilado desde el checkout `main` y la unidad `sentinel-qhc-agent.service`; quedó `enabled` y `active` bajo `jnovoas`.
- `/run/soma` quedó `jnovoas:linuxuser`, modo `2770`; socket `qhc.sock` modo `0660`, grupo GID 1000. `SNAPSHOT` fue consultado exitosamente como UID/GID 1000 (Cortex) y como `jnovoas` (owner del socket). `mycnetd.service` está activo bajo `jnovoas`, así que sus permisos de proceso permiten abrir el socket; esto no verifica que el código de MyCNet lo consuma. El primer intento falló porque `ExecStartPre` no tenía privilegio para cambiar el directorio; se corrigió con prefijo systemd `+` solo en ese paso.
- A las 04:39:10 UTC los logs de Cortex registraron `PULSE CHECK (T=17): ... QHC=true`. La autenticación humana del endpoint `/api/v1/qhc/status` no se probó; una solicitud sin bearer devuelve 401. La ingestión de snapshot y su visibilidad interna sí quedaron verificadas por IPC y log.
- La implementación actual hace que un snapshot QHC reciente invoque `record_pilot_heartbeat()` en `BioResonator`. Por tanto el agente QHC también mantiene vigente el reloj llamado “pilot”; registrar este acoplamiento para revisión del contrato, sin equipararlo a una presencia humana.

## Mapa de módulos y despliegue distribuido

| Módulo | Estado comprobado / ubicación | Brecha para aceptación integral |
|---|---|---|
| FastAPI, PostgreSQL, Redis | Fenix; contenedores `healthy`, Alembic en head. | Sesiones/WebSocket autenticados siguen sin validación independiente. |
| Cortex Rust | Fenix; imagen `sentinel-cortex:e096eaa9`, `/health` saludable. | Health no sustituye pruebas de cada runtime/contrato. |
| QHC | Fenix; unidad activa, IPC `SNAPSHOT` funciona para UID/GID 1000 y `jnovoas`; `mycnetd.service` activo como `jnovoas`; Cortex reporta `QHC=true`. | Permiso IPC de ambos procesos comprobado; falta verificar en una auditoría de MyCNet que el daemon consume el socket. |
| CrystalRuntime, matriz/cristales, memorias SHM | Fenix; `me60os_lattice`, `me60os_lattice_b`, ring de semillas y checkpoint persistente presentes. | Endpoint autenticado y contadores de runtime requieren sesión aprobada para aceptación completa. |
| PAI-60 | Código integrado en el camino de inyección Cortex. | Aceptación requiere trazas del camino real; benchmarks no acreditan ejecución del runtime. |
| Cristal isocrónico DTC | Runtime/código contiene frecuencia y constantes de IPC. | No se halló publicación efectiva de `me60os_dtc_clock`; symbols/constantes no son un contrato SHM activo. |
| FPU | Aparece como referencia en benchmarks comparativos, no como daemon o servicio desplegable. | Clasificar por ruta de cómputo; no reportarla como módulo autónomo activo. |
| Dual Lane | Hay implementación Python/Rust, WAL y pruebas/benchmarks. | No se comprobó una ruta de producción conectando eventos de Marte a ambas lanes con evidencia y observabilidad. |
| eBPF/Guardian | El bridge está en el código Cortex; no se encontraron programas/mapas Sentinel activos en Fenix. | Capa local Marte pendiente. Preflight obligatorio de whitelist/rutas críticas y recuperación fuera de banda; enforcement requiere autorización separada. |
| Frontend | Kingu sirve Next.js; handlers BFF en `frontend/src/lib/server/*` mantienen sesión/CSRF y reenvían a Fenix. El visualizador de lattice consume `/api/v1/lattice/hologram` por el BFF. | Frontend pequeño frente al backend; validar estado funcional autenticado y errores de upstream, sin exponer APIs al navegador. |
| Backend de observabilidad/seguridad en Marte → Sentinel central Fenix | Jaime asignó Grafana, Mimir, Prometheus, TruthSync y Loki a Marte (`10.88.0.6`), además de la capa Guardian/eBPF. Los módulos observan/consultan Sentinel en Fenix (`10.88.0.1`) por WireGuard. | Ubicación objetivo confirmada por el usuario; todavía no instalada ni verificada en Marte. SSH desde esta ruta devolvió `No route to host`, aunque notas previas registran acceso directo de Jaime por SSH 4222 y Firewalld. |

### Perfil y estado de Marte

- La memoria operativa registra Marte (`10.88.0.6`) con Debian 13 amd64, kernel `7.3.0-ifenix` activo y SSH administrativo en TCP 4222, sin listener en 22 en la verificación del 2026-10-30. También registra la instalación de Firewalld 2.3.1 como parte de una intervención en Fenix/Marte.
- En la continuación de esa auditoría se dejó explícito que el estado de firewall/puertos de Marte no se pudo volver a verificar directamente desde esa ruta; Jaime confirmó que él estaba conectado a Marte y que el host usa Firewalld. Para esta tarea Sentinel no se inspeccionaron en vivo `firewalld`, `wg0`, whitelist, mapas/programas BPF ni servicios de seguridad en Marte.
- Por ello, el estado de Sentinel Guardian/eBPF y del forwarder en Marte es **no verificado**; no se afirma que estén instalados, activos o ausentes. La capa Sentinel de Marte no se aplicó en esta sesión.
- El alias local `marte` resuelve a `10.88.0.6:4222`, pero el SSH ejecutado desde esta sesión recibió `No route to host`. Es un límite de esta ruta de ejecución, no evidencia de que Jaime carezca de acceso ni de que el nodo esté apagado.
- El backend Fenix ya incluye `POST /api/v1/cortex/events` con cuerpo `event_type`, `source`, `data`, y cabecera `X-Sentinel-Token`. Se propone como destino de eventos remotos, sujeto a probar compatibilidad del evento eBPF, autenticación, respuesta/persistencia y análisis en DB. El secreto no se distribuyó.
- `sentinel-ebpf-forwarder.service` actual ejecuta `bpftool prog tracelog` y escribe localmente; por sí solo no reenvía eventos a Fenix. Hace falta configurar o implementar un forwarder remoto verificable. También se debe comprobar en vivo el firewall actual de Fenix: la política observada en la auditoría previa limitaba los puertos API a Kingu, pero luego hubo intervención de Firewalld; no agregar reglas hasta revisar su estado efectivo.

La asignación explícita queda así: **Marte alojará Grafana, Mimir, Prometheus, TruthSync y Loki, además del sensor Guardian/eBPF; Fenix (`10.88.0.1`) seguirá siendo el backend central de Sentinel que esos módulos observan/consultan por WireGuard.** Kingu aloja el frontend.

### Stack de Marte y estado real en el repositorio/runtime

| Componente asignado a Marte | Rol objetivo apuntando a Fenix | Situación comprobada |
|---|---|---|
| Guardian/eBPF | Sensor del kernel local de Marte; auditoría inicial | Estado de Marte no verificado desde esta sesión. Requiere validar whitelist y recuperación fuera de banda antes de adjuntar; enforcement requiere autorización separada. |
| Prometheus | Servicio en Marte que scrapea Fenix (`10.88.0.1:8000`, `:8001`) y exporters autorizados en ambos nodos | `prometheus.fenix.yml` actual scrapea el hostname público `cortex.pinguinoseguro.cl:443`, usa `insecure_skip_verify: true` y labels Fenix. Para la nueva topología, reemplazar targets por IP/puertos privados validados y labels de cada nodo; evitar Compose `sentinel_internal` como única ruta. |
| Mimir | Almacenamiento/consulta de series en Marte, destino privado de `remote_write` Prometheus | Solo existe `scripts/mimir_standalone.yaml` (`:8080`, filesystem, replication factor 1); no hay servicio Mimir en Compose ni runtime activo verificado. Definir persistencia y destino `remote_write`. |
| Loki | Backend de logs en Marte, recibe agentes autorizados de Fenix/Marte | El Compose actual corre Loki como stack Fenix, config local sin autenticación y publicación solo en `127.0.0.1:3100`; no hay recepción remota configurada. Diseñar listener privado, auth y reglas de origen para la ubicación Marte. |
| Grafana | Dashboards en Marte; consulta Prometheus/Mimir/Loki en Marte con datos sobre Fenix | Datasources existentes usan DNS Docker `prometheus:9090` y `loki:3100`, no Mimir. Adaptar a la instancia instalada en Marte y no exponer sus APIs internas al navegador. |
| TruthSync | Servicio backend privado en Marte, invocado detrás del gateway FastAPI de Fenix | No hay daemon TruthSync en Compose. `truthsync-core` es biblioteca enlazada en Cortex/Fenix; FastAPI `/api/v1/truthsync` usa `LocalTruthSyncEngine` en Fenix. La dirección propuesta es Kingu/UI→Fenix API→TruthSync Marte; falta definir puerto privado, auth, timeout, fallback y retirar/delegar el engine local sin divergencia. |
| Forwarder Guardian | Llevar eventos eBPF de Marte al backend Fenix | La unidad existente `sentinel-ebpf-forwarder.service` solo ejecuta `bpftool prog tracelog` y escribe localmente; no reenvía a `POST /api/v1/cortex/events`. Falta adaptador remoto autenticado. |

En la captura de runtime posterior a instalar QHC estaban activos solo `sentinel-backend`, `sentinel-cortex`, `sentinel-postgres`, `sentinel-redis` y `sentinel-n8n`. Prometheus, Loki, Grafana, Alertmanager, exporters, Promtail y `neural-guard` declarados en Compose Fenix no aparecieron en `docker ps`; Mimir y TruthSync daemon tampoco están en Compose. El repo contiene configuraciones/código reutilizables, pero el stack asignado a Marte todavía no está desplegado. Las definiciones Compose actuales de Grafana/Prometheus/Loki son para servicios locales en Fenix; no deben copiarse sin adaptar URLs, red, persistencia y autenticación.

La parte de backend en Marte queda fijada por Jaime: Grafana, Mimir, Prometheus, TruthSync y Loki, además de Guardian/eBPF. Falta diseñar los contratos de consulta/ingesta hacia Fenix por módulo. `neural-guard` es otro worker existente pero Jaime no lo incluyó en la asignación confirmada; mantener su ubicación pendiente.

## Análisis funcional del frontend

- El navegador usa rutas same-origin `/api/v1/...`; el servidor Next.js valida cookie de sesión y CSRF, y agrega el bearer al upstream privado. `SENTINEL_BACKEND_URL` debe apuntar a Fenix por WireGuard; producción falla al iniciar si falta.
- Kingu aloja UI y BFF, no el backend de datos ni Cortex. Las rutas inspeccionadas cubren dashboard, analítica, IA, backups, failsafe y holograma lattice. El holograma se consulta por polling desde el frontend.
- La revisión de despliegue encontró la UI servida, pero no validó sesión autenticada extremo a extremo ni todos los contratos backend. El frente es una capa de acceso/visualización reducida respecto a los módulos de runtime en Fenix.

## Cambios en Git

- `1651a877 docs(deploy): define standard multi-node procedure`
- `e096eaa9 fix(deploy): persist Cortex crystal runtime state`
- Procedimiento: [`PROCEDIMIENTO_DESPLIEGUE_MULTINODO.md`](PROCEDIMIENTO_DESPLIEGUE_MULTINODO.md)

## Rollback del único servicio cambiado

La imagen previa sigue disponible. Si la nueva versión presenta una regresión, cambiar solo `SENTINEL_CORTEX_IMAGE` en `/etc/sentinel/backend.env` a `sentinel-cortex:da843a84` y recrear `cortex` con `--no-deps`. Conservar `sentinel_crystal_state`; no ejecutar `down`, eliminar volúmenes ni revertir DB. El tag `sentinel-cortex:preflight-20261029b` también permanece local.

## Pendientes antes de aceptar el despliegue integral

1. Usar la ruta administrativa confirmada por Jaime para inspeccionar Marte en vivo: identidad/hostname, Debian/kernel activo, SSH 4222, WireGuard hacia `10.88.0.1`, Firewalld/zona/interfaz/reglas, whitelist y servicios Sentinel. El error `No route to host` de esta sesión no es un diagnóstico global del nodo.
2. Desplegar en Marte el stack asignado: Grafana, Mimir, Prometheus, TruthSync y Loki, más Guardian/eBPF en auditoría y un forwarder autenticado de eventos. Construir cada servicio desde la configuración correcta para Marte, sin duplicar la autoridad de datos de Fenix.
3. Definir y probar los contratos por WireGuard: Prometheus en Marte scrapea Fenix; Prometheus conserva/remote-writes a Mimir Marte; logs de Fenix/Marte llegan a Loki Marte; FastAPI Fenix invoca TruthSync Marte por API privada; Guardian envía eventos a FastAPI Fenix. Revisar autenticación, persistencia, timeouts y firewall en ambos nodos antes de abrir puertos.
4. Adaptar Grafana datasources y dashboards para los servicios en Marte y métricas/eventos de Fenix. Validar señales representativas y salud de cada datasource.
5. Mantener `neural-guard` como ubicación pendiente; Jaime no lo incluyó en la lista asignada a Marte.
5. Verificar contrato MyCNet↔QHC desde el despliegue de MyCNet; no inferirlo de la salud de Sentinel.
6. Validar `/api/v1/crystal_runtime/status` y `/api/v1/qhc/status` mediante sesión aprobada, además de login y WebSocket autenticados.
7. Definir y probar publicación del tick DTC por SHM; hoy las constantes están pero no el objeto compartido.
8. Revisar headers TLS de Sentinel y backups/restauración antes de declarar cierre de producción. La advertencia TLS duplicada pertenece a otro vhost y requiere cambio separado.

**Estado operativo actualizado:** frontend y APIs accesibles; contenedores core saludables; Cortex nuevo y persistente desplegado; QHC activo y visto por Cortex; autenticación humana pendiente. La arquitectura ahora distingue backend central Fenix y backend de borde Marte. Los servicios de seguridad/telemetría de borde y los pipelines remotos de métricas/logs aún no están desplegados ni verificados. No se declara «despliegue integral Sentinel completado».
