# Planificación: Integración Completa de Contenedores al Frontend

**Fecha de inicio:** 2026-01-03
**Estado:** Pendiente
**Prioridad:** Alta

## Contexto

Sentinel tiene un ecosistema complejo de **16 contenedores** que necesitan ser integrados y controlados desde el frontend. Ya tenemos una DevOps Console básica, pero necesita expandirse para manejar toda la arquitectura.

## Contenedores del Ecosistema Sentinel

### Core Services
1. **sentinel-postgres** - PostgreSQL Database (puerto 5432)
2. **sentinel-redis** - Redis Cache (puerto 6379)
3. **sentinel-backend** - FastAPI Backend (puerto 8000)
4. **sentinel-worker** - Celery Worker
5. **sentinel-beat** - Celery Beat Scheduler

### Frontend & Proxy
6. **sentinel-frontend** - Next.js Frontend (puerto 3000)
7. **sentinel-nginx** - Nginx Reverse Proxy (puertos 80, 443)

### Observability Stack
8. **sentinel-prometheus** - Prometheus Metrics (puerto 9090)
9. **sentinel-loki** - Loki Log Aggregation
10. **sentinel-promtail** - Promtail Log Collector
11. **sentinel-node-exporter** - Node Exporter
12. **sentinel-postgres-exporter** - PostgreSQL Exporter
13. **sentinel-redis-exporter** - Redis Exporter
14. **sentinel-grafana** - Grafana Dashboards (puerto 3001)

### AI & Automation
15. **sentinel-ollama** - Ollama Local AI (puerto 11434)
16. **sentinel-n8n** - n8n Automation (puerto 5678)

## Tareas Pendientes

### Fase 1: Backend API Endpoints (Prioridad: ALTA)
- [ ] Crear endpoint `/api/v1/docker/containers` - Listar todos los contenedores
- [ ] Crear endpoint `/api/v1/docker/containers/{id}/start` - Iniciar contenedor
- [ ] Crear endpoint `/api/v1/docker/containers/{id}/stop` - Detener contenedor
- [ ] Crear endpoint `/api/v1/docker/containers/{id}/restart` - Reiniciar contenedor
- [ ] Crear endpoint `/api/v1/docker/containers/{id}/logs` - Obtener logs del contenedor
- [ ] Crear endpoint `/api/v1/docker/containers/{id}/stats` - Estadísticas en tiempo real
- [ ] Crear endpoint `/api/v1/docker/compose/status` - Estado del docker-compose completo
- [ ] Crear endpoint `/api/v1/docker/compose/restart` - Reiniciar stack completo

### Fase 2: Frontend - DevOps Console Mejorado (Prioridad: ALTA)
- [ ] **Dashboard de Arquitectura Visual**
  - Mapa visual de todos los contenedores
  - Conexiones entre servicios (flechas indicando dependencias)
  - Estado en tiempo real (running/stopped/error)
  - Uso de recursos (CPU, memoria) por contenedor
  
- [ ] **Panel de Control Individual**
  - Card expandible para cada contenedor
  - Botones de control (start/stop/restart/logs)
  - Métricas en tiempo real
  - Health checks visuales
  
- [ ] **Vista de Logs Unificada**
  - Logs de todos los contenedores en un solo lugar
  - Filtros por servicio, nivel, timestamp
  - Búsqueda en tiempo real
  - Export de logs

- [ ] **Terminal Mejorado**
  - Ejecutar comandos docker directamente
  - Auto-completado de comandos docker
  - Historial de comandos
  - Ejecución en contenedores específicos (docker exec)

### Fase 3: Visualización Avanzada (Prioridad: MEDIA)
- [ ] **Mapa de Dependencias**
  - Grafo visual de dependencias entre servicios
  - Indicadores de salud en cada nodo
  - Flujo de datos entre servicios
  
- [ ] **Dashboard de Métricas Agregadas**
  - CPU total del stack
  - Memoria total del stack
  - Network I/O total
  - Disk I/O total
  
- [ ] **Alertas y Notificaciones**
  - Alertas cuando un contenedor se cae
  - Notificaciones de alto uso de recursos
  - Sistema de health checks automático

### Fase 4: Orquestación Inteligente (Prioridad: BAJA)
- [ ] **Auto-scaling**
  - Detectar carga alta
  - Escalar workers automáticamente
  
- [ ] **Auto-healing**
  - Reiniciar contenedores que fallen
  - Logs de auto-recuperación
  
- [ ] **Backup y Restore**
  - Backup de volúmenes
  - Restore point-in-time
  - Snapshots del estado completo

## Concepto Nuevo: "Sovereign Container Matrix"

Crear una interfaz unificada que muestre:
- **Vista de Matriz 3D**: Todos los contenedores en un espacio 3D interactivo
- **Flujo de Datos en Tiempo Real**: Animaciones mostrando el flujo de requests
- **Quantum Health Status**: Indicadores cuánticos de salud del sistema
- **Neural Network View**: Vista de red neuronal de las conexiones

## Archivos a Modificar/Crear

### Backend
- `/home/jnovoas/sentinel/backend/app/routers/docker.py` (crear)
- `/home/jnovoas/sentinel/backend/app/services/docker_service.py` (crear)
- `/home/jnovoas/sentinel/backend/app/routers/system.py` (expandir)

### Frontend
- `/home/jnovoas/sentinel/frontend/src/app/devops/page.tsx` (expandir)
- `/home/jnovoas/sentinel/frontend/src/components/docker/ContainerMatrix.tsx` (crear)
- `/home/jnovoas/sentinel/frontend/src/components/docker/ServiceGraph.tsx` (crear)
- `/home/jnovoas/sentinel/frontend/src/components/docker/ContainerCard.tsx` (crear)
- `/home/jnovoas/sentinel/frontend/src/hooks/useDockerStatus.ts` (crear)

## Estimación de Tiempo
- Fase 1: 4-6 horas
- Fase 2: 6-8 horas
- Fase 3: 4-6 horas
- Fase 4: 8-10 horas

**Total estimado:** 22-30 horas de desarrollo

## Notas Técnicas
- Usar Docker SDK para Python en el backend
- WebSockets para actualizaciones en tiempo real
- React Query para cache y sincronización
- Framer Motion para animaciones fluidas
- Three.js para visualización 3D (opcional)

## Referencias
- Docker Compose file: `/home/jnovoas/sentinel/docker-compose.yml`
- DevOps Console actual: `/home/jnovoas/sentinel/frontend/src/app/devops/page.tsx`
- Documentación Docker API: https://docs.docker.com/engine/api/

---

**Última actualización:** 2026-01-03 00:26
**Responsable:** Sistema Sentinel IA
**Estado:** Documentado y listo para implementación
