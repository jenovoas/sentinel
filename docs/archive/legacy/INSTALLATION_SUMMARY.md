# 📦 Sentinel - Resumen de Instalación

**Guías de instalación disponibles para todos los sistemas operativos**

---

##  Instalación Rápida

### Linux (Ubuntu, Debian, CentOS, RHEL)

```bash
git clone https://github.com/jenovoas/sentinel.git
cd sentinel
chmod +x install.sh
./install.sh
```

### Windows (10/11 con WSL2)

```powershell
# PowerShell como Administrador
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/jenovoas/sentinel/main/install-windows.ps1" -OutFile "install-windows.ps1"
.\install-windows.ps1
```

### macOS (con Docker Desktop)

```bash
# Instalar Docker Desktop desde: https://www.docker.com/products/docker-desktop/
git clone https://github.com/jenovoas/sentinel.git
cd sentinel
cp .env.example .env
docker-compose up -d
```

---

## 📚 Documentación Completa

| Sistema | Guía | Script Automatizado |
|---------|------|---------------------|
| **Linux** | [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) | `install.sh` |
| **Windows** | [INSTALLATION_GUIDE_WINDOWS.md](INSTALLATION_GUIDE_WINDOWS.md) | `install-windows.ps1` |
| **Quick Start** | [QUICKSTART.md](QUICKSTART.md) | - |

---

##  Características de los Instaladores

### ✅ install.sh (Linux)
- Detección automática de distribución (Ubuntu, Debian, CentOS, RHEL)
- Instalación de Docker y Docker Compose
- Verificación de requisitos del sistema
- Configuración interactiva de contraseñas
- Generación automática de SECRET_KEY
- Construcción e inicio de servicios
- Verificación completa de salud
- Output colorido y amigable

### ✅ install-windows.ps1 (Windows)
- Verificación de versión de Windows
- Instalación automática de WSL2
- Guía para Docker Desktop
- Configuración de Ubuntu en WSL2
- Clonación y setup en WSL2
- Ejecución del instalador Linux en WSL2
- Verificación desde PowerShell
- Apertura automática del navegador

---

## 🌐 Acceso a Servicios

Una vez instalado, accede desde cualquier navegador:

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Dashboard** | http://localhost:3000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Grafana** | http://localhost:3001 | admin / (ver .env) |
| **n8n** | http://localhost:5678 | admin / (ver .env) |
| **Prometheus** | http://localhost:9090 | - |

---

## 📋 Requisitos Mínimos

| Componente | Linux | Windows | macOS |
|------------|-------|---------|-------|
| **CPU** | 4 cores | 4 cores | 4 cores |
| **RAM** | 8 GB | 8 GB | 8 GB |
| **Disco** | 50 GB | 50 GB | 50 GB |
| **OS** | Ubuntu 20.04+<br>Debian 11+<br>CentOS 8+ | Windows 10 (19041+)<br>Windows 11 | macOS 11+ |
| **Docker** | 24.0+ | Docker Desktop | Docker Desktop |
| **Extras** | - | WSL2 | - |

---

## 🔧 Comandos Útiles

### Linux / macOS / Windows (WSL2)

```bash
make help          # Ver todos los comandos
make up            # Iniciar servicios
make down          # Detener servicios
make restart       # Reiniciar servicios
make logs          # Ver logs
make health        # Verificar salud
docker-compose ps  # Ver estado
```

### Windows (PowerShell)

```powershell
# Acceder a WSL2
wsl

# Comandos directos desde PowerShell
wsl bash -c 'cd ~/sentinel && make logs'
wsl bash -c 'cd ~/sentinel && make health'
wsl bash -c 'cd ~/sentinel && docker-compose ps'
```

---

## 🆘 Solución de Problemas

### Linux
Ver [INSTALLATION_GUIDE.md - Solución de Problemas](INSTALLATION_GUIDE.md#-solución-de-problemas)

### Windows
Ver [INSTALLATION_GUIDE_WINDOWS.md - Solución de Problemas](INSTALLATION_GUIDE_WINDOWS.md#-solución-de-problemas)

### Problemas Comunes

**Puertos en uso**:
```bash
# Linux/macOS
sudo lsof -i :8000
sudo kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Docker no inicia**:
```bash
# Linux
sudo systemctl restart docker

# Windows
# Reiniciar Docker Desktop desde el icono en la bandeja
```

**Permisos**:
```bash
# Linux/WSL2
sudo chown -R $USER:$USER .
chmod +x *.sh
```

---

## 📊 Arquitectura Desplegada

Sentinel despliega **18 servicios** en contenedores Docker:

### Core Services
- **Frontend** (Next.js) - Puerto 3000
- **Backend** (FastAPI) - Puerto 8000
- **PostgreSQL** - Puerto 5432
- **Redis** - Puerto 6379
- **Nginx** - Puertos 80, 443

### Observability Stack
- **Prometheus** - Puerto 9090
- **Grafana** - Puerto 3001
- **Loki** - Puerto 3100
- **Promtail** - Puerto 9080

### Exporters
- **Node Exporter** - Puerto 9100
- **PostgreSQL Exporter** - Puerto 9187
- **Redis Exporter** - Puerto 9121

### Automation & AI
- **n8n** - Puerto 5678
- **Ollama** - Puerto 11434

### Workers
- **Celery Worker**
- **Celery Beat**
- **Ollama Init** (one-time)
- **n8n Loader** (one-time)

---

---

## 📞 Soporte

**Documentación**:
- [README.md](README.md) - Descripción general
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura técnica
- [docs/](docs/) - Documentación completa

**Comunidad**:
- **Issues**: https://github.com/jenovoas/sentinel/issues
- **Discussions**: https://github.com/jenovoas/sentinel/discussions
- **Email**: support@sentinel.dev

---

## 📝 Notas de Versión

### v1.0.0 - Instalación Multi-Plataforma

**Nuevas Características**:
- ✅ Instalador automatizado para Linux (`install.sh`)
- ✅ Instalador automatizado para Windows (`install-windows.ps1`)
- ✅ Guías completas de instalación
- ✅ Soporte para Ubuntu, Debian, CentOS, RHEL
- ✅ Soporte para Windows 10/11 con WSL2
- ✅ Verificación automática de requisitos
- ✅ Configuración interactiva
- ✅ Troubleshooting detallado

**Plataformas Soportadas**:
- Linux: Ubuntu 20.04+, Debian 11+, CentOS 8+, RHEL 8+
- Windows: Windows 10 (build 19041+), Windows 11
- macOS: macOS 11+ (manual con Docker Desktop)

---

**¡Disfruta Sentinel!** 

*Última actualización: Diciembre 2024*
