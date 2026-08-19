# 🐳 Guía de Migración: Podman Multi-Pod

Esta guía detalla la nueva arquitectura de **3 perfiles** optimizada para evitar sobrecalentamiento y sobreprocesamiento del host.

## 🎯 Arquitectura de Perfiles

Sentinel ahora usa **3 configuraciones independientes** con pods separados:

| Perfil | Consumo | Servicios | Uso |
|--------|---------|-----------|-----|
| **MINIMAL** | ~1.5GB RAM, 2 CPUs | postgres + redis | Desarrollo frío, certificación TruthSync |
| **BACKEND** | ~3.5GB RAM, 5 CPUs | + backend + frontend | Desarrollo full-stack, testing APIs |
| **FULL** | ~8GB RAM, 10 CPUs | + automation + observability | Testing producción, debugging telemetría |

---

## 🚀 Inicio Rápido con Script de Gestión

Usa el script unificado `pod-manager.sh` para gestionar los perfiles:

### Iniciar un Perfil
```bash
# Perfil minimal (solo base de datos)
./scripts/pod-manager.sh start minimal

# Perfil backend (desarrollo activo)
./scripts/pod-manager.sh start backend

# Perfil full (stack completo)
./scripts/pod-manager.sh start full
```

### Detener Todos los Servicios
```bash
./scripts/pod-manager.sh stop
```

### Ver Estado
```bash
./scripts/pod-manager.sh status
```

### Ver Logs
```bash
./scripts/pod-manager.sh logs sentinel-backend
```

### Monitorear Recursos
```bash
./scripts/pod-manager.sh stats
```

### Limpiar Todo
```bash
./scripts/pod-manager.sh clean
```

---

## 📋 Detalle de Perfiles

### 1. MINIMAL - Desarrollo Frío
**Archivo:** `podman-compose.minimal.yml`

**Servicios:**
- PostgreSQL (1GB RAM, 2 CPUs)
- Redis (512MB RAM, 1 CPU)

**Uso:**
- Certificación de código con TruthSync
- Desarrollo sin servicios pesados
- Testing de scripts quantum

**Comando:**
```bash
./scripts/pod-manager.sh start minimal
```

---

### 2. BACKEND - Desarrollo Activo
**Archivo:** `podman-compose.backend.yml`

**Servicios:**
- PostgreSQL (1GB RAM, 2 CPUs)
- Redis (512MB RAM, 1 CPU)
- Backend API (1GB RAM, 2 CPUs)
- Frontend (1GB RAM, 2 CPUs)

**Uso:**
- Desarrollo full-stack
- Testing de APIs
- Integración con TruthSync en tiempo real

**Comando:**
```bash
./scripts/pod-manager.sh start backend
```

**Verificación:**
```bash
curl http://localhost:8000/health
curl http://localhost:3000
```

---

### 3. FULL - Stack Completo
**Archivo:** `podman-compose.full.yml`

**Servicios:**
- **Data Pod:** postgres + redis
- **App Pod:** backend + frontend + nginx
- **Automation Pod:** n8n + celery-worker + celery-beat
- **Observability Pod:** prometheus + grafana + loki + exporters

**Uso:**
- Testing de producción
- Debugging de telemetría
- Validación de playbooks n8n
- Análisis de métricas en Grafana

**Comando:**
```bash
./scripts/pod-manager.sh start full
```

**Acceso a Servicios:**
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- n8n: http://localhost:5678
- Grafana: http://localhost:3001
- Prometheus: http://localhost:9090

---

## 📊 Límites de Recursos por Servicio

Todos los servicios tienen límites duros para evitar consumo excesivo:

| Servicio | CPU Limit | RAM Limit |
|----------|-----------|-----------|
| postgres | 2.0 | 1GB |
| redis | 1.0 | 512MB |
| backend | 2.0 | 1GB |
| frontend | 2.0 | 1GB |
| nginx | 1.0 | 256MB |
| n8n | 2.0 | 1GB |
| celery-worker | 1.0 | 512MB |
| celery-beat | 0.5 | 256MB |
| prometheus | 1.0 | 512MB |
| grafana | 1.0 | 512MB |
| loki | 1.0 | 512MB |
| promtail | 0.5 | 256MB |
| node-exporter | 0.5 | 128MB |
| postgres-exporter | 0.5 | 128MB |
| redis-exporter | 0.5 | 128MB |

---

## 🛠 Troubleshooting

### Verificar Consumo en Tiempo Real
```bash
./scripts/pod-manager.sh stats
```

### Ver Logs de un Servicio
```bash
./scripts/pod-manager.sh logs sentinel-postgres
./scripts/pod-manager.sh logs sentinel-backend
```

### Reiniciar un Perfil
```bash
./scripts/pod-manager.sh restart backend
```

### Problemas de Red
La red `sentinel-net` está configurada como `driver: bridge`, compatible con rootless podman. 

Si tienes problemas de resolución DNS entre contenedores:
```bash
# Verificar plugin dnsname
podman network inspect sentinel-net

# Recrear red si es necesario
podman network rm sentinel-net
podman network create sentinel-net
```

### Contenedores No Inician
```bash
# Ver estado detallado
podman ps -a

# Ver logs de error
podman logs sentinel-<servicio>

# Verificar imágenes
podman images | grep sentinel
```

---

## 🔥 Control Térmico

**IMPORTANTE:** Si el sistema se calienta, detén servicios inmediatamente:

```bash
# Detener todo
./scripts/pod-manager.sh stop

# Verificar que todo está apagado
podman ps

# Limpiar recursos
podman system prune -f
```

**Recomendaciones:**
- Usa `minimal` para desarrollo diario
- Usa `backend` solo cuando necesites probar APIs
- Usa `full` solo para validaciones críticas (máximo 30 minutos)
- Monitorea temperatura del CPU con `sensors` o `htop`

---

## 📦 Volúmenes Persistentes

Los datos se mantienen en volúmenes Podman:

```bash
# Listar volúmenes
podman volume ls

# Backup de PostgreSQL
podman exec sentinel-postgres pg_dump -U sentinel_user sentinel_db > backup.sql

# Restaurar backup
cat backup.sql | podman exec -i sentinel-postgres psql -U sentinel_user sentinel_db
```

---

## 🔄 Migración desde Docker

Si vienes de `docker-compose.yml`:

```bash
# 1. Detener Docker
docker-compose down

# 2. Exportar datos (opcional)
docker exec sentinel-postgres pg_dump -U sentinel_user sentinel_db > backup.sql

# 3. Iniciar con Podman
./scripts/pod-manager.sh start backend

# 4. Restaurar datos (opcional)
cat backup.sql | podman exec -i sentinel-postgres psql -U sentinel_user sentinel_db
```

---

## 📚 Comandos Útiles

```bash
# Ver ayuda del script
./scripts/pod-manager.sh help

# Ver todos los contenedores (activos e inactivos)
podman ps -a

# Ver consumo de recursos
podman stats --no-stream

# Limpiar todo (contenedores + volúmenes)
./scripts/pod-manager.sh clean

# Reconstruir imágenes
podman-compose -f podman-compose.backend.yml build --no-cache
```
