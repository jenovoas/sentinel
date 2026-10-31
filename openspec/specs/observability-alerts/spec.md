# sentinel/observability-alerts Specification

## Purpose

Definir el comportamiento observable de la observabilidad y alertas: Prometheus en Marte con 15+ targets, Alertmanager con SMTP a `monitoreo@pinguinoseguro.cl`, 3 reglas activas.

## Requirements

### Requirement: Plataforma de métricas

Prometheus SHALL observar todos los exporters y servicios core con `up=1`. Mimir SHALL devolver las mismas series tras `remote_write`.

#### Scenario: Verificar cobertura

- **WHEN** se consulta `/api/v1/targets` desde el contenedor Prometheus
- **THEN** todos los targets están `up`
- **AND** `pg_up{job="sentinel-postgres-fenix"}=1` existe en Prometheus y Mimir

### Requirement: Alertas email extremo a extremo

Alertmanager SHALL enviar a `monitoreo@pinguinoseguro.cl` vía `10.88.0.1:587` con TLS verificado por `server_name`. Las reglas SHALL ser: caída backend, disco <15%, réplica caída.

#### Scenario: Verificar canal

- **WHEN** se dispara una alerta de prueba
- **THEN** llega al buzón con `Notify success`
- **AND** las reglas están cargadas e inactivas cuando todo está sano
