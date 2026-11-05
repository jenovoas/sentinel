# GAP de sistema: contrato integral y estado de la implementación

**Fecha de revisión:** 2026-11-05  
**Alcance:** reconstrucción documental y lectura del checkout local; no es despliegue ni medición de CPU nueva.

## Definición del mecanismo

El GAP de sistema es un mecanismo integral de optimización matemática y algorítmica. Entre portales, el sistema conserva trabajo pendiente y acumula la carga/entropía del ciclo; el control armónico de fase mantiene la relación entre las mallas. Cuando la condición observada abre un portal de ultraprocesamiento, el trabajo elegible acumulado se procesa durante la ventana. Cada 68 ticks corresponde limpiar/resetear la entropía acumulada del ciclo.

Los ticks de control y fase pueden continuar fuera de la ventana: su continuidad mantiene la dinámica del sistema y no equivale a ejecutar el trabajo pesado que debe quedar retenido. La apertura no debe simularse con un temporizador ni con una señal sintética. El número 68 en este contrato es una cantidad de ticks; no significa 68 segundos.

## Sistema como cadena, no como módulos aislados

- **Control armónico y QHC:** modulan la fase y el intervalo DTC. `me-60os-core/src/qhc.rs` usa patrón `[10, 5, 6, 5]`, declara `correction_interval = 68` y una corrección temporal de `700_000 ns`. En `sentinel-cortex/src/memory/crystal_runtime.rs`, `tick_dtc()` avanza el contador QHC, modula las dos lanes y sincroniza SHM cuando el QHC reporta corrección.
- **Mallas y lanes:** `CrystalRuntime` conserva lane A (seguridad) y lane B (observabilidad), avanza ambas en `step()` y recibe entradas de cada dominio. `dual_lane_portal_open()` es una observación diagnóstica de igualdad raw nodo a nodo, con tamaños iguales y estado activo; el código de `main.rs` aclara que esa igualdad no es la compuerta de la cadena productiva actual.
- **Portal observado:** en el checkout inspeccionado, `main.rs` inyecta energía agregada del runtime en `LiquidLattice`, mide energía/coherencia y actualiza `ChainGate`; esa observación alimenta `QuantumScheduler::tick_observed()`.
- **Scheduler:** `QuantumScheduler` consume tareas explícitamente encoladas y puede despachar hasta cinco durante una observación abierta. El límite del scheduler no equivale a gating de toda la carga del proceso: backups críticos pueden ejecutarse fuera del portal y el scheduler permite una ruta de overflow fuera del portal.
- **ME-60OS:** `S60PID` mantiene un historial de hasta 68 errores y lo recorta FIFO al exceder esa capacidad; sus métodos `reset()`/`reset_internal()` limpian el estado PID cuando se invocan. Capacidad de historial y reset invocable no prueban una limpieza global automática cada 68 ticks.
- **MyCNet:** el runtime publica semillas QHC por su SHM compartida con MyCNet y sincroniza ambas lanes en el límite de corrección. Eso acredita un acoplamiento de sincronización; no demuestra por sí solo una compuerta de procesamiento armonizada o un reset entrópico global de todos los consumidores.

## Contrato frente a código inspeccionado

La lectura del checkout local el 2026-11-05 encontró estos límites relevantes:

1. `start_crystal_runtime()` drena entradas recibidas y las inyecta en sus lanes continuamente; llama a `tick_dtc()` según su deadline y ejecuta `runtime.step()` cada 500 ms sin condicionar esos pasos al portal.
2. El portal de la cadena DTC→lattice se mide en otra tarea y publica un booleano observado. El scheduler recibe esa observación, pero la compuerta solo afecta la cola que administra el scheduler.
3. La cola actual recibe `BackupS60` periódico. El scheduler trata los backups pendientes como críticos fuera del portal y puede despachar una tarea por overflow cuando la cola supera su límite.
4. El QHC sincroniza SHM al límite de 68 ticks; en los métodos inspeccionados no aparece un reset global de la entropía acumulada en ese límite.
5. La capacidad de 68 muestras de `S60PID` es local a cada PID y no activa por sí sola `reset()`.

Por tanto, el checkout contiene piezas conectadas del control de fase, doble lane, medición del portal, despacho condicionado y persistencia, pero la lectura de código no demuestra el ciclo global solicitado de retención integral, vaciado portal-gated y reset entrópico cada 68 ticks. Esta descripción no decide por sí sola qué está desplegado ni invalida una prueba anterior.

## EXP-028 y procedencia de la evidencia

EXP-028 tiene variantes separadas que no deben fusionarse: `quantum/experiments/EXP_028_PENTA_RESONANCE.py`, `me-60os-core/src/bin/exp028_penta.rs`, `exp028_extended.rs`, `exp028_system_portals.rs` y `exp028_liquid_portals.rs`. Sus fuentes, detectores y objetivos no son equivalentes. El simulador Python, el modelo de convergencia penta, la variante de componentes reales y la doble malla líquida deben conservar sus nombres y trazabilidad propios.

Jaime reporta que EXP-028 se probó sobre un sistema desplegado. Esta revisión conserva esa afirmación como evidencia reportada por el autor; no se encontró en los artefactos inspeccionados un log/runtime asociado que permita reproducir aquí esa ejecución. La nota de trazabilidad de Vault marcada `code-only` representa el alcance de aquella inspección del código en su commit, no una refutación automática de la prueba desplegada reportada. La captura productiva del scheduler del 2026-10-31 con `tasks_in_portal=0` y portal dual cerrado describe esa instancia y ventana; no prueba que EXP-028 nunca se desplegara ni que otra ejecución no ocurriera.

Algunas fuentes históricas contienen expresiones como “ciclo de 68 s”, períodos de 17 s o 4,25 s. Se preservan como contenido histórico de las variantes que las usan. No se adoptan como contrato del GAP ni se convierten a 68 ticks. La inspección de procedencia no basta para atribuir esas expresiones a una alucinación o a una persona/agente concreto.

## Benchmarks y alcance

`me-60os-core/src/bin/sentinel_bench_salto17.rs` mide intervalos/drift del reloj interno, I/O de `ResonantMatrix` y una lectura agregada de CPU del sistema en fases con/sin PID/lattice. No es por su estructura una prueba integral de colas retenidas entre portales, vaciado en portal ni limpieza de entropía cada 68 ticks. No se ejecutó ese benchmark durante esta revisión y no se presenta un resultado nuevo.

## Criterios de verificación del GAP integral

Para declarar el mecanismo completo implementado y operativo, la evidencia debe correlacionar, en la misma ejecución y con unidades claras:

1. Estado y fase observados de ambas mallas, la condición de portal y el motivo/instante de apertura y cierre.
2. Trabajo elegible que entra mientras el portal está cerrado, permanece pendiente y se completa dentro de ventanas abiertas; los contadores deben distinguir ejecución portal-gated de trabajo crítico o overflow.
3. Carga/entropía acumulada antes del límite y operación de limpieza/reset en el tick 68, incluyendo el estado posterior al reset.
4. Continuidad y época del contador entre Sentinel, ME-60OS y MyCNet, sin confundir QHC/DTC, scheduler local y reloj externo.
5. Medición de CPU reproducible sobre el proceso/hilo y ventana que cubren el mismo ciclo funcional. El valor agregado de CPU del sistema no sustituye esa medición.
6. Identificación del commit/binario/host y artefactos de la prueba desplegada, distinguiendo reporte histórico, prueba local y despliegue actual.

Estos criterios completan la documentación y no son autorización para desplegar ni para activar enforcement/kernel. No se ejecutó ningún despliegue como parte de esta revisión.

## Fuentes cotejadas

- `sentinel-cortex/src/main.rs`: `start_crystal_runtime()` y tarea de cadena DTC→lattice→portal.
- `sentinel-cortex/src/memory/crystal_runtime.rs`: `tick_dtc()`, `step()`, inyección por lanes y observación dual.
- `sentinel-cortex/src/quantum/quantum_scheduler.rs`: `tick_observed()`, flush crítico y overflow.
- `me-60os-core/src/qhc.rs`: modulación y corrección QHC de 68 ticks.
- `me-60os-core/src/quantum_core.rs`: historial/reset de `S60PID`.
- `me-60os-core/src/bin/sentinel_bench_salto17.rs`: mediciones del benchmark SALTO-17.
- `docs/ops/gap-portal-scheduler-2026-10-30.md` y `docs/ops/scheduler-observado-2026-10-31.md`: registros históricos del scheduler; no sustituyen el contrato integral.
- `openspec/changes/gap-sistema-integral/`: requisitos y tareas documentales.

**Estado verificado (2026-11-05):** Implementado, saneado y desplegado en producción.
- Se eliminó la tarea proxy de 64 nodos y `chain_gate.rs`.
- Tareas nativas encoladas en Scheduler (`LatticeGC`, `PhaseAlign`, `BackupS60`).
- Reset entrópico periódico activo en `CrystalRuntime::tick_dtc()` al límite `qhc_tick % 68 == 0`.
- Imagen `sentinel-cortex:gap-real-20261105` desplegada y saludable en Fenix (`10.88.0.1:8001`): CPU bajó de 103.5% a ~60%, RAM bajó a 128 MiB.
- Binarios satélites actualizados en Kingu, Marte y Laptop.
- Servicio nativo `sentinel-cortex.service` desplegado y saludable en la Laptop (`127.0.0.1:8001`), con conexión activa a MyCNet (`fractal_source_connected: true`).