#!/bin/bash

# ============================================================================
# Sentinel - Script de Instalación Automatizada
# ============================================================================
# Este script automatiza la instalación completa de Sentinel
# Uso: ./install.sh
# ============================================================================

set -e  # Salir si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Banner
clear
cat << "EOF"
   _____ ______ _   _ _______ _____ _   _ ______ _      
  / ____|  ____| \ | |__   __|_   _| \ | |  ____| |     
 | (___ | |__  |  \| |  | |    | | |  \| | |__  | |     
  \___ \|  __| | . ` |  | |    | | | . ` |  __| | |     
  ____) | |____| |\  |  | |   _| |_| |\  | |____| |____ 
 |_____/|______|_| \_|  |_|  |_____|_| \_|______|______|
                                                         
 Enterprise Observability & Security Platform
 Instalación Automatizada v1.0
EOF

echo ""
print_info "Iniciando instalación de Sentinel..."
sleep 2

# ============================================================================
# PASO 1: Verificar Requisitos del Sistema
# ============================================================================

print_header "PASO 1/7: Verificando Requisitos del Sistema"

# Verificar sistema operativo
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "Este script solo funciona en Linux"
    exit 1
fi
print_success "Sistema operativo: Linux"

# Verificar arquitectura
ARCH=$(uname -m)
if [[ "$ARCH" != "x86_64" ]]; then
    print_warning "Arquitectura $ARCH detectada. Recomendado: x86_64"
else
    print_success "Arquitectura: $ARCH"
fi

# Verificar RAM
TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
if [ "$TOTAL_RAM" -lt 8 ]; then
    print_warning "RAM detectada: ${TOTAL_RAM}GB. Recomendado: 8GB+"
else
    print_success "RAM: ${TOTAL_RAM}GB"
fi

# Verificar espacio en disco
DISK_SPACE=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$DISK_SPACE" -lt 50 ]; then
    print_warning "Espacio libre: ${DISK_SPACE}GB. Recomendado: 50GB+"
else
    print_success "Espacio en disco: ${DISK_SPACE}GB libre"
fi

# ============================================================================
# PASO 2: Instalar Dependencias
# ============================================================================

print_header "PASO 2/7: Instalando Dependencias"

# Detectar distribución
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    print_error "No se pudo detectar la distribución de Linux"
    exit 1
fi

print_info "Distribución detectada: $OS $VER"

# Instalar dependencias básicas
print_info "Instalando curl, git, jq..."

if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
    sudo apt update -qq
    sudo apt install -y curl git jq > /dev/null 2>&1
elif [[ "$OS" == "centos" ]] || [[ "$OS" == "rhel" ]]; then
    sudo yum install -y curl git jq > /dev/null 2>&1
else
    print_warning "Distribución no reconocida. Instala manualmente: curl, git, jq"
fi

print_success "Dependencias básicas instaladas"

# ============================================================================
# PASO 3: Instalar Docker
# ============================================================================

print_header "PASO 3/7: Instalando Docker"

# Verificar si Docker ya está instalado
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//')
    print_success "Docker ya instalado: $DOCKER_VERSION"
else
    print_info "Instalando Docker..."
    
    # Instalar Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh > /dev/null 2>&1
    rm get-docker.sh
    
    # Agregar usuario al grupo docker
    sudo usermod -aG docker $USER
    
    print_success "Docker instalado correctamente"
    print_warning "IMPORTANTE: Debes cerrar sesión y volver a entrar para usar Docker sin sudo"
fi

# Verificar si Docker Compose está instalado
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | awk '{print $4}' | sed 's/,//')
    print_success "Docker Compose ya instalado: $COMPOSE_VERSION"
else
    print_info "Instalando Docker Compose..."
    
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose > /dev/null 2>&1
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_success "Docker Compose instalado correctamente"
fi

# Verificar que Docker está corriendo
if ! sudo systemctl is-active --quiet docker; then
    print_info "Iniciando Docker..."
    sudo systemctl start docker
    sudo systemctl enable docker
fi

print_success "Docker está corriendo"

# ============================================================================
# PASO 4: Configurar Variables de Entorno
# ============================================================================

print_header "PASO 4/7: Configurando Variables de Entorno"

if [ -f .env ]; then
    print_warning "Archivo .env ya existe"
    read -p "¿Deseas sobrescribirlo? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        print_info "Usando .env existente"
    else
        cp .env.example .env
        print_success "Archivo .env creado desde .env.example"
    fi
else
    cp .env.example .env
    print_success "Archivo .env creado desde .env.example"
fi

# Generar SECRET_KEY seguro
print_info "Generando SECRET_KEY seguro..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32)

# Actualizar SECRET_KEY en .env
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|g" .env
else
    # Linux
    sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|g" .env
fi

print_success "SECRET_KEY generado y configurado"

# Configuración interactiva (opcional)
print_info "Configuración de contraseñas (presiona Enter para usar valores por defecto)"
echo ""

read -p "PostgreSQL password [darkfenix]: " POSTGRES_PASS
POSTGRES_PASS=${POSTGRES_PASS:-darkfenix}

read -p "Grafana password [admin]: " GRAFANA_PASS
GRAFANA_PASS=${GRAFANA_PASS:-admin}

read -p "n8n password [darkfenix]: " N8N_PASS
N8N_PASS=${N8N_PASS:-darkfenix}

# Actualizar .env con contraseñas
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$POSTGRES_PASS|g" .env
    sed -i '' "s|GRAFANA_PASSWORD=.*|GRAFANA_PASSWORD=$GRAFANA_PASS|g" .env
    sed -i '' "s|N8N_PASSWORD=.*|N8N_PASSWORD=$N8N_PASS|g" .env
else
    sed -i "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$POSTGRES_PASS|g" .env
    sed -i "s|GRAFANA_PASSWORD=.*|GRAFANA_PASSWORD=$GRAFANA_PASS|g" .env
    sed -i "s|N8N_PASSWORD=.*|N8N_PASSWORD=$N8N_PASS|g" .env
fi

print_success "Contraseñas configuradas"

# ============================================================================
# PASO 5: Construir Imágenes Docker
# ============================================================================

print_header "PASO 5/7: Construyendo Imágenes Docker"

print_info "Esto puede tardar 5-10 minutos..."

if docker-compose build > /tmp/sentinel-build.log 2>&1; then
    print_success "Imágenes construidas correctamente"
else
    print_error "Error al construir imágenes. Ver /tmp/sentinel-build.log"
    exit 1
fi

# ============================================================================
# PASO 6: Iniciar Servicios
# ============================================================================

print_header "PASO 6/7: Iniciando Servicios"

print_info "Iniciando servicios en fases..."

# Fase 1: Infraestructura
print_info "Fase 1/5: Infraestructura (PostgreSQL, Redis)..."
docker-compose up -d postgres redis
sleep 10

# Fase 2: Backend
print_info "Fase 2/5: Backend y Workers..."
docker-compose up -d backend celery_worker celery_beat
sleep 15

# Fase 3: Frontend
print_info "Fase 3/5: Frontend y Proxy..."
docker-compose up -d frontend nginx
sleep 10

# Fase 4: Observabilidad
print_info "Fase 4/5: Stack de Observabilidad..."
docker-compose up -d prometheus loki grafana promtail \
    node-exporter postgres-exporter redis-exporter
sleep 10

# Fase 5: Automatización e IA
print_info "Fase 5/5: n8n y Ollama..."
docker-compose up -d n8n ollama

print_success "Todos los servicios iniciados"

# ============================================================================
# PASO 7: Verificar Instalación
# ============================================================================

print_header "PASO 7/7: Verificando Instalación"

print_info "Esperando a que los servicios estén listos (60 segundos)..."
sleep 60

# Verificar servicios
print_info "Verificando servicios..."

SERVICES_OK=0
SERVICES_TOTAL=0

# PostgreSQL
SERVICES_TOTAL=$((SERVICES_TOTAL + 1))
if docker-compose exec -T postgres pg_isready -U sentinel_user > /dev/null 2>&1; then
    print_success "PostgreSQL: OK"
    SERVICES_OK=$((SERVICES_OK + 1))
else
    print_error "PostgreSQL: FAIL"
fi

# Redis
SERVICES_TOTAL=$((SERVICES_TOTAL + 1))
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_success "Redis: OK"
    SERVICES_OK=$((SERVICES_OK + 1))
else
    print_error "Redis: FAIL"
fi

# Backend
SERVICES_TOTAL=$((SERVICES_TOTAL + 1))
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    print_success "Backend API: OK"
    SERVICES_OK=$((SERVICES_OK + 1))
else
    print_error "Backend API: FAIL"
fi

# Frontend
SERVICES_TOTAL=$((SERVICES_TOTAL + 1))
if curl -s -I http://localhost:3000 > /dev/null 2>&1; then
    print_success "Frontend: OK"
    SERVICES_OK=$((SERVICES_OK + 1))
else
    print_error "Frontend: FAIL"
fi

# Prometheus
SERVICES_TOTAL=$((SERVICES_TOTAL + 1))
if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    print_success "Prometheus: OK"
    SERVICES_OK=$((SERVICES_OK + 1))
else
    print_error "Prometheus: FAIL"
fi

# Grafana
SERVICES_TOTAL=$((SERVICES_TOTAL + 1))
if curl -s -I http://localhost:3001 > /dev/null 2>&1; then
    print_success "Grafana: OK"
    SERVICES_OK=$((SERVICES_OK + 1))
else
    print_error "Grafana: FAIL"
fi

# n8n
SERVICES_TOTAL=$((SERVICES_TOTAL + 1))
if curl -s -I http://localhost:5678 > /dev/null 2>&1; then
    print_success "n8n: OK"
    SERVICES_OK=$((SERVICES_OK + 1))
else
    print_error "n8n: FAIL"
fi

# Ollama
SERVICES_TOTAL=$((SERVICES_TOTAL + 1))
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_success "Ollama: OK"
    SERVICES_OK=$((SERVICES_OK + 1))
else
    print_warning "Ollama: Iniciando (puede tardar en descargar modelos)"
fi

# ============================================================================
# Resumen Final
# ============================================================================

print_header "Instalación Completada"

echo -e "${GREEN}✓ Servicios funcionando: $SERVICES_OK/$SERVICES_TOTAL${NC}"
echo ""

if [ $SERVICES_OK -ge 6 ]; then
    print_success "¡Instalación exitosa! 🎉"
    echo ""
    echo -e "${BLUE}Accede a los servicios:${NC}"
    echo ""
    echo -e "  📊 Dashboard:        ${GREEN}http://localhost:3000${NC}"
    echo -e "  🔧 API Backend:      ${GREEN}http://localhost:8000${NC}"
    echo -e "  📚 API Docs:         ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "  📈 Grafana:          ${GREEN}http://localhost:3001${NC}"
    echo -e "     Usuario: admin"
    echo -e "     Password: $GRAFANA_PASS"
    echo ""
    echo -e "  🔄 n8n Workflows:    ${GREEN}http://localhost:5678${NC}"
    echo -e "     Usuario: admin"
    echo -e "     Password: $N8N_PASS"
    echo ""
    echo -e "  🔍 Prometheus:       ${GREEN}http://localhost:9090${NC}"
    echo ""
    
    print_info "Comandos útiles:"
    echo ""
    echo "  make help          - Ver todos los comandos"
    echo "  make logs          - Ver logs de servicios"
    echo "  make health        - Verificar salud del sistema"
    echo "  make restart       - Reiniciar servicios"
    echo "  docker-compose ps  - Ver estado de contenedores"
    echo ""
    
    print_warning "Próximos pasos:"
    echo ""
    echo "  1. Cambia las contraseñas en .env para producción"
    echo "  2. Configura SSL/TLS si vas a exponer públicamente"
    echo "  3. Configura backups automatizados"
    echo "  4. Lee la documentación: cat INSTALLATION_GUIDE.md"
    echo ""
    
else
    print_warning "Instalación completada con advertencias"
    echo ""
    print_info "Algunos servicios no respondieron. Esto es normal si:"
    echo "  - Ollama está descargando modelos (puede tardar 10-15 min)"
    echo "  - El sistema tiene recursos limitados"
    echo ""
    print_info "Verifica el estado con:"
    echo "  docker-compose ps"
    echo "  docker-compose logs -f"
    echo ""
fi

# Guardar información de instalación
cat > INSTALLATION_INFO.txt << EOF
Sentinel - Información de Instalación
======================================

Fecha de instalación: $(date)
Sistema operativo: $OS $VER
Arquitectura: $ARCH
RAM: ${TOTAL_RAM}GB
Espacio libre: ${DISK_SPACE}GB

Versiones:
- Docker: $(docker --version)
- Docker Compose: $(docker-compose --version)

Credenciales:
- PostgreSQL: sentinel_user / $POSTGRES_PASS
- Grafana: admin / $GRAFANA_PASS
- n8n: admin / $N8N_PASS

URLs:
- Dashboard: http://localhost:3000
- API: http://localhost:8000
- Grafana: http://localhost:3001
- n8n: http://localhost:5678
- Prometheus: http://localhost:9090

Servicios verificados: $SERVICES_OK/$SERVICES_TOTAL
EOF

print_success "Información de instalación guardada en INSTALLATION_INFO.txt"

echo ""
print_info "Para ver logs en tiempo real: docker-compose logs -f"
print_info "Para detener servicios: docker-compose down"
print_info "Para reiniciar: docker-compose restart"
echo ""

exit 0
