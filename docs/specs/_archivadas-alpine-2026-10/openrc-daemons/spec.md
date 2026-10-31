# sentinel/openrc-daemons Specification

## Purpose

Definir el ciclo de vida observable de los daemons nativos de Sentinel gestionados mediante OpenRC en Alpine Linux, incluyendo dependencias, arranque automático, PID files, logs y puertos.

## Requirements

### Requirement: Daemons Sentinel registrados

El sistema MUST registrar mediante OpenRC los servicios `sentinel-cortex`, `sentinel-verifier`, `qhc_agent`, `audit-watchdog`, `process-memory-collector` y `sentinel-ebpf-forwarder`.

#### Scenario: Servicios reconocidos por OpenRC

- **WHEN** se ejecuta `rc-service <nombre> status` para cualquiera de los seis servicios
- **THEN** OpenRC reconoce el servicio y no devuelve "servicio desconocido"

### Requirement: Control individual del ciclo de vida

Cada daemon SHALL responder a `start`, `stop`, `status` y `restart` mediante `rc-service`. Un daemon iniciado MUST mostrar `started` y uno detenido MUST mostrar `stopped`.

#### Scenario: Inicio y detención limpia

- **WHEN** se ejecuta `rc-service <nombre> start`
- **THEN** el servicio queda en estado `started`
- **WHEN** se ejecuta `rc-service <nombre> stop`
- **THEN** el servicio queda en estado `stopped` sin procesos zombie

### Requirement: Arranque automático en OpenRC

Los seis daemons MUST estar habilitados en el runlevel `default` y alcanzar el estado `started` después de un reinicio del host sin intervención manual.

#### Scenario: Runlevel default

- **WHEN** se ejecuta `rc-update show default`
- **THEN** aparecen los seis nombres de servicio bajo el runlevel `default`
- **AND** después de reiniciar Alpine todos alcanzan `started` antes de que el host quede disponible para la red

### Requirement: PID files verificables

Cada daemon activo MUST crear `/run/sentinel/<nombre>.pid`. El PID almacenado MUST corresponder a un proceso vivo en `/proc`.

#### Scenario: Proceso activo con PID válido

- **WHEN** un daemon muestra estado `started`
- **THEN** existe su PID file bajo `/run/sentinel/`
- **AND** el PID corresponde a un proceso vivo
- **WHEN** el daemon muestra estado `stopped`
- **THEN** no queda un PID file activo asociado al servicio

### Requirement: Puerto y logs de Sentinel

`sentinel-cortex` MUST escuchar en el puerto TCP configurado para su API REST. Cada daemon MUST escribir logs estructurados en `/var/log/sentinel/<nombre>.log` durante el arranque.

#### Scenario: Evidencia de red y filesystem

- **WHEN** `sentinel-cortex` está `started`
- **THEN** existe un proceso escuchando en su puerto TCP configurado
- **AND** cada daemon deja al menos una entrada de arranque en su log correspondiente

### Requirement: Coexistencia de daemons

Los seis daemons MUST coexistir sin conflictos de PID, nombre de servicio o puerto, y una detención limpia no SHALL dejar procesos zombie visibles en `ps aux`.

#### Scenario: Operación simultánea

- **WHEN** los seis servicios están habilitados y activos
- **THEN** todos conservan sus propios PID files y logs
- **AND** no se detectan conflictos de puertos ni procesos zombie después de detener uno de ellos
