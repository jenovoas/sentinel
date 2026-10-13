# 🚀 Guía Rápida: Sentinel Podman

## Instalación Inicial

```bash
# 1. Verificar que Podman está instalado
podman --version
podman-compose --version

# 2. Dar permisos al script
chmod +x scripts/pod-manager.sh
```

---

## Uso Diario

### Desarrollo Frío (Solo Base de Datos)
```bash
./scripts/pod-manager.sh start minimal
```
**Consumo:** ~1.5GB RAM  
**Servicios:** postgres + redis

---

### Desarrollo Full-Stack
```bash
./scripts/pod-manager.sh start backend
```
**Consumo:** ~3.5GB RAM  
**Servicios:** postgres + redis + backend + frontend

**Verificar:**
```bash
curl http://localhost:8000/health
curl http://localhost:3000
```

---

### Stack Completo (Producción/Testing)
```bash
./scripts/pod-manager.sh start full
```
**Consumo:** ~8GB RAM  
**Servicios:** Todo el stack (automation + observability)

**Acceso:**
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- n8n: http://localhost:5678
- Grafana: http://localhost:3001
- Prometheus: http://localhost:9090

---

## Comandos Esenciales

```bash
# Ver estado
./scripts/pod-manager.sh status

# Ver logs
./scripts/pod-manager.sh logs sentinel-backend

# Monitorear recursos
./scripts/pod-manager.sh stats

# Detener todo
./scripts/pod-manager.sh stop

# Limpiar todo
./scripts/pod-manager.sh clean
```

---

## Workflow TruthSync

```bash
# 1. Iniciar minimal
./scripts/pod-manager.sh start minimal

# 2. Certificar código
python3 quantum/certify_codebase.py

# 3. Detener (modo frío)
./scripts/pod-manager.sh stop
```

---

## Troubleshooting

### Sistema se calienta
```bash
# Detener inmediatamente
./scripts/pod-manager.sh stop

# Verificar que todo está apagado
podman ps
```

### Contenedor no inicia
```bash
# Ver logs de error
./scripts/pod-manager.sh logs sentinel-<servicio>

# Reconstruir imagen
podman-compose -f podman-compose.backend.yml build --no-cache
```

### Problemas de red
```bash
# Recrear red
podman network rm sentinel-net
podman network create sentinel-net
```

---

## Backup/Restore

```bash
# Backup PostgreSQL
podman exec sentinel-postgres pg_dump -U sentinel_user sentinel_db > backup.sql

# Restore
cat backup.sql | podman exec -i sentinel-postgres psql -U sentinel_user sentinel_db
```
