# Productor de memoria KV — MYKV v1

## Alcance y fuentes

Contrato del productor Rust `LiquidMemory`, integrado en `main` de Sentinel (`1f1b6b56`) y MyCNet (`e8cb1ad`) el 2026-11-11, y validado en la malla física real (Fénix, Kingu y Marte) el 2026-11-12 mediante el binario `kv_publish` release y `mycnetd` release SHA-256 `1854634b...`.

- [Especificación del productor](../../openspec/specs/kv-publisher/spec.md).
- [Implementación](../../me-60os-core/src/liquid_memory.rs) y [CLI](../../me-60os-core/src/bin/kv_publish.rs).
- Fuente cross-repo: repositorio **personalvault**, `openspec/changes/memoria-kv-distribuida/design.md` y sus specs; evidencia en `HANDOFF.md`, secciones «Memoria KV distribuida — implementación, pruebas y merge — 2026-11-11» y «Memoria KV distribuida — validación en malla real — 2026-11-12». Resolver el checkout del vault localmente, sin asumir que es hermano de este repositorio.
- Arquitectura y límites operativos: `docs/AGENT_BRAIN.md` del vault y [AGENTS.md](../../AGENTS.md). Runtime Rust; P0.2/P0.3 siguen pausados. La validación KV no tocó Cortex ni alteró sus estados.

## Store → replicate → publish

1. `LiquidMemory::store(key, payload)` escribe los bytes originales en SHM local, inyecta el canal dual en `LiquidLattice` y registra hash blake3, energía medida y `timestamp_ns` Unix. El timestamp crece estrictamente **por instancia**, incluso si retrocede el reloj; no es un reloj global ni sobrevive como garantía de monotonía entre instancias/reinicios.
2. `replicate(key)` devuelve `ReplicableSeed { key, amplitude_raw, hash, timestamp_ns }` de una entrada local existente. Retiene energía y timestamp originales aunque evolucione la lattice.
3. `publish(&seed)` bloquea hasta recibir `Committed` válido o un error. Usa UDP loopback; no abre ni escribe `/me60os_fractal_seeds`, no pausa Cortex ni modifica su ritmo/semilla.

Solo pueden salir claves UTF-8 de **1–512 bytes** con prefijo `crystal-` o `portal-metrics-`. Otras claves siguen siendo locales para store/retrieve. Clave inexistente o no autorizada produce error de `replicate`; `publish` también valida la whitelist.

Para reintentar tras resultado incierto, conservar y volver a publicar **la misma `ReplicableSeed`**, sin mutarla. No repetir `store`: crearía otra versión. Un nuevo store de la misma clave puede reemplazar la metadata local que devolvería un `replicate` posterior.

`retrieve` lee el payload local desde SHM y verifica blake3. El hash y la semilla distribuidos son **metadatos**, no los bytes originales: no permiten afirmar transferencia, reconstrucción ni recuperación del payload remoto.

## Configuración y uso del CLI

| Variable | Predeterminado | Contrato |
| --- | --- | --- |
| `MYCNET_KV_ADDR` | `127.0.0.1:4242` | `SocketAddr` numérico, solo IP loopback; admite IPv4/IPv6, no nombres DNS |
| `MYCNET_KV_TIMEOUT_MS` | `5000` | Entero u64 positivo en milisegundos; cero, formato inválido o duración fuera de rango se rechazan |

Con binario ya construido y daemon/peers MYKV disponibles en un entorno aislado:

```sh
MYCNET_KV_ADDR=127.0.0.1:4242 MYCNET_KV_TIMEOUT_MS=5000 \
  target/debug/kv_publish crystal-smoke valor-local
```

`kv_publish <crystal-clave|portal-metrics-clave> <valor-local>` ejecuta un store nuevo en cada invocación. Imprime `Committed`, clave, token, timestamp, amplitud y hash **solo tras confirmar**; no ofrece reanudación de una semilla previa. Reinvocarlo después de timeout no es un retry de la identidad original. No usar secretos como argumentos de esta demostración.

## Contrato wire y confirmación

UDP comparte el puerto de MyCNet (4242 por defecto), sin alterar el tráfico fractal legado de 40 bytes ni su ring. MYKV v1 contiene 80 bytes de cabecera más clave: máximo 592 bytes.

| Bytes (inclusivos) | Campo |
| --- | --- |
| 0–3 | ASCII `MYKV` |
| 4 | Tipo: Publish=1, Replicate=2, Ack=3, Committed=4 |
| 5 | Versión 1 |
| 6–7 | Longitud de clave u16 little-endian |
| 8–15 | Timestamp original u64 little-endian |
| 16–47 | Semilla binaria de 32 bytes, layout existente y CRC16-CCITT |
| 48–79 | Hash blake3 del payload original (32 bytes) |
| 80–fin | Clave UTF-8 de 1–512 bytes |

El productor deriva token/coordenadas de la clave, usa coordenadas cúbicas deterministas de radio 3 y conserva amplitud raw. El CRC de semilla usa polinomio `0x1021`, inicio `0xFFFF`, sobre sus primeros 28 bytes. Todos los tipos ecoan identidad completa: clave, timestamp, semilla y hash.

`publish` codifica una vez y retransmite el mismo datagrama cada 100 ms dentro del timeout total. El socket UDP conectado filtra el `SocketAddr` de origen. Solo acepta una respuesta del destino configurado idéntica al datagrama publicado en longitud y todos sus bytes excepto el tipo, que debe ser `Committed=4`. Respuestas ajenas o malformadas no confirman éxito.

MyCNet admite Publish solo por loopback y Replicate/Ack solo de peers configurados; valida formato, versión, clave, CRC y origen. La whitelist no equivale a autenticación pública. `Committed` exige ACK de **todos** los peers configurados, no un quorum parcial; sin peers no hay confirmación distribuida. Cada peer aplica LWW antes del ACK. El orden total para una clave es el máximo lexicográfico `(timestamp_ns, payload_hash, seed_bytes)`; duplicados y versiones perdedoras no reinyectan estado. Un ACK puede reconocer una versión ya supersedida: éxito no prueba que siga siendo ganadora. Relojes desajustados pueden dominar versiones; no se promete orden causal global.

## Errores y resultado incierto

Errores de clave/configuración se devuelven antes de enviar. Store puede fallar por reloj/agotamiento de timestamp o IO SHM; su éxito local no confirma réplica. Errores de socket/IO durante publicación y timeout no acreditan éxito ni ausencia de aplicación remota. El mensaje de timeout declara **commit desconocido**: puede haber réplica parcial o haberse perdido la confirmación.

Conservar la misma semilla para retry. No interpretar timeout como rollback ni lanzar un store nuevo para «completar» el anterior. El daemon admite como máximo 256 identidades pendientes globales (por tanto, como máximo 256 por peer); saturación no genera confirmación falsa. Estado, pendientes y ACK son volátiles: no se promete durabilidad ni recuperación automática de estos tras reinicio del daemon.

## Evidencia histórica y validación en malla real

### Pruebas de integración previas (2026-11-11)

- Sentinel `liquid_memory::tests`: 12/12; builds y Clippy estricto de los componentes afectados aprobados.
- MyCNet: daemon 14/14, `storage::kv_tests` 5/5, `s60::tests` 6/6, lattice 7/7 y storage legacy 4/4 en la primera tanda.
- Smoke con tres procesos locales y UDP loopback: Committed inicial en 163 ms en escenario con pérdida inducida.

### Validación en malla real (2026-11-12)

La tarea 3.2 fue verificada en la malla física activa (Fénix `10.88.0.1`, Kingu `10.88.0.2` y Marte `10.88.0.6`) con `kv_publish` release en Sentinel y `mycnetd` release SHA-256 `1854634b...`:

- **All-Peer ACK con nodo offline:** Como MYKV exige ACK de todos los peers configurados, y Hércules (`10.88.0.4`) se encuentra inaccesible a nivel de red (>3 días sin handshake WireGuard), los peers activos se acotaron a la terna viva Fénix-Kingu-Marte mediante drop-ins de systemd.
- **Bind de transporte:** Fénix configurado con `MYCNET_UDP_BIND=0.0.0.0:4242` para aceptar simultáneamente el loopback de `kv_publish` y el tráfico WireGuard de réplica/ACK.
- **Medición 1 (publicación inicial):** `crystal-mesh-latency-20261112` con valor `verificacion-malla-fenix-kingu-marte` confirmó `Committed` en **161 ms** (`timestamp_ns = 1794455381018816480`, `token_id = 2708293038`).
- **Medición 2 (actualización LWW):** misma clave con valor `actualizacion-lww-verificada` confirmó `Committed` en **162 ms** (`timestamp_ns = 1794455428316426647`).
- **Convergencia LWW:** Los tres nodos reportan metadatos idénticos (`timestamp_ns`, `payload_hash` y `seed_bytes`) vía `GET /api/v1/kv-metadata`.
- **Física de red:** Los 161–162 ms corresponden directamente al RTT físico de WireGuard entre Fénix y Marte (~158 ms de ping RTT).
- **Whitelist:** Claves fuera de lista fueron rechazadas en el productor antes de emitir, y devuelven HTTP 400 en los endpoints del daemon.

## Estado actual: 10/12 tareas completadas

El cambio OpenSpec central `memoria-kv-distribuida` se encuentra en **10/12**:
- Tarea 3.2 completada y verificada en producción/malla real.
- Tareas 4.1 (recall remoto de payload) y 4.3 (CRDT de resolución) permanecen **diferidas**. No archivar el cambio.
