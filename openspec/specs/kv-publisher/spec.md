# kv-publisher Specification

## Purpose

Definir el contrato observable del productor Rust de metadatos KV hacia MyCNet, conservando la identidad de escritura y distinguiendo confirmación distribuida de almacenamiento local y recuperación de payload.

Fuente cross-repo: repositorio personalvault, `openspec/changes/memoria-kv-distribuida/design.md` y sus specs. [Guía operativa del productor](../../../docs/ops/memoria-kv-mykv-v1.md). Validación en malla real (Fénix, Kingu y Marte; 161–162 ms) documentada el 2026-11-12.

## Requirements

### Requirement: Identidad estable de escritura

`store` SHALL conservar payload local en SHM y registrar hash blake3, energía medida y timestamp Unix ns estrictamente creciente por instancia. `replicate` SHALL conservar esos metadatos originales sin refrescarlos por evolución de la lattice ni reintento. No se garantiza monotonía entre instancias ni orden causal global.

#### Scenario: Replicación después de evolucionar la lattice

- **WHEN** una entrada almacenada se replica después de evolucionar la lattice
- **THEN** la semilla conserva clave, hash, energía y timestamp originales del store

#### Scenario: Retroceso del reloj local

- **WHEN** el reloj retrocede entre stores exitosos de la misma instancia
- **THEN** el timestamp del nuevo store es mayor que el anterior

### Requirement: Lista permitida de publicación

`replicate` y `publish` SHALL rechazar claves que no sean UTF-8 de 1–512 bytes con prefijo `crystal-` o `portal-metrics-`. `replicate` SHALL rechazar una clave sin entrada local. La restricción de réplica no impide almacenamiento y lectura locales de otras claves.

#### Scenario: Clave solo local

- **WHEN** el productor intenta replicar una clave almacenada sin prefijo autorizado
- **THEN** recibe error y esa operación no publica sus metadatos

### Requirement: Transporte MYKV independiente de Cortex

`publish` SHALL usar UDP loopback sin escribir el ring de Cortex. SHALL leer `MYCNET_KV_ADDR` como SocketAddr numérico, por defecto `127.0.0.1:4242`, y `MYCNET_KV_TIMEOUT_MS` como u64 positivo, por defecto 5000 ms. SHALL rechazar destino no loopback, configuración inválida o timeout no representable.

#### Scenario: Destino externo

- **WHEN** la dirección configurada no es loopback
- **THEN** publish devuelve error sin enviar la publicación

### Requirement: Envoltura wire v1

El productor SHALL emitir MYKV v1 con magic bytes 0–3, tipo 1 en byte 4, versión 1 en byte 5, longitud u16 LE en 6–7, timestamp u64 LE en 8–15, semilla con CRC de 32 bytes en 16–47, hash blake3 en 48–79 y clave UTF-8 en 80–fin; tamaño máximo 592 bytes. La semilla SHALL conservar el layout binario existente y coordenadas deterministas de radio 3.

#### Scenario: Publicación autorizada

- **WHEN** se publica una semilla con clave válida
- **THEN** se envía la envoltura Publish con identidad íntegra y sin incluir el payload original

### Requirement: Confirmación exacta y retransmisión

`publish` SHALL retransmitir el mismo datagrama cada 100 ms hasta timeout o `Committed`. SHALL retornar éxito solo con respuesta del SocketAddr configurado, idéntica en longitud y bytes salvo tipo 4. El contrato MyCNet exige ACK tras LWW de todos los peers configurados; sin peers no hay Committed. La confirmación puede corresponder a una versión ya supersedida.

#### Scenario: Respuesta de otra identidad

- **WHEN** llega una respuesta con timestamp, semilla, hash o clave diferentes
- **THEN** el productor no la acepta como confirmación

#### Scenario: Versión supersedida

- **WHEN** todos los peers reconocen la identidad publicada pero ya tienen una versión LWW superior
- **THEN** Committed confirma aceptación o supersesión, no que la versión publicada siga ganando

### Requirement: Timeout sin falso resultado

El productor SHALL tratar timeout como commit desconocido, sin afirmar pérdida, rollback ni éxito. Un retry de la misma publicación MUST conservar la misma `ReplicableSeed`. Estado y ACK del daemon son volátiles; no se garantiza durabilidad tras reinicio ni éxito por quorum parcial.

#### Scenario: Réplica parcial

- **WHEN** parte de los peers aplica la publicación pero falta confirmación completa al vencer el timeout
- **THEN** publish devuelve error con resultado incierto
- **AND** reintentar la misma semilla conserva la identidad original

### Requirement: CLI y frontera del payload

`kv_publish` SHALL ejecutar store, replicate y publish y mostrar Committed y metadatos solo tras confirmación. Cada invocación crea una escritura nueva, no reanuda otra. La vía KV SHALL transportar solo metadatos; el hash no acredita recuperación remota. `retrieve` SHALL verificar blake3 del payload local leído de SHM.

#### Scenario: Reinvocación del CLI

- **WHEN** se invoca nuevamente kv_publish después de un timeout
- **THEN** ejecuta un nuevo store y no reanuda la identidad anterior

#### Scenario: Integridad local

- **WHEN** retrieve lee bytes locales cuyo hash difiere del registrado
- **THEN** devuelve error de integridad, sin declarar recuperación válida
