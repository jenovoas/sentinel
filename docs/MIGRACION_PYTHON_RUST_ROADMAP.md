# 🛡️ ROADMAP: MIGRACIÓN PYTHON → RUST (módulo a módulo)

> Autor: Jaime Novoa Sepúlveda (con Hermes Agent)
> Regla de oro: migrar SOLO el núcleo matemático real. La capa fenomenológica
> (vimana / akáshica / royal-star / ea-nasir) NO se toca — es terreno de estudio.
> Cada módulo: migrar → documentar → bench. Verificación real, sin especular.

## ✅ YA MIGRADO (este sprint)
| Módulo Rust | Origen Python | Estado |
|---|---|---|
| `ram_meter` | `quantum_lite.get_available_memory_gb` (psutil) | commit 0e9287a4 |
| `buffer` | `quantum/ai_buffer_cascade.py` (kernel OU no-Markoviano) | commit 15e44b7f |
| `optomechanical` | (ya existía) fonones/sideband cooling | verificado |
| `resonant_matrix` + `liquid_lattice` | (ya existían) lattice hexagonal / memoria líquida | verificado |
| `spa` / `spa_math` | `yatra_core` / `yatra_math` (S60) | ya en Rust |
| `pai60_lib` | `plimpton_exact_ratios` (razones recíprocas) | ya en Rust |

## 📋 PENDIENTES (orden por dependencia, no por prioridad de negocio)

### NIVEL 1 — Fortalecer el núcleo (sin nuevas features)
1. **`optomechanical_simulator.py`** → extender `optomechanical.rs`
   - Clases: `MembraneParameters`, `OpticalParameters`, `OptomechanicalSystem`, `QuantumRiftDetector`.
   - Bench: ocupación fonónica vs pasos de enfriamiento.
   - Nota: `optomechanical_cooling.py` ya tiene `run_cooling_sequence`.
2. **`field_stabilization_sim.py`** → `FluxStabilizer` (estabilización de fase/rift)
   - Posible destino: `hexagonal_control.rs` (ya tiene `control_rift_propagation`).
   - Bench: drift residual tras N ciclos de estabilización.
3. **`coherence_mapping_calibration.py`** → `CoherenceMapper`
   - Mapea coherencia bio→S60. Destino: `sentinel-cortex/src/quantum/bio_resonator.rs`.
   - Bench: coherencia 0..1 vs umbral portal (90%).

### NIVEL 2 — Memoria y resonancia (mapear a lo ya en Rust)
4. **`quantum_lattice.py`** (`VimanaLattice`) → comparar con `ResonantMatrix` (ya Rust)
   - ¿Es lo mismo que `ResonantMatrix` o aporta topología distinta? LEER antes de migrar.
5. **`liquid_lattice_storage.py`** (`LiquidLatticeStorage`) → vs `LiquidLattice` (ya Rust, 3×3)
   - Posible duplicación. Unificar o documentar diferencia.
6. **`crystal_memory.py`** (`CrystalMemoryCore`) → vs `ResonantMatrix` + snapshot gzip.
7. **`liquid_memory_adapter.py`** (`LiquidMemory`, `get_memory_service`) → capa de servicio.

### NIVEL 3 — Dual-lane y optimización (recuperar del purge)
8. **`data_lanes.py`** (`DualLaneRouter`) — BORRADO en purge `aed3b377`.
   - Recuperar de `git show aed3b377^:backend/app/core/data_lanes.py` y migrar a Rust.
   - Es ingeniería real (security/observability lanes, WAL). NO es cáscara.

### NIVEL 4 — Validación / benchmarks existentes (solo correrlos y portar a Rust)
9. `EXP_012_PHASE_COMPRESSION.py` → compresión de fase (real, migrable).
10. `EXP_021_S60_DUAL_PATH_TEST.py` → test S60 vs float (dual-path, validación).
11. `verify_plimpton.py` / `verify_meijer_scale.py` → benchmarks de exactitud.

## 🚫 NO MIGRAR (capa fenomenológica — estudio de Jaime)
- `VIMANA_MASTER_V1_RECOVERED.py`, `EA_NASIR_MASTER_FORMULA.py`
- `celestial_navigation.py` (RoyalStar / SovereignAstrolabe)
- `vimana_yatra_driver.py`, `vimana_*.py` (internal/exploratory)
- `zpe_phase1_lab.py`, `zpe_simulation.py` (teatro disfrazado de ciencia — confirmado falso)

## 📊 Formato de cada entrega
Por módulo: `feat(core): ...` + bench en `me-60os-core/src/bin/` + doc en `docs/`.
Tests S60 puros (sin float). Working tree limpio entre commits.
