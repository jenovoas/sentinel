# sentinel/alpine-deployment Specification

## Purpose

Definir el comportamiento observable del despliegue de Sentinel como plataforma de nodo único sobre Fenix Alpine Linux, incluyendo su stack de servicios, endpoints TLS, compilación Rust, persistencia e inicio automático.

## Requirements

### Requirement: Stack de servicios Sentinel

El stack de Sentinel SHALL levantar mediante Docker Compose los servicios declarados para base de datos, cache, API, frontend, métricas, logs, alertas, automatización y protección neural: `postgres`, `redis`, `sentinel-cortex`, `sentinel-frontend`, `prometheus`, `node-exporter`, `postgres-exporter`, `redis-exporter`, `grafana`, `loki`, `promtail`, `alertmanager`, `n8n` y `neural-guard`.

#### Scenario: Estado saludable del stack

- **WHEN** se consulta el estado del stack con `docker compose -f docker-compose.fenix.yml ps`
- **THEN** todos los servicios declarados aparecen como `running` o `healthy` cuando tienen healthcheck
- **AND** ningún servicio aparece como `exited` o `restarting`

### Requirement: Endpoints públicos protegidos por TLS

Los endpoints públicos de Cortex, Grafana, Prometheus y n8n MUST responder por HTTPS sin errores de certificado autofirmado, timeout ni respuestas 5xx.

#### Scenario: Verificación de endpoints

- **WHEN** se consulta `https://cortex.pinguinoseguro.cl/health`, `https://grafana.pinguinoseguro.cl`, `https://prometheus.pinguinoseguro.cl` y `https://n8n.pinguinoseguro.cl`
- **THEN** cada endpoint responde HTTP 200 y presenta un certificado TLS válido
- **AND** Prometheus conserva la autenticación requerida cuando corresponda

### Requirement: Compilación Rust sin floats de negocio

El workspace Rust MUST compilar en Alpine Linux con `cargo build --release`, generar sus artefactos en `target/release/` y mantener el candado YATRA: la lógica Sistema-60 no usa `f32` ni `f64`.

#### Scenario: Build de release

- **WHEN** se ejecuta `cargo build --release` en Alpine Linux
- **THEN** los crates `sentinel-cortex`, `me-60os-core`, `truthsync-core`, `sentinel-verifier` y `neural-guard` compilan sin errores
- **AND** se generan los binarios de release correspondientes

### Requirement: Persistencia de datos del stack

Los volúmenes de PostgreSQL, Redis, Grafana, Loki y n8n MUST conservar sus datos y configuración después de detener y volver a iniciar el stack.

#### Scenario: Reinicio del stack

- **WHEN** se ejecuta un ciclo completo de `docker compose down` seguido de `docker compose up -d`
- **THEN** PostgreSQL arranca con los mismos esquemas y datos
- **AND** Grafana conserva sus dashboards y fuentes
- **AND** n8n conserva sus workflows

### Requirement: Arranque automático del nodo

El stack Docker Compose MUST arrancar automáticamente después de un reinicio del host sin intervención manual, y los endpoints públicos MUST volver a responder en un plazo razonable después de que Alpine esté disponible.

#### Scenario: Reinicio del sistema

- **WHEN** Fenix completa un reinicio del sistema
- **THEN** el stack arranca automáticamente
- **AND** los endpoints públicos definidos vuelven a responder sin una operación manual adicional

### Requirement: Integración segura con servicios del host

Nginx SHALL actuar como proxy inverso para los subdominios Sentinel. Docker Compose MUST NOT apropiarse de los puertos 80 o 443. PostgreSQL, Redis y la API MUST recibir credenciales desde un archivo de entorno no versionado, y PowerDNS, Nginx, Postfix/Dovecot y WireGuard MUST continuar operativos.

#### Scenario: Despliegue sin interferencia de host

- **WHEN** se inicia o reinicia el stack Sentinel
- **THEN** Nginx conserva los puertos 80 y 443
- **AND** los servicios de red existentes continúan operativos
- **AND** no aparecen credenciales hardcodeadas en el compose versionado
