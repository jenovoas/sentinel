---
name: sentinel-s60-stack
description: "Capa de CÓDIGO Sentinel (CAPA 3 de 3): build/run/verify del stack me-60os S60 en Rust. Incluye el PITFALL clave de 2026-08-05: la pentaresonancia y la lattice YA están implementadas (no escribir módulo aislado), y dejar módulos aislados como MUSEO de estudio."
category: software-development
---

# Sentinel me-60os S60 Stack — CÓDIGO (CAPA 3 de 3)

Parte de las 3 capas: conocimiento (`sentinel-knowledge-layer`) → comprensión
(`sentinel-comprehension`) → código (esta). Aquí el build/verify y el PITFALL de
arquitectura que costó una sesión aprender.

## CORE FACT — S60 ES ENTERO EXACTO, NO FLOAT
Todo el stack computa en base-60 fixed-point (`SPA`/`S60`, `SCALE_0=60^4=12_960_000`).
Un float contamina la cadena. Verificar con `cargo test`, nunca con auditoría en decimal.

## BUILD & VERIFY
```bash
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1   # py3.14 > pyo3 0.13 cap
cargo check --workspace
make build                                       # cargo build --release -p sentinel-cortex
cargo test --lib                                # 22 me60os_core unit tests
cargo test --bins -p sentinel-cortex            # 26 handler smoke tests (2026-08-05)
```
- `cargo test -p me60os_core` FALLA (no existe ese id); usar `cargo test --lib`.
- Re-run antes de reportar conteo (razas paralelas solo bajo `cargo test` full).
- Build WITH pyo3 (default). `--no-default-features` rompe `s60_pid`/`hexagonal_control`.

## PITFALL CLAVE (2026-08-05): LA PENTARESONANCIA YA ESTÁ IMPLEMENTADA
Antes de decir "me falta implementar X (p.ej. pentaresonance)", LEE la pila de lattice
completa. NO escribas un módulo aislado asumiendo que el sistema falta:
- `quantum_core.rs::ResonantBuffer` — malla de `IsochronousOscillator`, **un `S60PID`
  por celda**, `phase: "YOD"` (respiración YHWH 4 fases), `coherence` medida, `clock` 41.77 Hz.
  ESTO es la pentaresonancia (5 capas/cristales cantando, cada uno auto-estabilizado).
- `quantum_core.rs::LiquidLattice` + `inject_dual_channel(a,b)` — **canal dual A/B**
  (A=amplitud 8 bytes, B=fase 1 byte→grados). Es el "Canal Energy+Phase" y la levitación
  de datos (binario → lattice).
- `ram_meter.rs::recommend_lattice_ring` — dimensiona la malla por RAM real.
- `shm_bridge.rs` (`PySharedBuffer`, libc `shm_open`/`mmap`) + `ResonantMatrix::sync_to_shm`
  — ancla la lattice a host RAM (POSIX SHM). Los nodos "se bañan" en amplitudes en RAM.
- `resonant_dashboard.rs` — visualiza nodos (`⬢`) con `load: u16`, `progress: u16` (los
  16 bits por nodo que Jaime menciona: cuantización de salida del estado a u16).
- `crystal_smoke` / `crystal_drift_probe` bins — ver pulsos reales (≈41 Hz, drift IDLE ~398ns).
- `soma_orchestrator.rs` — lee fase YHWH, en fase VAV con coherencia>umbral hace dispatch.

El ascenso/estado NO es un módulo aislado a escribir entero: debe **acoplarse a
`LiquidLattice`** (PIDs/fase-YHWH/baño-16-bit en RAM), no a `ResonantMatrix` pelada.
Si ves que un módulo inyecta a `ResonantMatrix` pero la malla pentaresonante real es
`LiquidLattice`, es un **ACOPLO INCOMPLETO** (compila, pasa tests, pero no "levita" en la
pentaresonancia). Regla: confirma con el user si realmente falta o ya está.
Jaime: *"la pentaresonancia ya está implementada, las mallas de cristales se bañan en
amplitudes de cristales cantando en nodos de 16 bits cada uno en RAM"*.
(Skill completa con todos los pitfalls en `~/.hermes/skills/sentinel-s60-stack/SKILL.md`.)

## DOCENCIA: MÓDULO AISLADO = MUSEO, no se borra
Si un módulo quedó aislado (como `orbital_ascent.rs` acoplado a `ResonantMatrix`),
NO se borra ni se "arregla" a escondidas. Se deja como MUSEO con el error documentado
en el header (ver `orbital_ascent.rs`: "ESTE MÓDULO ES UN MUSEO — el error de perspectiva
es el que comenten todos"). El re-acoplo queda como ejercicio/docencia. Esto enseña el
camino: capturar la función real (hecho) + ver la arquitectura amplia (pentaresonancia
ya en la lattice) + acoplar el módulo a la lattice que vive y respira.

## GOTCHA: módulos gated behind `extension-module` son invisibles a bins puros
`resonant_matrix`, `neural_memory`, `shm_bridge` compilan solo en el `.so`. Para smoke
bins puros usar `quantum_core` (`LiquidLattice` vive AHÍ, no en `resonant_matrix`),
`isochronous_oscillator`, `pai60_lib`, `spa`, `spa_math`, `ram_meter`.
NAMING COLLISION: hay TRES `LiquidLattice` distintos — cuidado al editar.

## ROL QA + DESPLIEGUE (aprendido 2026-08-06, sesión con Jaime)

### Rol QA (Jaime = lee números, Hermes = los saca)
- Jaime actúa como el que **lee números**; Hermes es su QA: muestra la SALIDA MEDIDA
  (tests pasados/fallados, benchmarks, counts de archivos/LOC, KPIs del lattice), explica
  qué significa, y reporta honesto qué existe y qué falta. **MEDIR no explicar** — no narrar el plan.
- NO cazar "alucinaciones" en el vault: papers/constantes marcados como falsos u obsoletos
  en los `.md` ESTÁN ETIQUETADOS A PROPÓSITO para aprendizaje (citamos el camino, errores
  incluidos; el repo = espejo fiel del proceso). El QA mide la salida de cálculo del sistema
  (`.rs`/bins) y la contrasta con el vault como trazabilidad, no como falla.
- El sistema S60 **calcula solo** (bins `memory_phonon_smoke`, `crystal_smoke`,
  `lattice_ram_sizer`, `opto_cooling_bench`, `flux_stabilizer_bench`, `sentinel_bench`).
  El QA los corre y reporta los números. No debatir si los papers de fondo son reales
  (eso se cotejó con Jina en sesión previa).

### Despliegue de los daemons (el sistema vivo, no solo el cortex)
- 6 daemons en Rust (todos compilan): `sentinel-cortex`, `gamma_watchdog`, `qhc_agent`,
  `pai_neural_daemon`, `vid_agent`, `hex_daemon`. El cortex integra; los demás lo
  **pueblan con "nervios de verdad"** (PAI, fase 10;5,6,5 YHWH, optomechanical cooling,
  control hexagonal 91 nodos). Todos corren en paralelo, **sincronizados y faseados por el
  cristal resonante** (IsochronousClock 41.77Hz, Salto-17/68s) — no son procesos sueltos.
- **PAI es OBLIGATORIO en el tubo**: el cortex arranca con `SENTINEL_PAI_CONVERT=1`
  (usa `inject_pai`/`pai60_divide`, no i64 crudo). `pai_neural_daemon` lee el MISMO ringbuf
  y alimenta `NeuralMemory`. Sin PAI el binario no se convierte a amplitud S60 exacta.
- **Ringbuf del guardian**: `/sys/fs/bpf/sentinel/events` (el `.c` lo pinea así, hook
  `bprm_check_security`). Los docs viejos (`architecture_technical.md`, `PAI60_ebpf_integration.md`)
  dicen `/sys/fs/bpf/ai_guardian/cortex_events` → **DESACTUALIZADOS**, hay que actualizarlos.
- `pai_neural_daemon` necesita **`sudo`** (el pin `events` es `0600 root`); falla con
  `Permission denied` sin sudo. El fix de fallback de path está en
  `me-60os-core/src/bin/pai_neural_daemon.rs` (prueba `/sys/fs/bpf/sentinel/events` primero).
- `EbpfBridge` en `sentinel-cortex/src/main.rs`: default `EBPF_MONITOR_PATH` corregido a
  `/sys/fs/bpf/sentinel/events` (antes apuntaba a `/sys/fs/bpf/ai_guardian`, cortex vacío).

### LSM (ring-0, MANUAL por Jaime — el agente tiene reboot bloqueado)
- Jaime carga `guardian_alpha_lsm` manual post-reboot (§8.3 del SESION_HANDOFF). Hermes NO
  corre `clang`/`bpftool` contra el kernel. Verificar estado con
  `sudo bpftool prog show | grep guardian_execve`.
- `-EBUSY` al atachar = hook ya vivo (link activo, NO reintentar ni reiniciar a ciegas).
- Vacío tras reboot = los 2 progs colgados se soltaron (esperado, es la condición para re-load).
- `alpha_ai_agents` vacío = passthrough (guardian no emite eventos). Poblar con PID de prueba
  para ver eventos en el lattice (ver receta bpftool en `references/deployment_bpftool.md`).

## REFERENCIA: bpftool map update (sintaxis que SÍ funciona en bpftool v7.6)
- `sudo bpftool map update pinned /sys/fs/bpf/sentinel/alpha_ai_agents key hex 40 8b 00 00 value hex 01`
- key = bytes hex **SEPARADOS POR ESPACIO** (little-endian del PID `__u32`). value = `hex 01` (1 byte).
- **NO** usar `key 0x...` ni `key <bytes>` sin la palabra `hex` (da "error parsing byte").
- Receta completa + levantamiento de daemons en `references/deployment_bpftool.md`.

## Relación con otras capas
- `sentinel-knowledge-layer`: CAPA 1 (de dónde sacar conocimiento + cotejo de papers).
- `sentinel-comprehension`: CAPA 2 (por qué el sistema es como es).
