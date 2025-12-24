# ============================================================================
# Sentinel - Script de Instalación para Windows
# ============================================================================
# Este script automatiza la instalación de Sentinel en Windows con WSL2
# Uso: Ejecutar en PowerShell como Administrador
#      .\install-windows.ps1
# ============================================================================

#Requires -RunAsAdministrator

# Configuración de colores
$Host.UI.RawUI.ForegroundColor = "White"

function Write-Header {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "========================================`n" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

# Banner
Clear-Host
Write-Host @"
   _____ ______ _   _ _______ _____ _   _ ______ _      
  / ____|  ____| \ | |__   __|_   _| \ | |  ____| |     
 | (___ | |__  |  \| |  | |    | | |  \| | |__  | |     
  \___ \|  __| | . ` |  | |    | | | . ` |  __| | |     
  ____) | |____| |\  |  | |   _| |_| |\  | |____| |____ 
 |_____/|______|_| \_|  |_|  |_____|_| \_|______|______|
                                                         
 Enterprise Observability & Security Platform
 Instalación Automatizada para Windows v1.0
"@ -ForegroundColor Cyan

Write-Host ""
Write-Info "Iniciando instalación de Sentinel para Windows..."
Start-Sleep -Seconds 2

# ============================================================================
# PASO 1: Verificar Requisitos del Sistema
# ============================================================================

Write-Header "PASO 1/6: Verificando Requisitos del Sistema"

# Verificar versión de Windows
$osInfo = Get-CimInstance Win32_OperatingSystem
$buildNumber = [int]$osInfo.BuildNumber

Write-Info "Sistema: $($osInfo.Caption)"
Write-Info "Build: $buildNumber"

if ($buildNumber -lt 19041) {
    Write-Error-Custom "Windows build $buildNumber no soporta WSL2"
    Write-Warning-Custom "Se requiere Windows 10 build 19041+ o Windows 11"
    Write-Info "Actualiza Windows desde Settings > Update & Security"
    exit 1
}
Write-Success "Versión de Windows compatible"

# Verificar RAM
$totalRAM = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
if ($totalRAM -lt 8) {
    Write-Warning-Custom "RAM detectada: ${totalRAM}GB. Recomendado: 8GB+"
} else {
    Write-Success "RAM: ${totalRAM}GB"
}

# Verificar espacio en disco
$disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
$freeSpaceGB = [math]::Round($disk.FreeSpace / 1GB, 2)
if ($freeSpaceGB -lt 50) {
    Write-Warning-Custom "Espacio libre: ${freeSpaceGB}GB. Recomendado: 50GB+"
} else {
    Write-Success "Espacio en disco: ${freeSpaceGB}GB libre"
}

# Verificar virtualización
$hyperV = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All
if ($hyperV.State -eq "Enabled") {
    Write-Success "Virtualización: Hyper-V habilitado"
} else {
    Write-Info "Hyper-V no está habilitado (se habilitará con WSL2)"
}

# ============================================================================
# PASO 2: Instalar WSL2
# ============================================================================

Write-Header "PASO 2/6: Instalando WSL2"

# Verificar si WSL ya está instalado
$wslInstalled = $false
try {
    $wslVersion = wsl --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $wslInstalled = $true
        Write-Success "WSL ya está instalado"
    }
} catch {
    Write-Info "WSL no está instalado"
}

if (-not $wslInstalled) {
    Write-Info "Instalando WSL2..."
    
    # Habilitar WSL
    Write-Info "Habilitando Windows Subsystem for Linux..."
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart | Out-Null
    
    # Habilitar Virtual Machine Platform
    Write-Info "Habilitando Virtual Machine Platform..."
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart | Out-Null
    
    Write-Success "Características de WSL habilitadas"
    Write-Warning-Custom "Se requiere reiniciar Windows"
    
    $restart = Read-Host "¿Deseas reiniciar ahora? (S/N)"
    if ($restart -eq "S" -or $restart -eq "s") {
        Write-Info "Reiniciando en 10 segundos..."
        Write-Warning-Custom "Ejecuta este script nuevamente después del reinicio"
        Start-Sleep -Seconds 10
        Restart-Computer
        exit 0
    } else {
        Write-Warning-Custom "Debes reiniciar manualmente y ejecutar este script nuevamente"
        exit 0
    }
}

# Establecer WSL2 como versión por defecto
Write-Info "Configurando WSL2 como versión por defecto..."
wsl --set-default-version 2 | Out-Null

# Verificar si Ubuntu está instalado
$ubuntuInstalled = $false
try {
    $wslList = wsl --list --quiet
    if ($wslList -match "Ubuntu") {
        $ubuntuInstalled = $true
        Write-Success "Ubuntu ya está instalado en WSL2"
    }
} catch {
    Write-Info "Ubuntu no está instalado"
}

if (-not $ubuntuInstalled) {
    Write-Info "Instalando Ubuntu 22.04..."
    Write-Warning-Custom "Esto puede tardar varios minutos..."
    
    wsl --install -d Ubuntu-22.04
    
    Write-Success "Ubuntu instalado"
    Write-Info "Configura tu usuario y contraseña en la ventana de Ubuntu que se abrió"
    Write-Warning-Custom "Presiona Enter cuando hayas terminado de configurar Ubuntu..."
    Read-Host
}

# ============================================================================
# PASO 3: Instalar Docker Desktop
# ============================================================================

Write-Header "PASO 3/6: Verificando Docker Desktop"

# Verificar si Docker Desktop está instalado
$dockerInstalled = $false
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerInstalled = $true
        Write-Success "Docker Desktop ya está instalado: $dockerVersion"
    }
} catch {
    Write-Info "Docker Desktop no está instalado"
}

if (-not $dockerInstalled) {
    Write-Warning-Custom "Docker Desktop no está instalado"
    Write-Info "Descarga e instala Docker Desktop desde:"
    Write-Host "https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    Write-Info ""
    Write-Info "Instrucciones:"
    Write-Info "1. Descarga Docker Desktop for Windows"
    Write-Info "2. Ejecuta el instalador"
    Write-Info "3. Marca: 'Use WSL 2 instead of Hyper-V'"
    Write-Info "4. Reinicia Windows si se solicita"
    Write-Info "5. Abre Docker Desktop y espera a que inicie"
    Write-Info "6. Ejecuta este script nuevamente"
    Write-Info ""
    
    $openBrowser = Read-Host "¿Deseas abrir el navegador para descargar? (S/N)"
    if ($openBrowser -eq "S" -or $openBrowser -eq "s") {
        Start-Process "https://www.docker.com/products/docker-desktop/"
    }
    
    exit 0
}

# Verificar que Docker está corriendo
Write-Info "Verificando que Docker está corriendo..."
try {
    docker ps | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker está corriendo"
    } else {
        Write-Warning-Custom "Docker no está corriendo. Abre Docker Desktop y espera a que inicie"
        exit 1
    }
} catch {
    Write-Error-Custom "Error al conectar con Docker"
    Write-Info "Asegúrate de que Docker Desktop está corriendo"
    exit 1
}

# Verificar Docker Compose
try {
    $composeVersion = docker-compose --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker Compose instalado: $composeVersion"
    }
} catch {
    Write-Error-Custom "Docker Compose no está disponible"
    exit 1
}

# ============================================================================
# PASO 4: Instalar Git para Windows
# ============================================================================

Write-Header "PASO 4/6: Verificando Git"

$gitInstalled = $false
try {
    $gitVersion = git --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $gitInstalled = $true
        Write-Success "Git ya está instalado: $gitVersion"
    }
} catch {
    Write-Info "Git no está instalado"
}

if (-not $gitInstalled) {
    Write-Warning-Custom "Git no está instalado"
    Write-Info "Descarga e instala Git desde:"
    Write-Host "https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Info ""
    
    $openBrowser = Read-Host "¿Deseas abrir el navegador para descargar? (S/N)"
    if ($openBrowser -eq "S" -or $openBrowser -eq "s") {
        Start-Process "https://git-scm.com/download/win"
    }
    
    Write-Info "Instala Git y ejecuta este script nuevamente"
    exit 0
}

# ============================================================================
# PASO 5: Clonar Sentinel en WSL2
# ============================================================================

Write-Header "PASO 5/6: Configurando Sentinel en WSL2"

Write-Info "Ejecutando instalación en WSL2 (Ubuntu)..."

# Crear script de instalación para WSL2
$wslScript = @'
#!/bin/bash
set -e

echo "🔧 Configurando Sentinel en WSL2..."

# Actualizar sistema
echo "📦 Actualizando sistema..."
sudo apt update -qq > /dev/null 2>&1
sudo apt install -y curl git jq > /dev/null 2>&1

# Clonar repositorio si no existe
if [ ! -d "$HOME/sentinel" ]; then
    echo "📥 Clonando repositorio Sentinel..."
    cd ~
    git clone https://github.com/jaime-novoa/sentinel.git
    cd sentinel
else
    echo "✓ Repositorio ya existe"
    cd ~/sentinel
    git pull origin main
fi

# Dar permisos al instalador
chmod +x install.sh

echo "✓ Sentinel configurado en WSL2"
echo "📍 Ubicación: ~/sentinel"
'@

# Guardar script temporal
$tempScript = [System.IO.Path]::GetTempFileName()
$wslScript | Out-File -FilePath $tempScript -Encoding UTF8

# Ejecutar en WSL2
try {
    wsl bash $tempScript
    Write-Success "Sentinel configurado en WSL2"
} catch {
    Write-Error-Custom "Error al configurar Sentinel en WSL2"
    exit 1
} finally {
    Remove-Item $tempScript -ErrorAction SilentlyContinue
}

# ============================================================================
# PASO 6: Ejecutar Instalador en WSL2
# ============================================================================

Write-Header "PASO 6/6: Instalando Sentinel"

Write-Info "Ejecutando instalador automático en WSL2..."
Write-Warning-Custom "Esto puede tardar 10-15 minutos..."

# Ejecutar instalador
try {
    wsl bash -c "cd ~/sentinel && ./install.sh"
    Write-Success "Instalación completada"
} catch {
    Write-Error-Custom "Error durante la instalación"
    Write-Info "Revisa los logs en WSL2: wsl bash -c 'cd ~/sentinel && docker-compose logs'"
    exit 1
}

# ============================================================================
# Verificación Final
# ============================================================================

Write-Header "Verificación Final"

Write-Info "Esperando a que los servicios estén listos (30 segundos)..."
Start-Sleep -Seconds 30

# Verificar servicios
$servicesOK = 0
$servicesTotal = 0

# Backend
$servicesTotal++
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Success "Backend API: OK"
        $servicesOK++
    }
} catch {
    Write-Error-Custom "Backend API: FAIL"
}

# Frontend
$servicesTotal++
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Success "Frontend: OK"
        $servicesOK++
    }
} catch {
    Write-Error-Custom "Frontend: FAIL"
}

# Grafana
$servicesTotal++
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3001" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Success "Grafana: OK"
        $servicesOK++
    }
} catch {
    Write-Error-Custom "Grafana: FAIL"
}

# n8n
$servicesTotal++
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5678" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Success "n8n: OK"
        $servicesOK++
    }
} catch {
    Write-Error-Custom "n8n: FAIL"
}

# ============================================================================
# Resumen Final
# ============================================================================

Write-Header "Instalación Completada"

Write-Host "✓ Servicios funcionando: $servicesOK/$servicesTotal" -ForegroundColor Green
Write-Host ""

if ($servicesOK -ge 3) {
    Write-Success "¡Instalación exitosa! 🎉"
    Write-Host ""
    Write-Host "Accede a los servicios:" -ForegroundColor Blue
    Write-Host ""
    Write-Host "  📊 Dashboard:        " -NoNewline -ForegroundColor White
    Write-Host "http://localhost:3000" -ForegroundColor Green
    Write-Host "  🔧 API Backend:      " -NoNewline -ForegroundColor White
    Write-Host "http://localhost:8000" -ForegroundColor Green
    Write-Host "  📚 API Docs:         " -NoNewline -ForegroundColor White
    Write-Host "http://localhost:8000/docs" -ForegroundColor Green
    Write-Host "  📈 Grafana:          " -NoNewline -ForegroundColor White
    Write-Host "http://localhost:3001" -ForegroundColor Green
    Write-Host "  🔄 n8n Workflows:    " -NoNewline -ForegroundColor White
    Write-Host "http://localhost:5678" -ForegroundColor Green
    Write-Host ""
    
    Write-Info "Comandos útiles en WSL2:"
    Write-Host ""
    Write-Host "  wsl                           - Abrir terminal WSL2"
    Write-Host "  wsl bash -c 'cd ~/sentinel && make logs'    - Ver logs"
    Write-Host "  wsl bash -c 'cd ~/sentinel && make health'  - Verificar salud"
    Write-Host "  wsl bash -c 'cd ~/sentinel && make restart' - Reiniciar"
    Write-Host ""
    
    Write-Warning-Custom "Próximos pasos:"
    Write-Host ""
    Write-Host "  1. Abre http://localhost:3000 en tu navegador"
    Write-Host "  2. Configura tu primera organización"
    Write-Host "  3. Explora Grafana en http://localhost:3001"
    Write-Host "  4. Lee la documentación: INSTALLATION_GUIDE_WINDOWS.md"
    Write-Host ""
    
    # Abrir navegador automáticamente
    $openBrowser = Read-Host "¿Deseas abrir el dashboard en el navegador? (S/N)"
    if ($openBrowser -eq "S" -or $openBrowser -eq "s") {
        Start-Process "http://localhost:3000"
    }
    
} else {
    Write-Warning-Custom "Instalación completada con advertencias"
    Write-Host ""
    Write-Info "Algunos servicios no respondieron. Verifica con:"
    Write-Host "  wsl bash -c 'cd ~/sentinel && docker-compose ps'"
    Write-Host "  wsl bash -c 'cd ~/sentinel && docker-compose logs -f'"
    Write-Host ""
}

# Guardar información de instalación
$installInfo = @"
Sentinel - Información de Instalación (Windows)
================================================

Fecha de instalación: $(Get-Date)
Sistema operativo: $($osInfo.Caption)
Build: $buildNumber
RAM: ${totalRAM}GB
Espacio libre: ${freeSpaceGB}GB

Versiones:
- WSL2: $(wsl --version 2>&1 | Select-String "WSL version")
- Docker: $(docker --version)
- Docker Compose: $(docker-compose --version)
- Git: $(git --version)

Ubicación en WSL2:
- Repositorio: ~/sentinel
- Acceso desde Windows: \\wsl$\Ubuntu-22.04\home\<usuario>\sentinel

URLs:
- Dashboard: http://localhost:3000
- API: http://localhost:8000
- Grafana: http://localhost:3001
- n8n: http://localhost:5678
- Prometheus: http://localhost:9090

Servicios verificados: $servicesOK/$servicesTotal

Comandos útiles:
- wsl                                          - Abrir WSL2
- wsl bash -c 'cd ~/sentinel && make help'    - Ver comandos
- wsl bash -c 'cd ~/sentinel && make logs'    - Ver logs
- wsl bash -c 'cd ~/sentinel && make restart' - Reiniciar
"@

$installInfo | Out-File -FilePath "INSTALLATION_INFO_WINDOWS.txt" -Encoding UTF8
Write-Success "Información guardada en INSTALLATION_INFO_WINDOWS.txt"

Write-Host ""
Write-Info "Para acceder a WSL2: wsl"
Write-Info "Para ver logs: wsl bash -c 'cd ~/sentinel && make logs'"
Write-Info "Para detener: wsl bash -c 'cd ~/sentinel && docker-compose down'"
Write-Host ""

exit 0
