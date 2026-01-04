#  Sentinel - Guía de Instalación Completa

**Guía paso a paso para instalar Sentinel en cualquier entorno**

---

## 📋 Tabla de Contenidos

1. [Requisitos del Sistema](#-requisitos-del-sistema)
2. [Instalación Rápida (5 minutos)](#-instalación-rápida-5-minutos)
3. [Instalación Detallada](#-instalación-detallada)
4. [Verificación de la Instalación](#-verificación-de-la-instalación)
5. [Acceso a los Servicios](#-acceso-a-los-servicios)
6. [Configuración Avanzada](#-configuración-avanzada)
7. [Solución de Problemas](#-solución-de-problemas)

---

## 📦 Requisitos del Sistema

### Requisitos Mínimos

| Componente | Requisito |
|------------|-----------|
| **Sistema Operativo** | Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+) |
| **CPU** | 4 cores |
| **RAM** | 8 GB |
| **Disco** | 50 GB libres |
| **Docker** | 24.0+ |
| **Docker Compose** | 2.20+ |

### Requisitos Recomendados (con IA)

| Componente | Requisito |
|------------|-----------|
| **CPU** | 8 cores |
| **RAM** | 16 GB |
| **Disco** | 100 GB SSD |
| **GPU** | NVIDIA GTX 1050+ (3GB VRAM) - Opcional pero recomendado |

### Software Requerido

- **Docker Engine** 24.0 o superior
- **Docker Compose** 2.20 o superior
- **Git** (para clonar el repositorio)
- **curl** y **jq** (para verificación)

---

## ⚡ Instalación Rápida (5 minutos)

> **Nota**: Esta instalación usa configuraciones por defecto. Para producción, ver [Configuración Avanzada](#-configuración-avanzada).

### Paso 1: Instalar Docker y Docker Compose

#### En Ubuntu/Debian:

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y curl git jq

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker (evita usar sudo)
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker --version
docker-compose --version

# IMPORTANTE: Cerrar sesión y volver a entrar para aplicar permisos
```

#### En CentOS/RHEL:

```bash
# Actualizar sistema
sudo yum update -y

# Instalar dependencias
sudo yum install -y curl git jq

# Instalar Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# Iniciar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# IMPORTANTE: Cerrar sesión y volver a entrar
```

### Paso 2: Clonar el Repositorio

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/sentinel.git
cd sentinel

# Verificar que estás en el directorio correcto
ls -la
# Deberías ver: docker-compose.yml, README.md, backend/, frontend/, etc.
```

### Paso 3: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar configuración (IMPORTANTE: cambiar contraseñas en producción)
nano .env  # o usa vim, vi, o tu editor preferido
```

**Configuración mínima requerida en `.env`:**

```bash
# PostgreSQL
POSTGRES_USER=sentinel_user
POSTGRES_PASSWORD=TU_PASSWORD_SEGURO_AQUI  # ⚠ CAMBIAR
POSTGRES_DB=sentinel_db

# Backend
SECRET_KEY=tu-clave-secreta-minimo-32-caracteres-cambiar-en-produccion  # ⚠ CAMBIAR

# Grafana
GRAFANA_USER=admin
GRAFANA_PASSWORD=TU_PASSWORD_GRAFANA  # ⚠ CAMBIAR

# n8n
N8N_USER=admin
N8N_PASSWORD=TU_PASSWORD_N8N  # ⚠ CAMBIAR
```

### Paso 4: Iniciar Sentinel

```bash
# Construir e iniciar todos los servicios
docker-compose up -d

# Ver logs en tiempo real (Ctrl+C para salir)
docker-compose logs -f
```

**Tiempo estimado**: 5-10 minutos (dependiendo de tu conexión a internet)

### Paso 5: Verificar Instalación

```bash
# Esperar 2-3 minutos para que todos los servicios inicien
sleep 180

# Verificar estado de servicios
docker-compose ps

# Verificar salud del sistema
make health
```

**Salida esperada**: Todos los servicios deben estar "Up" y "healthy"

---

## 🔧 Instalación Detallada

### Arquitectura de Servicios

Sentinel despliega **18 servicios** en contenedores Docker:

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **Frontend** | 3000 | Dashboard Next.js |
| **Backend** | 8000 | API FastAPI |
| **PostgreSQL** | 5432 | Base de datos principal |
| **Redis** | 6379 | Cache y message broker |
| **Nginx** | 80, 443 | Reverse proxy |
| **Prometheus** | 9090 | Métricas |
| **Grafana** | 3001 | Dashboards |
| **Loki** | 3100 | Logs |
| **n8n** | 5678 | Automatización |
| **Ollama** | 11434 | IA local |
| **Node Exporter** | 9100 | Métricas del host |
| **PostgreSQL Exporter** | 9187 | Métricas de DB |
| **Redis Exporter** | 9121 | Métricas de Redis |
| **Promtail** | 9080 | Recolector de logs |
| **Celery Worker** | - | Tareas asíncronas |
| **Celery Beat** | - | Scheduler |
| **Ollama Init** | - | Descarga modelos IA |
| **n8n Loader** | - | Carga workflows |

### Instalación Paso a Paso

#### 1. Preparar el Sistema

```bash
# Crear directorio para Sentinel
mkdir -p ~/sentinel-install
cd ~/sentinel-install

# Clonar repositorio
git clone https://github.com/tu-usuario/sentinel.git
cd sentinel

# Verificar estructura
tree -L 1
```

#### 2. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Generar SECRET_KEY seguro
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Editar .env con tu editor favorito
nano .env
```

**Variables críticas a configurar:**

```bash
# ============================================================================
# SEGURIDAD (⚠ CAMBIAR EN PRODUCCIÓN)
# ============================================================================
POSTGRES_PASSWORD=<PASSWORD_SEGURO>
SECRET_KEY=<GENERAR_CON_COMANDO_ANTERIOR>
GRAFANA_PASSWORD=<PASSWORD_SEGURO>
N8N_PASSWORD=<PASSWORD_SEGURO>

# ============================================================================
# OBSERVABILIDAD (Opcional - Protección con contraseña)
# ============================================================================
OBSERVABILITY_METRICS_PASSWORD=<PASSWORD_PROMETHEUS>
OBSERVABILITY_LOGS_PASSWORD=<PASSWORD_LOKI>

# ============================================================================
# BACKUP (Opcional - Configurar después)
# ============================================================================
S3_ENABLED=false
MINIO_ENABLED=false
ENCRYPT_ENABLED=false

# ============================================================================
# IA (Opcional - Configurar si tienes GPU)
# ============================================================================
OLLAMA_MODEL=phi3:mini  # Modelo ligero (1.9GB)
# OLLAMA_MODEL=llama3.2:1b  # Alternativa más ligera (1.3GB)
AI_ENABLED=true
```

#### 3. Configurar GPU (Opcional - Solo NVIDIA)

Si tienes GPU NVIDIA y quieres acelerar la IA:

```bash
# Instalar NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Verificar GPU
nvidia-smi
```

#### 4. Construir Imágenes

```bash
# Construir todas las imágenes
docker-compose build

# Ver imágenes creadas
docker images | grep sentinel
```

#### 5. Iniciar Servicios por Fases

**Fase 1: Infraestructura Base**

```bash
# Iniciar PostgreSQL y Redis
docker-compose up -d postgres redis

# Esperar a que estén listos
docker-compose logs -f postgres redis
# Esperar mensaje: "database system is ready to accept connections"
# Ctrl+C para salir
```

**Fase 2: Backend y Workers**

```bash
# Iniciar backend y workers
docker-compose up -d backend celery_worker celery_beat

# Verificar logs
docker-compose logs -f backend
# Esperar mensaje: "Application startup complete"
```

**Fase 3: Frontend y Proxy**

```bash
# Iniciar frontend y nginx
docker-compose up -d frontend nginx

# Verificar
docker-compose logs -f frontend
```

**Fase 4: Observabilidad**

```bash
# Iniciar stack de observabilidad
docker-compose up -d prometheus loki grafana promtail \
  node-exporter postgres-exporter redis-exporter

# Verificar
docker-compose ps
```

**Fase 5: Automatización e IA**

```bash
# Iniciar n8n y Ollama
docker-compose up -d n8n ollama

# Esperar a que Ollama descargue modelos (puede tardar 5-10 minutos)
docker-compose logs -f ollama-init
# Esperar mensaje: "🎉 All models ready!"
```

#### 6. Verificación Completa

```bash
# Verificar todos los servicios
docker-compose ps

# Deberías ver 18 servicios "Up"
# Algunos servicios (ollama-init, n8n-loader) estarán "Exit 0" (normal)

# Verificar salud
make health

# Verificar API
curl http://localhost:8000/api/v1/health | jq .
```

---

## ✅ Verificación de la Instalación

### Verificación Automática

```bash
# Usar el script de verificación incluido
./verify.sh

# O usar Makefile
make health
```

### Verificación Manual

#### 1. Verificar Contenedores

```bash
docker-compose ps

# Salida esperada:
# NAME                          STATUS
# sentinel-backend              Up (healthy)
# sentinel-postgres             Up (healthy)
# sentinel-redis                Up (healthy)
# sentinel-frontend             Up
# sentinel-nginx                Up (healthy)
# sentinel-prometheus           Up
# sentinel-grafana              Up
# sentinel-loki                 Up
# sentinel-n8n                  Up (healthy)
# sentinel-ollama               Up (healthy)
# ... (más servicios)
```

#### 2. Verificar Base de Datos

```bash
# Conectar a PostgreSQL
docker-compose exec postgres psql -U sentinel_user -d sentinel_db

# Ejecutar dentro de psql:
\dt  # Listar tablas
\q   # Salir
```

#### 3. Verificar API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Respuesta esperada:
# {"status":"healthy","database":"connected","redis":"connected"}

# Verificar documentación API
curl http://localhost:8000/docs
# Debería devolver HTML de Swagger UI
```

#### 4. Verificar Frontend

```bash
# Verificar que responde
curl -I http://localhost:3000

# Respuesta esperada:
# HTTP/1.1 200 OK
```

#### 5. Verificar Observabilidad

```bash
# Prometheus
curl http://localhost:9090/-/healthy

# Grafana
curl -I http://localhost:3001

# Loki
curl http://localhost:3100/ready
```

#### 6. Verificar IA (Ollama)

```bash
# Listar modelos descargados
curl http://localhost:11434/api/tags

# Probar generación
curl http://localhost:11434/api/generate -d '{
  "model": "phi3:mini",
  "prompt": "Hello, what is Sentinel?",
  "stream": false
}'
```

---

## 🌐 Acceso a los Servicios

### URLs de Acceso

Una vez instalado, puedes acceder a:

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Dashboard Principal** | http://localhost:3000 | - |
| **API Backend** | http://localhost:8000 | - |
| **API Docs (Swagger)** | http://localhost:8000/docs | - |
| **Grafana** | http://localhost:3001 | admin / (ver .env) |
| **Prometheus** | http://localhost:9090 | - |
| **n8n Workflows** | http://localhost:5678 | admin / (ver .env) |
| **Nginx Proxy** | http://localhost | - |

### Credenciales por Defecto

> ⚠ **IMPORTANTE**: Cambiar todas las contraseñas en producción

```bash
# Grafana
Usuario: admin
Password: (definido en .env - GRAFANA_PASSWORD)

# n8n
Usuario: admin
Password: (definido en .env - N8N_PASSWORD)

# PostgreSQL
Usuario: sentinel_user
Password: (definido en .env - POSTGRES_PASSWORD)
Database: sentinel_db
```

### Primer Acceso

1. **Dashboard Principal** (http://localhost:3000)
   - Interfaz principal de Sentinel
   - Visualización de métricas en tiempo real
   - Gestión de organizaciones y usuarios

2. **Grafana** (http://localhost:3001)
   - Dashboards pre-configurados
   - Métricas de infraestructura
   - Logs centralizados

3. **API Docs** (http://localhost:8000/docs)
   - Documentación interactiva
   - Prueba de endpoints
   - Esquemas de datos

---

## ⚙ Configuración Avanzada

### Alta Disponibilidad (HA)

Para entornos de producción con HA:

```bash
# Usar docker-compose con HA
docker-compose -f docker-compose.yml -f docker-compose-ha.yml up -d

# Esto despliega:
# - PostgreSQL con Patroni + etcd
# - Redis con Sentinel
# - HAProxy para load balancing
```

Ver [HA_REFERENCE_DESIGN.md](docs/HA_REFERENCE_DESIGN.md) para detalles.

### Backup Automatizado

```bash
# Configurar en .env
BACKUP_DIR=/var/backups/sentinel/postgres
BACKUP_RETENTION_DAYS=7
S3_ENABLED=true
S3_BUCKET=s3://tu-bucket/sentinel-backups

# Ejecutar backup manual
make db-backup

# Configurar backup automático (cron)
crontab -e

# Agregar línea (backup diario a las 2 AM):
0 2 * * * cd /ruta/a/sentinel && make db-backup
```

Ver [BACKUP_SETUP_GUIDE.md](docs/BACKUP_SETUP_GUIDE.md) para detalles.

### Configurar SSL/TLS

```bash
# 1. Obtener certificados (Let's Encrypt)
sudo apt install certbot
sudo certbot certonly --standalone -d tu-dominio.com

# 2. Copiar certificados
sudo cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem docker/nginx/ssl/
sudo cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem docker/nginx/ssl/

# 3. Actualizar nginx.conf
# Descomentar sección SSL en docker/nginx/nginx.conf

# 4. Reiniciar nginx
docker-compose restart nginx
```

### Configurar Autenticación Observabilidad

```bash
# Generar contraseñas para Prometheus y Loki
htpasswd -c docker/nginx/.htpasswd_metrics admin
htpasswd -c docker/nginx/.htpasswd_logs admin

# Reiniciar nginx
docker-compose restart nginx

# Ahora Prometheus y Loki requieren autenticación
```

### Optimización de Recursos

#### Para Servidores con Recursos Limitados (4GB RAM):

```bash
# Editar docker-compose.yml
# Agregar límites de memoria a servicios:

services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
  
  postgres:
    deploy:
      resources:
        limits:
          memory: 1G
  
  redis:
    deploy:
      resources:
        limits:
          memory: 256M
```

#### Deshabilitar Servicios Opcionales:

```bash
# Si no necesitas IA, comentar en docker-compose.yml:
# - ollama
# - ollama-init

# Si no necesitas automatización:
# - n8n
# - n8n-loader

# Reiniciar
docker-compose up -d
```

---

## 🔧 Solución de Problemas

### Problema: Servicios no inician

**Síntoma**: `docker-compose ps` muestra servicios "Exit 1" o "Restarting"

**Solución**:

```bash
# Ver logs del servicio problemático
docker-compose logs <nombre-servicio>

# Ejemplo: si postgres falla
docker-compose logs postgres

# Verificar permisos de volúmenes
sudo chown -R $USER:$USER .

# Limpiar y reiniciar
docker-compose down -v
docker-compose up -d
```

### Problema: Puerto ya en uso

**Síntoma**: `Error: bind: address already in use`

**Solución**:

```bash
# Identificar proceso usando el puerto
sudo lsof -i :8000  # Cambiar 8000 por el puerto problemático

# Matar proceso
sudo kill -9 <PID>

# O cambiar puerto en docker-compose.yml
# Ejemplo: cambiar "8000:8000" a "8001:8000"
```

### Problema: Base de datos no conecta

**Síntoma**: Backend muestra "Database connection failed"

**Solución**:

```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps postgres

# Verificar logs
docker-compose logs postgres

# Verificar conectividad
docker-compose exec postgres pg_isready -U sentinel_user

# Reiniciar PostgreSQL
docker-compose restart postgres

# Esperar 30 segundos y reiniciar backend
sleep 30
docker-compose restart backend
```

### Problema: Ollama no descarga modelos

**Síntoma**: `ollama-init` falla o se queda descargando

**Solución**:

```bash
# Verificar espacio en disco
df -h

# Descargar modelo manualmente
docker-compose exec ollama ollama pull phi3:mini

# Ver progreso
docker-compose logs -f ollama-init

# Si falla, usar modelo más pequeño
# Editar .env: OLLAMA_MODEL=llama3.2:1b
docker-compose up -d ollama-init
```

### Problema: Frontend no carga

**Síntoma**: http://localhost:3000 no responde

**Solución**:

```bash
# Verificar logs
docker-compose logs frontend

# Reinstalar dependencias
docker-compose exec frontend npm install

# Reconstruir
docker-compose build frontend
docker-compose up -d frontend

# Verificar que backend está corriendo
curl http://localhost:8000/api/v1/health
```

### Problema: Permisos de Docker

**Síntoma**: `permission denied while trying to connect to the Docker daemon socket`

**Solución**:

```bash
# Agregar usuario a grupo docker
sudo usermod -aG docker $USER

# Cerrar sesión y volver a entrar
exit
# (volver a conectar)

# Verificar
docker ps
```

### Problema: Memoria insuficiente

**Síntoma**: Servicios se reinician constantemente, sistema lento

**Solución**:

```bash
# Verificar uso de memoria
docker stats

# Deshabilitar servicios opcionales
# Editar docker-compose.yml y comentar:
# - ollama (si no usas IA)
# - n8n (si no usas automatización)
# - grafana (si solo necesitas API)

# Reiniciar
docker-compose down
docker-compose up -d
```

### Logs y Debugging

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend

# Ver últimas 100 líneas
docker-compose logs --tail=100 backend

# Entrar a un contenedor
docker-compose exec backend bash

# Verificar variables de entorno
docker-compose exec backend env

# Verificar conectividad entre servicios
docker-compose exec backend ping postgres
docker-compose exec backend ping redis
```

---

## 📚 Recursos Adicionales

### Documentación

- [README.md](README.md) - Descripción general del proyecto
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura técnica
- [API Documentation](http://localhost:8000/docs) - Documentación de API
- [HA_REFERENCE_DESIGN.md](docs/HA_REFERENCE_DESIGN.md) - Alta disponibilidad
- [BACKUP_SETUP_GUIDE.md](docs/BACKUP_SETUP_GUIDE.md) - Sistema de backups

### Comandos Útiles (Makefile)

```bash
make help              # Ver todos los comandos disponibles
make up                # Iniciar servicios
make down              # Detener servicios
make restart           # Reiniciar servicios
make logs              # Ver logs
make health            # Verificar salud
make db-backup         # Backup de base de datos
make clean             # Limpiar todo (⚠ elimina datos)
```

### Soporte

- **Issues**: https://github.com/tu-usuario/sentinel/issues
- **Documentación**: https://sentinel.dev/docs
- **Email**: support@sentinel.dev

---

## 🎉 ¡Instalación Completada!

Si llegaste hasta aquí, **¡felicitaciones!** 🎊

Sentinel está instalado y corriendo. Ahora puedes:

1. ✅ Acceder al dashboard: http://localhost:3000
2. ✅ Ver métricas en Grafana: http://localhost:3001
3. ✅ Explorar la API: http://localhost:8000/docs
4. ✅ Crear workflows en n8n: http://localhost:5678

---

**¿Problemas?** Consulta la sección [Solución de Problemas](#-solución-de-problemas) o abre un issue en GitHub.

**¡Disfruta Sentinel!** 
