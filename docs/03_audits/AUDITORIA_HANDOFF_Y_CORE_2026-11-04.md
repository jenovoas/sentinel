# Auditoría del HANDOFF y cobertura de pruebas del core — 2026-11-04

**Autor:** Hermes (auditoría) · **Alcance:** notas del `HANDOFF.md` de `personalvault` referidas a Sentinel, más el núcleo `me-60os-core` del repositorio.
**Método:** contraste de cada afirmación con `git log`/`git show`, código fuente, servicios y contenedores en vivo, `/health` de `sentinel-cortex` y ejecución real de `cargo test`. Nada de esta auditoría se basa en memoria ni en resúmenes previos.
**Estado:** auditoría local; no se modificó código de producción, no hubo despliegue, no se hizo commit.

---

## 1. Línea base ejecutada

| Comprobación | Comando | Resultado real |
|---|---|---|
| Rama y árbol | `git status -sb` | `main`, igual a `origin/main`, árbol limpio antes de los cambios |
| HEAD | `git log -1` | `e80439ad fix(core): endurecer aritmética y scheduler SOMA` (2026-11-04 12:08 UTC) |
| Pruebas del core (defecto) | `cargo test -p me60os --lib` | 109 pasan (antes de esta sesión) |
| Pruebas del core (con feature) | `cargo test -p me60os --lib --features extension-module` | 133 pasan, 1 ignorada (después de añadir pruebas) |
| Clippy | `cargo clippy -p me60os --lib` | sin advertencias |
| Formato | `cargo fmt -p me60os -- --check` | conforme |

---

## 2. Verificación de afirmaciones del HANDOFF (Sentinel)

### 2.1 Verificado con evidencia

| Afirmación del HANDOFF | Evidencia observada | Veredicto |
|---|---|---|
| `mem_limit: 512m` para `sentinel-fenix-alloy` y sin OOM | `service-operation/deploy/marte/compose.fenix-agent.yaml:22`; `docker inspect` → `536870912`; uso 59,9 MiB / 512 MiB (11,7 %) | Correcto |
| Huérfano `silly_snyder` en estado `Created` | `docker ps -a --filter status=created` → `silly_snyder Created` | Correcto |
| `switch-backend-traffic.sh` versionado en Kingu | `service-operation/deploy/kingu/switch-backend-traffic.sh`, commit `379cdc91` | Correcto |
| Puente DTC (`charge_from_crystal_energy`, tick maestro 41 Hz, `reset_to_truth`) | `sentinel-cortex/src/main.rs:462`, `DTC_TICK_INTERVAL_NS` en `main.rs:200`; commits `73ee4bf2`, `f68b35c3` presentes | Correcto en código |
| `Valid=true` estable | `docker logs sentinel-cortex` → PULSE CHECK `Valid=true, Coherence=Unison raw=12960000` sostenido; `/health` → `coherence: 12960000` | Correcto en runtime |
| `PROCESSOR RESULT: True` | 407 ocurrencias en los últimos 2000 renglones de log | Correcto |
| `hex_daemon` activo en kingu y marte leyendo el cristal de fenix | `systemctl is-active sentinel-hex-daemon` → `active` en 10.88.0.2 y 10.88.0.6; ambos obtienen `/health` desde 10.10.0.1:8001 | Correcto (el binario real se llama `sentinel-hex-daemon`) |
| Crash loop de `pai-neural` detenido en kingu y marte | `docker ps -a` en ambos: sin contenedor `pai-*` | Correcto |
| Malla `bat0` con 5 vecinos | `batctl n` en fenix → 5 vecinos (vxmc2..vxmc6), `bat0 10.10.0.1/24` | Correcto |
| Replicación de respaldos a kingu | `backup-db.sh` con `KINGU_HOST=10.10.0.2`; `recovery.py` 03:00 con `ssh_host: kingu`; corridas 2026-11-02/03/04 con `restore_verified: true` | Correcto |
| Migración 0006 `mfa_trusted_devices` aplicada | `pinguinoseguro-db-1` lista la tabla `mfa_trusted_devices` | Correcto |
| Grupos AD de la Fase 0 (T1) | `samba-tool group show` OK para `SP-Portal-Admins`, `SP-Guacamole-Remote`, `SP-N8N-Flows`, `SP-Monitoring-View`, `SP-VPN-Access`, `SP-VM-Server` | Correcto |
| Gateway y CLIProxy activos | unidades de usuario activas; listeners `10.88.0.1:8317` y `10.88.0.1:8642` | Correcto |

### 2.2 Incompleto, impreciso o directamente falso

| Afirmación | Evidencia contraria | Veredicto |
|---|---|---|
| «T4 (módulo Podman `tenant-compute`)» consolidado el 2026-10-31 | No existe módulo Terraform: `docs/ops/terraform-tenant-compute.md` es sólo especificación. `grep tenant-compute` no encuentra `.tf`/`.hcl` en el repo | **Falso como implementación**: sólo hay spec |
| «Código trusted-device + `grafana-token` sólo en working tree sin commitear» | `git status` de `pinguinoseguro_web` está limpio; el WIP vive en `stash@{1} wip-previo-trusted-device-grafana-token-20261102` (14 archivos, incluidos `app/api/auth/request/route.ts` y dos suites de pruebas) | Impreciso: está en **stash**, no en el árbol |
| HANDOFF «actualizado 2026-11-03» | El archivo fue modificado 2026-11-04 12:05 y **no registra** el commit `e80439ad` de 2026-11-04 12:08 ni el cambio OpenSpec `remediacion-alertas-clippy` | **Desactualizado** |
| Evidencia OpenSpec: «2.2 scheduler SOMA verificado con escenarios de ventana» | La ventana de portal no abre nunca: 0 aperturas en 681 muestras del ciclo (ver §3.1) y en producción `tasks_in_portal=0`, `efficiency=0`, `dual_lane_portal_open=false` | **Evidencia no válida** |
| «`hex_daemon`» | El binario es `/usr/local/bin/sentinel-hex-daemon` | Nombre impreciso |
| «Malla emitiendo 966k semillas» | No se encontró métrica ni consulta reproducible en esta sesión | **No verificado** |
| «cron diario 03:15 AM» para respaldos de Sentinel (§1, línea de Base de Datos) | Sentinel usa `recovery.py` a las 03:00; el 03:15 corresponde a `backup-db.sh` de pinguinoseguro | Confusión entre dos respaldos distintos |

---

## 3. Defectos del core detectados durante la auditoría

### 3.1 La ventana de portal SOMA es inalcanzable

`QuantumSchedulerCore::phi` construye ángulos como `2π·(t/T)` y los pasa a `SPAMath::sin`, que interpreta la entrada como **grados** (`normalize_quadrants` usa 360 como vuelta completa y `DEG_TO_RAD_FACTOR = π/180`). Con esa mezcla de unidades, la amplitud máxima de `phi` en el ciclo de 68 s es **0,6175** (8.003.279 raw), por debajo del umbral `THETA_RAW = 0,75`.

Evidencia ejecutada: prueba `caracterizacion_la_ventana_de_portal_no_abre_en_el_ciclo_actual` recorre el ciclo a 0,1 s y cuenta **0 aperturas**; en producción `/health` devuelve `tasks_in_portal=0`, `efficiency=0`, `dual_lane_portal_open=false`.

Consecuencia: la ruta de vaciado por portal del `QuantumSchedulerDaemon` (lotes de 2 a 5 eventos) nunca se ejecuta; sólo queda la ruta de overflow. `sin(2π)` en esta semántica da `0,1094`, no `0`.

### 3.2 El «ciclo maestro» de 68 s no es período común

`T_CYCLE = 68 s = 4·T_BIO = 16·T_CRYS`, pero `T_VENUS = 16,18 s` no lo divide (68 / 16,18 = 4,2027). Por eso `phi(68 s) = 0,6175 ≠ phi(0) = 0`: cada vuelta desplaza la fase de la componente Venus. Mientras no se ajuste `T_VENUS` o `T_CYCLE`, el ciclo no cierra y no puede hablarse de «ciclo completo».

### 3.3 Dos motores de coherencia, uno sin carga

`/health` expone `coherence` (ResonanceEngine, cargado desde la energía del cristal) y `bio_coherence_raw` (`bio_resonator`, **0**). El `bio_resonator` se instancia en `sentinel-cortex/src/main.rs:396` y se entrega al `QuantumScheduler`, pero no recibe energía en ninguna ruta: su portal y su eficiencia quedan inertes. El log «Coherence=Unison raw=12960000» corresponde al primero, no al segundo.

### 3.4 Visibilidad de las pruebas de SOMA

`soma/mod.rs` declara `quantum_scheduler` y `anomaly_detector` sólo bajo `feature = "extension-module"`. Con los rasgos por defecto, `cargo test -p me60os --lib` **no ejecuta ninguna prueba de SOMA**; hay que usar `--features extension-module` o `--all-features`. Toda la evidencia de OpenSpec que cite «pruebas del scheduler» debe declarar el rasgo utilizado.

### 3.5 Cobertura previa del núcleo aritmético

`me-60os-core/src/spa.rs` (tipo `SPA`, escalas, operadores, conversiones) **no tenía ni una prueba unitaria** antes de esta sesión. Lo mismo ocurría en `soma/quantum_scheduler.rs`, `soma/anomaly_detector.rs`, `s60_pid.rs`, `quantum_core.rs`, `shm_bridge.rs`, `guardian_lsm.rs`, `resonant_loop.rs`, `time_crystal.rs`, `hexagonal_control.rs`, `soma_orchestrator.rs`, `physics.rs`, `scv.rs`, `qhc.rs`, `bcm.rs`/`bio.rs`, `agent_manager.rs` y `adm.rs`.

### 3.6 Brechas menores confirmadas

- `pai60_lib::is_regular` reconoce denominadores regulares que la tabla no cubre (p. ej. 72 = 2³·3²): `pai60_divide` devuelve `None` aunque el recíproco sea finito en base-60.
- `SPA::from_raw(i64::MIN)` desborda en `raw.abs()`; no hay prueba ni contrato documentado para ese límite.
- `QuantumBuffer` usa dos umbrales distintos (`overflow_limit` para `is_overflow`, `2·overflow_limit` para descartar) y sólo contabiliza `stats_dropped`, no `stats_overflow`, en el descarte por `push`: la métrica `efficiency` no refleja esos descartes.
- El commit `e80439ad` añade la regla 6 de `AGENTS.md` («no modificar prototipos Python») y en el mismo commit modifica `quantum/yatra_core.py`. La regla no puede aplicarse retroactivamente, pero la contradicción debe quedar registrada.

---

## 4. Pruebas unitarias añadidas (esta sesión)

| Archivo | Pruebas | Qué fija |
|---|---:|---|
| `me-60os-core/src/spa.rs` | 13 | Biyección `from_raw`/`to_raw`, exactitud de 1/3, 1/6 y 1/12, trampa `from_int` vs `from_raw`, suma/resta inversas, desbordamiento explícito, producto y división exactos entre SPA, `div_safe` vs división por cero, doble semántica de `%`, signo/valor absoluto, `TWO_PI`, conversión legacy de tertias |
| `me-60os-core/src/soma/quantum_scheduler.rs` | 8 (1 ignorada) | `phi(0)=0`, amplitud acotada a ±1, determinismo bit a bit, coherencia entre `is_portal_open` y el umbral, caracterización del portal cerrado, invariante deseado del portal (ignorada), relaciones enteras del ciclo maestro, no periodicidad por Venus |
| `me-60os-core/src/pai60_lib.rs` | 3 nuevas | Recíprocos exactos para los 25 denominadores de la tabla, `None` para no regulares, brecha de regulares fuera de tabla |

Totales: `cargo test -p me60os --lib` → **126 pasan**; `cargo test -p me60os --lib --features extension-module` → **133 pasan, 1 ignorada**; `cargo clippy -p me60os --lib` limpio; `cargo fmt --check` conforme.

---

## 5. Lo que esta auditoría NO verificó

- Contenido de la malla en laptop, hercules y ocean (no se accedió a esos nodos).
- La afirmación de las 966k semillas en la malla.
- El estado de OpenCode en kingu y hércules, y OMP en ocean.
- El comportamiento del portal con sesión autenticada real en navegador.
- Rendimiento, latencia o disipación del lattice: no se ejecutaron benchmarks.
