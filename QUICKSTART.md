# 🚀 Sentinel - Quick Start

**Instala Sentinel en 5 minutos**

---

## 🐧 Linux

### Opción 1: Instalación Automática (Recomendado)

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/sentinel.git
cd sentinel

# Ejecutar instalador automático
chmod +x install.sh
./install.sh
```

El script automáticamente:
- ✅ Verifica requisitos del sistema
- ✅ Instala Docker y Docker Compose
- ✅ Configura variables de entorno
- ✅ Construye e inicia todos los servicios
- ✅ Verifica que todo funcione correctamente

---

### Opción 2: Instalación Manual

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/sentinel.git
cd sentinel

# 2. Copiar configuración
cp .env.example .env

# 3. Editar .env y cambiar contraseñas
nano .env

# 4. Iniciar servicios
docker-compose up -d

# 5. Verificar instalación
make health
```

---

## 🪟 Windows

### Opción 1: Instalación Automática con WSL2 (Recomendado)

```powershell
# 1. Abrir PowerShell como Administrador
# Clic derecho en Inicio > Windows PowerShell (Administrador)

# 2. Descargar e ejecutar instalador
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/jenovoas/sentinel/main/install-windows.ps1" -OutFile "install-windows.ps1"
.\install-windows.ps1
```

El script automáticamente:
- ✅ Verifica requisitos de Windows
- ✅ Instala WSL2 y Ubuntu
- ✅ Guía instalación de Docker Desktop
- ✅ Clona y configura Sentinel
- ✅ Inicia todos los servicios

### Opción 2: Instalación Manual

```powershell
# 1. Instalar WSL2
wsl --install -d Ubuntu-22.04

# 2. Instalar Docker Desktop
# Descargar desde: https://www.docker.com/products/docker-desktop/
# Marcar: "Use WSL 2 instead of Hyper-V"

# 3. Abrir Ubuntu (WSL2)
wsl

# 4. Dentro de WSL2
cd ~
git clone https://github.com/jenovoas/sentinel.git
cd sentinel
chmod +x install.sh
./install.sh
```

**📚 Guía Completa**: [INSTALLATION_GUIDE_WINDOWS.md](INSTALLATION_GUIDE_WINDOWS.md)

---

## Acceso a Servicios

Una vez instalado:

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Dashboard** | http://localhost:3000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Grafana** | http://localhost:3001 | admin / (ver .env) |
| **n8n** | http://localhost:5678 | admin / (ver .env) |

### AI (Local LLM)

- Ollama API: `http://localhost:11434` (models are downloaded automatically by `ollama-init` when using the `ai` profile)
- Start CPU-only AI services:

```bash
# Recommended: use the helper scripts
./scripts/start-cpu-ollama.sh
# Or (Windows PowerShell)
./scripts/start-cpu-ollama.ps1
```

---

## Requisitos Mínimos

- **OS**: Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disco**: 50 GB
- **Docker**: 24.0+
- **Docker Compose**: 2.20+

---

## Comandos Útiles

```bash
make help          # Ver todos los comandos
make logs          # Ver logs
make restart       # Reiniciar servicios
make health        # Verificar salud
docker-compose ps  # Ver estado
```

---

## Documentación Completa

📚 **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Guía completa de instalación

Incluye:
- Instalación detallada paso a paso
- Configuración avanzada (HA, SSL, backups)
- Solución de problemas
- Optimización de recursos

---

## Soporte

- **Issues**: https://github.com/tu-usuario/sentinel/issues
- **Documentación**: Ver carpeta `docs/`
- **Email**: support@sentinel.dev

---

**¡Disfruta Sentinel!** 🛡️
