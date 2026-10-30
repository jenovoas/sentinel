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

### Cotejo de papers y experimentos para decidir qué desplegar

El seguimiento se hizo desde las citas en `me-60os-core/src/` y las trazas de `personalvault/Experimentos/`, hasta los consumidores Rust. Los papers de memoria Bateman, memoria fonónica/fotónica, optomecánica y eBPF no justifican instalar hardware o servicios adicionales solo por aparecer citados. La correspondencia y los criterios completos quedan en [`ARQUITECTURA_FUNCIONAL_SENTINEL_Y_EXPERIMENTOS.md`](ARQUITECTURA_FUNCIONAL_SENTINEL_Y_EXPERIMENTOS.md).

| Línea cotejada | Hallazgo código/experimento | Decisión de despliegue |
|---|---|---|
| Nandi–Vitiello 2026/2025; EXP-001/028 | `S60PID`/`CrystalRuntime` implementan memoria y mallas A/B; no son el reloj de tiempo. `TimeCrystalClock` y `NetworkTimeCrystal` están en `quantum/`; `time_crystal.rs` solo reexporta `quantum_core`. | Fenix ejecuta el Cortex Rust, no `quantum/cortex_main.py`; no se verificó `NetworkTimeCrystal` en producción. Falta un tick común con contrato/época compartidos entre Cortex, QHC y MyCNet. |
| EXP-021/030 — NPU tetra-lógica | La NPU es software Rust: `ResonanceEngine` llama a `HarmonicProcessor::process_signal` desde `verify_pulse`. No es un acelerador NPU de hardware. | El binario activo la contiene y ejecuta verificaciones, pero Fenix lleva 393 `PULSE CHECK` en las últimas 3 h con `Valid=false`; no hay `PROCESSOR RESULT` ni `Bio-Pulse received` en esa ventana. Investigar el canal de entrada antes de declararla operativa. |
| Regulador Atlanteano / Maat | `MaatStabilizer` y `GpuController` están en `me-60os-core/src/atlantean.rs`, y el Cortex activo los instancia en su tarea térmica. La verdad de entrada es constante `58/60`; `gpu_batch` solo se registra en nivel `trace`, sin consumidor GPU. | El código está incluido y la tarea está conectada al muestreo térmico/lattice, pero no se ha demostrado regulación basada en TruthSync ni control efectivo de una carga GPU/inferencia. |
| Zhang–Wang 2025 y memoria fotónica; EXP-009/016 | Cortex tiene `LiquidLattice`/`NeuralMemory` y checkpoint de software; los papers describen dispositivos mecánicos/fotónicos físicos. | No desplegar hardware de laboratorio. Aceptar la ruta de software solo con eventos BPF reales y recuperación validada del checkpoint. |
| Papers eBPF 2021/2026 | El código contiene lector de ring buffer local y bridge Cortex. La arquitectura objetivo mueve Guardian a Marte y exige retorno de eventos a Fenix. | Marte necesita sensor local en auditoría más forwarder de red autenticado. La unidad actual `bpftool prog tracelog` no satisface ese flujo. |
| EXP-015/020/021 y PAI/FPU | `inject_pai` está en rutas de Cortex; `fpu_vs_pai_bench` es un bin auxiliar y su output no está archivado en la traza. | Desplegar/aceptar el camino PAI de Cortex; no desplegar FPU como daemon ni reclamar resultados del bench sin salida reproducible. |
| EXP-031 / dual lane | `CrystalRuntime` A/B por SHM está conectado; `DualLaneRouter` de Security/Observability no se encontró conectado a la ingesta principal. Son dos mecanismos diferentes. | Falta cablear y verificar WAL/carril de seguridad y colector/carril de observabilidad para los eventos remotos de Marte. |
| Crystal Cipher | La implementación Rust no tiene consumidor productivo; deriva claves del estado determinista del cristal/pulso. | No usarlo para proteger SHM/ring buffer todavía. Resolver consumidor, claves secretas/rotación/reinicio y unicidad de nonce antes de incluirlo en el despliegue de seguridad. |

Esta adición es un cotejo documental de citas, experimentos y código. **No añade evidencia nueva de runtime ni indica que el despliegue en Marte se haya ejecutado.**

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

### Brecha de arquitectura TruthSync: filtro integrado y pod

La inspección de código encontró dos funciones compatibles dentro de una arquitectura mayor, no dos implementaciones intercambiables:

- **Seguridad/filtro integrado:** `me-60os-core/src/scv.rs` implementa `ScvEngine` y `EntropicFirewall`, con cálculo de entropía y decisión de validez. `sentinel-cortex/src/security/lfm_security_pipeline.rs` integra sanitizador de ingreso y certificación de salida mediante `TruthSyncEngine`. Esto acredita código integrado; no acredita por sí solo que cada ruta de producción lo invoque ni que el filtro de entropía esté aplicado a todo dato.
- **Verificación y score de contenidos (pod/Truth Core):** el historial conserva `truthsync-poc/k8s-deployment.yaml`, `k8s-truthsync.yaml`, Dockerfile, Compose y servidor. El commit `639383a2` (2025-12-18) incorporó paquete de deployment/guía; `86bdffdd` (2025-12-30) consolidó K8s con Deployment (3 réplicas), Service y HPA (3–10). `backend/truthsync_core.py` también implementa un worker de verificación/scoring. `truthsync-core` Rust y FastAPI local son rutas distintas, no sustitutos del pod.
- **Madurez funcional histórica:** el servidor Python de `639383a2` marca procesamiento simulado y llamada Rust como TODO (`truthsync_server.py`, líneas 87–116). El servidor Rust de `86bdffdd` extrae claims/cache pero asigna `confidence = 0.95` fija (`src/main.rs`, líneas 103–117). Esto acredita infraestructura/prototipo versionado; no scoring semántico validado.
- **Eliminación del árbol activo:** `0c5780f7` (2026-01-21) eliminó `truthsync-poc/`, `k8s-truthsync.yaml` e `infrastructure/kubernetes/k8s/apps/truthsync-edge.yaml`. Es recuperable desde Git; el commit no demuestra despliegue en producción, autoría de una IA ni por sí solo la razón funcional del olvido. En el inventario actual de Fenix no apareció TruthSync; Marte no fue inspeccionado en vivo.
- **Antecedente de Jaime:** el filtro integrado y el pod eran piezas distintas de un sistema común, separadas por una IA que dejó el pod olvidado. La separación reportada es consistente con la existencia histórica del paquete independiente; atribución y despliegue efectivo siguen sin corroborarse.
- **Brecha y acción:** auditar y recuperar el artefacto histórico antes de restaurar; corregir simulación y score fijo/no calibrado, acordar contrato de contenidos y agregar evidencia de runtime. Mantener Truth Core en Marte, privado detrás de FastAPI en Fenix, separado del filtro integrado. Definir API/auth/timeout/persistencia/fallback y aceptar ambos caminos con validaciones independientes.

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
7. Desplegar y probar el reloj real (`NetworkTimeCrystal`/`TimeCrystalClock` o su migración Rust) y su contrato de tick común. `CrystalRuntime` y sus mallas A/B no son evidencia del cristal de tiempo; sus constantes DTC no crean un reloj compartido.
8. Revisar headers TLS de Sentinel y backups/restauración antes de declarar cierre de producción. La advertencia TLS duplicada pertenece a otro vhost y requiere cambio separado.

**Estado operativo actualizado:** frontend y APIs accesibles; contenedores core saludables; Cortex nuevo y persistente desplegado; QHC activo y visto por Cortex; autenticación humana pendiente. La arquitectura ahora distingue backend central Fenix y backend de borde Marte. Los servicios de seguridad/telemetría de borde y los pipelines remotos de métricas/logs aún no están desplegados ni verificados. No se declara «despliegue integral Sentinel completado».

## Inicio de despliegue — continuación 2026-10-30

Se inició el preflight de aplicación a las 05:33 UTC. Las comprobaciones remotas de Fenix confirman FastAPI (`10.88.0.1:8000`) y Cortex (`:8001`) con HTTP 200, el servicio `sentinel-qhc-agent` activo y un `SNAPSHOT` reciente por `/run/soma/qhc.sock`. Sin embargo, los logs de Cortex siguen registrando `QHC=true` con `Valid=false` y `Coherence=false`; la salud HTTP/QHC no satisface el gate de coherencia.

Marte (`10.88.0.6`) responde ICMP desde Fenix, pero TCP 4222 devuelve `No route to host` desde Fenix y desde la ruta pública probada también desde laptop. No se ejecutó comando remoto ni se cambió su firewall. Por tanto, Grafana, Mimir, Prometheus, TruthSync, Loki y Guardian/eBPF no se aplicaron. El stack de monitoreo permanece asignado a Marte; no se desplazó a Fenix como sustituto.

En Kingu siguen activos frontend y Nginx. `nginx -t` falla al leer el certificado de `impacta.pinguinoseguro.cl` por permisos; es un vhost ajeno a Sentinel y quedó intacto. No hubo despliegue de frontend.

**Resultado de esta continuación:** preflight iniciado, despliegue remoto de Marte bloqueado por conectividad administrativa desde esta sesión. No hay cambios operativos nuevos. Próximo paso: habilitar SSH TCP 4222 desde la ruta de administración de esta sesión o establecer una ruta administrativa aprobada; luego volver a verificar el firewall activo, whitelist, recuperación fuera de banda y estado real de Marte antes de aplicar servicios. Guardian/eBPF solo podrá adjuntarse en auditoría tras pasar esos gates; enforcement no está autorizado.

## Resultado operativo posterior — stack de observabilidad en Marte

La nota anterior es una captura previa a resolver el acceso administrativo y queda superada por esta verificación del 2026-10-30. Se usó la sesión SSH multiplexada disponible para Marte (`10.88.0.6:4222`); no se pidió ni se necesitó que el usuario cambiara su acceso.

- Marte: Debian 13, kernel `7.3.0-ifenix`, `wg0=10.88.0.6`, Firewalld activo. Se instalaron Docker Engine/Compose y se aplicó `/opt/sentinel-marte` desde `service-operation/deploy/marte/`.
- Contenedores `Up`: Grafana 13.2.1, Prometheus 3.15.1, Mimir 3.2.3, Loki 3.7.0, Alloy 1.21.3 y node-exporter 1.12.1. Grafana `/api/health` devolvió `database=ok`. Loki `/ready` devolvió `ready`.
- Prometheus reportó `up=1` para sí mismo, node-exporter de Marte y las métricas FastAPI/Cortex de Fenix (`10.88.0.1:8000/metrics`, `:8001/metrics`). Mimir respondió por su API y devolvió las cuatro series remotas `up`; `prometheus_remote_storage_samples_failed_total=0`.
- Se consultaron logs reales de Fenix en Loki: etiquetas `cluster`, `filename`, `job`, `node`, `service_name`; streams `node=fenix, job=docker-container` devolvieron líneas recientes, incluidas respuestas reales de `/metrics` y el pulso de Cortex. Alloy Fenix reportó `loki_write_sent_entries_total=48`, 13.588 bytes enviados, cero reintentos y cero entradas descartadas en la captura posterior al arreglo.
- Hallazgo y corrección: Alloy empezó en la red bridge Docker. Desde ese namespace, `/ready` a Marte expiraba porque la IP de origen no estaba autorizada por la regla Firewalld restringida a Fenix (`10.88.0.1`). Se cambió `compose.fenix-agent.yaml` a `network_mode: host`, conservando Alloy HTTP en `127.0.0.1:12345`; con ello el egreso usa la IP WireGuard permitida. No se amplió el firewall ni se montó el socket Docker. Verificación: Alloy saludable y entradas visibles en Loki.
- Firewalld Marte activo/permanente: Loki TCP 3100 solo desde Fenix; Grafana TCP 3000 desde Fenix, Kingu y el host administrador `10.88.0.3`; puerto clipboard SSH 4222 desde Fenix y host administrador. Prometheus/Mimir no publican puertos en el host.
- Firewall Docker de Fenix conserva Kingu (`10.88.0.2`) para 8000/8001/5678 y autoriza Marte (`10.88.0.6`) solo para 8000/8001; el puerto 5678 sigue bloqueado desde Marte. La regla se gestiona por `scripts/sentinel-docker-user-firewall.sh` y `sentinel-docker-user-firewall.service`.
- La contraseña de Grafana vive solo en `.env` de root, modo `0600`; no se copió al repo ni se mostró. Mimir/Loki usan filesystem local, replicación 1 y retención 30 días; no es HA y requiere backup/restore que aún no se ha verificado.
- **Fuera del despliegue aplicado:** TruthSync Core (el pod/verificador histórico), Guardian/eBPF y su forwarder autenticado. Se conserva separado el filtro de entropía integrado en Fenix. TruthSync requiere corregir el score fijo/procesamiento simulado y definir API privada; Guardian requiere whitelist verificada y recuperación fuera de banda. No hay enforcement.
- No se desplegó frontend en Kingu en esta intervención. QHC queda como componente compartido requerido por Sentinel/MyCNet; esta tarea no valida integración del lado MyCNet. Cortex sigue mostrando `Valid=false` y `Coherence=false` en los pulsos observados, por lo que la salud de servicios no se interpreta como coherencia total.

**Estado:** backend de observabilidad aplicado y verificado con métricas y logs reales Marte↔Fenix. La red completa de Sentinel no está aceptada: TruthSync, Guardian/eventos y gates funcionales/auth del backend/frontend siguen pendientes. El despliegue y rollback reproducibles quedan en [`service-operation/deploy/marte/README.md`](../service-operation/deploy/marte/README.md) y la guía estándar se actualizó en [`PROCEDIMIENTO_DESPLIEGUE_MULTINODO.md`](PROCEDIMIENTO_DESPLIEGUE_MULTINODO.md).

### Aclaración de identidad: cristal de tiempo y mallas

`sentinel-cortex/src/memory/crystal_runtime.rs` gestiona las matrices de memoria dual (lane A seguridad, lane B observabilidad), semillas y checkpoints. **No es el módulo de sincronización del cristal de tiempo**, aunque contiene un contador interno y usa `IsochronousClock`. Su estado `active` no demuestra que el reloj de red esté desplegado.

El reloj local está representado por `quantum/time_crystal_clock.py::TimeCrystalClock`; la coordinación distribuida está en `quantum/time_crystal_network.py::NetworkTimeCrystal`, iniciada desde `quantum/cortex_main.py`. `me-60os-core/src/time_crystal.rs` solo reexporta `quantum_core`, donde vive la primitiva Rust `IsochronousClock`; no crea por sí sola un servicio distribuido. En Fenix se observan el binario `sentinel-cortex` Rust y `sentinel-qhc-agent`, no el entrypoint Python. No hay evidencia de que `NetworkTimeCrystal` esté ejecutándose ni de que su consenso QNTP sincronice los nodos.

Las mallas `/dev/shm/me60os_lattice` y `/dev/shm/me60os_lattice_b` sí existen en Fenix y pertenecen a `CrystalRuntime`; son estado compartido de las dos lanes, no el reloj común. QHC entrega snapshots a una ruta de Cortex, pero sus pulsos aún indican `Valid=false`, `Coherence=false`; tampoco está verificado el consumidor MyCNet↔QHC. Estos contratos quedan separados hasta integrar y observar el sincronizador real.

## Actualización del borde de seguridad — 2026-10-30

- Se instaló `bpftool` y se actualizó el objeto Guardian en Marte. `sentinel-ebpf.service` queda activo; el enlace LSM Guardian Alpha está adjunto, whitelist con 2.747 entradas y `guardian_mode_map=0` (auditoría). El rollback independiente por SSH sigue disponible. No se habilitó enforcement.
- Se corrigieron dos fallos del bootstrap que impedían acreditar el inventario: el conteo de mapas interpretaba el JSON de `bpftool` como salida de texto y `read -a` truncaba claves de ruta al primer renglón de `od`.
- Se desplegó `sentinel-security-gateway.service` en Marte. Está activo en `:8090`, el lector abrió `/sys/fs/bpf/guardian_alpha/events`, `/health` devuelve healthy y `/metrics` expone contadores de Guardian/AIOps. Firewalld permite Fenix (`10.88.0.1/32`) y la red del Prometheus local (`172.18.0.0/24`) para ese puerto; el target de Prometheus aparece `up`.
- El gateway aplica `AIOpsSemanticFirewall` y `TelemetrySanitizer` a todos los campos string, deja hash/categorías en WAL con clave local y reenvía eventos a `POST /api/v1/cortex/events` con el token interno transferido sin imprimirlo. El bundle desplegado incorpora el contrato de evento eBPF de 32 bytes con todos los campos y padding inicializados.
- La primera entrega real fue autenticada pero devolvió HTTP 500 porque Python intentó serializar un objeto `SPA` dentro de JSONB. Se corrigió a unidades base exactas; el cálculo de riesgo/confianza ahora usa `S60` y nanosegundos enteros, y las salidas de Cortex/Gamma se expresan con `confidence_s60_raw`. Las columnas históricas `FLOAT` reciben únicamente enteros escalados exactos en los nuevos registros; no hubo migración de esquema porque no se encontró backup verificado.
- Se publicó y desplegó en Fenix `sentinel-backend:68ccc8ad` (imagen `sha256:cea249ef8529b8c3d646136bf3f5ce788aac1e425ea39536f9026da462b2f43d`). Compose recreó solo `backend`; Alembic conservó el head existente. El contenedor quedó `healthy`, `/api/v1/health` respondió HTTP 200 y los eventos Guardian reales recibieron HTTP 201 tras persistencia/decisión.
- A las 06:50 UTC el gateway Marte registraba 33 reenvíos exitosos, 24 errores HTTP 500 previos a la actualización de Fenix y 0 descartes del ring buffer. El WAL forense mide 20.720 bytes con modo 0600. El contador de errores es acumulativo desde el arranque y no representa fallos posteriores a la actualización; los logs más recientes de Fenix muestran respuestas 201.
- El endpoint AIOps de Marte está desplegado con autenticación bearer configurada; no se ha validado todavía una llamada cliente autenticada. No se migró el workflow n8n antiguo, que todavía referencia rutas Fenix (`/api/security/sanitize`) inexistentes en el backend actual. El workflow es un artefacto desconectado, no consumidor verificado.
- La asignación de interfaz queda explícita: Next.js/BFF y la GUI Tauri de administración pertenecen a Kingu y consumen Fenix. Git history confirma que `gui/` fue eliminado en `0c5780f7`; el prototipo recuperable usaba telemetría aleatoria (`Math.random`) y comandos semánticos sin integración comprobada, por lo que no se empaqueta como dashboard operativo. En el checkout activo no hay fuente Tauri.
- Guardian Alpha vive en Marte; Beta/Cortex y Gamma/API permanecen en Fenix, con la interfaz de decisión humana en Kingu. La conexión Beta→Gamma sigue sin acreditarse. AIOpsShield/sanitizador son procesos activos en Marte; Truth Core/pod separado sigue pendiente y no se confunde con el filtro integrado en Fenix.
- Para guardar `risk_score` en la columna histórica `FLOAT`, el parche usa solo el entero `S60::to_base_units()`; todos los valores posibles (0..12.960.000) son exactamente representables en ese tipo binario, sin aritmética flotante. La columna sigue siendo legado y su migración a entero queda pendiente de backup DB verificado.

**Estado en la captura de las 06:50 UTC:** Guardian Alpha y gateway activos en Marte, modo auditoría; Prometheus muestra el gateway `up`; eventos reales ya eran aceptados y procesados en Fenix. Esta captura fue superada por la actualización de las 07:00 UTC, que conecta el path de ejecutable y activa los cinco patrones.

### NPU tetra-lógica y regulador Atlanteano en el Cortex desplegado

El inventario de `sentinel-cortex/` contiene 53 archivos `.rs` y 11.769 líneas contando bins y pruebas. La imagen Fenix `sentinel-cortex:e096eaa9` se cotejó contra Git: incluye `HarmonicProcessor`, `ResonanceEngine`, `MaatStabilizer` y `GpuController`.

- **NPU:** el flujo activo verifica cada tick QHC múltiplo de 17 y `ResonanceEngine::verify_pulse()` llama al NPU. La coherencia de `ResonanceEngine` parte en cero y solo crece con `inject_pulse()`. El listener Rust se suscribe a Redis `sentinel:bio_pulse`; el entrypoint Python histórico publica `sentinel:quantum:pulse`, y no se encontró publicador del primer canal en el código revisado. El heartbeat QHC actualiza otro `BioResonator`; no llama a `ResonanceEngine::inject_pulse()`. En vivo, 393 checks durante 3 h resultaron `Valid=false`, sin `PROCESSOR RESULT` ni `Bio-Pulse received`. El NPU está compilado y se evalúa, pero no alcanza una ruta aceptada.
- **Maat/Atlantean:** la tarea térmica de Cortex se crea cada 500 ms y llama a Maat, pero `current_truth` está fijado en `58/60`; `current_speed` es estado local. El tamaño de lote calculado se emite solo con `tracing::trace!` y no se pasa a un consumidor GPU. La tarea también inyecta su amplitud térmica al lattice y a la lane de observabilidad; esa ruta no prueba que Maat controle un workload real.
- **Alcance del análisis:** ninguna de estas brechas se corrigió ni se desplegó en esta auditoría. La acción siguiente es diseñar el contrato de pulsos y conectar las salidas de Maat a consumidores reales, con aceptación en logs/métricas antes de atribuirles efecto operativo.

## Actualización operativa — carga de patrones y ABI extendida Guardian — 2026-10-30 07:00 UTC

- Commit desplegado: `b73aa357` (`fix(security): forward Guardian exec paths and seed Cortex patterns`), rama `main`. Incluye ABI eBPF de ejecución de 292 bytes (header Cortex estable de 32 bytes + ruta de 256 bytes + UID), parser Rust retrocompatible con eventos antiguos de 32 bytes, normalización de `EXEC_ALLOWED/BLOCKED` a `syscall/execve`, y carga idempotente de patrones faltantes al arrancar FastAPI.
- Builds: `cargo check --locked --bin sentinel-security-gateway` terminó correctamente; build release del gateway finalizó con cuatro warnings previos de constantes DTC SHM no usadas. `make -C ebpf OBJECT=/tmp/guardian_cognitive.o` compiló el objeto. `cargo fmt --check`, `python3 -m py_compile backend/app/init_cortex.py` y `git diff --check` pasaron. No se ejecutó la suite de tests.
- Marte: `sentinel-ebpf.service` y `sentinel-security-gateway.service` activos. Guardian LSM programa `guardian_cognitive`, tag `5475c1c5366fb560`; objeto instalado SHA-256 `e81633bf54c97fd872383f4ae31232306da4bdbb9e86a1d4bd2c6349416d1713`. Gateway instalado SHA-256 `f7e56978be9e5941bd15d404b046632c7d4206d5de72a885fabb5e9b0594f7b0`. Whitelist verificada: 2.748 entradas (incluye el binario gateway); modo `guardian_mode_map=0`; enforcement desactivado.
- Empaquetado reproducible: eBPF bundle SHA-256 `c1a911cfe415bc584d2f329e75cb8891fd1fe11e3f5a65138b7989a41e41cc7b`; gateway bundle SHA-256 `c4d22a46526264f4d6900d3cdaf2fe0ed8c36f2aab7cf91e1e2695aecaff62f1`.
- Fenix: `sentinel-backend:b73aa357`, imagen `sha256:d5cc4d5ddaed851977b205310549d0a1e2184091f27e5451f61810d2d5c5e282`, `running/healthy`; se recreó solo `backend`, sin cambiar esquema DB. El entrypoint ejecutó migraciones al head y el seeder idempotente. PostgreSQL confirma cinco patrones habilitados: `privilege_escalation`, `suspicious_network`, `malicious_binary`, `data_exfiltration`, `lateral_movement`.
- Prueba operativa segura: se ejecutó `/bin/true` copiado temporalmente como `/tmp/sentinel-guardian-probe`; Guardian auditó la ejecución, el gateway la envió a Fenix y FastAPI devolvió HTTP 201. Cortex registró `Loaded 5 active security patterns`, detectó `malicious_binary` sobre `syscall/execve` con la ruta `/tmp`, calculó confianza S60 `10090285` y persistió/procesó la decisión. El ejecutable temporal se eliminó. No se usaron secretos ni se activó enforcement.
- Gateway: `/health` healthy; Prometheus `sentinel-security-gateway-marte` `up`; contadores observados tras el despliegue: 14 eventos reenviados, 1 error acumulado de transición/reinicio y 0 ring drops. La métrica de errores es acumulativa; los eventos posteriores a la actualización llegan con HTTP 201.
- Brecha de interpretación de health: `/api/v1/health` de Fenix reporta `components.guardian.active=false/status=unprotected` porque busca el proceso legacy `watchdog_service.py`. Ese booleano no consulta el Guardian remoto de Marte y no invalida la evidencia eBPF/gateway anterior; debe corregirse para distinguir watchdog local de protección remota y evitar presentar el health general `healthy` como cobertura Guardian.
- Kingu: Next.js/BFF y el dashboard Tauri pertenecen a Kingu. No hay fuente Tauri activa en el checkout; el prototipo histórico era mock y no se desplegó. Para instalarlo hace falta recuperar una versión funcional, eliminar datos aleatorios, integrar la API/BFF autenticada de Fenix y producir un paquete reproducible.
- Aún no se acepta Sentinel completo. Permanecen Truth Core/pod de scoring, la llamada Beta→Gamma, reloj de red, QHC con `Valid=false/Coherence=false`, integración MyCNet↔QHC (fuera del alcance de esta verificación), rutas NPU/Atlantean con consumidores efectivos y gates de autenticación. No se afirma que Crystal Time sea `CrystalRuntime` ni que el despliegue integral esté terminado.

## Continuación de auditoría — NPU/QHC, reloj de red y TruthSync — 2026-10-30 14:06 UTC

### Estado operativo QHC y NPU

- Cortex sigue `healthy` y QHC conectado, pero los logs recientes muestran cada verificación de salto 17 con `QHC=true`, `Valid=false`; no aparece `PROCESSOR RESULT`.
- En `sentinel-cortex/src/main.rs`, cada snapshot QHC reciente llama `BioResonator::record_pilot_heartbeat()`, pero no llama `ResonanceEngine::inject_pulse()`. El `ResonanceEngine` parte con coherencia cero y solo cambia por su propia entrada de pulso.
- El listener de ResonanceEngine está suscrito a Redis `sentinel:bio_pulse`; `PUBSUB NUMSUB` mostró un suscriptor en ese canal y cero en `sentinel:quantum:pulse`. El árbol Sentinel no contiene un publicador de `sentinel:bio_pulse`. `bci/mantra_bridge.py` y `quantum/cortex_main.py` publican en el otro canal; no se despliegan como productores actuales y el pulso de Cortex es sintético, por lo que no se conectarán como si fueran presencia humana. MyCNet no se inspeccionó.
- Resultado: QHC evita el watchdog por ausencia de heartbeat, pero no carga la coherencia que valida NPU. Se mantiene pendiente identificar/activar el productor autorizado del pulso humano y cablear su contrato sin convertir un heartbeat sintético o QHC en presencia humana.

### Cristal de tiempo distribuido

- En Fenix, Marte y Kingu, `timedatectl` reportó NTP habilitado y `NTPSynchronized=yes` en esta captura. Los servicios `sentinel-time-crystal.service` y `network-time-crystal.service` no están activos ni instalados.
- `quantum/time_crystal_network.py` no constituye sincronización operativa: serializa `time.perf_counter_ns()` (reloj monotónico local no comparable entre hosts), envía `phase_raw=0`, calcula `network_consensus_drift_ns` pero no aplica una corrección a `TimeCrystalClock`. El módulo requiere Redis local por defecto y no tiene contrato de transporte autenticado entre nodos.
- No se desplegó como reemplazo de NTP. La implementación futura debe definir época común, unidad/tick, medición de offset/retardo entre hosts, autenticación por WireGuard y consumo observable; no se expondrá Redis.

### TruthSync de contenido

- El motor activo de FastAPI en Fenix es `LocalTruthSyncEngine`; el runtime reportó `enabled=false` porque falta `truth_algorithm`. Antes del cambio, `/api/v1/truthsync/health` afirmaba `healthy` y `/verify` devolvía el error dentro de HTTP 200.
- Commit `1096065f` corrige la señalización: `health_check` responde `status=unavailable`, `enabled=false`; `/api/v1/truthsync/verify` y `/search` responden HTTP 503 con `truthsync_engine_unavailable` cuando el motor falta. Se desplegó solo backend Fenix como `sentinel-backend:1096065f`, ID `sha256:f84e301ca5588f0f035e35ddfc65734ea15cc60e4478462aa6dbb004b726b723`; quedó `running/healthy`. `/api/v1/health` permanece HTTP 200 para DB/Redis y expone TruthSync `available=false`; TruthSync health devolvió `unavailable`; verify devolvió HTTP 503 en sonda sintética.
- Auditoría de Git: el pod histórico se eliminó del árbol activo en `0c5780f7`. `truthsync-core/src/lib.rs` actual calcula `overall_trust_score` a partir del primer byte de SHA3, no de fuentes que apoyen/refuten el claim; el benchmark de `truthsync-core` mide rendimiento. El servidor de `86bdffdd` fijaba confianza `0.95`. El algoritmo Python histórico (por ejemplo `8c78e470`) usa consenso sobre una clasificación de snippets por palabras clave y `source_search.py` cae a MOCK cuando falla proveedor o dependencia. No es aceptable desplegar cualquiera de esos scores como verificación real sin corregir el algoritmo y exigir evidencia verificable.
- La capa integrada de seguridad/entropía se mantiene distinta del Truth Core de scoring; el endpoint que ahora reporta `unavailable` corresponde al motor de verificación de contenido, no invalida el filtro de telemetría Guardian que se ejecuta en Marte.

### Maat / Atlantean

El código vivo sigue fijando `current_truth=58/60`; `GpuController` regula un batch usando latencia local, pero el resultado solo se escribe con nivel `trace` y no llega a carga GPU/inferencia identificada. No se fabricó una medida TruthSync ni se conectó un workload por esta continuación.

**Siguiente bloque de implementación:** recuperar una fuente de pulso humano real y autorizada para NPU; definir un contrato de tiempo común sobre WireGuard; reconstruir el Truth Core con evidencia y abstención cuando no existan fuentes fiables. No se inspeccionó MyCNet ni se cambió su runtime.

## Seguimiento de GUI Tauri para Kingu — 2026-10-30

La GUI administrativa Tauri queda asignada a Kingu como componente de presentación, consumiendo el BFF/API autenticado de Fenix. En una comprobación de solo lectura no aparecieron unidades systemd Tauri/Sentinel GUI ni artefactos Tauri bajo `/opt/sentinel`; esto no descarta una instalación manual por usuario fuera de esas ubicaciones.

- El árbol actual no contiene `gui/src-tauri`; Git confirma que el prototipo fue retirado en `0c5780f7`. El manifest recuperado desde su padre usa Tauri 1.6, Svelte 4 y Vite 5, de modo que es una base histórica y sus dependencias/build no se deben asumir compatibles con el toolchain actual.
- `gui/src/routes/+page.svelte` del prototipo asigna métricas iniciales constantes y luego genera `entropy`/`tte` con `Math.random()` cuando corre en navegador. La interfaz puede, por tanto, mostrar datos aparentes sin telemetría.
- `gui/src-tauri/src/main.rs` documenta que `execute_semantic_command` está simulado y devuelve aprobación fija (`LSM`, `TTE: 3.23us`) sin ejecutar SemSH. No debe habilitarse como terminal de administración.
- `get_system_vector` abre `/var/run/sentinel/truthsync_shm`, lee 32 bytes y decodifica tres `f64` little-endian. Ese layout/ruta no se ha cotejado con un productor SHM desplegado, y no coincide por sí mismo con la telemetría autenticada del BFF. El fallback a ceros tampoco separa “sin dato” de medición cero.
- Próxima etapa para Kingu: recuperar el prototipo como trabajo aislado; reemplazar comandos mock por consultas permitidas al BFF y autenticadas mediante la sesión del usuario; definir un contrato de telemetría con timestamp/estado de frescura; retirar SHM local y cualquier credencial embebida; actualizar dependencias Tauri/Svelte; producir bundle reproducible y verificar firma/hash antes de instalar.

**Estado:** destino arquitectónico confirmado (Kingu); artefacto no recuperado ni listo para instalación. No se modificó el runtime de Kingu.

## Corrección de health Guardian en Fenix — 2026-10-30

El endpoint `/api/v1/health` confundía el proceso legacy local `watchdog_service.py` con Guardian Alpha remoto en Marte. Se corrigió en `cb9a4ba6`: `components.guardian.active=null`, `status=unknown`, `source=marte`, `reason=remote_guardian_not_probed`, y el resultado del proceso local ahora aparece como `local_watchdog_active`. La API deja explícito que Fenix no hizo una sonda remota; no altera el resultado de la cadena Guardian ya aceptada por eventos.

- Construcción en Fenix desde `main`, SHA `cb9a4ba6`; imagen `sentinel-backend:cb9a4ba6`, digest `sha256:bd0862f57666ed7e434a4570902c614fb924717e79742936849606743e70f100`.
- Se recreó exclusivamente `backend` con `--no-build --no-deps`. Quedó `running/healthy`; `/api/v1/health` por `10.88.0.1:8000` devolvió HTTP 200, Guardian `unknown`/no probado remotamente y TruthSync `unavailable` (como corresponde al motor deshabilitado). Cortex, PostgreSQL y Redis siguieron `healthy`.
- `/etc/sentinel/backend.env` conservó propietario `root:docker` y modo `0640`. No hubo cambios de esquema ni se activó/desactivó protección.

**Resultado:** se eliminó la afirmación falsa `unprotected` para un componente remoto que el endpoint de Fenix no consulta. El estado real de Guardian sigue acreditado por las verificaciones Marte→Fenix anteriores; este health no lo vuelve a sondear.

## Truth Core Cortex: abstención hasta disponer de evidencia — 2026-10-30

La inspección del código activo encontró una segunda ruta de score engañoso además del FastAPI TruthSync ya corregido:

- `truthsync-core/src/lib.rs` extrae frases con patrones regex y asigna scores fijos 0.95/0.70; el score global proviene del primer byte de SHA3-512 (`digest[0]/255`) menos una penalización por frases de una lista. No consulta ni adjunta fuentes que respalden/refuten el claim, ni calibra la probabilidad. El bench de un millón de claims mide throughput/latencia, no validez factual.
- Cortex exponía ese resultado en `/api/v1/ai/query` como `certified` y en `/api/v1/truth_claim` como `claim_valid`; también anunciaba `truthsync=active` en `/api/v1/ai/health`. Se corrigió en `ed5cfc8e`: las consultas normales devuelven HTTP 503 con verificación `unavailable`, score nulo y sin certificación. Los patrones críticos/semánticos siguen bloqueándose (403) y escribiéndose al WAL. El health Cortex ahora reporta TruthSync `unavailable`; el motor de score se quitó del estado del binario servidor. No se eliminó el código experimental ni el uso aislado en herramientas.
- Build validado con `cargo fmt --check`, `cargo check --locked --package sentinel-cortex --bin sentinel-cortex` y empaquetado release en Fenix. Imagen desplegada `sentinel-cortex:ed5cfc8e`, digest `sha256:c72d25c48bd38c3db233937e26b37c18b630d83c95461032d4261729476ee78b`; contenedor `running/healthy`. Solo se recreó Cortex. Backend `sentinel-backend:cb9a4ba6`, PostgreSQL y Redis permanecieron healthy; `/etc/sentinel/backend.env` siguió `root:docker 0640`.
- Logs posteriores muestran `QHC=true`, pero los ticks NPU siguen `Valid=false`, `Coherence=false`. La mejora de honestidad del Truth Core no restaura scoring ni NPU.

**Límite de verificación:** no se probó una sesión humana aprobada contra las rutas Cortex protegidas; no se generó ni usó un token para ese fin. La imagen y health fueron comprobados en vivo; la respuesta de las rutas se verifica por código/compilación, pendiente de aceptación funcional con una sesión autorizada.

## Verificación posterior de Marte y métrica AIOpsShield — 2026-10-30 14:27 UTC

Inventario de solo lectura en Marte (`10.88.0.6`): `sentinel-security-gateway.service` y `sentinel-ebpf.service` están activos; Guardian `guardian_cognitive` está adjunto como LSM, el mapa whitelist contiene 8.246 entradas y `guardian_mode_map=0` (auditoría). `/health` del gateway responde HTTP 200. Sus métricas observadas: 7.860 eventos enviados, 1.418 intentos de reenvío fallidos acumulados y 0 descartes del ring buffer. El contador de errores incrementa por intento, no equivale a 1.418 eventos perdidos: los logs de Fenix muestran que el mismo intervalo tuvo múltiples POST de Marte aceptados con HTTP 201. En la lectura de targets, Prometheus informó `up` para sus cinco targets: node-exporter Marte, Prometheus, FastAPI Fenix, Cortex Fenix y Gateway Marte. Grafana `/api/health` respondió con DB `ok`; Grafana, Prometheus, Mimir, Loki, Alloy y node-exporter aparecen como contenedores `Up`.

El compose y runtime listan esos seis servicios de observabilidad; no listan un TruthSync/Truth Core separado. El gateway desplegado aplica sanitización Rust internamente antes de Fenix, lo cual es la capa integrada de seguridad/entropía; no sustituye el Truth Core/pod de scoring de contenido. El último sigue ausente y el score actual no es aceptable, como se detalla arriba.

Al cotejar `sentinel-security-gateway.rs`, el handler `/api/v1/aiops/sanitize` incrementaba `sentinel_aiops_shield_blocked_total`, pero `forward_event` retenía eventos Guardian detectados, los registraba al WAL y no incrementaba el mismo contador. Eso hacía que métricas pudieran subcontar bloqueos del flujo eBPF. Se corrigió el incremento en la rama de retención de Guardian. No se ejecutó un payload de bloqueo para evitar generar un evento de seguridad artificial.

### Gateway actualizado en Marte

Commit Sentinel `092f474e` incluye la corrección. `cargo fmt --check`, `cargo check --locked --package sentinel-cortex --bin sentinel-security-gateway` y el build release del binario pasaron; no se ejecutó la suite. El bundle transferido tuvo SHA-256 `9a7cd175c029876ad65c22e1272bf4f99160a873ebfa066efa85e238b6070db2`; el binario instalado quedó con SHA-256 `63a9c45d43b32578a4ef206440a2051111433ec80aec242e252566c20200f670`. Se preservó la versión anterior en `/var/tmp/sentinel-security-gateway-rollback-092f474e`.

Tras reiniciar únicamente `sentinel-security-gateway.service`, su log confirmó que enlazó el ring buffer; el health HTTP 200 y la métrica se comprobaron tras estar listo el listener (la primera consulta inmediata al restart ocurrió antes de que aceptara conexión). En esa lectura posterior: `forwarded_total=7`, `forward_errors_total=0`, `ring_drops_total=0`; Fenix registró los eventos posteriores con HTTP 201. Guardian permaneció en auditoría (`guardian_mode_map=0`) y `sentinel-ebpf.service` siguió activo. El nuevo contador de bloqueos reporta 0 después del reinicio; como no se generó un evento malicioso, esa lectura no prueba un incremento positivo, solo que la ruta de despliegue y telemetría está activa.

## Separación del QHC, el runtime de mallas y el reloj — 2026-10-30

La revisión de `Experimentos/EXP_027_YHWH_PULSE_MONITOR.md`, la nota `Experimentos/qm_rev_EXP001_vs_timecrystal.md` de la vault y el código Rust distingue tres rutas que antes aparecían agrupadas como “cristal de tiempo”:

1. **QHC Agent compartido (Fenix):** `me-60os-core/src/bin/qhc_agent.rs` avanza un tick cada segundo y publica `QhcSnapshot` por `/run/soma/qhc.sock`; `QhcTensor` entrega patrón/corrección. Cortex usa el snapshot para su heartbeat/pilot. Eso acredita IPC QHC, no un tick de 41 Hz ni sincronización con Marte/Kingu.
2. **CrystalRuntime de mallas (Cortex/Fenix):** es el runtime de las dos mallas/cristales y memoria A/B, no el servicio de reloj. Su loop usa `std::time::Instant` para llamar `tick_dtc()` a intervalos devueltos por una tabla fija de frecuencias QHC (~41–44 Hz). El método actual aplica fase a ambas mallas y sincroniza SHM en el tick 68. Aunque contiene un `IsochronousClock`, el runtime solo incrementa manualmente su contador; no invoca `tick_internal()`. Las constantes `DTC_CLOCK_SHM`/`DTC_CLOCK_SHM_BYTES` están declaradas pero no tienen lector/escritor en ese archivo. Por tanto, la tabla de fases sí impulsa localmente las mallas, pero no publica una época/tick de reloj compartido para otros procesos o nodos.
3. **NetworkTimeCrystal Python:** permanece como legado no desplegado. El protocolo serializa `perf_counter_ns()` local, `phase_raw=0` está reservado y el consenso de drift no corrige el reloj. No sustituye la ruta Rust ni NTP.

La traza de EXP-027 describe simulación de ticks y codifica sus frecuencias en el código; `get_tick_interval_ns()` devuelve esas frecuencias desde una tabla fija. Eso no es una medición física en vivo del reloj. El paper citado, [Nandi y Vitiello, arXiv:2606.30890](https://arxiv.org/abs/2606.30890), desarrolla dinámica tipo cristal de tiempo y memoria no-Markoviana de un oscilador dual de Bateman; no acredita por sí solo sincronización de relojes entre hosts.

El runtime Cortex sigue registrando `QHC=true`, pero las sondas NPU de cada salto 17 continúan `Valid=false` y `Coherence=false`. **Dictamen afinado:** QHC agent está conectado; QHC modula localmente las mallas; el reloj temporal común entre procesos/nodos y la ruta que haga válida la verificación NPU siguen sin estar aceptados. No se cambió código ni se instaló un servicio de reloj en esta revisión.
