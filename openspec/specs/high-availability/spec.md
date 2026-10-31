# sentinel/high-availability Specification

## Purpose

Definir el comportamiento observable de la alta disponibilidad async Fenix→Marte: standby PostgreSQL en streaming, réplica Redis, backend en espera y procedimiento de promoción ensayado.

## Requirements

### Requirement: Réplicas async verificables

PostgreSQL SHALL mantener `pg_stat_replication` con 1 conexión `streaming` desde `10.88.0.6`. Redis SHALL reportar `connected_slaves=1, lag=0`. El backend en espera SHALL responder 503 con `is_primary:false`.

#### Scenario: Verificar réplicas

- **WHEN** se consulta el primario y Marte
- **THEN** ambas réplicas están sincronizadas en timeline vigente
- **AND** el backend de Marte reporta modo espera, no fallo

### Requirement: Promoción manual con pérdida cero

La promoción SHALL seguir `docs/ops/failover-fenix-marte.md`. El ensayo 2026-10-31 demostró pérdida cero (LSN idéntico). No existe failover automático.

#### Scenario: Consultar procedimiento

- **WHEN** un agente necesita promover
- **THEN** encuentra comandos exactos, precondiciones anti-split-brain y registro obligatorio
- **AND** no ejecuta promoción sin ventana autorizada
