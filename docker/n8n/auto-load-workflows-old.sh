#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# ESTRATEGIA 3: Auto-loader activado por Docker Healthcheck
# ═══════════════════════════════════════════════════════════════
#
# CÓMO FUNCIONA:
# 1. Docker detecta que n8n está "healthy"
# 2. Este servicio "n8n-loader" se ejecuta automáticamente
# 3. Inyecta workflows una sola vez
# 4. Se detiene (no queda corriendo)
#
# VENTAJAS:
# ✅ Totalmente automático
# ✅ No necesitas ejecutar nada manualmente
# ✅ Perfecto para producción

set -e

N8N_URL="http://n8n:5678"
N8N_API_KEY="${N8N_API_KEY}"
N8N_USER="admin"
N8N_PASSWORD="${N8N_PASSWORD}"
WORKFLOWS_DIR="/workflows"
MAX_RETRIES=30
RETRY_DELAY=2

echo "🤖 [AUTO-LOADER] Iniciando..."

# Esperar a que n8n esté listo
echo "⏳ Esperando a que n8n esté listo..."
count=0
while [ $count -lt $MAX_RETRIES ]; do
    if curl -sf "${N8N_URL}/api/v1/health" > /dev/null 2>&1; then
        echo "✅ n8n está listo!"
        sleep 3  # Espera adicional de seguridad
        break
    fi
    count=$((count + 1))
    echo "⌚ Intento $count/$MAX_RETRIES..."
    sleep $RETRY_DELAY
done

if [ $count -eq $MAX_RETRIES ]; then
    echo "❌ TIMEOUT: n8n no respondió"
    exit 1
fi

# Verificar si ya se ejecutó antes (para no duplicar)
if [ -f "/tmp/.workflows-loaded" ]; then
    echo "ℹ️  Workflows ya fueron cargados anteriormente"
    exit 0
fi

echo "📦 Buscando workflows en $WORKFLOWS_DIR..."

if [ ! -d "$WORKFLOWS_DIR" ]; then
    echo "⚠️  Directorio de workflows no encontrado"
    exit 0
fi

success_count=0
for workflow_file in "$WORKFLOWS_DIR"/*.json; do
    if [ ! -f "$workflow_file" ]; then
        continue
    fi
    
    filename=$(basename "$workflow_file")
    echo "📝 Inyectando: $filename"
    
    response=$(curl -s -X POST \
        -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
        -H "Content-Type: application/json" \
        -d @"$workflow_file" \
        "${N8N_URL}/api/v1/workflows" 2>&1)
    
    if echo "$response" | grep -q '"id"'; then
        workflow_id=$(echo "$response" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
        echo "✅ Creado: $filename (ID: $workflow_id)"
        ((success_count++))
    else
        echo "⚠️  Error/Duplicado: $filename"
    fi
done

# Marcar como ejecutado
touch /tmp/.workflows-loaded

echo "✨ Auto-loader completado: $success_count workflows procesados"
exit 0
