# Tasks

## 1. Fijar el contrato integral

- [x] 1.1 Definir la relación entre control armónico de fase, portales entre mallas, acumulación de trabajo/entropía entre ventanas y procesamiento de trabajo pendiente al abrirse el portal.
- [x] 1.2 Especificar el reset/limpieza entrópica cada 68 ticks, sin sustituir ticks por segundos ni atribuir al QHC una limpieza global que el código inspeccionado no demuestra.
- [x] 1.3 Precisar los límites entre Sentinel, ME-60OS y MyCNet y distinguir pulso/QHC, avance de mallas, scheduling y persistencia.

## 2. Registrar implementación y evidencia sin colapsar variantes

- [x] 2.1 Clasificar por separado contrato del usuario, variantes EXP-028, código local inspeccionado, evidencia operativa reportada y validación independiente disponible.
- [x] 2.2 Registrar las rutas de ejecución fuera del portal y los componentes aún no integrados en el ciclo global; preservar nombres originales y referencias históricas.
- [x] 2.3 Crear y enlazar la nota espejo de auditoría en personalvault y actualizar la arquitectura funcional de Sentinel.

## 3. Validación documental

- [x] 3.1 Ejecutar `openspec validate gap-sistema-integral --strict` y `git diff --check` en Sentinel.
- [x] 3.2 Revisar los diffs para confirmar que no cambió código ni se incluyeron archivos preexistentes ajenos.
- [x] 3.3 Registrar commits/push por separado y el estado real de validación; no declarar despliegue.

## 4. Implementación nativa y despliegue productivo verificado (2026-11-05)

- [x] 4.1 Saneamiento de código: Eliminación del proxy artificial de 64 nodos y `chain_gate.rs`.
- [x] 4.2 Tareas nativas encoladas en Scheduler: `LatticeGC` (17s), `PhaseAlign` (4.25s) y `BackupS60` (60s).
- [x] 4.3 Reset entrópico periódico implementado en `CrystalRuntime::tick_dtc()` a cada tick `qhc_tick % 68 == 0`.
- [x] 4.4 Evaluación armónica directa con `PortalDetector` en el bucle del runtime.
- [x] 4.5 Construcción y despliegue de imagen `sentinel-cortex:gap-real-20261105` en Fenix:
  - CPU de Cortex cayó de 103.5% a ~60%.
  - RAM cayó de 189 MiB a 128 MiB.
  - `tasks_in_portal` acumulando trabajo real dentro de la ventana armónica.
- [x] 4.6 Despliegue en nodos satélites:
  - Binarios `sentinel-hex-daemon`, `sentinel-qhc-agent` y `sentinel-pai-neural` actualizados en Kingu, Marte y Laptop.
  - Servicio nativo `sentinel-cortex.service` desplegado y activo en la Laptop (puerto 8001), conectando a la malla MyCNet (`fractal_source_connected: true`).

## Evidencia de ejecución

- 2026-11-05: inspección documental y de código local en `sentinel-cortex/src/main.rs`, `sentinel-cortex/src/memory/crystal_runtime.rs`, `sentinel-cortex/src/quantum/quantum_scheduler.rs`, `me-60os-core/src/qhc.rs` y `me-60os-core/src/quantum_core.rs`.
- Observado en el checkout: `tick_dtc()` modula fase y sincroniza SHM al límite QHC de 68 ticks; el hilo ejecuta `step()` cada 500 ms y procesa entradas de manera continua; el scheduler gatea solo el trabajo que recibe y permite rutas críticas/overflow fuera del portal.
- El repositorio no fue desplegado ni se ejecutaron pruebas durante esta revisión. El usuario reporta que EXP-028 se probó en un sistema desplegado; esta revisión no obtuvo un registro de esa ejecución y conserva el reporte atribuido, sin invalidarlo.
- La sincronización QHC de 68 ticks y la capacidad de historial PID de 68 entradas no son por sí mismas evidencia de limpieza global de entropía cada 68 ticks.

## Workflow follow-up

- Cerrar las tareas documentales tras validar los artefactos y registrar el cambio en ambos repositorios.
- La brecha de integración operativa queda documentada como estado pendiente de verificación, no como redefinición ni reemplazo del mecanismo.