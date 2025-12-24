# 🪟 Sentinel - Guía de Instalación para Windows

**Guía paso a paso para instalar Sentinel en Windows 10/11**

---

## 📋 Tabla de Contenidos

1. [Requisitos del Sistema](#-requisitos-del-sistema)
2. [Opción 1: WSL2 + Docker Desktop (Recomendado)](#-opción-1-wsl2--docker-desktop-recomendado)
3. [Opción 2: Docker Desktop sin WSL2](#-opción-2-docker-desktop-sin-wsl2)
4. [Verificación de la Instalación](#-verificación-de-la-instalación)
5. [Acceso a los Servicios](#-acceso-a-los-servicios)
6. [Solución de Problemas](#-solución-de-problemas)

---

## 📦 Requisitos del Sistema

### Requisitos Mínimos

| Componente | Requisito |
|------------|-----------|
| **Sistema Operativo** | Windows 10 (build 19041+) o Windows 11 |
| **CPU** | 4 cores con virtualización habilitada |
| **RAM** | 8 GB (16 GB recomendado) |
| **Disco** | 50 GB libres en SSD |
| **Virtualización** | Intel VT-x o AMD-V habilitado en BIOS |

### Software Requerido

- **Windows 10/11** (64-bit)
- **WSL2** (Windows Subsystem for Linux 2)
- **Docker Desktop** para Windows
- **Git** para Windows

---

## 🚀 Opción 1: WSL2 + Docker Desktop (Recomendado)

Esta es la opción **recomendada** porque ofrece mejor rendimiento y compatibilidad completa con Linux.

### Paso 1: Habilitar WSL2

#### 1.1 Abrir PowerShell como Administrador

```powershell
# Clic derecho en el menú Inicio > Windows PowerShell (Administrador)
```

#### 1.2 Habilitar WSL y Virtualización

```powershell
# Habilitar WSL
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Habilitar Virtual Machine Platform
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Reiniciar Windows
Restart-Computer
```

#### 1.3 Instalar WSL2 (después del reinicio)

```powershell
# Abrir PowerShell como Administrador nuevamente

# Establecer WSL2 como versión por defecto
wsl --set-default-version 2

# Instalar Ubuntu (recomendado)
wsl --install -d Ubuntu-22.04

# O listar distribuciones disponibles
wsl --list --online
```

#### 1.4 Configurar Ubuntu

```bash
# WSL abrirá Ubuntu automáticamente
# Crear usuario y contraseña cuando se solicite

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y curl git jq
```

### Paso 2: Instalar Docker Desktop

#### 2.1 Descargar Docker Desktop

1. Ir a: https://www.docker.com/products/docker-desktop/
2. Descargar **Docker Desktop for Windows**
3. Ejecutar el instalador `Docker Desktop Installer.exe`

#### 2.2 Configurar Docker Desktop

1. Durante la instalación, **marcar**:
   - ✅ Use WSL 2 instead of Hyper-V
   - ✅ Add shortcut to desktop

2. Después de instalar, **reiniciar Windows**

3. Abrir **Docker Desktop**

4. Ir a **Settings** (⚙️) > **General**:
   - ✅ Use the WSL 2 based engine
   - ✅ Start Docker Desktop when you log in

5. Ir a **Settings** > **Resources** > **WSL Integration**:
   - ✅ Enable integration with my default WSL distro
   - ✅ Ubuntu-22.04 (activar)

6. Clic en **Apply & Restart**

#### 2.3 Verificar Instalación de Docker

```powershell
# En PowerShell o CMD
docker --version
docker-compose --version

# Debería mostrar:
# Docker version 24.x.x
# Docker Compose version v2.x.x
```

### Paso 3: Instalar Sentinel en WSL2

#### 3.1 Abrir Terminal de Ubuntu (WSL2)

```powershell
# En PowerShell o desde el menú Inicio, buscar "Ubuntu"
wsl
```

#### 3.2 Clonar Repositorio

```bash
# Dentro de WSL2 (Ubuntu)
cd ~
git clone https://github.com/jaime-novoa/sentinel.git
cd sentinel
```

#### 3.3 Ejecutar Instalador Automático

```bash
# Dar permisos de ejecución
chmod +x install.sh

# Ejecutar instalador
./install.sh
```

El script automáticamente:
- ✅ Verifica requisitos
- ✅ Configura variables de entorno
- ✅ Construye imágenes Docker
- ✅ Inicia todos los servicios
- ✅ Verifica instalación

**Tiempo estimado**: 10-15 minutos

### Paso 4: Acceder desde Windows

Una vez instalado, puedes acceder a Sentinel desde tu navegador en Windows:

- **Dashboard**: http://localhost:3000
- **API**: http://localhost:8000
- **Grafana**: http://localhost:3001
- **n8n**: http://localhost:5678

---

## 🐳 Opción 2: Docker Desktop sin WSL2

Si no puedes usar WSL2, puedes instalar Docker Desktop con Hyper-V (menos recomendado).

### Paso 1: Habilitar Hyper-V

#### 1.1 Verificar Requisitos

- Windows 10 Pro, Enterprise o Education (no funciona en Home)
- Virtualización habilitada en BIOS

#### 1.2 Habilitar Hyper-V

```powershell
# PowerShell como Administrador
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

# Reiniciar
Restart-Computer
```

### Paso 2: Instalar Docker Desktop

1. Descargar: https://www.docker.com/products/docker-desktop/
2. Ejecutar instalador
3. Durante instalación, **desmarcar** "Use WSL 2"
4. Reiniciar Windows

### Paso 3: Instalar Git para Windows

1. Descargar: https://git-scm.com/download/win
2. Instalar con opciones por defecto
3. Abrir **Git Bash**

### Paso 4: Instalar Sentinel

```bash
# En Git Bash
cd ~
git clone https://github.com/jaime-novoa/sentinel.git
cd sentinel

# Copiar configuración
cp .env.example .env

# Editar .env (usar notepad o tu editor favorito)
notepad .env

# Iniciar servicios
docker-compose up -d

# Verificar
docker-compose ps
```

---

## ✅ Verificación de la Instalación

### Verificación Automática

```bash
# En WSL2 (Ubuntu) o Git Bash
cd ~/sentinel

# Verificar servicios
docker-compose ps

# Verificar salud
curl http://localhost:8000/api/v1/health
```

### Verificación desde Windows

1. **Abrir navegador** (Chrome, Edge, Firefox)

2. **Verificar servicios**:
   - Dashboard: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - Grafana: http://localhost:3001

3. **Verificar Docker Desktop**:
   - Abrir Docker Desktop
   - Ver **Containers** tab
   - Deberías ver ~18 contenedores corriendo

### Verificación Manual

```bash
# En WSL2 o Git Bash
cd ~/sentinel

# Ver logs
docker-compose logs -f

# Ver estado de contenedores
docker-compose ps

# Verificar PostgreSQL
docker-compose exec postgres pg_isready -U sentinel_user

# Verificar Redis
docker-compose exec redis redis-cli ping

# Verificar API
curl http://localhost:8000/api/v1/health | jq .
```

---

## 🌐 Acceso a los Servicios

### URLs de Acceso (desde Windows)

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Dashboard Principal** | http://localhost:3000 | - |
| **API Backend** | http://localhost:8000 | - |
| **API Docs (Swagger)** | http://localhost:8000/docs | - |
| **Grafana** | http://localhost:3001 | admin / (ver .env) |
| **Prometheus** | http://localhost:9090 | - |
| **n8n Workflows** | http://localhost:5678 | admin / (ver .env) |
| **Loki** | http://localhost:3100 | - |

### Acceder a Archivos desde Windows

#### Con WSL2:

Los archivos de WSL2 están accesibles desde Windows:

```
\\wsl$\Ubuntu-22.04\home\<tu-usuario>\sentinel
```

También puedes abrir en VS Code:

```bash
# Dentro de WSL2
cd ~/sentinel
code .
```

#### Con Git Bash:

Los archivos están en tu carpeta de usuario:

```
C:\Users\<tu-usuario>\sentinel
```

---

## 🔧 Solución de Problemas

### Problema: WSL2 no instala

**Síntoma**: Error al ejecutar `wsl --install`

**Solución**:

```powershell
# Verificar versión de Windows
winver
# Debe ser build 19041 o superior

# Actualizar Windows
# Settings > Update & Security > Windows Update

# Habilitar virtualización en BIOS
# Reiniciar > F2/DEL > Advanced > Virtualization > Enabled
```

### Problema: Docker Desktop no inicia

**Síntoma**: "Docker Desktop starting..." infinito

**Solución**:

1. **Verificar Hyper-V/WSL2**:
   ```powershell
   # PowerShell como Administrador
   Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V
   # o
   wsl --status
   ```

2. **Reiniciar servicios**:
   ```powershell
   # PowerShell como Administrador
   Restart-Service docker
   ```

3. **Reinstalar Docker Desktop**:
   - Desinstalar completamente
   - Eliminar: `C:\ProgramData\Docker`
   - Eliminar: `C:\Users\<usuario>\.docker`
   - Reinstalar

### Problema: Puertos ya en uso

**Síntoma**: `Error: bind: address already in use`

**Solución**:

```powershell
# PowerShell como Administrador
# Ver qué proceso usa el puerto (ejemplo: 8000)
netstat -ano | findstr :8000

# Matar proceso
taskkill /PID <PID> /F

# O cambiar puerto en docker-compose.yml
```

### Problema: Lentitud en WSL2

**Síntoma**: Servicios muy lentos

**Solución**:

1. **Limitar memoria de WSL2**:

   Crear archivo: `C:\Users\<usuario>\.wslconfig`

   ```ini
   [wsl2]
   memory=8GB
   processors=4
   swap=2GB
   ```

2. **Reiniciar WSL2**:
   ```powershell
   wsl --shutdown
   wsl
   ```

### Problema: No se puede acceder a localhost

**Síntoma**: http://localhost:3000 no carga

**Solución**:

1. **Verificar que Docker Desktop está corriendo**

2. **Verificar firewall**:
   ```powershell
   # PowerShell como Administrador
   New-NetFirewallRule -DisplayName "Sentinel" -Direction Inbound -LocalPort 3000,8000,3001,5678 -Protocol TCP -Action Allow
   ```

3. **Usar IP de WSL2**:
   ```bash
   # En WSL2
   ip addr show eth0 | grep inet
   # Usar esa IP: http://<IP>:3000
   ```

### Problema: Ollama no descarga modelos

**Síntoma**: `ollama-init` falla

**Solución**:

```bash
# En WSL2
cd ~/sentinel

# Verificar espacio en disco
df -h

# Descargar modelo manualmente
docker-compose exec ollama ollama pull phi3:mini

# Si falla, usar modelo más pequeño
# Editar .env: OLLAMA_MODEL=llama3.2:1b
docker-compose up -d ollama-init
```

### Problema: Permisos en WSL2

**Síntoma**: Permission denied

**Solución**:

```bash
# En WSL2
cd ~/sentinel

# Arreglar permisos
sudo chown -R $USER:$USER .

# Dar permisos a scripts
chmod +x install.sh
chmod +x *.sh
```

### Problema: Docker no encuentra archivos

**Síntoma**: `Error: file not found`

**Solución**:

```bash
# NO clonar en /mnt/c/ (unidad de Windows)
# Clonar en home de WSL2

# Correcto:
cd ~
git clone https://github.com/jaime-novoa/sentinel.git

# Incorrecto:
cd /mnt/c/Users/...
```

---

## 💡 Consejos para Windows

### 1. Usar Windows Terminal

Mejor experiencia que CMD o PowerShell:

1. Instalar desde Microsoft Store: **Windows Terminal**
2. Configurar Ubuntu como perfil por defecto
3. Usar atajos: `Ctrl+Shift+T` (nueva pestaña)

### 2. Usar VS Code con WSL2

```bash
# En WSL2
cd ~/sentinel
code .
```

VS Code se abrirá con extensión WSL automáticamente.

### 3. Comandos Útiles de WSL2

```powershell
# PowerShell

# Ver distribuciones instaladas
wsl --list --verbose

# Establecer distribución por defecto
wsl --set-default Ubuntu-22.04

# Apagar WSL2
wsl --shutdown

# Exportar/Importar WSL2
wsl --export Ubuntu-22.04 D:\backup-wsl.tar
wsl --import Ubuntu-22.04 D:\WSL D:\backup-wsl.tar
```

### 4. Acceso Rápido

Crear accesos directos en el escritorio:

- **Dashboard**: http://localhost:3000
- **Grafana**: http://localhost:3001
- **API Docs**: http://localhost:8000/docs

### 5. Rendimiento

Para mejor rendimiento:

1. **Usar SSD** para WSL2
2. **Asignar suficiente RAM** en `.wslconfig`
3. **Cerrar aplicaciones** innecesarias
4. **Deshabilitar antivirus** para carpeta de WSL2 (opcional)

---

## 📚 Recursos Adicionales

### Documentación Oficial

- [WSL2 Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/)
- [Sentinel Documentation](README.md)

### Tutoriales en Video

- [Instalar WSL2 en Windows](https://www.youtube.com/results?search_query=install+wsl2+windows)
- [Docker Desktop en Windows](https://www.youtube.com/results?search_query=docker+desktop+windows)

### Comandos Útiles

```bash
# En WSL2 (Ubuntu)
make help              # Ver comandos disponibles
make up                # Iniciar servicios
make down              # Detener servicios
make restart           # Reiniciar servicios
make logs              # Ver logs
make health            # Verificar salud
docker-compose ps      # Ver estado
```

---

## 🎉 ¡Instalación Completada!

Si llegaste hasta aquí, **¡felicitaciones!** 🎊

Sentinel está instalado y corriendo en tu Windows. Ahora puedes:

1. ✅ Acceder al dashboard: http://localhost:3000
2. ✅ Ver métricas en Grafana: http://localhost:3001
3. ✅ Explorar la API: http://localhost:8000/docs
4. ✅ Crear workflows en n8n: http://localhost:5678

---

## 🆘 Soporte

**¿Problemas?**

1. Consulta [Solución de Problemas](#-solución-de-problemas)
2. Revisa [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) (Linux)
3. Abre un issue: https://github.com/jaime-novoa/sentinel/issues

**Comunidad**:
- Discord: (próximamente)
- Email: support@sentinel.dev

---

**¡Disfruta Sentinel en Windows!** 🪟🛡️
