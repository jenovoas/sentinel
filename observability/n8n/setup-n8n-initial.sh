#!/bin/bash
# Setup inicial para n8n - Crea workflows de ejemplo

set -e

echo "📋 Setup n8n - Creando workflows de ejemplo..."
echo ""

# Esperar a que n8n esté disponible
echo "⏳ Esperando n8n..."
for i in {1..30}; do
  if curl -s http://localhost:5678 >/dev/null 2>&1; then
    echo "✓ n8n disponible"
    break
  fi
  sleep 1
done

# Crear archivo temporal con workflow
TEMP_WORKFLOW=$(mktemp)

cat > "$TEMP_WORKFLOW" << 'WORKFLOW_DEFINITION'
{
  "name": "Health Check - Example",
  "active": true,
  "nodes": [
    {
      "parameters": {
        "interval": [15],
        "unit": "minutes"
      },
      "id": "trigger1",
      "name": "Every 15 Minutes",
      "type": "n8n-nodes-base.interval",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "http://prometheus:9090/-/healthy",
        "method": "GET"
      },
      "id": "http1",
      "name": "Ping Prometheus",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [450, 300]
    }
  ],
  "connections": {
    "Every 15 Minutes": {
      "main": [[{"node": "Ping Prometheus", "type": "main", "index": 0}]]
    }
  }
}
WORKFLOW_DEFINITION

# Intentar inyectar via API
echo ""
echo "📤 Intentando inyectar workflow via API..."

RESULT=$(curl -s -X POST http://localhost:5678/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d @"$TEMP_WORKFLOW" 2>/dev/null)

rm -f "$TEMP_WORKFLOW"

if echo "$RESULT" | grep -q '"id"'; then
  echo "✅ Workflow creado exitosamente"
  echo "$RESULT" | jq '.name, .id'
else
  echo "⚠️ API de n8n respondió (pero no creó workflow)"
  echo ""
  echo "Alternativa: Importa manualmente"
  echo "1. Ve a http://localhost:5678"
  echo "2. New → Workflow"
  echo "3. Menú (⋮) → Import from JSON"
  echo "4. Copia: cat observability/n8n/workflow-daily-report-template.json"
fi

echo ""
echo "✨ Setup completado"
echo ""
echo "Próximos pasos:"
echo "1. Accede a n8n: http://localhost:5678"
echo "2. Verifica si hay workflows en 'Workflows' tab"
echo "3. Si no, importa template: observability/n8n/workflow-daily-report-template.json"
