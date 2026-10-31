# sentinel/console Specification

## Purpose

Definir el comportamiento observable de la Consola Sentinel: login contra AD por LDAPS, navegación en español con lucide, dashboard con datos vivos, revisión Gamma solo superusuario.

## Requirements

### Requirement: Autenticación contra directorio

El login SHALL validar contra Samba AD por LDAPS con CA privada y devolver 401 con credenciales inválidas, 503 solo si el directorio no responde.

#### Scenario: Inicio de sesión

- **WHEN** un superusuario inicia sesión con su UPN y clave AD
- **THEN** recibe JWT y accede a `/dashboard`
- **AND** la cola Gamma se abre solo con `is_superuser=true`

### Requirement: Interfaz en español sin placeholders

La consola SHALL mostrar español en navegación, estados y acciones, iconos lucide (sin emojis), y datos vivos del backend. N/D solo donde el contrato no expone la fuente.

#### Scenario: Verificar dashboard

- **WHEN** se abre el dashboard con backend sano
- **THEN** muestra CPU/RAM/disco/DB reales con hora de actualización
- **AND** el indicador de nav dice "Backend conectado"
