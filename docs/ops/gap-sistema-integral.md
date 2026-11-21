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
## Corrección del despacho dual — 2026-11-18

Preparación local. Cortex entrega al planificador la observación
`CrystalRuntime::dual_lane_portal_open()` y publica esa misma observación en los
campos de apertura dual. Este criterio exige concordancia exacta de fase y
amplitud con actividad. El umbral estadístico retrospectivo de EXP-028 Liquid
es un criterio experimental distinto.

Cortex conserva como máximo una solicitud periódica pendiente por tipo para
limpieza de malla y alineación de fase. Mientras el portal está cerrado, estas
solicitudes se acumulan sin duplicarse. El respaldo conserva su vía crítica.
El avance de ambas mallas y el reset al tick 68 conservan su cadencia.

El despacho autónomo de Cortex usa el cristal como referencia armónica. El
corte por presencia del piloto se aplica en las rutas que dependen del
biorresonador. Con el portal del cristal cerrado, las tareas ordinarias
esperan incluso si la cola supera el umbral histórico de desborde.

El planificador observa el estado resultante de ambas mallas tras los
pasos del runtime. La apertura surge de su evolución bajo el acoplamiento
y el bombeo QHC. El despacho carece de una ventana temporal adicional.

### Medición tras aplicar en Fénix

El 2026-11-18 se recreó únicamente Cortex con `sentinel-cortex:d8c109b9`
(`sha256:ad570b825736f20e2dc848e39c2c8bcd8e00d12dbec1d45b5396cfd0ecdc05fc`).
Compose confirmó estado saludable y cero reinicios; `/health` respondió 200
y el endpoint privado de estado respondió 401 sin credenciales.

Antes del cambio, Docker mostró 81,26 % de un núcleo, 66.925 tareas
pendientes y el corte por piloto activo. Después, el contador del cgroup
mostró un promedio de 78,27 % de un núcleo durante 45 s. El DTC avanzó
de 1.145 a 3.017 ticks, la cola se mantuvo en dos tareas y el corte por
piloto estuvo inactivo. Hubo un respaldo crítico, cero despachos por
portal y cero fallos. El objetivo operativo del 5–6 % de un núcleo sigue
incumplido.

### Coste de la modulación QHC de mantenimiento

Preparación local. El tick calcula una vez su desplazamiento SPA y reutiliza
la operación de fase de la malla en ambos carriles. Cada nodo mantiene la suma
comprobada y la normalización SPA. La prueba verificó equivalencia exacta de
componentes en los cuatro estados QHC con fases positivas, negativas y al
cruzar 360°. La sonda optimizada alternó ambas rutas durante 136 ticks sobre
67.951 nodos y comparó todas las fases al final: 4.665.993 ns por aplicación
anterior y 3.962.003 ns por aplicación candidata. Son tiempos de pared
aislados. El despacho GAP y la medición productiva de CPU siguen pendientes.

### Gradientes fonónicos observados en Fénix

Observación de solo lectura con Ring 0 restablecido. AGY analizó diez pares
de capturas estables de SHM. Para las 202.810 aristas de la topología que
recorre `ResonantMatrix::step`, la suma de las diferencias absolutas entre
gradientes A y B osciló entre 324.142.866.342 y 329.787.579.768 unidades
raw y cambió en las nueve transiciones. Las fases coincidieron en los
67.951 pares durante toda la muestra. El gradiente conserva información
espacial variable que no aparece en la igualdad de fase. La muestra carece
de marca DTC por captura y prueba de despacho, por lo que no determina
ventanas válidas ni autoriza una compuerta. Sonda SHA-256 `64c88903888701e3bb9498cc11b1c1e66db3b32b012fd21d4977b3f2f09a8a3a`.
Capturas temporales eliminadas. Sin cambio operativo.

### Contraste del bombeo P1.7 con la compuerta actual

El commit `0151c53a` aplica el desplazamiento QHC como amplitud en un
nodo rotativo durante el calentamiento del productor, antes de inyectar
la semilla. AGY ejecutó una prueba aislada de 37 nodos por malla, 60 pasos
por caso, comparando el operador rotativo con un control. Con entradas
asimétricas, el desacuerdo espacial de amplitudes al final fue 87.915.397
sin bombeo y 87.915.274 con bombeo, sin aperturas en ninguno. Con estado
inicial simétrico vacío, el bombeo abrió al activar ambas mallas por igual.
No se demuestra convergencia por el bombeo común. La sonda se retiró y no
se aplicó a producción.

### Respuesta cruzada en una perturbación unilateral

Prueba aislada en Rust ejecutada por AGY con 37 nodos por carril,
204 pulsos DTC y nueve pasos. Una excitación SPA 12 aplicada solo al
centro A apareció en B al primer paso (tick 21: centro 44.153 raw,
vecino 1.471 raw). Al fijar las ganancias de PID B en cero en el
control, B quedó vacío. El comparador exacto estuvo cerrado los
204 ticks en ambos casos. Con excitación simétrica directa se mantuvo
abierto los 204 ticks. Esto acredita una respuesta cruzada y difusión
con la implementación actual en el ensayo, pero la compuerta no las
distingue de la excitación compartida. Sonda retirada, sin despliegue.

### Prueba de despacho a partir de mínimos del gradiente relativo

AGY ejecutó cuatro brazos aislados en el runtime Rust de 37 nodos por
carril, 680 ticks y 32 pasos, con 12 tareas ordinarias iguales en cola.
La señal experimental marcaba una apertura al confirmar un mínimo
estricto de la discrepancia de gradientes. Vacío y excitación común
retuvieron las 12 tareas. La excitación unilateral produjo cuatro
flancos y despachó las 12 tareas, tanto con PID B activo como con su
salida anulada. En ambos casos el primer despacho fue al tick 147.
El disparador confundió cambios de la excitación unilateral con la
respuesta de la otra malla. Se retiró la sonda. Sin despliegue.

### Fase espacial frente a fase uniforme

El checkpoint activo de Fénix en tick QHC 70.086.328 contenía una sola
fase circular por malla en los 67.951 nodos. La inicialización espacial
`(n*17) mod 60` existe en `HexagonalController::new`, documentada
en `62b3e446`. AGY ejecutó dos runtimes Rust aislados de 37 nodos por
carril con pulsos asimétricos idénticos, 2.040 ticks y 97 pasos. Al
usar el patrón espacial como condición inicial, la superposición
`A*sin(fase)` presentó cancelación en 26 pasos, frente a ninguno con
fase uniforme. La alineación mínima raw pasó de 12.960.000 a 332.543.
Todas las amplitudes evolucionaron de forma idéntica entre controles
y ambos conservaron cero aperturas. La geometría cambia la señal
observada, pero no cierra el lazo fase-amplitud del runtime actual.
La prueba no supone correspondencia topológica ni aplica la fase al
checkpoint de producción. Sonda retirada, sin despliegue.

## Candidato de despacho por pulso DTC

Cortex entrega al detector temporal existente el tiempo programado del pulso en segundos S60, con origen en el primer pulso de la instancia. El intervalo que devuelve `CrystalRuntime::tick_dtc` programa el pulso siguiente. El planificador usa la intensidad calculada para dimensionar el lote y conserva la vía crítica de respaldo. La intensidad es una salida del modelo temporal. La prueba en memoria verifica apertura, despacho y cierre con los intervalos generados por el runtime. Pasaron las 76 pruebas del binario Cortex.
