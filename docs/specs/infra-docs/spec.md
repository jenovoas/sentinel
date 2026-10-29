# sentinel/infra-docs Specification

## Purpose

Mantener la documentación técnica de Sentinel alineada con el estado real de Fenix como único nodo activo de producción sobre Alpine Linux, sin describir a Kingu como infraestructura operativa vigente.

## Requirements

### Requirement: Documentación de topología Alpine actual

La documentación de infraestructura MUST describir Fenix como servidor único de producción, Alpine Linux como sistema operativo, `apk` como gestor de paquetes y OpenRC como sistema de init. Las referencias a Kingu sólo pueden aparecer como historia o nodo dado de baja.

#### Scenario: Agente consulta la topología

- **WHEN** un agente consulta `AGENTS.md` o `CLAUDE.md` del repositorio Sentinel
- **THEN** obtiene Fenix como nodo único, Alpine Linux, OpenRC y Docker Compose como modelo operativo
- **AND** no interpreta Kingu como nodo activo
- **AND** no recibe instrucciones actuales basadas en `systemctl`, `systemd`, `dnf` o `yum`

### Requirement: Coherencia entre documentos operativos

`AGENTS.md`, `CLAUDE.md` y `personalvault/IA/Fenix/REGISTRO_AUDITORIA.md` MUST ser coherentes respecto a Fenix, Alpine Linux y la IP pública `172.233.24.102`.

#### Scenario: Validación de coherencia documental

- **WHEN** se comparan los tres documentos en una revisión operativa
- **THEN** los tres describen un único nodo Fenix con Alpine Linux
- **AND** ninguno contradice el uso de `apk`, `rc-service` y Docker Compose

### Requirement: Evidencia de auditoría del despliegue

El registro de auditoría MUST incluir una entrada real del despliegue de Sentinel en Alpine Linux, con fecha real, migración desde Rocky Linux, baja de Kingu y al menos una evidencia observable como URL, hash de commit o resultado de comando.

#### Scenario: Auditoría del despliegue

- **WHEN** se revisa `personalvault/IA/Fenix/REGISTRO_AUDITORIA.md`
- **THEN** existe una entrada fechada del despliegue
- **AND** la entrada identifica el cambio de Rocky Linux a Alpine Linux y la baja de Kingu
- **AND** contiene evidencia verificable del estado desplegado
