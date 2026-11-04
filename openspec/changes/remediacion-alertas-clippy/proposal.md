# Proposal

## Why

La compilación estricta de `me60os` falla por conversiones con posible truncamiento, mientras que aún hay operaciones de punto flotante en lógica incluida en el core. La remediación debe resolver las causas y preservar la política YATRA sin debilitar las reglas del compilador ni los lints existentes.

## What Changes

- Sustituir casts numéricos potencialmente truncantes por conversiones comprobadas o acotadas con una semántica explícita.
- Retirar las operaciones de punto flotante de la lógica numérica del core y conservar representaciones enteras S60.
- Mantener intactos `Cargo.toml`, las reglas de compilación y el contrato de escala `SPA`.
- Verificar biblioteca, todos los objetivos, pruebas y auditorías de dependencias que estén disponibles en el entorno.

## Capabilities

### New Capabilities
- `core-arithmetic`: La lógica numérica del core usa aritmética entera S60 y no depende de punto flotante; conversiones con pérdida potencial deben comprobar rango explícitamente.

### Modified Capabilities

## Impact

Afecta `me-60os-core` (aritmética `SPA`, utilidades matemáticas, scheduling, medición y pruebas), las fronteras Python que hoy reciben valores flotantes y los artefactos de OpenSpec. No incluye modificar reglas de compilación, despliegues ni cambios remotos.
