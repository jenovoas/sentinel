#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# n8n Workflow Initialization Script
# ═══════════════════════════════════════════════════════════════
#
# PROPÓSITO: Inyectar workflows en n8n automáticamente en el startup
# 
# CÓMO FUNCIONA:
# 1. El contenedor Docker ejecuta este script en /docker-entrypoint-init.d/
# 2. Script espera a que n8n esté listo (health check)
# 3. Script descubre todos los JSON en /tmp/workflows/
# 4. Para cada JSON: Hace POST a la API de n8n
# 5. Los workflows quedan guardados en la BD de n8n
#
# RESULTADO:
# - Primera vez: Workflows se crean automáticamente
# - Próximas veces: Ya existen, n8n no los recrea

set -e

# ═══════════════════════════════════════════════════════════════
# VARIABLES DE CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════

N8N_URL="http://localhost:5678"
WORKFLOWS_DIR="/tmp/workflows"
MAX_RETRIES=30
RETRY_DELAY=2

# Colores para terminal (educativo, para ver el progreso)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ═══════════════════════════════════════════════════════════════
# FUNCIONES
# ═══════════════════════════════════════════════════════════════

# Función: Esperar a que n8n esté ready
wait_for_n8n() {
    echo -e "${CYAN}⏳ Esperando a que n8n esté listo...${NC}"
    
    local count=0
    while [ $count -lt $MAX_RETRIES ]; do
        # Hacer health check a n8n
        if curl -sf "${N8N_URL}/api/v1/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ n8n está listo! (intento $((count+1))/${MAX_RETRIES})${NC}"
            sleep 2  # Espera adicional para que la BD esté completamente lista
            return 0
        fi
        
        count=$((count + 1))
        echo -e "${YELLOW}⌚ Intento $count/$MAX_RETRIES (espera ${RETRY_DELAY}s)${NC}"
        sleep $RETRY_DELAY
    done
    
    echo -e "${RED}❌ TIMEOUT: n8n no respondió después de $((MAX_RETRIES * RETRY_DELAY))s${NC}"
    return 1
}

# Función: Inyectar un workflow
inject_workflow() {
    local json_file="$1"
    local filename=$(basename "$json_file")
    
    echo -e "${BLUE}📝 Procesando: $filename${NC}"
    
    # Validar que el archivo existe
    if [ ! -f "$json_file" ]; then
        echo -e "${RED}   ❌ Archivo no encontrado: $json_file${NC}"
        return 1
    fi
    
    # Extraer el nombre del workflow del JSON
    local workflow_name=$(grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' "$json_file" | head -1 | cut -d'"' -f4)
    
    # Si no encontró nombre, usar el nombre del archivo
    if [ -z "$workflow_name" ]; then
        workflow_name="${filename%.*}"
    fi
    
    echo -e "${BLUE}   📦 Nombre del workflow: '$workflow_name'${NC}"
    
    # Construir el payload para la API de n8n
    # n8n espera un JSON con "name", "nodes", "connections", "active", etc.
    local workflow_json=$(cat "$json_file")
    
    # Hacer POST a la API de n8n
    # La API endpoint es: POST /api/v1/workflows
    local response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$workflow_json" \
        "${N8N_URL}/api/v1/workflows" 2>&1 || echo '{"error":"curl_failed"}')
    
    # Verificar si fue exitoso (la API devuelve el workflow creado con ID)
    if echo "$response" | grep -q '"id"'; then
        local workflow_id=$(echo "$response" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
        echo -e "${GREEN}   ✅ Workflow creado exitosamente (ID: $workflow_id)${NC}"
        return 0
    else
        echo -e "${YELLOW}   ⚠️  Respuesta de API: $(echo "$response" | head -c 100)...${NC}"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════
# EJECUCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     n8n Workflow Initialization                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# PASO 1: Esperar a que n8n esté ready
if ! wait_for_n8n; then
    echo -e "${RED}No se pudo conectar a n8n. Abortando inicialización.${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}🔍 Buscando workflows en: $WORKFLOWS_DIR${NC}"
echo ""

# PASO 2: Verificar si existe el directorio de workflows
if [ ! -d "$WORKFLOWS_DIR" ]; then
    echo -e "${YELLOW}⚠️  Directorio de workflows no existe: $WORKFLOWS_DIR${NC}"
    echo -e "${YELLOW}   Se esperaban workflows en este directorio${NC}"
    exit 0  # No es un error fatal
fi

# PASO 3: Contar JSON files
workflow_count=$(find "$WORKFLOWS_DIR" -maxdepth 1 -name "*.json" 2>/dev/null | wc -l)
echo -e "${CYAN}📊 Encontrados $workflow_count workflow(s)${NC}"
echo ""

# PASO 4: Procesar cada workflow
if [ "$workflow_count" -eq 0 ]; then
    echo -e "${YELLOW}ℹ️  No hay workflows para cargar${NC}"
else
    success_count=0
    for workflow_file in "$WORKFLOWS_DIR"/*.json; do
        if [ -f "$workflow_file" ]; then
            if inject_workflow "$workflow_file"; then
                ((success_count++))
            fi
        fi
    done
    
    echo ""
    echo -e "${CYAN}📊 Resumen: $success_count/$workflow_count workflows procesados${NC}"
fi

echo ""
echo -e "${GREEN}✨ Inicialización completada${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

exit 0
