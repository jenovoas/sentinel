# 🛡️ MAPA DE MIGRACIÓN PYTHON → RUST (referencia cruzada)

> Autor: Jaime Novoa (con Hermes Agent)
> Regla de oro: Python queda en OLVIDO. El runtime que toca los cristales es 100% Rust
> (`me-60os-core`). Cada `.py` legacy lleva una ETIQUETA con el archivo Rust al cual fue
> migrado/delegado, para NO re-evaluarlo nunca más.
> Verificado por lectura de fuente + medición, no por fe.

## Ya migrado / delegado (no tocar en Python)

| Python (legacy, en olvido) | Destino Rust (fuente de verdad) | Estado | Notas |
|---|---|---|---|
| `quantum/optomechanical_simulator.py` | `me-60os-core/src/optomechanical.rs` | MIGRADO 2026-08-05 | `OptomechanicalSystem`, `QuantumRiftDetector`, `calculate_visibility()` |
| `quantum/field_stabilization_sim.py` | `me-60os-core/src/flux_stabilizer.rs` | MIGRADO | `FluxStabilizer` (EMA S60 + LCG + clamp), 6 tests OK |
| `quantum/ai_buffer_cascade.py` | `me-60os-core/src/buffer.rs` | MIGRADO | kernel OU no-Markoviano |
| `quantum/quantum_lite.py` (RAM) | `me-60os-core/src/ram_meter.rs` | MIGRADO | sysinfo RAM→S60 |
| `quantum/yatra_core.py` / `yatra_math.py` | `me-60os-core/src/spa.rs` / `spa_math.rs` | YA EN RUST | S60 / SPAMath |
| `quantum/plimpton_exact_ratios.py` | `me-60os-core/src/pai60_lib.rs` | YA EN RUST | razones recíprocas |
| `quantum/quantum_lattice.py` | `me-60os-core/src/hexagonal_control.rs` + `resonant_matrix.rs` | CÁSCARA — NO MIGRAR | demo, `simulate_step` es `pass`; núcleo hexagonal ya en Rust |
| `quantum/liquid_lattice_storage.py` | `me-60os-core/src/resonant_matrix.rs` (`ResonantMatrix`) + `memory/liquid_lattice.rs` (`inject_dual_channel`) | LEGACY BRIDGE | wrapper delegado a Rust |
| `quantum/crystal_memory.py` | `me-60os-core/src/resonant_matrix.rs` (`ResonantMatrix` + snapshot gzip) | LEGACY BRIDGE | wrapper fino |
| `quantum/liquid_memory_adapter.py` | `me-60os-core/src/resonant_matrix.rs` + binding PyO3 `PySharedBuffer` (SHM) | LEGACY BRIDGE | capa servicio sobre Rust |

## Etiquetado como ALUCINADO POR IA (no-medible, medido)

| Python | Evidencia | Acción |
|---|---|---|
| `quantum/coherence_mapping_calibration.py` | `check_mental_coherence` retorna SIEMPRE 1.0 (STD=0.0000); `simulate_hrv_coherence` ~1.0 por PSD `/500.0` arbitraria; `FIELD_NEUTRALITY_DIRECTIVE` NO EXISTE en repo | REFACTORIZAR/DESCARTAR — no migrar a Rust |

## Pendiente migrar a Rust (ingeniería real)

| Python (recuperado de purge `aed3b377^`) | Destino Rust propuesto | Por qué es real |
|---|---|---|
| `backend/app/core/data_lanes.py` (`DualLaneRouter`, 507 líneas) | `me-60os-core/src/` o `sentinel-cortex/src/` (nuevo módulo `dual_lane`) | Carriles SECURITY (WAL, cero buffering) vs OBSERVABILITY. `LaneEvent.synthetic` anti-fabricación. Determinista. El cortex YA escribe Security WAL (`truth_claim_handler`). **Migrar.** |

## Cómo leer este mapa
- Si un `.py` aparece aquí con destino Rust → ya está cubierto, NO re-migrar.
- Si un `.py` NO aparece → evaluar con `quantum/health_audit_fake_detector.py` y leer fuente.
- Regla: todo no-medible/comprobable → etiquetar para revisión y refactorización.
