# sentinel/topology Specification

## Purpose

Definir el comportamiento observable del despliegue real de Sentinel sobre Debian/systemd en tres nodos (Fenix primario, Marte segundo backend/observabilidad, Kingu frontal), con red WireGuard 10.88.0.0/24.

## Requirements

### Requirement: Topología de tres nodos

El sistema SHALL operar con Fenix (`10.88.0.1`) como backend primario, Marte (`10.88.0.6`) como segundo backend y observabilidad, y Kingu (`10.88.0.2`) como frontal nginx. Cada nodo SHALL usar Debian con systemd y Docker Engine.

#### Scenario: Identificar rol por nodo

- **WHEN** un agente consulta la topología
- **THEN** obtiene Fenix=primario, Marte=espera+obs, Kingu=frontal
- **AND** no recibe Alpine, OpenRC ni nodo único como estado vigente

### Requirement: Frontal único en Kingu

Todo tráfico público HTTPS SHALL terminar en nginx de Kingu (`sentinel.pinguinoseguro.cl` → Consola Sentinel, `pinguinoseguro.cl` → portal). Ningún puerto de backend SHALL publicarse en Internet.

#### Scenario: Verificar frontal

- **WHEN** se consulta `https://sentinel.pinguinoseguro.cl/login`
- **THEN** responde 200 con la Consola Sentinel
- **AND** el backend solo es alcanzable por WireGuard
