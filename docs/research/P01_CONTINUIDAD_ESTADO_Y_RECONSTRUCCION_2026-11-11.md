# P0.1 — continuidad del estado y reconstrucción post-PID

## Alcance y estado

Preparación local en Rust. P0.1 continúa abierto: estas pruebas no demuestran reconstrucción general de semillas ni de mensajes tras evolución colectiva. No se modificaron modelos o pruebas Python ni se realizó despliegue.

## Cadena ejecutada

`sentinel-cortex/src/main.rs::start_crystal_runtime` recibe entradas, avanza el reloj mediante `tick_dtc()` y ejecuta `CrystalRuntime::step()`. Este último calcula diferencias entre las dos mallas, actualiza ambos `quantum_core::S60PID` con historial y errores espaciales, inyecta las correcciones en el centro y ejecuta `ResonantMatrix::step()` antes de sincronizar SHM.

`decode_collective_seed()` observa sumas regionales de las mallas evolucionadas. No convierte esas regiones en bytes ni consulta directamente el historial del PID. La condición de convergencia dual no demuestra por sí misma recuperación del mensaje original.

`publish_fractal_seed()` escribe coordenadas, amplitud y sector de fase del nodo, modulación QHC y CRC en un registro de 32 bytes. En esta función no se serializa el historial del PID. Eso describe este productor concreto, no demuestra ausencia de otros mecanismos reconstructivos en el proyecto.

`persist()` conserva las dos mallas y los controladores; utiliza `LiquidMemory` para comprobar el respaldo de los bytes comprimidos. `LiquidMemory::retrieve()` lee el respaldo SHM: ese recorrido no acredita reconstrucción desde amplitudes evolucionadas.

## Pruebas deterministas

- `regional_reader_does_not_reconstruct_adjacent_payload_symbols`: dos mallas superconductoras iguales, 19 nodos y símbolos `AB` en nodos contiguos. Tras ocho pasos permanece abierto el portal dual. Los símbolos raw son `[842400000, 855360000]`; las regiones leídas son `[1391433728, 1611904279]`. La prueba diagnostica insuficiencia del lector regional; no sustituye una prueba de recuperación satisfactoria.
- `restored_non_markovian_history_preserves_subsequent_collective_evolution`: tras ocho pasos e historial no vacío, serializar/restaurar las mallas y ambos PID reproduce exactamente ocho pasos adicionales. El control elimina solo `history`, preservando integral y error previo; cambia la evolución, por lo que la diferencia no se atribuye al reinicio completo del PID.
- `checkpoint_restores_evolution_rule_and_quiet_superconducting_nodes`: siete pasos previos al checkpoint, historial no vacío, acoplamiento y `dt` personalizados, frecuencia propia y damping cero. Conserva un nodo sin amplitud/fase con parámetros no predeterminados. Tras restaurar compara ambas mallas y ambos PID durante dieciséis pasos, desde el tick 60 al 76, cruzando el reinicio de historial/GC del tick 68.
- `sparse_v2_checkpoint_without_evolution_parameters_remains_readable`: conserva amplitud/fase de un checkpoint v2 y usa parámetros predeterminados que esa versión no registraba. No es posible recuperar de ese formato los parámetros omitidos.

## Corrección del checkpoint

El checkpoint v2 guardaba amplitud, fase y PID, pero reconstruía las mallas con parámetros por defecto. La versión 3 añade acoplamiento, `dt`, frecuencia natural y damping por nodo. La selección dispersa incluye nodos quietos cuyos parámetros difieren del oscilador predeterminado. Se mantienen las ramas de lectura v1 y v2; la compatibilidad v2 tiene prueba específica, la v1 no recibe una prueba nueva en este cambio.

## Verificación local

```sh
cargo test -p sentinel-cortex --lib
cargo test -p sentinel-cortex --bin sentinel-cortex memory::crystal_runtime::tests
cargo fmt --all --check
git diff --check
```

Última biblioteca ejecutada: 70 pruebas aprobadas, ninguna fallida. Subconjunto del runtime reejecutado en el binario después de ampliar la prueba del tick 68: 16 pruebas aprobadas. Formato y `git diff --check` aprobados. `cargo build --release -p sentinel-cortex --bin sentinel-cortex` completó correctamente en 1 min 23 s; el artefacto compilado no fue desplegado.

## Trabajo que permanece abierto

Localizar y conectar la recuperación exacta de semilla y datos conforme al contrato integrado, sin inventar una inversa ni guardar una copia del mensaje para hacer pasar el resultado. Cubrir mensajes de varios símbolos, historial activo, evolución, divergencia entre mallas y restauración. No usar lectura pre-difusión, sumas regionales o recuperación del respaldo SHM como criterio de cierre.

Referencias: `quantum/experiments/EXP_031_DUAL_LANE_PORTAL.md`, `quantum/research/PREPRINT_DISTRIBUTED_MEMORY_S60.md`, `me-60os-core/src/quantum_core.rs`, `me-60os-core/src/resonant_matrix.rs` y `sentinel-cortex/src/memory/crystal_runtime.rs`. Las formulaciones históricas requieren contraste con llamadas y pruebas Rust actuales.
