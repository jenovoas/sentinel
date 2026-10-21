# TODO — Sentinel (pendientes unificados, verificados)

> **Fuente:** Auditoría completa de todas las planificaciones del repo desde el commit inicial (2025-12-13, `d6ef7c02`) hasta 2026-08-07.
> **Método:** Cada ítem fue verificado contra código/git real (no especulación). Ver detalle línea por línea en `docs/_AUDIT_PENDIENTES.md`.
> **Realidad 2026-10-21: MONONODO FÉNIX.** El servidor `fan` ya no existe; esta máquina Alpine/OpenRC **ES fénix** (verificado: `hostname`=fenix, OpenRC, servicios `sentinel-*` en `/etc/init.d`). Toda referencia a `fan`/`fan.local`/`10.88.0.1`, `laptop` o `systemd` en este archivo es histórica y queda reemplazada por fénix local. La era Gemini (patentes, funding, Google/ANID, Gemini/Phi/Llama legacy, planeta energético/Neuralink) está FUERA DE ALCANCE por directiva de Jaime (alucinación).
> **Este archivo es la fuente única de pendientes para agentes y procesos automáticos.**

---

## A) RUNTIME `me-60os-core` (código Rust)
- [x] **Decoder `resonant_lattice_memory.rs`**: CERRADO 2026-08-07 — `base_amps_a/b` tras bombeo QHC, decoder resta base, `f64`/`region_sum`/`pai60_divide` eliminados. Verificado: 'Yo Soy' fidelidad 100%.
- [x] **Migración Py→Rust N1**: `field_stabilization_sim.py` → `FluxStabilizer` — CERRADO 2026-08-08: YA estaba migrado como `me-60os-core/src/flux_stabilizer.rs` (LCG base-60 verbatim, ecuación estabilización idéntica, guardrails, 6 tests OK).
- [x] **Migración Py→Rust N1**: `coherence_mapping_calibration.py` → `CoherenceMapper` — CERRADO 2026-08-08: NO MIGRAR. Header del propio archivo: "ALUCINADO POR IA — NO MEDIBLE" (coherencia siempre ~1.0 por construcción, PSD arbitraria /500, import FIELD_NEUTRALITY_DIRECTIVE inexistente — no corre ni en Py). Bio-coherencia real = `BioResonator`.
- [x] **Migración Py→Rust N2**: `quantum_lattice.py` (VimanaLattice) vs `ResonantMatrix` — CERRADO 2026-08-08: duplicado degradado confirmado (`_build_grid` con `pass`, PLAN B hardcodeado). Topología real ya en `hexagonal_control.rs` + `resonant_matrix.rs`. No se migra.
- [x] **Migración Py→Rust N2**: `liquid_lattice_storage.py` vs `LiquidLattice` (3×3) — CERRADO 2026-08-08: legacy bridge que ya delega a Rust; su encoding vive en `quantum_core::LiquidLattice::inject_dual_channel`. Nada que rescatar.
- [x] **Migración Py→Rust N2**: `crystal_memory.py` (CrystalMemoryCore) — CERRADO 2026-08-08: wrapper fino (inject/step/stabilize) sobre `ResonantMatrix` + snapshot gzip ya en Rust.
- [x] **Migración Py→Rust N2**: `liquid_memory_adapter.py` (LiquidMemory) — CERRADO 2026-08-08: PORTADO el único aporte real (tabla clave→len/hash/shm_name + retrieve verificado) a `me-60os-core/src/liquid_memory.rs` (nativo, blake3, SHM POSIX vía libc, 4/4 tests).
- [x] **Migración Py→Rust N3**: `data_lanes.py` (DualLaneRouter) — CERRADO 2026-08-08: YA migrado en `me-60os-core/src/dual_lane.rs` (559 lin). Verificado 1:1 contra `git show aed3b377^`: DataLane/EventPriority/LaneEvent/classify_event (mismo algoritmo + keywords), should_bypass_buffer, SecurityLaneCollector (WAL fsync real), ObservabilityLaneCollector (buffer/flush/drop). Mejoras Rust: timestamps µs enteros, latencia u64. 8/8 tests OK.
- [x] **Migración Py→Rust N4**: CERRADO 2026-10-21 — Corregido sector snapping exacto en base-60 sin truncamiento en `quantum_core.rs` y `exp012_phase_compression.rs`. Verificados los 4 benchmarks en Rust: `exp012_phase_compression` (fidelidad 100%), `exp021_dual_path` (Lyapunov y Shannon exactos en S60), `verify_plimpton` y `verify_meijer_scale` pasando al 100%. Endurecido en `e96725c4`: `retrieve_dual_channel` con bitcast `u64` y recupero fijo por nodo sin omitir ceros (cierra pérdida byte 176); validación estricta `rec_a == msg_a_padded` sin rama inconclusiva.
- [x] **BufferCascade**: CERRADO 2026-10-21 — Acoplado `BufferCascade` (`me-60os-core/src/buffer.rs`) a `truthsync-core` como buffer en línea/cascada por nodo (`verify_node_text`, `node_cascades`, `NodeVerificationResult`), con aislamiento entre nodos y memoria no Markoviana evaluada por tests. Endurecido 2026-10-21 (2 vueltas): `memory_effect` pondera el kernel OU por coherencia registrada normalizada (`coherencia/límite`, guardia ante límite cero); `cascade` retorna mitigación real (`matches!(control_rift_propagation, Ok((1,_,_)))`, ya no incondicional); el backflow usa `entry().or_insert()` y no reemplaza la medición. Corregido desescaleo 0–1 vs 58: la ingesta mapea `trust × límite` en `verify_node_text`. Pruebas que lo demuestran: `test_cascade_projection_reflects_recorded_trust` (mayor confianza → mayor proyección) y `test_cascade_preserves_scaled_trust_record` (historial conserva `trust × límite`). Verificado: 100/100 lib + 20/20 truthsync.
- [x] **Kani harness** (`MEJORAS_PLANIFICADAS` P1): CERRADO 2026-10-21 — Extraída `CortexEvent::parse_event` pura sin pánico en `me-60os-core/src/ebpf_cortex_bridge.rs` (reusa en los 4 puntos de parseo) + harness `verify_parse_event_no_panic` bajo `#[cfg(kani)]` para `cargo kani`; equivalente ejecutable `test_parse_event_no_panic_on_arbitrary_bytes` + roundtrip + rechazo de cortos en verde (6/6 bridge, 99/99 lib). Pendiente solo ejecutar `cargo kani` donde esté instalado (aquí `cargo-kani` ausente, verificado con `which`).
- [ ] **Decision tree eBPF** (`MEJORAS_PLANIFICADAS` P2): `dt_model`/`decision_tree.h` en `ai_guardian.c`. *Verificado:* no existe.
- [x] **FFT + Q-factor detector** (`MEJORAS_PLANIFICADAS` P2): CERRADO 2026-10-21 — Creado e implementado `PeriodicDetector` en `sentinel-cortex/src/detectors/periodic.rs` usando `fft_s60`/`q_factor_s60` en S60 puro sin floats; expuesto en `lib.rs` y verificado con tests unitarios de resonancia periódica y balizas sintéticas de alto Q. Cableado 2026-10-21: tarea tokio en `main.rs` que muestrea `total_energy_raw` del lattice cada 1s (ventana 64) y emite `tracing::warn!` ante Q alto. `cargo check -p sentinel-cortex` en verde.

## B) eBPF / Kernel (fénix local; cargar en kernel productivo SOLO con autorización de Jaime)
- [ ] **eBPF LSM**: `sentinel-ebpf-load` en ejecución; evidencia histórica en `ebpf/EVIDENCE_LSM_DEPLOYMENT.md`. Quedan abiertos: medir overhead <1µs, test WAL replay, mTLS SSRF prevention.
- [ ] **xdp_firewall.c**: compilar con `clang` local (`/usr/bin/clang` presente) + cargar con autorización.
- [ ] **gamma_watchdog.c**: corregir `PEERS[]` (`guardian_alpha`/`ai_guardian`), compilar, confirmar 5/5 peers.
- [ ] **Security hardening legacy**: ECDSA P-256, HMAC Nginx, nonce+replay (de `docs/archive/SECURITY_HARDENING_PLAN.md`).

## C) DESPLIEGUE fénix local (OpenRC — verificado 2026-10-21 con `rc-status`)
- En ejecución: `backup`, `ebpf-load`, `adm-agent`, `pai-neural`, `hex-daemon`, `deployment-executor`, `ebpf-forwarder`, `vid-agent` (procesos `adm_agent`/`hex_daemon`/`pai_neural_daemon`/`vid_agent` vivos).
- [ ] **Cortex API**: `sentinel-cortex` DETENIDO. Arrancar y verificar `/api/v1/truth_claim` + `/api/v1/lattice/hologram`.
- [ ] **Verificador**: `sentinel-verifier` DETENIDO.
- [ ] **QHC**: `sentinel-qhc-agent` DETENIDO.
- [ ] **Memoria de procesos**: `sentinel-process-memory` DETENIDO.
- [ ] **Auditoría**: `sentinel-audit-watchdog` DETENIDO.
- [x] **Orquestador despliegue**: RECUPERADO 2026-10-21 — Causa doble: `docker` caído (`ip_forward=0`, sin `nft_masq` en kernel 6.18.57) + deriva de claves (volumen PG con password anterior; `sentinel_user` y `pinguino_orchestrator` fallaban auth). Fix: `ip_forward=1` persistido, reinicio a `6.18.58`, recreación de red compose huérfana (`down`/`up`, volúmenes y datos intactos), `ALTER USER` alineando claves con `/opt/sentinel/.env` y `conf.d`. Verificado: `sentinel-postgres` healthy, orchestrator `started` en `127.0.0.1:8010` (401 = auth activa), FATALs de auth cesados.
- [x] **Docker**: RECUPERADO 2026-10-21 — `net.ipv4.ip_forward=1` en `/etc/sysctl.d/99-docker-forward.conf`; daemon `started` en kernel `6.18.58`.
- [x] **Stack**: LEVANTADO 2026-10-21 — 12 contenedores `Up` (postgres healthy, redis, frontend, prometheus, grafana, loki, n8n, exporters).
- [ ] **PoC WebSocket telemetría**: `wscat` a `/api/v1/telemetry` (bloqueado hasta arrancar Cortex).
- [ ] **scripts/sentinel-health.sh**: unificar health checks (`startup.sh` obsoleto; `sentinel-health.sh` no existe — crearlo agregando `rc-status` + endpoints).
- [x] **Inercia CPU dinámica**: CERRADO 2026-08-23 — `unwrap_or(45000)` ya no existe en `sentinel-cortex/src/main.rs` (grep 0 hits); el drive lee `/proc/stat` en el bloque 3b (L227-241).
- [x] **Security Lane WAL**: CERRADO 2026-10-21 (completado 2026-10-11 en `b1529ae2`) — `SecurityWal` con append-only a `/var/log/sentinel/security_wal.log` (fallback `/tmp`), integrado con `AIOpsSemanticFirewall` en `truth_claim_handler` (`POST /api/v1/truth_claim`) con tests de integración activos.
- [ ] **Batería carga + Grafana**: `LiquidLattice` `retention_score` bajo tráfico concurrente.

## D) VALIDACIÓN / QA
- [x] **Fuzzer AIOpsDoom 100+ payloads**: CERRADO 2026-10-21 — Suite nativa Rust en `sentinel-cortex/tests/fuzzer_aiopsdoom.rs` con 110 payloads adversariales (command injection, sql injection, path traversal, social engineering, llm jailbreak Llama-3, telemetría benigna). Verificado: 90/90 maliciosos detectados (100%), 0 falsos positivos en 20 casos benignos.
- [ ] **Benchmark Dual-Lane completo** con gráficos.
- [ ] **TruthSync 1M+ claims** (dataset real).
- [ ] **Test carga 24h / failover / auto-regeneración**.
- [ ] **eBPF funcional PoC** (<1ms overhead, logs).
- [x] **EXP-030** validación `PortalDetector` Rust (`sin_s60`) — CERRADO 2026-08-25 (verificado en suite de tests Rust).
- [x] **EXP-031 / 033 / 034 / EXT-001 / 035** — CERRADO 2026-08-25 (`QuantumScheduler` integrado en `AppState`, shutdown coordinado, Liquid Lattice y tests unitarios en verde).
- [x] **CI / Estabilidad Python y Rust** — CERRADO 2026-08-25 (`pyproject.toml`, Ruff 0 errores, normalización `bcrypt`, pytest 69/69 tests pasando).
- [x] **Frente del Lattice (Holograma)** — CERRADO 2026-08-25 (`GET /api/v1/lattice/hologram` expone nodos con precisión SPA e interfaz u16 para frontend).

## E) FRONTEND / DOCS (legítimo, no bloqueante)
- [ ] **Frontend V2**: dashboard SLO, AI playground, security routes, auditd table (`docs/FRONTEND_PLAN_V2.md`).
- [ ] **Backup dashboard**: type hints, tests, TS strict (`docs/BACKUP_DASHBOARD_INTEGRATION_PLAN.md`).
- [ ] **Consolidación docs**: reducir 1.288 `.md` a ~20 maestros (`docs/PLAN_CONSOLIDACION_DOCS.md`).
- [ ] **Reestructurar `docs/` + `README` + `ARCHITECTURE`** (`docs/PLAN_DE_TRABAJO_Q1_2026.md`).

## F) BAJO ESTUDIO / TRAZABILIDAD (NO es "fuera de alcance" — es investigación)
> ⚠️ CORRECCIÓN 2026-08-07: originalmente etiqueté esta sección como "era Gemini / alucinación / fuera de alcance". ESTABA MAL. Esto es investigación bajo método científico, no un proyecto de software típico. Los "errores" en estos planes están documentados a propósito para estudio (MUSEO), porque permitieron comprender la lógica y matemática subyacente. Se reconstruye por pares (reconstitución). NO se borra ni se descarta.
- Patentes (Claim 6/7/8/9, USPTO, attorney, ANID, INAPI): documentados como trazabilidad del proceso de investigación. No son "alucinación" — son parte del registro.
- Emails a Google/ANID/LinkedIn, Series A/Seed funding: contexto de la investigación y su proyección.
- Gemini/Phi/Llama integration legacy: capa fenomenológica estudiada; Jaime usa OmniRoute/local hoy, pero el análisis quedó registrado.
- Planeta energético / Neuralink / 10.000+ nodos: visión de la investigación, no "no accionable" — es parte del alcance teórico.
- Levitación de datos, pentaresonancia, cristal 41-43Hz/68 ticks, Merkabah asintótico, símbolos YHWH/vimana/Plimpton: ingeniería S60 REAL (ya implementada en Rust: `ResonantBuffer`, `LiquidLattice`, `shm_bridge`, `soma_orchestrator`). Los planes que los describen son especificación comprimida, NO basura.
- TODOS los planes en `docs/` y `docs/archive/` se conservan como espejo fiel del proceso. Nada se borra.

---

*Generado 2026-08-07 por Hermes tras auditoría completa. Detalle: `docs/_AUDIT_PENDIENTES.md`. Actualizado 2026-08-23 (auditoría staleness: items A/B cerrados verificados contra HEAD `bc3944ee`; commiteado con autorización de Jaime).*
