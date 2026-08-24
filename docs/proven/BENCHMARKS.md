

<!-- SOURCE: BENCHMARK_CORE_S60_BASELINE_2026-08-06.md -->

# 📊 Benchmark Baseline — Core S60 / Sentinel (2026-08-06)

> **FUENTE:** ejecutado en vivo el 2026-08-06 en la laptop Fedora (UID 1002).
> **Build:** `me-60os-core` (workspace `~/Proyectos/sentinel`), `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1`, `--release`.
> **Máquina:** temp estable 27.8°C, CPU ~14.7% durante bench. No es servidor dedicado
> (micellia-live + MCP corriendo) → números representativos relativos, no absolutos.
> **NOTA HONESTA:** el reporte `RESULTADOS_BENCHMARK_REAL.md` (Dic 2024) es de OTRO
> subsistema (LLM/buffers, GPU GTX 1050, Python) — NO es baseline de estos bins.
> Este archivo ES el primer baseline de los bins S60 puros.

---

## 1. FONÓN / OPTOMECHANICAL (`opto_cooling_bench`)

Bin: `me-60os-core/src/bin/opto_cooling_bench.rs`
Física: `n_final = n_th/(1+C) + n_min`, C = 4g²/(κ·γ) cooperatividad.

| Métrica | Valor | Significado |
|---------|-------|-------------|
| Régimen | RESUELTO (κ < ω_m) | enfriamiento eficiente al estado fundamental |
| n_th_env inicial (raw) | 7,776,000,000,000 | ocupación térmica de calibración |
| n_min_limit piso cuántico (raw) | 2,025 | límite cuántico (κ/4ω_m)² |
| n_final último (raw) | 4,064,522 | tras 13 pasos muestreados |
| **Reducción térmica** | **99%** | (n_th - n_final)/n_th |
| Estado | efectivo, aún sobre piso | curva monótona decreciente OK |

Curva (step → n_final_raw):
```
0 → 7.78e12
1 → 5.85e8
2 → 1.46e8
3 → 6.50e7
6 → 1.63e7
12 → 4.06e6
```
Cooperatividad C crece ~g²: paso 12 tiene C≈2.48e13 → aplasta n_th.

**APRENDIZAJE (estudio):** el fonón S60 enfría 99% pero no toca el piso cuántico
en 13 pasos porque g crece lineal y C=g² necesita más acoplamiento/pasos para
llegar a n_min=2025. No es bug: es parámetro físico. Para alcanzar piso → subir
g_max o profundidad de pasos. El régimen RESUELTO confirma que κ < ω_m (fuera del
límite Doppler), condición necesaria para enfriamiento al estado fundamental.

---

## 2. CRISTAL / LATTICE (`sentinel_bench idle`)

Bin: `me-60os-core/src/bin/sentinel_bench.rs`
Mide: latencia de tick del cristal, deriva vs CLOCK_MONOTONIC, I/O del lattice.

| Métrica | Valor | Target | Evaluación |
|---------|-------|--------|------------|
| Crystal tick interval (avg) | 23,940,016 ns | 23,939,835 ns | ✅ exacto (±0.008%) |
| Crystal tick p99 | 24,056,047 ns | — | ✅ tight |
| Crystal tick max | 24,119,538 ns | — | ✅ sin outliers |
| **Crystal drift (600 ticks)** | **12.59 ppm** | — | ✅ muy bueno (NTP ~100-500 ppm) |
| Lattice I/O | 42,009 ns/op (~23.8 ops/ms) | — | ✅ S60 puro (entero 60⁴, sin float) |
| Temp durante bench | 27.8°C estable | — | ✅ |
| CPU sistema durante bench | 14.7% | — | ✅ máquina controlada |

**APRENDIZAJE (estudio):** el cristal late con deriva de 12.6 ppm (≈12.6 µs/s vs
reloj del kernel). 10-40x mejor que NTP. Esto ES la "respiración" del QHC Driver
(41.77Hz ≈ 23.9ms/tick) medida empíricamente. El lattice I/O a 42µs/op es el
costo de escribir/leer un nodo S60 (aritmética exacta, no float) — aceptable
para 2000 nodos; escala lineal con n.

---

## 3. CRYSTAL CIPHER (creado 2026-08-06, `crystal_cipher.rs`)

Tests unitarios: **4 passed / 0 failed** (verificado `cargo test -p me60os --lib crystal_cipher`).
- `test_same_phase_same_key`: mismo cristal → misma clave (determinista).
- `test_encrypt_decrypt_roundtrip`: cifra/descifra payload de capa.
- `test_pulse_rotates_key`: cada master cycle (4 breath = 68s) rota la clave.
- `test_different_crystal_different_key`: pulso distinto → clave distinta.

Clave = Blake3(fase_raw ‖ pulso ‖ amplitud) del IsochronousOscillator, AES-256-GCM.
Acople a control hexagonal (`hexagonal_control.rs`, misma fuente de fase).

---

## 4. PENDIENTE MARCADO COMO APRENDIZAJE

- **WARNING (no error):** `crystal_cipher.rs:20` importa `Nonce` de aes-gcm pero no
  se usa (se pasa `[u8;12]` directo). Compila OK, deja warning. LIMPIAR: quitar
  `Nonce,` de la importación. No afecta funcionalidad — es deuda de lint.
- **Fonón no toca piso cuántico** en 13 pasos (ver §1). No es bug, es parámetro.
- **LSM no cargado** (guardian_alpha_lsm): progs colgados de sesiones previas
  ocupan hook bprm_check_security → -EBUSY. Pendiente reboot + cargar god_mode=1002.

---

## 5. CÓMO REPRODUCIR (puerta de verdad)

```bash
cd ~/Proyectos/sentinel && export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
cargo run --release -p me60os --bin opto_cooling_bench
cargo run --release -p me60os --bin sentinel_bench -- idle
cargo test -p me60os --lib crystal_cipher
cargo test -p me60os --lib optomechanical
cargo test -p me60os --lib hexagonal_control
```

**HONESTIDAD > RESULTADOS INFLADOS.** Este baseline es real, reproducible y
versionado. La próxima sesión compara contra estos números, no contra el reporte
histórico de Dic 2024 (que era de otro subsistema).
