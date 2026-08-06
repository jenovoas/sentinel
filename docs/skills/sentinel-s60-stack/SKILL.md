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

## Relación con otras capas
- `sentinel-knowledge-layer`: CAPA 1 (de dónde sacar conocimiento + cotejo de papers).
- `sentinel-comprehension`: CAPA 2 (por qué el sistema es como es).
