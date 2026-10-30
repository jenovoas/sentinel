# Auditoría de Crystal Cipher — 2026-10-30

## Alcance y resultado

Revisión estática de `me-60os-core/src/crystal_cipher.rs`, su oscilador, llamadas de producción y cambios históricos de Git. No se ejecutaron pruebas ni se modificó el cifrador o el runtime.

Crystal Cipher existe como módulo Rust exportado por `me-60os-core`, pero no tiene consumidor fuera de sus pruebas. No está conectado a SHM, al ring buffer LSM ni al gateway de Marte. No hay evidencia de despliegue del módulo.

## Evidencia del diseño actual

- `CrystalCipher::new()` crea `IsochronousOscillator::new(name)`. El oscilador inicializa fase y amplitud en cero; el nombre solo ocupa el campo descriptivo y no participa en la derivación.
- `rotate()` calcula `BLAKE3(phase_raw || pulse || amplitude_raw)`. El pulso y fase evolucionan determinísticamente; no se inyecta amplitud en el cristal de este módulo, por lo que la amplitud permanece en cero. Instancias nuevas comienzan con la misma clave inicial y el mismo pulso produce la misma clave.
- AES-256-GCM antepone un nonce aleatorio de 96 bits al ciphertext. Git muestra que el 22-10-2026 se sustituyó la derivación determinista anterior del nonce por aleatoriedad del sistema (`5cb4e51a`, luego ajuste de fachada `5ff5cb32`). Esto corrige el nonce, pero no convierte en secreta la clave determinista.
- `current_key()` devuelve los 32 bytes de la clave en claro. No hay contrato de secreto compartido, establecimiento de claves, sincronización de rotación, recuperación tras reinicio ni aislamiento de claves.
- `tick_breath()` rota cada cuatro pulsos. `force_rotate()` vuelve a derivar del mismo estado y no aporta entropía nueva.
- `rg CrystalCipher` encuentra solo las llamadas dentro del módulo de pruebas; no hay callsite productivo en Cortex, Gateway o backend.

## Decisión operativa

No conectar ni desplegar este módulo para confidencialidad de datos reales todavía. AES-GCM es la primitiva AEAD utilizada, pero el secreto efectivo depende de la clave: el estado inicial reproducible y su getter público hacen que la implementación actual no proporcione confidencialidad frente a quien conozca el código/estado. El nonce aleatorio actual no resuelve esa brecha.

Antes de integrar con SHM/ring buffer se requiere definir propietario y provisión de secreto, derivación con KDF y entradas secretas, ciclo de vida/rotación coordinado entre extremos y reinicios, límites de uso por clave para AES-GCM, serialización/versionado del mensaje, autenticación de contexto y manejo de errores. La integración debe preservar la matemática S60 donde corresponda sin tratar determinismo como entropía criptográfica.

## Trazabilidad

- Código vigente: `me-60os-core/src/crystal_cipher.rs` y `me-60os-core/src/isochronous_oscillator.rs`.
- Historial consultado: creación `b0b2bca4` (2026-08-06); corrección de nonce `5cb4e51a` y cambio de fachada `5ff5cb32` (2026-10-22).
- Runtime: no inspeccionado para este módulo porque no hay consumidor productivo identificado. No se afirma despliegue ni ausencia de archivos del módulo en hosts.
- Validación: lectura de código, callsites e historial. Pruebas no ejecutadas.
