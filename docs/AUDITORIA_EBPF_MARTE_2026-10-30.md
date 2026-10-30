# Auditoría eBPF de Marte — 2026-10-30

## Captura viva

Solo lectura por SSH a `marte`, 2026-10-30 16:16 UTC; recaptura 16:54 UTC:

- `sentinel-ebpf.service` activo; `sentinel-security-gateway.service` activo; `sentinel-ebpf-forwarder.service` inactivo.
- `bpftool prog show` encontró `guardian_cognitive` como único programa Sentinel por nombre, ID 292. El link LSM está adjunto.
- Pines presentes: `guardian_alpha/events`, `guardian_alpha/guardian_link`, `guardian_alpha/guardian_mode_map`, `guardian_alpha/guardian_prog`, `guardian_alpha/guardian_rodata`, `guardian_alpha/whitelist_map`.
- `guardian_mode_map[0]=0` (auditoría). La primera nota contó líneas del volcado y reportó 8.246 como entradas; recuento posterior del JSON de `bpftool` da **2.748 entradas**. El rollback está instalado y SSH administrativo escucha en TCP/4222.
- `/usr/local/lib/sentinel/ebpf/` contiene solo `guardian_cognitive.o` y `attacher`.
- En la recaptura 16:54 UTC, ambos servicios siguen `active` y `enabled`; `guardian_cognitive` (ID 292) continúa como único LSM Sentinel adjunto. `EBPF_EVENTS_PATH` apunta a `/sys/fs/bpf/guardian_alpha/events`; no está configurado `EBPF_EVENTS_PATHS`.

## Código de despliegue frente a fuentes eBPF

El paquete systemd (`scripts/package-sentinel-ebpf.sh`, `scripts/install-sentinel-ebpf.sh`, `ebpf/Makefile`) construye e instala solo `guardian_cognitive.o`. Las fuentes `ai_guardian.c`, `guardian_gamma.c` y `float_detector.c` no están en ese bundle.

- `guardian_gamma.c` es observador (kprobes de detach/desaparición), pero `gamma_watchdog.c` busca los pines peer directamente bajo `/sys/fs/bpf`; en Marte Guardian está bajo `/sys/fs/bpf/guardian_alpha/`. Sus mapas/eventos tampoco están integrados al servicio Gateway actual.
- `ai_guardian.c` tenía hooks LSM que retornaban `-EPERM` para decisiones de whitelist/clasificador. Commit `4d8f65ca` añade mapa `ai_guardian_mode` con auditoría por defecto y eventos separados de denegación potencial; aún falta loader, política de agentes y consumidor configurado.
- `float_detector.c` permite desconocidos por defecto y emite eventos, pero puede negar entradas en `float_block_map`. Commit `4d8f65ca` añade `float_detector_mode`, auditoría por defecto y evento `FLOAT_WOULD_BLOCK`; aún falta loader, política de mapas y consumidor configurado. No copiar la whitelist general como clasificación S60 sin evidencia experimental.
- No se debe adjuntar estos módulos sin modo de auditoría predeterminado y ruta de eventos validada.

## Preparación verificada

- `clang -target bpf` compiló correctamente `ai_guardian.c`, `guardian_gamma.c` y `float_detector.c` a `/dev/null` (verificación de compilación, sin instalarlos ni adjuntarlos).
- Commit `8e15c786` añade al Gateway `EBPF_EVENTS_PATHS`, una lista de mapas ring buffer como `<pin>=<guardian_code>`. Mantiene compatibilidad con `EBPF_EVENTS_PATH`; asigna fuente/WAL por código Guardian y permite consumir varios mapas.
- Commit `4d8f65ca` añade modos fail-open de auditoría para AI Guardian/Float y reconoce los eventos ABI 19–23 en el parser. Ambos objetos BPF y el Gateway compilan localmente.
- `cargo check --locked --package sentinel-cortex --bin sentinel-security-gateway` pasó. `cargo fmt --check` y `git diff --check` pasaron después del formateo. No se ejecutaron pruebas.

## Estado

Marte sigue ejecutando solo el Guardian actual en modo auditoría. Los otros objetos no se instalaron ni adjuntaron en esta intervención. Para completar el despliegue se requiere empaquetar y cargar los objetos con mapas separados, definir/poblar mapas AI/Float desde políticas verificables, configurar sus pins en `EBPF_EVENTS_PATHS`, corregir el pinning y consumidor de Gamma, y validar recepción en Gateway→WAL→Fenix. Enforcement queda fuera de este cambio.
