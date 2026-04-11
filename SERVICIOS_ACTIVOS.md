# 🚀 Servicios Activos de Sentinel (Producción Fenix)

**Última actualización**: 11 de Abril, 2026
**Estado**: 🟢 OPERATIVO (Axioma S60)
**Infraestructura**: Podman Rootless (Rocky Linux 9)

---

## 📋 Servicios de Núcleo (Core)

### 1. Sentinel Cortex (Rust/Axum)
- **URL**: <https://cortex.pinguinoseguro.cl/api>
- **Descripción**: Motor principal asíncrono. Gestiona la lógica de negocio y la integración eBPF.
- **Estado**: ✅ Activo (Ring-0 Enabled)
- **Endpoints Clave**:
  - `/api/health` - Salud del sistema S60.
  - `/api/metrics` - Exportador nativo de Prometheus.

### 2. Dashboard UI (Next.js)
- **URL**: <https://cortex.pinguinoseguro.cl>
- **Descripción**: Interfaz de control y visualización de la malla Sentinel.
- **Estado**: ✅ Activo

---

## 🗄️ Persistencia y Mensajería

### 3. PostgreSQL 16 (Relational DB)
- **Container**: `sentinel-postgres`
- **Uso**: Configuración, auditoría persistente y gestión de tenants.
- **Estado**: ✅ Healthy

### 4. Redis 7 (Cache & Streams)
- **Container**: `sentinel-redis`
- **Uso**: Message broker para eventos eBPF y caché de alta velocidad.
- **Estado**: ✅ Healthy

---

## 📊 Stack de Observabilidad

### 5. Grafana (Visualización)
- **URL**: <https://grafana.pinguinoseguro.cl>
- **Descripción**: Centro de mando para métricas térmicas y de seguridad.
- **Estado**: ✅ Activo

### 6. Prometheus (Time Series)
- **URL**: <https://prometheus.pinguinoseguro.cl>
- **Descripción**: Recolección de métricas de Cortex, Neural Guard y exporters del sistema.
- **Estado**: ✅ Activo

### 7. Loki (Logs)
- **Host**: `sentinel-loki:3100` (Agregado en Grafana)
- **Descripción**: Almacenamiento distribuido de logs de contenedores y sistema.
- **Estado**: ✅ Activo

---

## 🛡️ Seguridad y Cognición

### 8. Neural Guard (Decision Engine)
- **Container**: `sentinel-neural-guard`
- **Descripción**: Nervio cognitivo que ajusta umbrales de seguridad basado en carga térmica y eventos de red.
- **Estado**: ✅ Activo (Thermal Coupling ON)

---

## 🤖 Automatización

### 9. n8n (Workflow Automation)
- **URL**: <https://n8n.pinguinoseguro.cl>
- **Descripción**: Orquestación de respuestas ante incidentes y reportes automáticos.
- **Estado**: ✅ Activo

---

## 🌐 Sitios Web Adicionales

### 10. Portfolio Pinguino Seguro
- **URL**: <https://portfolio.pinguinoseguro.cl>
- **Estado**: ✅ Activo

### 11. La Espiguita (ERP/Landing)
- **URL**: <https://laespiguita.pinguinoseguro.cl>
- **Estado**: ✅ Activo

---

## 🔧 Comandos de Supervisión (Fenix)

```bash
# Verificar estado global
podman ps --all

# Ver logs del motor Cortex
podman logs -f sentinel-cortex

# Ejecutar certificación de integridad aritmética S60
cargo run --release -p sentinel-cortex --bin certify_s60
```

---

**Nota**: Todos los accesos están protegidos vía Traefik con autenticación BasicAuth o TLS según configuración.
