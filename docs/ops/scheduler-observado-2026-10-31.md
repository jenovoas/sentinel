# Scheduler observado de Cortex — 2026-10-31

## Problema comprobado

El binario anterior encolaba `LatticeGC`, `PhaseAlign` y `BackupS60` con callbacks vacíos. El worker no consultaba su contador ni ejecutaba operaciones a raíz de esos callbacks. Además, el heartbeat del agente QHC invocaba `inject_bio_pulse`: vitalidad de proceso se convertía en coherencia biológica acumulada.

Antes de corregirlo, `/health` informó `tasks_in_portal=1278`, `efficiency=100`, `bio_coherence_raw=12942000`, `bio_portal_open=true`, con QHC conectado y `coherence=0` en el otro motor. Ese100 no era medición de energía ni prueba de tareas productivas completadas.

## Fuente y decisión operativa

- [EXP031](../../quantum/experiments/EXP_031_DUAL_LANE_PORTAL.md) documenta igualdad de fase y amplitud entre lanes, pero no define una agregación de vectores. Aquí se usa una interpretación conservadora suficiente: igualdad raw **nodo a nodo**, igual tamaño no vacío y alguna amplitud no nula. No se afirma equivalencia con otras definiciones experimentales ni validación física.
- `CrystalRuntime::dual_lane_portal_open` observa sus dos matrices existentes. No crea otra lattice, no copia arrays y no modifica fase, amplitud, QHC o PID para conseguir una apertura.
- El análisis mediana/MAD de EXP028 clasifica retrospectivamente muestras de un ciclo. No se transforma en una autorización online usando datos futuros.
- El detector sinusoidal permanece para la interfaz C/experimentos. El binario productivo usa exclusivamente `tick_observed` con el estado dual observado, acoplado al tick DTC; no usa un temporizador para declarar portales.

## Trabajo real y propiedad

El thread propietario de CrystalRuntime posee también `QuantumScheduler<CrystalTask>`. Las tareas nativas llevan datos tipados y un ejecutor que devuelve `Result`; no necesitan callbacks con captura alojados en heap ni una segunda instancia del runtime.

La tarea nativa implementada es `BackupS60`: llama al `persist()` existente, verifica su resultado y solo entonces acredita éxito. Mantiene el plazo local anterior de60s. Si no se despacha por el portal, se ejecuta como **crítica**, incluso con dead-man latched; no se presenta como una tarea ejecutada en portal ni como overflow. Un error suma `tasks_failed`, no éxito. No se añaden reintentos ni cola durable.

No se inventó una política de GC ni se reutilizó `reset()` para borrar cristales. La modulación QHC y la corrección dual PID ya corren mediante `tick_dtc()` y `step()`; no se duplican como `PhaseAlign`. Se retiraron los tres encolados periódicos ficticios. Las clasificaciones del ABI C siguen existiendo para callbacks suministrados por sus consumidores; no son operaciones nativas incorporadas.

Los checkpoints son estado local publicado por el mecanismo existente de escritura/rename; no equivalen a backup externo, garantía ante pérdida de energía, HA ni restauración de toda la plataforma.

## Presencia y seguridad

Se retiró `record_pilot_heartbeat` y su llamada desde QHC. El QHC conectado sigue visible como vitalidad del agente; no genera coherencia BIO ni demuestra presencia humana. Se conserva el dead-man latched para trabajo no crítico; no se rearma automáticamente por recuperar QHC.

La entrada BIO autorizada del scheduler productivo no queda implementada por este cambio: el listener Redis anterior actualiza otro ResonanceEngine, y el singleton FFI es otra instancia. No se conecta un publicador sintético ni se autoriza trabajo por una señal no validada. Sin presencia real, puede observarse `scheduler_emergency_shutdown=true`: es el latch del planificador no crítico, **no** apagado del servidor, DTC, drive o checkpoint crítico.

## Métricas y límites

- `tasks_in_portal`, `tasks_forced`, `tasks_critical`: ejecuciones exitosas por ruta de despacho.
- `tasks_failed`: intentos que devolvieron error.
- `scheduler_queue_len`, `scheduler_emergency_shutdown`, `dual_lane_portal_open`: estado del planificador y observación dual.
- `dtc_ticks`: contador software existente de CrystalRuntime, publicado para monitorizar la cadencia; no es el tick externo QHC ni un reloj físico medido.
- `efficiency`: porcentaje de éxitos despachados por portal, no eficiencia energética. Sin éxitos, `efficiency_available=false`.

Health y dashboard leen un snapshot breve; no mantienen el mutex del scheduler durante compresión/escritura del checkpoint. El campo histórico `timestamp_s60` de health no se usa como evidencia temporal en esta verificación.

## Verificación de código

- 62 pruebas de biblioteca pasaron con el motor y observación dual integrados.
- 70 pruebas del binario pasaron; se excluyó expresamente `tests::test_truth_claim_handler_smoke_aiopsdoom_intercept`, cuyo fallo ya estaba registrado. No se declara suite completa verde.
- Compilaron EXP033/EXP034 tras anotar el tipo de callback C. No se ejecutaron ni se usaron sus callbacks vacíos como evidencia productiva.
- Pruebas de comportamiento cubren gates, ausencia/latch, backup crítico posterior al latch, fallos sin éxitos ficticios, orden FIFO y no duplicación; la observación dual cubre estados iguales activos, diferencias de fase/amplitud, ground state y no mutación.

La verificación productiva se registra separadamente de estas pruebas; ninguna prueba de modelo demuestra apertura física de un portal.

La interfaz C conserva callbacks `void(void)`: puede acreditar su retorno, no
confirmar por sí sola el resultado de negocio de un callback externo. La
confirmación `Result` se aplica al ejecutor nativo de este despliegue. No se
publicó ni se validó aquí el bridge Python histórico como servicio productivo.

## Primer smoke del trabajo crítico

La versión intermedia `scheduler-observed-1` acreditó dos checkpoints reales
en una observación de125.97s: el contador crítico pasó1→3, no hubo tareas de
portal/overflow ni errores, y se verificaron dos cambios de archivo gzip/JSON
con ambas lanes y67951 nodos. La coherencia BIO permaneció0 con QHC conectado.
Esa prueba verifica el ejecutor/checkpoint; la versión final `-2` acopla además
la observación a cada tick DTC en vez del sondeo intermedio de1Hz.

## Despliegue final y smoke productivo

- Fenix/main: `sentinel-cortex:7252de99-scheduler-observed-2`, imagen
  `sha256:4640cb7d6bf78801e30bd83a4d2c1a7c52547922d1b9c4ef32dc1ac6ca4c509a`.
- Se recreó únicamente Cortex entre05:10:15 y05:10:56 UTC; terminó healthy.
  No se reiniciaron Docker global, bases, Redis, MyCNet ni firewall.
- Configuración validada con el script existente; backup protegido:
  `/etc/sentinel/backend.env.pre-cortex-uplink-20261031T051015Z`.
  La imagen anterior se conserva para rollback.
- El binario final volvió a pasar70 pruebas con la misma exclusión explícita
  de TruthSync; no se repitió ese fallo.
- Observación de125.79s: se verificaron dos cambios posteriores del checkpoint
  real, gzip/JSON válidos, versión2,67951 nodos y ambas lanes con67951 registros.
  El tick guardado avanzó3711251→3716261; no se infirió éxito por tamaño de archivo.

Muestras de la misma instancia final:

| Campo | Inicio | Final |
|---|---:|---:|
| `tasks_critical` | 1 | 3 |
| `tasks_in_portal` | 0 | 0 |
| `tasks_forced` | 0 | 0 |
| `tasks_failed` | 0 | 0 |
| `scheduler_queue_len` | 0 | 0 |
| `bio_coherence_raw` | 0 | 0 |
| `dtc_ticks` | 3002 | 8246 |
| Envíos MyCNet acumulados | 3982395 | 4010240 |

QHC permaneció conectado/no obsoleto y la fuente SHM de MyCNet conectada.
`scheduler_emergency_shutdown=true`: no hubo pulso de operador validado en
esa instancia; aun latched se completó trabajo crítico. El campo dual fue
false en las muestras registradas y no se acredita una apertura de portal.
No se inyectaron señales para forzar el resultado.

El contador DTC avanzó5244 en125556422670ns entre las lecturas temporizadas:
`5244 * 10^12 / 125556422670`, truncado a41766mHz (aprox.41,766Hz).
Es tasa observada del contador **software**, con muestreo HTTP y su latencia;
no certifica cada fase, deriva del reloj, sincronización distribuida ni cristal
físico. El endpoint detallado del runtime conserva autenticación.

## Índice y pendientes explícitos

Graphify extrajo71 archivos por AST local, pero la actualización global volvió
a agotar300s sin completar. No se declara el índice actualizado. Informó
extractor SQL ausente y extracción parcial en dos archivos C no modificados.

Fuera de esta corrección: entrada autorizada de presencia de operador, política
real de GC si se necesita, acciones nativas adicionales con contrato probado,
backup externo/HA, fallo TruthSync conocido y rotación de secretos ya registrada.
No se promueven los experimentos o callbacks C a servicios desplegados por
haber compilado.
