# Continuación de auditoría eBPF de Marte — 2026-10-30

## Estado

**Preparación local; no desplegada en Marte.** La captura de runtime registrada en `AUDITORIA_EBPF_MARTE_2026-10-30.md` mostró únicamente `guardian_cognitive` adjunto y en auditoría. Esta nota no cambia esa evidencia.

Recaptura de solo lectura por SSH, 2026-10-30 16:54 UTC: los servicios `sentinel-ebpf` y `sentinel-security-gateway` siguen activos/habilitados; el ID 292 `guardian_cognitive` es el único LSM Sentinel adjunto; Gateway consume `/sys/fs/bpf/guardian_alpha/events` mediante `EBPF_EVENTS_PATH` (sin `EBPF_EVENTS_PATHS`). Recuento JSON verificado de `whitelist_map`: 2.748 entradas. La cifra 8.246 de la primera captura contaba líneas y queda corregida.

## Hallazgos de código

- `scripts/package-sentinel-ebpf.sh` empaqueta solo `guardian_cognitive.o`; `install-sentinel-ebpf.sh` instala y configura únicamente ese Guardian.
- `ai_guardian.c` tenía cuatro retornos LSM `-EPERM` sin mapa de modo. Su whitelist y mapas de agentes tampoco los inicializa el bootstrap de producción.
- `float_detector.c` bloqueaba coincidencias explícitas de `float_block_map`; si la whitelist está vacía, emite un evento para cada ejecutable desconocido. Adjuntarlo sin preparar y verificar los mapas podría generar denegaciones o volumen de eventos no previsto.
- El bridge Rust ya admite ring buffers múltiples por `EBPF_EVENTS_PATHS`, pero el parser omitía códigos de evento 19–20 definidos en el ABI.
- `guardian_gamma.c` y `gamma_watchdog.c` tienen requisitos adicionales de pins, mapas peer y consumidor; no son parte de esta preparación.

## Cambios locales preparados

- Se añadió `ai_guardian_mode` y `float_detector_mode` (mapas ARRAY de una entrada). Valor `0`/no inicializado conserva auditoría; enforcement solo ocurre con valor exacto `1`.
- AI Guardian informa denegaciones potenciales como `FILE_WOULD_BLOCK`/`EXEC_WOULD_BLOCK`, sin devolver error en auditoría. Los eventos llevan `GUARDIAN_CODE_AI` y estado de modo en `reserved[1]`.
- Float Detector informa la coincidencia explícita de blacklist como `FLOAT_WOULD_BLOCK` y permite la operación en auditoría.
- El bridge ahora interpreta eventos 19–23.

## Validaciones

- Compilación BPF a objetos temporales: `ai_guardian.c` y `float_detector.c`, `clang -target bpf`: correcta.
- `cargo check --locked --package sentinel-cortex --bin sentinel-security-gateway`: correcto; quedan cuatro warnings preexistentes de constantes DTC SHM sin uso.
- `cargo fmt --check` y `git diff --check`: correctos.
- No se cargó ni adjuntó ningún objeto; no se modificó Marte. No se habilitó enforcement.

## Trabajo pendiente antes del despliegue

1. Diseñar carga/attach con pins estables y recuperación segura para cada programa; el attacher actual está acoplado al objeto y link de Guardian cognitive.
2. Definir y poblar mapas AI (`ai_agents_map`, whitelist, god-mode y decision tree) y Float (`float_safe_map`, `float_block_map`, `float_redirect_map`) desde fuentes verificadas. No asumir que la whitelist de ejecutables implica certificación S60.
3. Integrar sus mapas de eventos en el Gateway y definir límites/retención para eventos por ejecutable.
4. Corregir y validar el contrato de peers/pins de Gamma, luego agregar consumidor y servicio watchdog según su diseño.
5. Empaquetar, instalar en modo auditoría y verificar runtime en Marte; enforcement queda separado y requiere autorización explícita.
