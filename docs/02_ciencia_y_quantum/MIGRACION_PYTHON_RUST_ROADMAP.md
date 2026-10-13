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
| `optomechanical` (core) | (ya existía) fonones/sideband cooling | verificado |
| `optomechanical` (sim) | `optomechanical_simulator.py` — `calculate_visibility()` | ✅ completado 2026-08-05 |
| `resonant_matrix` + `liquid_lattice` | (ya existían) lattice hexagonal / memoria líquida | verificado |
| `spa` / `spa_math` | `yatra_core` / `yatra_math` (S60) | ya en Rust |
| `pai60_lib` | `plimpton_exact_ratios` (razones recíprocas) | ya en Rust |

### Detalle de completados

#### ✅ `optomechanical_simulator.py` → `optomechanical.rs` (2026-08-05)
**Migrado:**
- `MembraneParameters` ✅ (ya existía)
- `OpticalParameters` ✅ (ya existía)
- `OptomechanicalSystem` ✅ (ya existía: `new`, `calculate_coupling`, `evolve`)
- `QuantumRiftDetector` ✅ (ya existía: `correlation_matrix`, `detect_rift`)
- `calculate_visibility()` ✅ **NUEVO** — visibilidad de interferencia V = (P_corr - P_anti)/(P_corr + P_anti) desde matriz densidad 4×4. S60 puro.

**Placeholders intencionales (no migrados, documentados en código):**
- `measure_quality_factor()` — en Python retorna Q nominal, no mide nada real (ring-down simulado).
- `simulate_axion_detection()` — en Python la confianza es hardcoded (98% placeholder), no físico.

**Bench:** `me-60os-core/src/bin/opto_cooling_bench.rs`
- CSV: `step,g_raw,cooperativity_raw,n_final_raw`
- Resultado registrado (2026-08-05):
  - n_th_env (inicial) raw: 7,776,000,000,000
  - n_final (tras 13 muestras) raw: 4,064,522
  - n_min_limit (piso cuántico) raw: 2,025
  - **Reducción térmica: 99%**
  - Régimen: RESUELTO (kappa < omega_m) — enfriamiento eficiente
  - Estado: aún sobre piso cuántico (n_final > n_min_limit) — físicamente correcto
- Comando: `cargo run --release --bin opto_cooling_bench` (output a stdout)

**Tests:** 41 tests pasan (3 nuevos: `test_visibility_max_coherent`, `test_visibility_anticorrelated`, `test_visibility_zero_total`)
- Comando: `cargo test --manifest-path me-60os-core/Cargo.toml --lib`

## 📋 PENDIENTES (orden por dependencia, no por prioridad de negocio)

### NIVEL 1 — Fortalecer el núcleo (sin nuevas features)
1. ~~**`optomechanical_simulator.py`** → extender `optomechanical.rs`~~ ✅ COMPLETADO 2026-08-05
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
