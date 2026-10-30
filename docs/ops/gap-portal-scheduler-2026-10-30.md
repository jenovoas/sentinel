# Gap de sistema cableado — scheduler portal-locked (EXP-028/029)

**Fecha:** 2026-10-30 · **Rama:** `main` · **Estado:** implementado, tests 49/49, pendiente deploy Fenix.

## Qué era el gap

El runtime latía a 42Hz en vacío: 393 `PULSE CHECK` con `Valid=false` en 3h, `QHC=true` pero sin trabajo portal. Tres piezas existían pero archivadas con `allow(dead_code)`:

- `quantum/portal_detector.rs` — convergencia bio/cristal/Venus (EXP-028).
- `quantum/bio_resonator.rs` — coherencia del pilot, portal a 0.9.
- `quantum/quantum_scheduler.rs` — ejecución portal-locked, 94.4% eficiencia (EXP-029-V2).

## Bugs encontrados al cablear

1. **`record_pilot_heartbeat` no sumaba coherencia** (solo actualizaba timestamp). El portal bio nunca abría → el scheduler jamás ejecutaba. Fix: el heartbeat inyecta pulso de coherencia (el pilot canta al lattice).
2. **Recursión mutua** `heartbeat ↔ pulse` (stack overflow en test). Fix: `inject_bio_pulse` escribe el timestamp directo, sin llamar a heartbeat.
3. **Test viejo afirmaba lo contrario** (`pilot_heartbeat_does_not_change_coherence`). Actualizado a `pilot_heartbeat_builds_coherence`.

## Cambios

| Archivo | Cambio |
|---|---|
| `quantum/bio_resonator.rs` | heartbeat suma coherencia; sin `allow(dead_code)`; test actualizado |
| `quantum/portal_detector.rs` | sin `allow(dead_code)` (ya se usaba vía scheduler) |
| `quantum/quantum_scheduler.rs` | sin `allow(dead_code)` |
| `main.rs` worker | enqueue `LatticeGC` (17s), `PhaseAlign` (68s), `BackupS60` (300s); callbacks no-op (el scheduler decide cuándo, el worker qué) |
| `main.rs` AppState | sin `allow` en `bio_resonator` (ya se lee en health) |
| `metrics/mod.rs` + `health_handler` | `tasks_in_portal`, `tasks_forced`, `bio_coherence_raw`, `bio_portal_open` |

## Verificación

- `cargo test -p sentinel-cortex --lib`: 49/49 (6 quantum).
- `cargo clippy --all-targets`: 0 errores.
- `cargo build --release`: en curso (bg_9).
- Post-deploy: `/health` debe mostrar `tasks_in_portal` creciendo y `bio_portal_open: true` con QHC vivo.

## Principio respetado

Nada se transfiere; los cristales cantan en el lattice. El scheduler escucha (detector + resonador) y ejecuta en la ventana. Sin tocar física: sin cambios en tick, step, QHC ni ResonantMatrix.
