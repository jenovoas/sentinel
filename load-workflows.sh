#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# ESTRATEGIA 2: Script Manual de Carga de Workflows
# ═══════════════════════════════════════════════════════════════
#
# USO: ./load-workflows.sh
# 
# CUÁNDO USAR:
# - Después de docker-compose up -d
# - Cuando quieras agregar nuevos workflows
# - Para debugging (ves TODO el proceso)
#
# VENTAJAS:
# ✅ Control total - TÚ decides cuándo ejecutar
# ✅ No rebuild de Docker necesario
# ✅ Perfecto para desarrollo/testing

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

clear

echo -e "${MAGENTA}"
cat << 'EOF'
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🎪 CARGADOR MANUAL DE WORKFLOWS n8n                      ║
║                                                               ║
║     Estrategia 2: Tú tienes el control                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

N8N_URL="http://localhost:5678"
N8N_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiOThhZDkwNy1mNGMzLTRmZDctOGU0My04MDc1OWExY2ExYjAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY1NzQ3MTkyfQ.7hh3m40tGptnS8zE_m7-FpiLXr66QMYiZw_r-JdATqE"
N8N_USER="admin"
N8N_PASSWORD="darkfenix"
WORKFLOWS_DIR="./docker/n8n/workflows"

echo -e "${CYAN}📋 PASO 1: Verificando que n8n esté corriendo...${NC}"
echo ""

if ! curl -sf "${N8N_URL}" > /dev/null 2>&1; then
    echo -e "${RED}❌ ERROR: n8n no está respondiendo en ${N8N_URL}${NC}"
    echo -e "${YELLOW}💡 Ejecuta primero: docker-compose up -d n8n${NC}"
    exit 1
fi

echo -e "${GREEN}✅ n8n está corriendo y respondiendo${NC}"
echo ""

echo -e "${CYAN}📋 PASO 2: Buscando workflows en ${WORKFLOWS_DIR}...${NC}"
echo ""

if [ ! -d "$WORKFLOWS_DIR" ]; then
    echo -e "${RED}❌ Directorio no encontrado: $WORKFLOWS_DIR${NC}"
    exit 1
fi

workflow_files=$(find "$WORKFLOWS_DIR" -name "*.json" 2>/dev/null)
workflow_count=$(echo "$workflow_files" | grep -c . || echo 0)

if [ "$workflow_count" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No se encontraron workflows en $WORKFLOWS_DIR${NC}"
    exit 0
fi

echo -e "${GREEN}✅ Encontrados ${workflow_count} workflow(s)${NC}"
echo ""

echo -e "${CYAN}📋 PASO 3: Inyectando workflows via API...${NC}"
echo ""

success_count=0
fail_count=0

for workflow_file in $workflow_files; do
    filename=$(basename "$workflow_file")
    workflow_name=$(grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' "$workflow_file" | head -1 | cut -d'"' -f4 || echo "$filename")
    
    echo -e "${BLUE}📝 Procesando: ${filename}${NC}"
    echo -e "   ${CYAN}Nombre: ${workflow_name}${NC}"
    
    # Inyectar via API con API Key
    response=$(curl -s -X POST \
        -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
        -H "Content-Type: application/json" \
        -d @"$workflow_file" \
        "${N8N_URL}/api/v1/workflows" 2>&1)
    
    if echo "$response" | grep -q '"id"'; then
        workflow_id=$(echo "$response" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
        echo -e "   ${GREEN}✅ Creado exitosamente (ID: ${workflow_id})${NC}"
        ((success_count++))
    else
        echo -e "   ${YELLOW}⚠️  Posible duplicado o error${NC}"
        echo -e "   ${YELLOW}   Respuesta: $(echo "$response" | head -c 80)...${NC}"
        ((fail_count++))
    fi
    echo ""
done

echo ""
echo -e "${MAGENTA}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║                      RESUMEN FINAL                            ║${NC}"
echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Exitosos: ${success_count}${NC}"
echo -e "${YELLOW}⚠️  Fallidos/Duplicados: ${fail_count}${NC}"
echo ""
echo -e "${CYAN}🌐 Abre n8n en: ${N8N_URL}${NC}"
echo -e "${CYAN}🔐 Usuario: ${N8N_USER} / Contraseña: ${N8N_PASSWORD}${NC}"
echo ""
echo -e "${GREEN}✨ ¡Listo! Revisa tus workflows en la UI de n8n${NC}"
echo ""
