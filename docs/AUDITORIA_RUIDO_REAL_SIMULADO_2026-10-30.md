# Auditoría de ruido real, señales del host y simulación — 2026-10-30

## Alcance y fuentes cotejadas

Esta nota distingue el uso histórico de entropía para simulaciones, los experimentos que someten el sistema a carga real y la señal que inyecta el Cortex vigente. La nota vault `Simulacion/ruido_real_vs_simulado.md` sirve como pista conceptual; no acredita por sí sola un experimento controlado ni describe el runtime actual.

Fuentes verificadas en esta revisión:

- `quantum/quantum_noise_s60.py` y `quantum/experiments/EXP_007_QUANTUM_STABILITY_TEST.py`, `EXP_008_ECC_ARRAY.py`, `EXP_009_LIQUID_LATTICE.py`.
- `quantum/experiments/EXP_021_S60_DUAL_PATH_TEST.py` y su contraparte vigente `me-60os-core/src/bin/exp021_dual_path.rs`.
- `me-60os-core/src/bin/crystal_drift_probe.rs`, `sentinel_bench.rs` y `sentinel_bench_salto17.rs`.
- Experimento de carga real registrado en la vault: `Experimentos/SESION_2026-08-06_BENCHMARK_CARGA_DRIFT.md`.
- Ruta Cortex vigente en `sentinel-cortex/src/main.rs` y captura Fenix de métricas/health del 2026-10-30 14:55 UTC.
- Historial Git: `e1a5c523` añadió el probe de deriva y el benchmark de carga; `69e53327` unificó la amplitud del drive con PAI-60.

## Qué significa “ruido real” en cada etapa

1. **Experimentos Python iniciales:** `QuantumNoise.depolarizing_noise` lee bytes de `os.urandom` para decidir si aplica puertas Pauli dentro de un modelo. La fuente de bytes es del sistema operativo; el canal de despolarización y el sistema afectado siguen siendo parte de una simulación. EXP-007/008/009 no miden la temperatura de una CPU ni un dispositivo cuántico físico.
2. **EXP-021:** el Python histórico formaba muestras BPM con `os.urandom`; el bin Rust actual sustituye la entrada por un LCG determinista para hacer reproducible la comparación numérica float/S60. Este experimento compara cálculos con una misma señal de entrada; no compara ruido térmico medido contra ruido simulado ni valida el clasificador de producción.
3. **Carga real del host:** `crystal_drift_probe.rs` propone fases idle, carga externa y enfriamiento y compara el reloj del cristal con `Instant`. No usa PRNG, pero tampoco lee el sensor térmico ni ejecuta una rama equivalente de ruido simulado. Además, el probe crea el `IsochronousClock` una sola vez, pero reinicia el `Instant t0` en cada fase mientras `get_nanos_internal()` conserva el origen del reloj; desde la segunda fase compara relojes con orígenes distintos. Ese bin no debe tratarse como medición válida de drift entre fases hasta corregir el protocolo. La sesión del 6 de agosto registró por separado `stress-ng --cpu 4` con `sentinel_bench`: CPU 37.2→82.1%, drift 4.39→50.76 ppm y mayor jitter/I/O. Eso es una medición reportada de respuesta bajo carga real del host, no un A/B térmico real-versus-sintético.

## Señal del Cortex desplegado

El Cortex vigente lee la primera línea de `/proc/stat`, suma los contadores `user+sys`, calcula `(user+sys) mod 60 + 20` —35 como fallback— y convierte ese entero una sola vez con `pai60_divide(SPA::from_int(sample), 60)`. La amplitud resultante se inyecta periódicamente en `ResonantMatrix`, `LiquidLattice` y `NeuralMemory`; CrystalRuntime la recibe si está habilitado. No se lee `/sys/class/thermal/thermal_zone0/temp` para formar esa amplitud.

La métrica `sentinel_cpu_temperature_celsius` sí intenta leer `/sys/class/thermal/thermal_zone0/temp`, pero es observabilidad separada, con fallback. En Fenix dio 49.00 °C a las 14:55 UTC. Ese valor confirma que el endpoint expone una lectura del sensor en esa captura; no demuestra que la temperatura sea la entrada del drive. `sentinel_bench.rs` y `sentinel_bench_salto17.rs` también consultan la temperatura solo al inicio/final del bench. Los contadores `/proc/stat` son señal de actividad del host derivada del sistema operativo. El código no demuestra que sean una medición directa de calor.

## Dictamen y brechas

- La ruta histórica `os.urandom` no debe describirse como ruido físico medido: introduce entropía del sistema operativo en una simulación de ruido.
- Hay mediciones versionadas con carga real del host y una ruta Cortex activa basada en contadores CPU. Son fases distintas y no deben colapsarse en una sola afirmación de “sensor térmico usado como ruido”.
- En esta revisión no se encontró un bench que ejecute lado a lado, con protocolo y resultados archivados, temperatura física medida contra ruido sintético bajo las mismas condiciones.
- La nota vault `Simulacion/ruido_real_vs_simulado.md` atribuye temas de entropía/ruido a varios identificadores arXiv que no corresponden a los PDFs locales: `2006.10113` es un trabajo de modelos integrate-and-fire neuronales; `2208.11625` trata de federated prompt learning; `2106.08947` es un artículo matemático en ruso sobre funciones subarmónicas. Esas citas no respaldan las afirmaciones de ruido que el apunte les atribuye. El apunte se conserva como rastro histórico, pero esas referencias no se usaron como sustento.
- Tampoco hay un contrato de producción que conecte el drive PAI-60 con `entropy_signal` de Guardian/eBPF o con el filtro SCV del Gateway Marte. Ese filtro permanece pendiente, según la auditoría de despliegue.
- La nota vault `Simulacion/ruido_real_vs_simulado.md` contiene referencias comentadas como inválidas y generalizaciones sobre origen de entropía. No se usó como evidencia científica ni como descripción del runtime. Los PDFs locales con títulos de optomecánica/ruido no cambian lo que efectivamente consume el Cortex.

## Estado de despliegue

El drive periódico de amplitud CPU/PAI-60 ya forma parte del Cortex desplegado en Fenix; no se desplegó ni probó una ruta de temperatura física hacia el lattice o el filtro de seguridad. No se modificó código ni runtime durante esta auditoría. No se ejecutaron pruebas.
