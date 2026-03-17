#!/bin/bash

# Auto-loader para Alpine con wget
set -e

N8N_URL="http://n8n:5678"
N8N_API_KEY="${N8N_API_KEY}"
WORKFLOWS_DIR="/workflows"
MAX_RETRIES=60
RETRY_DELAY=1

echo "🤖 [AUTO-LOADER v2] Iniciando..."

# Esperar a que n8n esté listo
echo "⏳ Esperando a que n8n esté listo..."
count=0
while [ $count -lt $MAX_RETRIES ]; do
    if curl -sf "${N8N_URL}/" > /dev/null 2>&1; then
        echo "✅ n8n está listo!"
        sleep 2
        break
    fi
    count=$((count + 1))
    echo "⌚ Intento $count/$MAX_RETRIES..."
    sleep $RETRY_DELAY
done

if [ $count -eq $MAX_RETRIES ]; then
    echo "❌ TIMEOUT"
    exit 1
fi

# Verificar si ya se ejecutó
if [ -f "/tmp/.workflows-loaded" ]; then
    echo "ℹ️  Ya cargado anteriormente"
    exit 0
fi

echo "📦 Buscando workflows..."

if [ ! -d "$WORKFLOWS_DIR" ]; then
    echo "⚠️  No existe $WORKFLOWS_DIR"
    exit 0
fi

success_count=0
for workflow_file in "$WORKFLOWS_DIR"/*.json; do
    [ ! -f "$workflow_file" ] && continue
    
    filename=$(basename "$workflow_file")
    echo "📝 $filename"
    
    response=$(wget -q -O- \
        --header="X-N8N-API-KEY: ${N8N_API_KEY}" \
        --header="Content-Type: application/json" \
        --post-file="$workflow_file" \
        "${N8N_URL}/api/v1/workflows" 2>&1 || echo "error")
    
    if echo "$response" | grep -q '"id"'; then
        echo "✅ Creado"
        success_count=$((success_count + 1))
    else
        echo "⚠️ Error"
    fi
done

touch /tmp/.workflows-loaded
echo "✨ Completado: $success_count workflows"
exit 0
