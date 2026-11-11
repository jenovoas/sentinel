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

## 6. Registro de verificaciones Rust — 2026-11-11

Esta sección añade evidencia posterior; no reemplaza el baseline histórico.
Fuente ejecutada: `859c6dd2598bc4d2a8be09dbba02ec5594d212c2`, host `fenix`.
Python fue el prototipo y no se ejecutó ni modificó. No hubo despliegue ni cambios de servicios/kernel.

| Comando ejecutado | Resultado observado | Alcance |
| --- | --- | --- |
| `cargo run --locked -p me60os --bin exp012_phase_compression` | Recuperación exacta de 193 bytes de amplitud y `PHASE_KEY` tras ruido de 0,5° y cinco ciclos de snapping; sección dual recupera `Yo Soy` | Experimento Rust local |
| `cargo run --locked -p me60os --bin memory_phonon_smoke` | Salida satisfactoria; ocupación fonónica raw `50901825600000` → `26595203`; amplitud `72623859790382856`; PAI `30/60` raw `6480000` | Cálculo del modelo fonónico y codificación dual/PAI; no hardware fonónico |
| `cargo test --locked -p me60os --lib resonant_matrix::tests` | 11 aprobadas | Propagación, conservación superconductora, disipación, fase circular, escala SPA/PAI y evolución sincronizada |
| `cargo test --locked -p sentinel-cortex --lib quantum::quantum_scheduler::tests` | 9 aprobadas | Compuertas, retención, emergencia, backups críticos, errores y contabilidad |
| `cargo test -p sentinel-cortex --lib memory::crystal_runtime::tests` | 10 aprobadas | Portal dual, entrada remota, ring y avance DTC/control con historial |
| `cargo test -p sentinel-cortex --test test_p01_holographic_e2e` | 3 aprobadas | Escenario de integración definido en ese test; no sustituye prueba desplegada |

La prueba `test_warm_up_uses_configured_damping_and_dual_lanes_converge` ejecuta calentamiento, inyección idéntica y diez pasos posteriores, comprobando igualdad de amplitudes de ambas mallas en cada paso.

**Evitar repeticiones:** estas ejecuciones ya constan realizadas para esa revisión. No repetirlas para reconstruir contexto ni porque cambió solo documentación. Reejecutar únicamente las rutas afectadas por un cambio de código/dependencias/configuración relevante, una regresión reportada o una nueva medición solicitada. Una corrida posterior usa su propio commit/host; no trasladar estos resultados automáticamente.

**Pendiente P1.2:** el benchmark `sentinel_bench_salto17` vigente llama a `update_with_history_internal()` en modo `kernel`, pero descarta su retorno. El reloj medido sigue `IsochronousClock::tick_internal`; el benchmark no aplica esa salida al deadline ni invoca `calculate_drift_correction()`. Además usa `clock.ticks` como raw medido y `dt_raw=1`, mientras el runtime usa energías SPA y un paso de control de medio segundo. Medir ese bin sirve para registrar su escenario concreto; no acredita por sí solo corrección predictiva del reloj ni aislamiento RT del loop vivo.

## 7. P1.2: medición local de Salto-17 — 2026-11-11

**Ejecutado, no extraído de resultados anteriores.** Fénix, seis CPU disponibles, código `859c6dd2`; build `cargo build --locked --release -p me60os --bin sentinel_bench_salto17` terminado correctamente. Benchmark y trabajador de carga fijados únicamente a CPU 5 mediante `taskset -c 5`; no se alteró afinidad de procesos ajenos ni configuración del kernel.

Salida original y parámetros: [salto17_2026-11-11_fenix.json](salto17_2026-11-11_fenix.json). SHA-256 de la fuente del benchmark: `378f53d0f0f35b8935c2c089fb80339ff285e1c693678023257907dad3507681`.

| Escenario, en orden de ejecución | Tick medio (ns) | Tick p99 (ns) | Deriva absoluta (ns / 600 ticks) | ppm impresos | I/O (ns/op) | CPU host |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline sin history | 23939992 | 25602437 | 96021 | 6 | 25291 | 31,5% |
| Baseline con history | 23942684 | 26047760 | 96881 | 6 | 25625 | 31,0% |
| Carga sin history | 23939940 | 24465233 | 63554 | 4 | 51707 | 47,8% |
| Carga con history | 23939962 | 24735257 | 77418 | 5 | 50856 | 47,5% |

- Cada escenario ejecutó 600 ticks para intervalos y otros 600 para deriva; duración ideal de la segunda ventana `14363901000 ns`. I/O: 50.000 operaciones por escenario. Una corrida por escenario, todos terminaron con código 0. Baseline significa sin carga añadida por esta medición, no host inactivo.
- Comando del bin: `taskset -c 5 target/release/sentinel_bench_salto17 <escenario> [kernel]`. `kernel` significa cálculo del historial S60PID del benchmark, no kernel Linux/eBPF.
- Carga añadida: un proceso `taskset -c 5 openssl speed -seconds 120 -bytes 16384 sha256`, OpenSSL 3.5.7. El proceso se inició inmediatamente antes de cada escenario con carga y se terminó/esperó al concluir ese escenario. Consumió 2993 y 2992 ticks CPU respectivamente (`CLK_TCK=100`), durante ventanas de aproximadamente 31 segundos. No se instalaron herramientas ni se saturaron deliberadamente los seis CPU.
- `-1.000C` es el fallback del lector térmico: temperatura no disponible, no una lectura física de −1 °C. Los porcentajes CPU son agregados del host, no del hilo del cristal. Los ppm están truncados a enteros y la deriva impresa es absoluta, sin signo.
- **Resultado delimitado:** el benchmark y el cálculo con historial se ejecutaron bajo contención real de CPU. Sus números no prueban mejora predictiva: el retorno PID no gobierna el reloj en este bin (§6), no se ejecutó el loop vivo y una sola muestra por escenario no establece causalidad ni significancia.
- **P1.2 continúa abierto:** aislamiento RT y efecto de corrección aplicada al loop vivo no verificados. No se cambiaron `isolcpus`, LSM, QHC, parámetros del controlador ni servicios. No repetir estas cuatro corridas por falta de registro: conservar el JSON y usar un protocolo ligado al loop real para la siguiente validación pertinente.

## 8. P1.2: ejecución aislada de CrystalRuntime — 2026-11-11

Fuente `f6a6b939` (lógica Rust sin cambios respecto de `859c6dd2`), Fénix, kernel `7.2.12+deb13-amd64`, rustc 1.99.1. Se compiló una sonda temporal contra la biblioteca existente mediante `cargo build --locked -p sentinel-cortex --example p12_runtime_probe`, perfil **dev sin optimización**. La fuente exacta, su SHA-256, comandos, muestras y salida original quedan archivados en [p12_runtime_2026-11-11_fenix.json](p12_runtime_2026-11-11_fenix.json); el archivo temporal de ejemplo se retiró después de medir, sin cambiar la lógica del core.

**Protocolo:** `CrystalRuntime::in_memory(2000)`, 680 ticks por escenario, primer deadline `23_939_835 ns`, siguientes intervalos devueltos por `tick_dtc()`. `step()` cada 500 ms aplica las salidas de ambos S60PID a las mallas; no se sustituyó por el benchmark que descarta su retorno. Drive en lane B calculado desde `/proc/stat` con la misma transformación de borde y `pai60_divide` del runtime. No se inyectaron eventos de seguridad ni se forzó igualdad entre lanes o apertura de portal.

Cada proceso usó un directorio temporal nuevo y vacío mediante `SENTINEL_CRYSTAL_STATE_DIR`. La sonda comprobó contador inicial cero, SHM/ring desactivados y cero sincronizaciones/escrituras; el directorio seguía vacío al finalizar. Aunque `status().checkpoint_active` declara capacidad, no indica escritura: `liquid_memory_sync_count=0`, bytes de checkpoint=0 y no se llamó a `persist()`.

| Métrica | Sin carga añadida | Con carga añadida |
| --- | ---: | ---: |
| Ticks DTC/QHC completados | 680 | 680 |
| Pasos de malla/control completados | 32 | 32 |
| Fronteras QHC observadas (68…680) | 10 | 10 |
| Retraso medio frente a deadline (ns) | 556342 | 1350163 |
| Retraso p99 frente a deadline (ns) | 15256196 | 24812583 |
| Retraso máximo frente a deadline (ns) | 21665527 | 46960262 |
| Duración media de `step()` (ns) | 16873377 | 28071759 |
| Duración máxima de `step()` (ns) | 23377676 | 46298691 |
| Energía final lane A (raw SPA) | 26663 | 18859 |
| Energía final lane B (raw SPA) | 333256269 | 347510023 |

- Benchmark y carga compartieron CPU 5. Carga: un proceso OpenSSL SHA-256, 1511 ticks CPU consumidos (`CLK_TCK=100`) durante aproximadamente 16,3 s; fue terminado y esperado al acabar. Los dos procesos de medición devolvieron 0.
- Las diez fronteras de 68 ticks informaron `qhc_last_drift_correction_ns=700000`. Ese campo es el marcador del QHC; **no se interpreta como 700000 ns restados al deadline**. La implementación de `tick_dtc()` ejecuta su reset de PID/ruido en esas fronteras.
- La lane A partió sin amplitud y no recibió drive externo: el primer paso registró raw 57/99 en baseline/carga respectivamente. El camino ejecutado de `CrystalRuntime::step` inyecta las correcciones cruzadas del PID y evoluciona las mallas. Esto acredita uso de la salida del controlador en esa instancia, no solo cálculo descartado.
- Tiempo esperado del tick 680: `16290263804 ns`. El retraso de ese último tick fue `1180191 ns` sin carga y `73403 ns` con carga; un último tick menor no borra el aumento de p99/máximo durante la ventana ni demuestra mejora causal del controlador.
- **Alcance:** biblioteca Rust real en instancia aislada, con instrumentación propia y 2000 nodos por lane. No ejecuta el servicio productivo completo, su scheduler, SHM/MyCNet, eBPF, checkpoints, el dimensionamiento productivo ni una comparación history ON/OFF. Las muestras del drive del host difieren entre corridas. Una observación por escenario y perfil dev: no atribuir significancia estadística ni comparar sus tiempos directamente con el bin release de §7.
- **Estado P1.2:** queda realizada la medición aislada del control aplicado bajo carga; siguen pendientes aislamiento RT y medición del loop desplegado con su configuración efectiva. No se modificaron constantes físicas, QHC, PID, kernel ni servicios. No repetir estas corridas por falta de contexto; consultar el JSON y ejecutar únicamente el siguiente protocolo pertinente.
