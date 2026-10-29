# 🚀 Servicios Activos de Sentinel (Producción Fenix)

**Última actualización**: 17 de Abril, 2026
**Estado**: 🟢 OPERATIVO (Estabilización Post-Conflicto de Puertos Completada)
**Infraestructura**: Podman Rootless (Rocky Linux 9)

---

## 📋 Servicios de Núcleo (Core)

### 1. Sentinel Cortex (Backend FastAPI)
- **URL**: <https://cortex.pinguinoseguro.cl/api>
- **Puerto Interno (Host)**: `8000`
- **Estado**: ✅ Activo

### 2. Dashboard UI (Next.js)
- **Puerto Host**: `3030`
- **Descripción**: Interfaz de control y visualización.
- **Estado**: ✅ Activo

### 3. Nginx Gateway (Sentinel Proxy)
- **Puerto Host**: `8082`
- **Estado**: ✅ Activo (Proxy hacia Frontend/Backend en localhost)

---

## 📊 Stack de Observabilidad

### 5. Grafana (Visualización)
- **Puerto Host**: `3011` (Interno contenedor: 3005)
- **Estado**: ✅ Activo

### 12. Uptime Kuma (PinguinoSeguro)
- **Puerto Host**: `3002`
- **Estado**: ✅ Activo

---

## 🛠️ Procedimientos de Mantenimiento de Infraestructura

### ⚠️ Reseteo de Red (En caso de "Address already in use")
Si un contenedor falla al arrancar alegando que el puerto está ocupado pero `netstat` no muestra culpables claros, ejecutar:
```bash
# 1. Detener todos los pods
podman pod stop --all

# 2. Eliminar procesos de red huérfanos (RootlessPort)
killall -9 rootlessport

# 3. Reiniciar el stack
podman-compose up -d
```

### 🛡️ Arquitectura de Comunicación en el Pod
**IMPORTANTE**: Dentro del Pod `pod_sentinel`, los servicios **DEBEN** comunicarse vía `localhost:<puerto>` (ej: Nginx -> `localhost:8000`). El uso de nombres de servicio de Docker-Compose no es confiable dentro de un mismo Pod Rootless.

---

**Nota**: Todos los accesos están protegidos vía Traefik con autenticación BasicAuth o TLS según configuración.
