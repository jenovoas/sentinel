# Arquitectura funcional de Sentinel y lectura de sus experimentos

**Corte operativo usado:** auditoría multi-nodo del 2026-10-30.  
**Fuentes de diseño:** índices y experimentos de `personalvault/Experimentos/`, `INDICE_MAESTRO_EXPERIMENTOS_RUST.md`, `PROGRESO_TEMPORAL_PY_A_RUST.md` y `MAPA_ISOMETRIAS.md`.  
**Regla:** los documentos de la vault conservan modelo, hipótesis, resultados y recorrido histórico. Git/código y verificaciones de runtime determinan qué está implementado y activo hoy.

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
- El filtro integrado SCV/`EntropicFirewall` calcula entropía y decide validez; `LfmSecurityPipeline` también sanitiza ingreso y audita salida. La cobertura de cada ruta de producción aún se debe trazar de extremo a extremo.
- TruthSync conserva dos responsabilidades: el filtro integrado de seguridad/entropía y el pod/Truth Core de verificación y score de contenidos. Git conserva un paquete Kubernetes/Compose histórico (`639383a2`, `86bdffdd`) que fue eliminado del árbol activo por `0c5780f7`. Ese artefacto contiene partes simuladas y score fijo; es recuperable, pero necesita auditoría funcional. No hay evidencia Git/runtime de que se aplicara en producción.
- Crystal Cipher vive en `me-60os-core/src/crystal_cipher.rs` y deriva una clave usada con AES-256-GCM; el comentario especifica intención de proteger SHM/ringbuf. No se encontraron consumidores fuera de la declaración pública/documentación: su integración operativa está pendiente.

## 5. Topología multi-nodo acordada y estado

- **Kingu:** frontend/BFF; el navegador entra a la API de Fenix.
- **Fenix:** backend central de Sentinel (FastAPI, Cortex Rust, PostgreSQL, Redis y QHC). MyCNet y Sentinel comparten QHC; SOMA queda fuera.
- **Marte:** backend de seguridad/observabilidad asignado por Jaime: Guardian/eBPF, Grafana, Mimir, Prometheus, TruthSync y Loki. Marte observa/consulta Fenix por WireGuard; Truth Core debe ser privado y quedar detrás del gateway FastAPI de Fenix.
- **Estado observado en auditoría 2026-10-30:** backend core de Fenix y QHC comprobados; el stack de Marte todavía no estaba desplegado/verificado en esta sesión. No se declaró completada la red completa. La ubicación objetivo no sustituye a evidencia de instalación ni aceptación de flujo.

## 6. Criterio común para afirmar estado

Clasificar cada componente como **modelo documentado**, **prototipo/experimento**, **implementado en código**, **integrado en una ruta**, **desplegado en host** o **validado de extremo a extremo**. Son estados diferentes. Antes de atribuir una capacidad, registrar fuente, commit, versión, host, runtime y resultado observable. Los índices de vault de agosto son mapas de navegación; sus estados de producción deben reconciliarse con el corte operativo actual.
