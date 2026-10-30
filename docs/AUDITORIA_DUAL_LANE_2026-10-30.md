# Auditoría Dual Lane de eventos — 2026-10-30

## Separación de conceptos

Sentinel tiene dos arquitecturas distintas llamadas Dual Lane:

1. **Memoria/cristales A/B:** `CrystalRuntime` en Cortex/Fenix mantiene lanes de memoria compartida.
2. **Enrutamiento Security/Observability:** `me-60os-core::dual_lane::DualLaneRouter` clasifica eventos y los entrega a un WAL Security sin buffer o a un colector Observability con buffer/backpressure.

La primera no demuestra que el router de eventos esté conectado.

## Call graph de producción

- `sentinel-security-gateway` de Marte lee `/sys/fs/bpf/guardian_alpha/events`.
- Para todo evento permitido, `forward_event()` llama `ForensicWal::append(..., DataLane::Security)` antes del POST a Fenix. El WAL usa `sync_data`; si el append falla, el evento se retiene y no se reenvía. Los eventos retenidos por sanitización también guardan evidencia en `Security`.
- El Gateway no llama `me-60os-core::DualLaneRouter` ni sus colectores y no escribe registros `Observability` en ese WAL. Aunque `ForensicWal` define la variante Observability, el único call site de la ruta Gateway pasa Security.
- `me-60os-core/src/dual_lane.rs` se importa como módulo de biblioteca, pero las búsquedas de call sites lo encuentran en `dual_lane_bench.rs` y código de pruebas, no en los servicios desplegados.
- El equivalente Python `backend/app/core/data_lanes.py` se mantiene como módulo; el singleton `dual_lane_router`, `WAL` y colectores no tienen consumidores desde routers o `main.py` en el camino revisado. El default WAL Python es `/tmp/sentinel/wal`, por lo que su existencia como código tampoco acredita almacenamiento productivo.
- La observabilidad sí está desplegada mediante pipeline separado: Alloy recoge journald/auditd; Prometheus scrapea métricas y usa remote-write hacia Mimir; Loki recibe logs. Eso no es el `ObservabilityLaneCollector` del router Dual Lane.

## Evidencia runtime en Marte

Consulta de solo lectura a las 15:18 UTC:

- `sentinel-security-gateway.service`: `active/running`, activo desde 14:30 UTC. La unidad limita escritura a `/var/log/sentinel`; no se leyó el `EnvironmentFile` ni la clave del WAL.
- El WAL configurado por defecto, `/var/log/sentinel/guardian_security_wal.jsonl`, tenía modo `0600`, tamaño 7.747.007 bytes y 9.141 líneas en consultas consecutivas. Un conteo JSON procesado en memoria dio `{'security': 9141}`; no se imprimieron payloads, nonces o firmas.
- Los seis contenedores de Marte (`alloy`, `grafana`, `prometheus`, `mimir`, `loki`, `node-exporter`) figuraban `Up` en la captura.

Esta evidencia acepta la escritura duradera de la lane Security del Gateway y la presencia de servicios separados de observabilidad. No prueba firma/verificación reciente del WAL ni aceptación de enrutamiento mediante `DualLaneRouter`.

## Dictamen

La cadena actualmente desplegada implementa `Guardian Alpha → sanitización → WAL Security local → POST autenticado a Fenix`, mientras que las métricas y logs salen por colectores distintos. El router Dual Lane Security/Observability del core está implementado como biblioteca/bench, no integrado en el camino de producción revisado. Mantener este gap explícito; no declarar que el nombre del WAL o la disponibilidad de Alloy constituyen aceptación de ambas lanes bajo ese router.

No se modificó runtime ni código operativo y no se ejecutaron pruebas.
