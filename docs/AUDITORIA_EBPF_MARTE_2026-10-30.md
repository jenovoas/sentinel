# Auditoría eBPF de Marte — 2026-10-30

## Captura viva

Solo lectura por SSH a `marte`, 2026-10-30 16:16 UTC:

- `sentinel-ebpf.service` activo; `sentinel-security-gateway.service` activo; `sentinel-ebpf-forwarder.service` inactivo.
- `bpftool prog show` encontró `guardian_cognitive` como único programa Sentinel por nombre, ID 292. El link LSM está adjunto.
- Pines presentes: `guardian_alpha/events`, `guardian_alpha/guardian_link`, `guardian_alpha/guardian_mode_map`, `guardian_alpha/guardian_prog`, `guardian_alpha/guardian_rodata`, `guardian_alpha/whitelist_map`.
- `guardian_mode_map[0]=0` (auditoría); whitelist con 8.246 entradas. El rollback está instalado y SSH administrativo escucha en TCP/4222.
- `/usr/local/lib/sentinel/ebpf/` contiene solo `guardian_cognitive.o` y `attacher`.

## Código de despliegue frente a fuentes eBPF

El paquete systemd (`scripts/package-sentinel-ebpf.sh`, `scripts/install-sentinel-ebpf.sh`, `ebpf/Makefile`) construye e instala solo `guardian_cognitive.o`. Las fuentes `ai_guardian.c`, `guardian_gamma.c` y `float_detector.c` no están en ese bundle.

- `guardian_gamma.c` es observador (kprobes de detach/desaparición), pero `gamma_watchdog.c` busca los pines peer directamente bajo `/sys/fs/bpf`; en Marte Guardian está bajo `/sys/fs/bpf/guardian_alpha/`. Sus mapas/eventos tampoco están integrados al servicio Gateway actual.
- `ai_guardian.c` tiene hooks LSM que retornan `-EPERM` para decisiones de whitelist/clasificador; no tiene un modo auditoría común al Guardian instalado.
- `float_detector.c` permite desconocidos por defecto y emite eventos, pero puede negar entradas en `float_block_map`; requiere modo seguro explícito y un plan para poblar la whitelist/event reader.
- No se debe adjuntar estos módulos sin modo de auditoría predeterminado y ruta de eventos validada.

## Preparación verificada

- `clang -target bpf` compiló correctamente `ai_guardian.c`, `guardian_gamma.c` y `float_detector.c` a `/dev/null` (verificación de compilación, sin instalarlos ni adjuntarlos).
- Commit `8e15c786` añade al Gateway `EBPF_EVENTS_PATHS`, una lista de mapas ring buffer como `<pin>=<guardian_code>`. Mantiene compatibilidad con `EBPF_EVENTS_PATH`; asigna fuente/WAL por código Guardian y permite consumir varios mapas.
- `cargo check --locked --package sentinel-cortex --bin sentinel-security-gateway` pasó. `cargo fmt --check` y `git diff --check` pasaron después del formateo. No se ejecutaron pruebas.

## Estado

Marte sigue ejecutando solo el Guardian actual en modo auditoría. Los otros objetos no se instalaron ni adjuntaron en esta intervención. Para completar el despliegue se requiere añadir modo auditoría fail-open a los hooks AI/Float, corregir el pinning/observador Gamma, empaquetar y cargar los objetos con mapas separados, configurar sus pins en `EBPF_EVENTS_PATHS`, y validar recepción en Gateway→WAL→Fenix. Enforcement queda fuera de este cambio.
