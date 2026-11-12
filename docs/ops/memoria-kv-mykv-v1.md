# Productor de memoria KV — MYKV v1

## Alcance y fuentes

Contrato del productor Rust `LiquidMemory`, integrado y publicado en `main` de Sentinel (`1f1b6b56`) y MyCNet (`e8cb1ad`) el 2026-11-11. Publicación en Git **no significa despliegue** ni habilitación en la malla real.

- [Especificación del productor](../../openspec/specs/kv-publisher/spec.md).
- [Implementación](../../me-60os-core/src/liquid_memory.rs) y [CLI](../../me-60os-core/src/bin/kv_publish.rs).
- Fuente cross-repo: repositorio **personalvault**, `openspec/changes/memoria-kv-distribuida/design.md` y sus specs; evidencia en `HANDOFF.md`, sección «Memoria KV distribuida — implementación, pruebas y merge — 2026-11-11». Resolver el checkout del vault localmente, sin asumir que es hermano de este repositorio.
- Arquitectura y límites operativos: `docs/AGENT_BRAIN.md` del vault y [AGENTS.md](../../AGENTS.md). Runtime Rust; P0.2/P0.3 siguen pausados. Esta guía no autoriza despliegues ni cambios de servicios.

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

## Evidencia histórica y pendientes reales

Resultados registrados el **2026-11-11**, no mediciones nuevas de esta documentación:

- Sentinel `liquid_memory::tests`: 12/12; builds y Clippy estricto de los componentes afectados aprobados.
- MyCNet: daemon 14/14, `storage::kv_tests` 5/5, `s60::tests` 6/6, lattice 7/7 y storage legacy 4/4 en la primera tanda.
- Smoke con tres procesos reales aislados por UDP loopback: una réplica y un ACK descartados se recuperaron; `Committed` inicial en 163 ms. Empate temporal, reordenamiento y duplicados convergieron; origen no configurado fue rechazado.
- Peer ausente produjo timeout sin falso éxito pese a aplicación parcial en otro peer; reiniciarlo permitió completar el pendiente.
- El primer smoke detectó overflow de sumas i64. Las medias globales/regionales/vecinos pasaron a acumulación i128 antes de dividir y SPA con cociente/resto firmado admite `i64::MIN`; regresiones y smoke posterior aprobados.

OpenSpec central permanece **9/12**: 3.2 (medición en malla real después de habilitar MYKV) sigue pendiente; 4.1 recall remoto y 4.3 CRDT están diferidos. No archivar el cambio como completo. Los 163 ms no son latencia productiva ni evidencia de despliegue. No se transfirió payload remoto ni se pausaron servicios en esta fase.
