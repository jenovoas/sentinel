# Arquitectura funcional de Sentinel y lectura de sus experimentos

**Corte operativo usado:** auditoría multi-nodo del 2026-10-30.  
**Fuentes de diseño:** índices y experimentos de `personalvault/Experimentos/`, `INDICE_MAESTRO_EXPERIMENTOS_RUST.md`, `PROGRESO_TEMPORAL_PY_A_RUST.md` y `MAPA_ISOMETRIAS.md`.  
**Regla:** los documentos de la vault conservan modelo, hipótesis, resultados y recorrido histórico. Git/código y verificaciones de runtime determinan qué está implementado y activo hoy.

Los PDFs fuente entregados por Jaime están en la laptop, `~/Documentos/Papers/` (P mayúscula), accesible desde Fenix por el alias SSH `laptop`. Seguir las citas que aparecen en los headers Rust y en las trazas de `Experimentos/`; las notas indexadas de la vault no reemplazan la lectura del paper citado.

## 1. Qué es Sentinel

Sentinel es una plataforma de seguridad y cómputo con estado. Su diseño combina análisis de eventos del host, validación de datos, lógica matemática de fase/amplitud, memoria distribuida y una capa de API/visualización. Los experimentos de cristales, resonancia, mallas y memoria explican el modelo computacional que guía sus módulos; los despliegues llevan partes concretas de ese modelo a servicios y nodos.

La división Python/Rust es deliberada. Según Jaime, Python conserva el modelo y la lógica matemática, junto con los experimentos y su historia; Rust migró la mayoría de los caminos de ejecución intensivos, en especial memoria de cristales y mallas. Python es referencia activa del modelo y banco de estudio, no material redundante que se pueda borrar por estar migrada una ruta. El runtime actual tampoco debe describirse como “100% Rust”: el backend FastAPI de Fenix es Python y Cortex y los componentes numéricos/mallas son Rust.

## 2. Modelo numérico y ciclo del sistema

- El núcleo usa SPA en punto fijo sexagesimal, con `SCALE_0 = 60^4 = 12_960_000` en `me-60os-core/src/spa.rs`. Para control/seguridad se priorizan enteros escalados. Otros tipos y métricas pueden tener escalas distintas; no asumir que todo `S60` tiene la misma unidad.
- PAI-60 convierte entradas discretas a amplitudes antes de inyectarlas en osciladores/matrices. Los métodos de inyección que reciben enteros reescalan internamente; no pasarles valores raw SPA.
- QHC mantiene el pulso compartido y el patrón de corrección temporal. Es requerido por Sentinel y MyCNet. La sincronización temporal impulsa las estructuras; el paso de una malla puede ser disipativo y necesita drive activo donde corresponda.
- `ResonantMatrix` representa mallas/cristales con estado de fase y amplitud. `LiquidLattice` explora difusión local y retención; la evolución de EXP-001–016 va de oscilador individual, pruebas que fallan bajo ruido, ECC, malla líquida, almacenamiento en canales de energía/fase y problemas de escala hacia estructuras Rust más compactas.
- Las memorias SHM/dual lane separan estados A/B y permiten compartirlos entre procesos. QHC y las semillas sincronizan las mallas; snapshot/checkpoint aporta recuperación. Cada pieza debe verificarse en el runtime actual: una clase compilada o un binario experimental no prueba el flujo completo entre daemons.

## 3. Qué enseñan los experimentos

| Línea experimental | Aporte al diseño | Límite de evidencia registrado |
|---|---|---|
| EXP-001–008: resonancia, almacenamiento, PID, ruido y ECC | Expone disipación, pérdida bajo ruido y límites de una celda/arreglo discreto; motiva mallas y control activo. | Varios resultados son simulaciones Python históricas. Los reportes no demuestran por sí solos física de hardware. EXP-006–008 no tienen bin Rust directo según el índice. |
| EXP-009/011: Liquid Lattice | Malla 3×3 con difusión de vecinos y retención como criterio; es la ruta de memoria líquida atribuida al Cortex Rust. | El 72% frente al 44% es un resultado reportado del modelo/benchmark, no una garantía para toda carga o nodo. |
| EXP-010/013/014/015: capacidad y memoria dispersa | Señala que la representación Python densa no escala; Rust reduce overhead y hace viable trabajar con matrices grandes. | Los multiplicadores de rendimiento requieren salida reproducible del benchmark. No extrapolarlos automáticamente a producción. |
| EXP-012: canal dual fase/energía | Almacena payloads en canales diferentes y define estabilización/recuperación de fase. | La traza Rust lo marca `verification: code-only`; cuantización byte/grado, padding y round-trip requieren pruebas vigentes antes de aceptar recuperación exacta. |
| EXP-016: persistencia | Contrasta snapshot, limpieza de RAM y recuperación; el experimento Python requiere backend Rust y se preserva como referencia. | No equivale a probar crash recovery de todos los procesos/volúmenes del despliegue actual. |
| EXP-019–021: migración S60 | Compara Python/Rust y reemplaza una ruta Python que recurría a `math.log` por matemática entera (`SPAMath::ln`) en la traza Rust. | La traza EXP-021 es explícitamente code-only; umbrales y divergencia deben sostenerse con resultados archivados, no solo con el criterio del bin. |
| EXP-026–028: calibración y resonancia | EXP-026 conserva resultado negativo; EXP-027 define QHC; EXP-028 desarrolla detección de ventanas/convergencia y distintas implementaciones. | La traza EXP-028 distingue simulación por senos de convergencia entre componentes reales. No presentar “portal” de simulación como estado detectado en producción ni como validación externa. |
| EXP-029 y EXP-031: scheduler/dual lane | Exploran ejecutar o leer con base en convergencia y sincronía A/B. | Hay implementaciones paralelas/no conectadas y métricas de vault que deben cotejarse con código y capturas runtime. La auditoría Oct-30 no aceptó todavía el flujo remoto dual-lane integral. |
| EXP-005/017/018: G-Zero, levitación y deriva relativista | Conservan hipótesis y modelos matemáticos que pueden alimentar investigación futura. | EXP-005 tiene una réplica Rust con fórmula, no evidencia de reducción de masa física; EXP-017/018 están clasificadas como hipótesis y no son funciones del runtime. |

Los artefactos Python con resultados imperfectos son preservados por política de la vault. No se eliminan ni se “limpian” automáticamente. Cada reporte debe seguir etiquetando método, código, dato observado, simulación, hipótesis y validación pendiente.

## 4. Seguridad, confianza y monitoreo

- Guardian/eBPF/LSM observa eventos del kernel; su presencia en código no demuestra que esté adjunto en un host. En Marte, cualquier attach requiere whitelist de ejecutables/rutas críticas y recuperación fuera de banda verificada. Enforcement es una autorización separada.
- `me-60os-core/src/scv.rs` contiene SCV/`EntropicFirewall`, pero el call graph no lo conecta al Gateway ni al Cortex servidor desplegados. `ScvEngine` aparece en rutas SOMA y `GuardianLsm` construidas desde SOMA; `EntropicFirewall::verify` aparece en BCI; `LfmSecurityPipeline` se usa en el binario TUI. El Gateway Marte activo ejecuta AIOpsShield semántico + `TelemetrySanitizer`, módulos diferentes. El eBPF desplegado `guardian_cognitive.c` emite `entropy_signal=0`; no hay dato válido para alimentar SCV. Por tanto, la capa integrada de entropía está pendiente en producción; el código del filtro no acredita despliegue.
- TruthSync conserva dos responsabilidades: el filtro integrado de seguridad/entropía y el pod/Truth Core de verificación y score de contenidos. Git conserva un paquete Kubernetes/Compose histórico (`639383a2`, `86bdffdd`) que fue eliminado del árbol activo por `0c5780f7`. Ese artefacto contiene partes simuladas y score fijo; es recuperable, pero necesita auditoría funcional. No hay evidencia Git/runtime de que se aplicara en producción.
- Crystal Cipher vive en `me-60os-core/src/crystal_cipher.rs` y deriva una clave usada con AES-256-GCM; el comentario especifica intención de proteger SHM/ringbuf. No se encontraron consumidores fuera de la declaración pública/documentación: su integración operativa está pendiente.

## 5. Topología multi-nodo acordada y estado

- **Kingu:** frontend/BFF; el navegador entra a la API de Fenix.
- **Fenix:** backend central de Sentinel (FastAPI, Cortex Rust, PostgreSQL, Redis y QHC). MyCNet y Sentinel comparten QHC; SOMA queda fuera.
- **Marte:** backend de seguridad/observabilidad asignado por Jaime: Guardian/eBPF, Grafana, Mimir, Prometheus, TruthSync y Loki. Marte observa/consulta Fenix por WireGuard; Truth Core debe ser privado y quedar detrás del gateway FastAPI de Fenix.
- **Estado observado en auditoría 2026-10-30:** backend core de Fenix y QHC comprobados; el stack de Marte todavía no estaba desplegado/verificado en esta sesión. No se declaró completada la red completa. La ubicación objetivo no sustituye a evidencia de instalación ni aceptación de flujo.

## 6. Criterio común para afirmar estado

Clasificar cada componente como **modelo documentado**, **prototipo/experimento**, **implementado en código**, **integrado en una ruta**, **desplegado en host** o **validado de extremo a extremo**. Son estados diferentes. Antes de atribuir una capacidad, registrar fuente, commit, versión, host, runtime y resultado observable. Los índices de vault de agosto son mapas de navegación; sus estados de producción deben reconciliarse con el corte operativo actual.

## 7. Cotejo de papers, experimentos, código y despliegue

Los papers se siguen desde las referencias que Jaime dejó en el código Rust y las trazas de la vault. La cita explica el fundamento o analogía del módulo; no demuestra por sí sola que el resultado físico del paper se replique en Sentinel ni que el módulo esté desplegado.

| Paper / experimento rastreado | Ruta que realmente implementa Sentinel | Consecuencia para el despliegue |
|---|---|---|
| Nandi–Vitiello, arXiv:2606.30890 y Nandi, arXiv:2503.19688; EXP-001/028 | `quantum_core.rs` / `S60PID` mantienen historia no Markoviana; `CrystalRuntime` avanza dos `ResonantMatrix` y publica lanes A/B en SHM. Cortex/Fenix es el proceso que ejecuta ese runtime. El paper deriva una dinámica Bateman dual y memoria reducida; no es evidencia de que Sentinel tenga el mismo sistema físico. | Aceptar Cortex solo con tick, historial, sincronizaciones A/B y checkpoint observables. Las constantes `DTC_CLOCK_SHM` no crean un reloj IPC: el objeto/tick DTC compartido sigue pendiente. QHC es servicio común Sentinel–MyCNet, pero `QHC=true` en Cortex no demuestra que MyCNet consuma el mismo snapshot ni que ambas aplicaciones compartan época/tick. |
| Zhang–Wang, arXiv:2511.13543; EXP-009 y persistencia EXP-016 | `LiquidLattice` y `NeuralMemory` se actualizan desde la ruta de eventos del Cortex; el checkpoint `.crystal` se escribe periódicamente. El paper estudia aprendizaje mecánico en una metasuperficie fonónica física. | LiquidLattice/SNN son componentes de software en Fenix; no requieren instalar una metasuperficie. La aceptación debe comprobar que el ring BPF real alimenta Cortex y que el checkpoint sobrevive reinicio/restauración; el código o un smoke bench no prueban por sí solos esos dos flujos en producción. |
| Lv et al., arXiv:2511.12537; `liquid_memory.rs` | La referencia trata memoria cuántica fotónica en cristales dopados de europio. Sentinel implementa almacenamiento lógico/SHM/snapshot, no fotones ni cristales materiales. | No sumar un servicio de hardware fotónico al despliegue. Mantener la referencia como motivación del modelo; validar persistencia y recuperación de software con su propio contrato y medidas. |
| Papers de optomecánica, arXiv:2412.14117, 2511.15492 y 2605.20902; `memory_phonon_smoke` / `opto_cooling_bench` | `optomechanical.rs` es modelo/bench. La tarea de Cortex descrita en `main.rs` deriva una señal térmica de `/proc/stat` y la inyecta como drive; no controla un resonador mecánico ni una cámara física. | No hay daemon de hardware que instalar. Describirlo como entrada térmica simulada/de host hasta que exista un driver y una fuente física medible. Conservar el drive periódico requerido por las mallas disipativas. |
| Bachl et al., arXiv:2102.09980 y Heimdall, arXiv:2605.25411; EXPs de seguridad | Bachl evalúa IDS de flujos con árbol de decisión dentro de eBPF; Heimdall presenta un proceso externo de migración verificada C-eBPF→Rust. `guardian_lsm`, `ebpf_cortex_bridge` y el lector en `sentinel-cortex/src/main.rs` son piezas Sentinel kernel/userspace; el daemon espera un ring buffer BPF fijado. Las citas no prueban que Sentinel use el mismo clasificador ni que su migración tenga verificación formal. | La meta es sensor Guardian/eBPF local en Marte y envío autenticado de eventos al backend FastAPI de Fenix. El lector local de Cortex no equivale a un forwarder Marte→Fenix. Falta desplegar/verificar el sensor de Marte y su forwarder de red; iniciar en auditoría tras whitelist y recuperación fuera de banda verificadas. |
| EXP-015/020/021, PAI-60 y comparaciones FPU | `CrystalRuntime`/`ResonantMatrix` usan `inject_pai`; el bin `fpu_vs_pai_bench` compara rutas numéricas fuera del servicio. La traza de EXP-015 marca el output reproducible como pendiente. | PAI-60 es lógica de runtime, no daemon. FPU es una característica del procesador y ruta de benchmark, no un módulo desplegable. No afirmar rendimiento, “liberación de FPU” ni cobertura exacta basándose solo en el header del bench. Respetar `SPA::from_int`/`from_raw` y no pasar raw SPA a métodos que reescalan enteros. |
| EXP-031, `ResonantMatrix` y `DualLaneRouter` | Hay dos conceptos distintos: lanes de memoria A/B en `CrystalRuntime` (SHM, Cortex/Fenix) y lanes de seguridad/observabilidad de `me-60os-core/src/dual_lane.rs`. El router de eventos aparece en tests/bench; no se encontró conectado a la ruta principal de ingesta de Cortex. | Desplegar/verificar memoria A/B no acepta el enrutamiento de seguridad/telemetría. Falta cablear Security/Audit con WAL síncrono y Observability con su colector/backpressure, y demostrar el recorrido de eventos de Marte hasta esos destinos. No llamar a ambos mecanismos “dual lane” sin especificar cuál. |

### Componentes que el cotejo deja fuera de un despliegue inmediato

- **Crystal Cipher:** `me-60os-core/src/crystal_cipher.rs` no tiene consumidor en la ruta Cortex observada. Su clave deriva de fase/amplitud/pulso deterministas, sin secreto de gestión de claves en el contrato actual; AES-GCM por sí solo no hace segura esa derivación. No usarlo para cifrar SHM/ring buffer en producción hasta integrar consumidores, definir claves secretas/rotación/reinicio y verificar unicidad de nonce bajo cada clave.
- **TruthSync:** el filtro SCV integrado y el servicio independiente Truth Core son funciones distintas. Truth Core en Marte sigue siendo una brecha de implementación/operación: el paquete histórico contiene procesamiento simulado o score fijo, así que primero se debe corregir y definir contrato privado autenticado; no basta con restaurar el manifiesto del pod.
- **FPU y hardware cuántico/fonónico/fotónico:** no son servicios ni artefactos de contenedor. Los papers de hardware sustentan analogías y preguntas de investigación; el código Sentinel actual es un modelo de software y no adquiere el hardware experimental por citar esos artículos.

### Brechas concretas derivadas para la red completa

1. Definir un contrato de época/unidad del QHC compartido y publicar el tick DTC por IPC/SHM para consumidores locales en Fenix; contrastar después el consumidor MyCNet sin inferirlo del estado de Sentinel.
2. En Marte, desplegar Guardian/eBPF en auditoría y un forwarder autenticado hacia `POST /api/v1/cortex/events` de Fenix; verificar BTF/LSM, whitelist, recuperación fuera de banda, identidad y evento recibido antes de ampliar firewall.
3. Desplegar Prometheus, Mimir, Loki y Grafana en Marte con destinos privados explícitos: scrape de Fenix, remote-write a Mimir, logs Fenix/Marte a Loki y datasources locales en Grafana. No reutilizar DNS interno de Compose entre hosts.
4. Recuperar y auditar Truth Core, reemplazar el procesamiento simulado/score fijo, y ponerlo detrás del gateway FastAPI de Fenix.
5. Conectar `DualLaneRouter` a la ingesta de eventos si las lanes de seguridad/observabilidad forman parte del alcance; aceptar esa ruta por WAL, persistencia y métricas independientes de las SHM A/B.
6. Mantener `CrystalCipher` fuera del despliegue de seguridad hasta resolver las brechas criptográficas documentadas arriba.

**Estado de esta actualización:** cotejo documental de papers/citas, experimentos y código local en rama `main`. No constituye despliegue nuevo ni cambia el estado operativo fechado en la auditoría 2026-10-30.
