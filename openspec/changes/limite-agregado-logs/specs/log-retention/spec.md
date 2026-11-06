# Spec Delta

## Purpose

Define límites agregados verificables para el almacenamiento local de logs por host y restringe la exportación central a eventos de seguridad y errores.

## ADDED Requirements

### Requirement: Límite físico agregado por host
El sistema SHALL limitar a 1 GiB el almacenamiento físico agregado de todas las rutas locales de logs incluidas en cada host, independientemente del servicio productor.

#### Scenario: Fuentes distribuidas alcanzan el límite
- **WHEN** journald, syslog/audit, Docker, Loki y logs Sentinel ocupan rutas distintas en un host
- **THEN** la suma de bloques asignados para las rutas incluidas no puede exceder 1 GiB
- **AND** el crecimiento de logs no puede consumir espacio fuera del límite para eludirlo

#### Scenario: Presupuesto agotado
- **WHEN** la asignación agregada llega al límite de 1 GiB
- **THEN** la retención configurada libera espacio elegible o las escrituras adicionales se rechazan
- **AND** otros datos del host no se quedan sin espacio por crecimiento de logs

#### Scenario: Escritor con capacidades elevadas
- **WHEN** un proceso con `CAP_SYS_RESOURCE` escribe en una ruta incluida
- **THEN** el filesystem de tamaño fijo rechaza escrituras cuando se agota su capacidad
- **AND** el límite no depende de cuotas de proyecto que el proceso pueda eludir

#### Scenario: Agotamiento de logs de contenedores
- **WHEN** Docker no puede persistir más mensajes porque el filesystem de logs alcanzó su límite
- **THEN** la entrega no bloqueante permite continuar a la aplicación del contenedor
- **AND** Docker descarta los mensajes nuevos si también se llena el búfer finito

### Requirement: Exportación limitada a seguridad y errores
El forwarder SHALL enviar a Loki únicamente eventos clasificados como seguridad o error y SHALL excluir eventos informativos y de depuración.

#### Scenario: Evento de seguridad o error
- **WHEN** el forwarder procesa un evento clasificado como seguridad o error
- **THEN** el evento puede enviarse a Loki

#### Scenario: Evento informativo, depuración o sin clasificación
- **WHEN** el forwarder procesa un evento informativo, de depuración o sin clasificación verificable
- **THEN** el evento no se envía a Loki

### Requirement: Preservación antes de retirar historial
La rotación SHALL preservar los logs históricos existentes hasta que la copia de respaldo y la política de retención correspondientes estén verificadas.

#### Scenario: Historial sin respaldo verificado
- **WHEN** una rotación afectaría un archivo histórico sin copia de respaldo verificada
- **THEN** el sistema conserva ese historial y no lo trunca ni elimina

#### Scenario: Retención acordada y respaldo verificado
- **WHEN** existe una política de retención aprobada y una copia verificable del historial que se retirará
- **THEN** la rotación puede retirar únicamente los datos que excedan esa política
