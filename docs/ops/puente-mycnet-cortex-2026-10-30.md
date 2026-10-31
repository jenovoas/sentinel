# Puente MyCNet → CrystalRuntime Cortex — 2026-10-30

## Alcance y preflight

Trabajo autorizado en Fenix, rama `main`/systemd; no se mezcla `alpine_fenix`. Se preservan cambios previos de `Cargo.lock`, Compose y Guacamole. El agente principal integra los cambios y sus commits; el agente del puente no publica por separado. Referencias normativas: [procedimiento estándar](procedimiento-despliegue-estandar.md), [procedimiento multinodo](../PROCEDIMIENTO_DESPLIEGUE_MULTINODO.md) y T8 de [fase0-tareas](fase0-tareas.md).

Antes del cambio: Cortex `sentinel-cortex:8f0423f3`, imagen `sha256:9f97d8acaae4c21fb30b113205a407c1b79b810466ea830c28b1c23dab334227`, en estado healthy; `sudo -n true` pasa. MyCNet host escucha `10.88.0.1:7474/TCP` y `10.88.0.1:4242/UDP`, no en la gateway Docker de la URL efectiva anterior `ws://172.20.0.1:7474/api/v1/stream`. Cortex tiene `eth0` con salida por `172.29.0.1` y dirección `172.29.0.2`; su otra red efectiva es `172.25/16` (no asumir el antiguo `172.20/16`). Zona Docker efectiva con target `ACCEPT`.

## Cambio implementado

- `sentinel-cortex/src/mycnet_stream.rs` sustituye el bloque WS permisivo del `main`: conexión/handshake acotados a 10 s, espera entre frames a 30 s (MyCNet emite `mesh_tick` cada segundo), reconexión a 5 s. No hay operación de suscripción adicional: `api.rs::handle_ws` de MyCNet suscribe al broadcast tras el upgrade HTTP.
- Parser tipado: únicamente `fractal_seed_ingested` produce `CrystalInput::Security`; exige `token_id: u32` y `amplitude_s60: i64`. Rechaza explícitamente bool, float, string, null, ausencia y desbordamiento; no convierte errores en cero. `amplitude_s60=0` válido sigue siendo cero. Otros tipos del stream no inyectan.
- Conversión exacta `SPA::from_raw(amplitude_s60)`, sin `from_int` ni segunda escala. Se conserva el mapeo existente `token_id % 64`.
- Cola llena y canal desconectado dejan evidencia de rechazo. El log de aceptación se emite **solo en el hilo propietario de CrystalRuntime**, después de actualizar lane A; incluye token, índice, amplitud raw recibida y amplitud raw resultante. No se confunde encolado con inyección.
- Importación remota actualiza lane A con suma entera comprobada, rechaza índice inexistente/desbordamiento y no publica inmediatamente la semilla importada de nuevo al ring SHM. No modifica lane B directamente, scheduler, bio ni drive térmico continuo.
- `config/systemd/sentinel-cortex-uplink.env.example` fija la URL privada real. `scripts/configure-cortex-uplink.sh` cambia únicamente esa URL y el tag Cortex de `/etc/sentinel/backend.env`, prepara un archivo protegido, valida Compose sin imprimir secretos, guarda backup y conserva `root:docker 0640`. La recreación se limita a `cortex --no-deps --no-build`.

## Realimentación: alcance de la prevención

Fuente MyCNet inspeccionada: `state.rs::ingest_remote_seed` emite `fractal_seed_ingested` después de aceptar un datagrama UDP. `poll_local_fractal_seeds` consume SHM e inyecta MyCNet local, pero **no** emite ese evento WS. El contrato actual no incluye bool `remote`, dirección origen, identificador global ni hop count: exigir campos inventados impediría toda recepción y el token por sí solo no demuestra origen Marte.

Se corta el eco inmediato importación remota → publicación SHM del mismo seed. Siguen exportándose el estado de lane A por SHM y las semillas periódicas del runtime DTC; los peers pueden recibir estado derivado y devolverlo. Por ello esto **no** demuestra ausencia de realimentación distribuida ni protección frente a replay. No se inventaron deduplicación/TTL ni una arquitectura de transporte alternativa. Correlación Marte→Fenix requiere evidencia simultánea del uplink/UDP MyCNet y del token aceptado por Cortex.

## Qué significa la evidencia

- Handshake HTTP 101 y recepción de frames desde el contenedor prueban conexión y suscripción, no aceptación de una semilla ni resonancia.
- Log de aceptación en el hilo del cristal acredita recepción/aplicación software del valor raw. Para raw=0 no acredita excitación no nula; una amplitud previa no nula puede venir de drive local, PID u otros eventos.
- QHC externo (snapshot IPC consultado cada segundo) y DTC local son distintos: el runtime DTC usa intervalos software alrededor de 23.94 ms (aprox. 40–43 Hz según modulación). El campo `qhc_tick` de CrystalRuntime es un contador propio, no el tick del agente QHC externo. No se alteran sus algoritmos.
- Ni nombres, SHM, healthcheck ni ticks software prueban reloj sincronizado distribuido, dispositivo cuántico/fotónico/fonónico físico, latencia end-to-end ni un veredicto de seguridad/HITL.
- No se inspecciona portal ni se modifica enforcement eBPF, Docker global, proxy/DNAT, reglas globales o servicios ajenos.

## Pruebas finales realizadas

`cargo test --locked --package sentinel-cortex --bin sentinel-cortex`: **59 pasan, 1 falla** (60 totales). Pasan las cinco pruebas de `mycnet_stream` (tipos inválidos, cero válido, raw exacto, canal lleno/desconectado y handshake/frame WS real de loopback) y la prueba de inyección remota de CrystalRuntime (lane A, lane B intacta, índice inválido, cero y overflow). Falló `tests::test_truth_claim_handler_smoke_aiopsdoom_intercept`, aserción `verification_time_us.is_number()` en `main.rs:1782`. No se repitió ni se cambió esa ruta de TruthSync; la causalidad respecto del cambio no está establecida. La suite completa no está verde.

Al integrar se retiró la prueba permanente de eco WebSocket (solo comprobaba
cableado); la evidencia de conexión real del smoke se conserva abajo.

## Seguridad de la captura

Durante diagnóstico se imprimió accidentalmente `Config.Env` completo en la salida interna de una herramienta. No se copian valores a esta nota ni a la vault. Credenciales afectadas por nombre: `SECRET_KEY`/`SENTINEL_JWT_SECRET`, `POSTGRES_PASSWORD`, `REDIS_PASSWORD` (y URLs derivadas `DATABASE_URL`, `REDIS_URL`, `SENTINEL_REDIS_URL`), `INTERNAL_TELEMETRY_TOKEN` y `GF_ADMIN_PASSWORD`. Main fue notificado; requieren rotación coordinada con sus consumidores, **no ejecutada** en este cambio. Las siguientes capturas usan campos permitidos y nunca el entorno completo.

## Despliegue y smoke observados en Fenix

- Build release con `scripts/build-sentinel-cortex-image.sh sentinel-cortex:8f0423f3-uplink-a1e1fe4a1045` correcto; imagen `sha256:878ce8ddc65a4e10fe2aa70cdb71d5d0db6742724faf28bd9d206201d84b6bf3`. El sufijo identifica la huella de los archivos del cambio, **no un commit publicado**; árbol con cambios autorizados sin commit.
- `sudo -n bash scripts/configure-cortex-uplink.sh ...` validó Compose y guardó `/etc/sentinel/backend.env.pre-cortex-uplink-20261030T235426Z`. Después, `sudo -n docker compose --env-file /etc/sentinel/backend.env -f docker-compose.fenix.yml up -d --no-build --no-deps --wait --wait-timeout 90 cortex` recreó únicamente Cortex y terminó `Healthy`. No se recargó Firewalld ni se reinició Docker.
- Captura propia 2026-10-30 23:55:22 UTC: contenedor con tag/digest anteriores y `healthy`; entorno privado sigue `root:docker 0640`; `curl` dentro del contenedor a `/health` devuelve `status=OK`, QHC `connected=true`, `stale=false`, tick `69382`.
- Logs del contenedor: a **23:54:37.347 UTC**, handshake WebSocket `status=101`; a **23:54:37.356**, recepción del primer frame del stream. Demuestra conexión/suscripción desde la red efectiva de Cortex al listener privado real.
- El hilo CrystalRuntime restauró checkpoint de 67.951 nodos (tick propio `2921883`). A **23:54:41.628**, aceptó `token_id=647121428`, `index=20`, `amplitude_raw=0`, `crystal_amplitude_raw=16634433`; a **23:55:18.279**, aceptó `token_id=626267908`, `index=4`, `amplitude_raw=0`, `crystal_amplitude_raw=16177561`. Es aplicación software de cero, **no** excitación atribuible al evento remoto.
- `PULSE CHECK` reportó `QHC=true` en ticks externos `69343`, `69360`, `69377`, pero también `Valid=false, Coherence=False`. No elevar la recepción al estado de veredicto/coherencia válida.
- El endpoint DTC existe bajo autenticación. No se encontró archivo de sesión autorizado en las ubicaciones operativas consultadas; no se generó un JWT ni se quitó middleware. No hay medición de tasa DTC 40–43 Hz en esta captura.
- Riesgo de recreación existente: CrystalRuntime reinicializa `head` del ring de semillas a cero; un lector MyCNet vivo puede conservar un `last_tail` anterior y pausar exportación hasta recuperar/reabrir el ring. Se notificó a Main (dueño MyCNet); la entrada UDP→WS y la aceptación observada no dependen de ese lector SHM.

Rollback preparado, no ejercido: conservar imagen anterior y backup; restaurar únicamente ambas claves Cortex desde el backup protegido y recrear solo `cortex --no-deps --no-build`, con validación Compose previa. No restaurar ciegamente todo el entorno si otros consumidores lo han cambiado.

## Correlación final de evento realmente emitido

Captura propia a **2026-10-30 23:57:56 UTC**: por SSH privado a Marte (`-p 4222`, `sudo -n`) se leyó una ventana final acotada del WAL `/var/log/sentinel/guardian_security_wal.jsonl`, extrayendo exclusivamente `event_id`, PID, tipo y `entropy_s60_raw` de doce eventos. Se calculó `token_id` con el mismo código de `guardian-uplink`: `DefaultHasher::new()`, `event_id.hash(&mut h)`, `h.finish() & 0xFFFF_FFFF`. El helper Rust se ejecutó sobre esos identificadores reales y se eliminó; no se generaron ni enviaron semillas de prueba.

Los **12/12 identificadores calculados** aparecen en los logs de aceptación de CrystalRuntime ya capturados en Fenix (normalizando únicamente secuencias ANSI para comparar). Tres ejemplos:

| event_id del WAL Marte | PID | token_id | Aceptación Fenix UTC | Índice lane A | raw recibido → raw resultante |
|---|---:|---:|---|---:|---|
| `guardian-alpha-80939895600467-225424-EXEC_ALLOWED` | 225424 | 1781737057 | 23:57:50.202401 | 33 | 0 → 17374162 |
| `guardian-alpha-80940394451675-225427-EXEC_ALLOWED` | 225427 | 2796910440 | 23:57:50.536937 | 40 | 0 → 17790892 |
| `guardian-alpha-80945644173814-225437-EXEC_ALLOWED` | 225437 | 711715798 | 23:57:55.950191 | 22 | 0 → 16797993 |

Esto acredita eventos Guardian efectivamente presentes en WAL Marte → token de transporte → aceptación software real en lane A de Cortex Fenix. Un hash u32 no es una identidad global sin colisiones ni una firma criptográfica. No acredita excitación remota no nula: los doce eventos transportan exactamente raw0 y las amplitudes resultantes incluyen el estado previo.

Límite de la sonda coordinada: Main informó que `/usr/bin/true`, PID **225249**, terminó con código 0 pero no apareció en el WAL observado durante **22 s**. No se atribuye a esa sonda ninguna de las filas anteriores ni se declara captura completa de todo `exec`. Se usaron eventos que sí fueron emitidos, no una cadena sintética. `/api/v1/crystal_runtime/status` sin sesión devolvió **401** en el contenedor; frecuencia DTC continúa no medida.

## Continuidad de SHM corregida — 2026-10-31

La limitación de reinicio descrita arriba se corrigió sin cambiar el contrato
binario del ring. `initialize_fractal_ring` conserva el head publicado al abrir
un objeto POSIX válido bajo el lock de escritor único. La cabecera desconocida
se rechaza sin resetear su contador. `PySharedBuffer::load_u64_acquire` comprueba
mapping abierto, alineación y límites antes de la lectura atómica.

MyCNet limita su cursor a las últimas1024 posiciones retenidas y recupera una
disminución observada de head. Se reprodujo antes el fallo de overrun: tokens
1024–1055 en vez de40–71; la regresión pasa con el lector corregido.

Verificación:37 pruebas del workspace MyCNet y5 pruebas seleccionadas de
CrystalRuntime pasan. Estas últimas prueban reapertura del productor con el
head publicado conservado, header desconocido, mapping cerrado y las2 pruebas
anteriores del runtime. No se repitió el fallo TruthSync ni se declara verde la
suite completa; la compilación mantiene avisos de código no utilizado.

Despliegue Fenix: MyCNet SHA256
`4a2d1675a6e85e30a7901f149cc5abc264627b8e310269ce581eedfdbd643c0b`;
Cortex `sentinel-cortex:8ee902e9-shm-continuity-2`, imagen
`sha256:5392ea57246d58c86487c260124c3869774412675607bae2af8a21b4f1f4a2d1`.
Entre00:16:12 y00:16:53 UTC se recreó únicamente Cortex, que terminó healthy,
sin reiniciar MyCNet (PID1759643), Docker global ni Firewalld.
Backup de entorno: `/etc/sentinel/backend.env.pre-cortex-uplink-20261031T001612Z`;
el script modificó solo las claves Cortex permitidas.

Tras la recreación: WS101 a00:16:23.122 y token1836041237/raw0 aceptado a
00:16:23.545. Marte reportó72091 recepciones acumuladas desde Fenix.

Observación continua de180s, con intervalo solicitado de100ms, manteniendo
abierto el mapping anterior a la recreación:

| Campo | Antes | Después |
|---|---:|---:|
| Head publicado | 55908 | 63866 |
| Envíos MyCNet acumulados | 43550 | 83360 |
| Inode SHM | 25 | 25 |
| PID MyCNet | 1759643 | 1759643 |

No se observaron retrocesos de head; fuente conectada al inicio y al final.
Esto no mide latencia por evento ni acredita frecuencia DTC.

Alcance: cierre/reapertura del mismo objeto SHM, que PySharedBuffer no elimina
al salir. No cubre unlink/reemplazo manual del objeto, garantía de entrega bajo
overrun, persistencia al reiniciar el host, reloj distribuido ni medición DTC.
La corrección no cambia fases, modulación, amplitudes o modo eBPF.

Publicación: Sentinel `28945cd7` y MyCNet `2ed55f0`, ambos en `main`.
Memoria persistente de la prueba: vault `db8ac96`.

Graphify: MyCNet completó actualización AST local (2241 nodos,2543 aristas).
En Sentinel la extracción de80 archivos terminó, pero el comando no completó
la actualización del grafo dentro de300s y fue terminado por timeout. No se
declara ese índice actualizado. También informó extractor SQL ausente y
extracción parcial en dos archivos C ajenos a este cambio; no se alteraron
dependencias ni esos archivos para cerrar esta corrección de SHM.
