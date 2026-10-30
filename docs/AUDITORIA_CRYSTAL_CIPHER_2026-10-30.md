# Auditoría de Crystal Cipher — 2026-10-30

## Alcance y resultado

Revisión de `me-60os-core/src/crystal_cipher.rs`, su oscilador, llamadas de producción, documentación de diseño en `personalvault/Sistemas/Crystal_Cipher.md`, rutas eBPF→Cortex e historial Git. No se ejecutaron pruebas ni se modificó el cifrador o runtime.

La especificación de la vault define el pulso del cristal como semilla y declara el acople a datos que watchdog/Cortex/Guardian comparten por SHM y ring buffer. La ausencia actual de esa integración y de la entrada eBPF necesaria es una brecha de despliegue/cableado; la auditoría anterior la presentó erróneamente como defecto aislado del diseño criptográfico. El módulo Rust sigue sin consumidores productivos fuera de sus pruebas y no está conectado a SHM, ring buffer LSM ni Gateway.

## Evidencia del código y del diseño

- `CrystalCipher::new()` crea un `IsochronousOscillator` local. El oscilador inicializa fase y amplitud en cero; la ruta externa que debe alimentar/compartir el estado del cristal todavía no aparece conectada en este módulo.
- `rotate()` calcula `BLAKE3(phase_raw || pulse || amplitude_raw)`, coherente con la intención documentada de derivar del pulso/fase del cristal. En la implementación aislada actual el estado empieza desde cero y no recibe entrada eBPF; por eso no debe usarse este estado como evidencia de que la cadena desplegada alimenta Cipher.
- Existe una ruta general de eventos eBPF: `EbpfBridge` entrega `entropy_signal` a consumidores Cortex/lattice. El binario `ebpf/guardian_cognitive.c` actualmente asigna `entropy_signal=0`, y no se encontró conexión de esa ruta con `CrystalCipher`. El empaquetador/instalador systemd vigente (`scripts/package-sentinel-ebpf.sh`, `scripts/install-sentinel-ebpf.sh`, `ebpf/Makefile`) compila e instala solo `guardian_cognitive.o`; `ai_guardian.c`, `guardian_gamma.c` y `float_detector.c` no están incluidos. Estas fuentes producen señales distintas; mapearlas al recorrido y experimentos previstos antes de incorporarlas al bundle.
- El empaquetador/instalador systemd vigente (`scripts/package-sentinel-ebpf.sh`, `scripts/install-sentinel-ebpf.sh`, `ebpf/Makefile`) compila e instala solo `guardian_cognitive.o`. Otros productores están en fuentes separadas: `ai_guardian.c` emite señales 0.15/0.85·SCALE_0, `guardian_gamma.c` emite guardian_code·SCALE_0, y `float_detector.c` emite severidad/señal PAI. No están incluidos en ese bundle. Esta brecha de alcance coincide con la falta de fuentes eBPF que señalaste; el objeto cognitivo instalado no representa toda la cadena.
- Hay además una ruta dinámica histórica distinta: `hex_daemon` consulta `sentinel_lattice_total_energy` en `/metrics` y llama `HexagonalController::compute_crystal_coupled_key(energy, tick)`. Esta función combina energía del lattice y tick, devuelve un entero módulo 60 y el daemon lo imprime; no cifra payloads con AES-GCM ni instancia `CrystalCipher`. Por eso el nombre `CrystalCipher` no basta para representar la ruta histórica completa. El origen de energía de esa métrica debe cotejarse con eBPF y los drives Cortex activos.
- Los experimentos de la vault explican el papel de la alimentación: EXP-001/002 describen el cristal como sistema impulsado y la pérdida bajo disipación; EXP-003 añade feedback PID para recuperar amplitud. Esto hace que una instancia local aislada sin el flujo de excitación no represente el cristal operativo completo. El drive CPU de Cortex observado en código es otra entrada existente; no equivale a los eventos Guardian/eBPF que faltan en la cadena de seguridad.
- AES-256-GCM antepone un nonce aleatorio de 96 bits al ciphertext desde los cambios Git del 2026-10-22 (`5cb4e51a`, luego ajuste de fachada `5ff5cb32`).
- `current_key()` devuelve los 32 bytes de la clave en claro. Debe revisarse en el contexto de la integración prevista: quién la llama, cómo se comparte entre extremos, cómo se sincroniza la rotación y cómo se recupera el estado tras reinicio. Esta revisión sin cableado no determina por sí sola el comportamiento previsto del protocolo completo.
- `tick_breath()` rota cada cuatro pulsos. `force_rotate()` vuelve a derivar del mismo estado local.
- `rg CrystalCipher` encuentra llamadas solo en las pruebas; no hay callsite productivo en Cortex, Gateway o backend.

## Decisión operativa

El despliegue de Crystal Cipher queda pendiente porque falta completar la cadena eBPF→Cortex/cristal→Cipher→SHM/ring buffer y demostrar su sincronización. El bundle actual instala solo `guardian_cognitive.o` (cuya señal es cero); `ai_guardian`, `guardian_gamma` y `float_detector` existen como fuentes separadas pero no están en el paquete systemd de instalación. El puente general no llega a `CrystalCipher`. También existe una ruta histórica `hex_daemon` que deriva un valor S60 de energía agregada, pero no cifra payloads AES-GCM. No concluir que la intención de derivación del cristal sea un error a partir del estado aislado.

Como gate de integración: identificar el eBPF y productor de señal previstos; documentar unidades/escala S60; confirmar cómo se actualiza el estado del cristal en ambos extremos; sincronizar tick/rotación y reinicios; y verificar protocolo, nonce, contexto autenticado y manejo/exposición de claves en la ruta real. Preservar el diseño del cristal; no sustituirlo por una fuente aleatoria genérica sin cotejar documentación y experimentos.

## Trazabilidad

- Código vigente: `me-60os-core/src/crystal_cipher.rs`, `me-60os-core/src/isochronous_oscillator.rs`, `me-60os-core/src/ebpf_cortex_bridge.rs`, `me-60os-core/src/cortex.rs` y `ebpf/guardian_cognitive.c`.
- Paquete eBPF contrastado: `ebpf/Makefile`, `scripts/package-sentinel-ebpf.sh`, `scripts/install-sentinel-ebpf.sh`; productores separados `ebpf/ai_guardian.c`, `ebpf/guardian_gamma.c`, `ebpf/float_detector.c`.
- Ruta dinámica histórica: `me-60os-core/src/bin/hex_daemon.rs` y `me-60os-core/src/hexagonal_control.rs::compute_crystal_coupled_key`.
- Diseño y experimentos persistentes consultados: `personalvault/Sistemas/Crystal_Cipher.md`, `Experimentos/EXP_001_CRYSTAL_RESONANCE.md`, `EXP_002_CRYSTAL_NETWORK_FULL_REPORT.md`, `EXP_003_PID_STABILIZATION.md`, `EXP_027_YHWH_PULSE_MONITOR.md` y `EXP_031_DUAL_LANE_PORTAL.md`.
- Historial: creación `b0b2bca4` (2026-08-06); cambios de nonce `5cb4e51a` y `5ff5cb32` (2026-10-22).
- Runtime: no inspeccionado para el módulo Cipher porque no tiene consumidor productivo identificado. No se afirma despliegue ni ausencia de archivos del módulo en hosts.
- Validación: lectura de diseño, código, callsites e historial. Pruebas no ejecutadas.
