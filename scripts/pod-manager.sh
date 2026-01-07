#!/bin/bash
# ==========================================
# Sentinel Pod Manager
# Gestión unificada de perfiles Podman
# ==========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función de ayuda
show_help() {
    cat << EOF
${BLUE}Sentinel Pod Manager${NC}

${GREEN}Uso:${NC}
  $0 <comando> [perfil]

${GREEN}Comandos:${NC}
  start <perfil>   Iniciar perfil (minimal|backend|full)
  stop             Detener todos los contenedores
  restart <perfil> Reiniciar perfil
  status           Ver estado de contenedores
  logs <servicio>  Ver logs de un servicio
  stats            Ver consumo de recursos en tiempo real
  clean            Limpiar contenedores y volúmenes

${GREEN}Perfiles:${NC}
  minimal          Solo postgres + redis (~1.5GB RAM)
  backend          + Backend API + Frontend (~3.5GB RAM)
  full             Stack completo con observabilidad (~8GB RAM)

${GREEN}Ejemplos:${NC}
  $0 start minimal
  $0 stop
  $0 logs sentinel-backend
  $0 stats
EOF
}

# Función para iniciar perfil
start_profile() {
    local profile=$1
    
    case $profile in
        minimal)
            echo -e "${GREEN}Iniciando perfil MINIMAL...${NC}"
            podman-compose -f "$PROJECT_ROOT/podman-compose.minimal.yml" up -d
            ;;
        backend)
            echo -e "${GREEN}Iniciando perfil BACKEND...${NC}"
            podman-compose -f "$PROJECT_ROOT/podman-compose.backend.yml" up -d
            ;;
        full)
            echo -e "${YELLOW}⚠️  ADVERTENCIA: Perfil FULL consume ~8GB RAM${NC}"
            read -p "¿Continuar? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo -e "${GREEN}Iniciando perfil FULL...${NC}"
                podman-compose -f "$PROJECT_ROOT/podman-compose.full.yml" up -d
            else
                echo -e "${RED}Cancelado${NC}"
                exit 1
            fi
            ;;
        *)
            echo -e "${RED}Error: Perfil desconocido '$profile'${NC}"
            echo "Perfiles válidos: minimal, backend, full"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}✓ Perfil '$profile' iniciado${NC}"
    echo -e "${BLUE}Verificando estado...${NC}"
    sleep 2
    podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

# Función para detener todos los servicios
stop_all() {
    echo -e "${YELLOW}Deteniendo todos los servicios...${NC}"
    
    # Intentar detener todos los perfiles
    for compose_file in "$PROJECT_ROOT"/podman-compose.*.yml; do
        if [ -f "$compose_file" ]; then
            echo -e "${BLUE}Deteniendo $(basename $compose_file)...${NC}"
            podman-compose -f "$compose_file" down 2>/dev/null || true
        fi
    done
    
    echo -e "${GREEN}✓ Todos los servicios detenidos${NC}"
}

# Función para reiniciar perfil
restart_profile() {
    local profile=$1
    echo -e "${YELLOW}Reiniciando perfil '$profile'...${NC}"
    stop_all
    sleep 2
    start_profile "$profile"
}

# Función para ver estado
show_status() {
    echo -e "${BLUE}Estado de contenedores Sentinel:${NC}"
    podman ps -a --filter "name=sentinel-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

# Función para ver logs
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        echo -e "${RED}Error: Especifica un servicio${NC}"
        echo "Ejemplo: $0 logs sentinel-backend"
        exit 1
    fi
    
    echo -e "${BLUE}Logs de $service:${NC}"
    podman logs -f "$service"
}

# Función para ver stats
show_stats() {
    echo -e "${BLUE}Consumo de recursos en tiempo real:${NC}"
    podman stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
}

# Función para limpiar
clean_all() {
    echo -e "${RED}⚠️  ADVERTENCIA: Esto eliminará todos los contenedores y volúmenes${NC}"
    read -p "¿Continuar? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        stop_all
        echo -e "${YELLOW}Eliminando volúmenes...${NC}"
        podman volume prune -f
        echo -e "${GREEN}✓ Limpieza completada${NC}"
    else
        echo -e "${RED}Cancelado${NC}"
    fi
}

# Main
case ${1:-} in
    start)
        if [ -z "${2:-}" ]; then
            echo -e "${RED}Error: Especifica un perfil${NC}"
            show_help
            exit 1
        fi
        start_profile "$2"
        ;;
    stop)
        stop_all
        ;;
    restart)
        if [ -z "${2:-}" ]; then
            echo -e "${RED}Error: Especifica un perfil${NC}"
            show_help
            exit 1
        fi
        restart_profile "$2"
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "${2:-}"
        ;;
    stats)
        show_stats
        ;;
    clean)
        clean_all
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Error: Comando desconocido '${1:-}'${NC}"
        echo
        show_help
        exit 1
        ;;
esac
