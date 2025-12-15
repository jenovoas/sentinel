#!/bin/bash
# Script para crear workflows en n8n via API REST

set -e

echo "🤖 Inyectando workflows en n8n..."
sleep 1

# Workflow 1: Health Check
echo ""
echo "1️⃣ Creando 'Health Check' workflow..."

WORKFLOW1=$(cat <<'WORKFLOW_EOF'
{
  "name": "Health Check - 15 min",
  "description": "Verifica health de Prometheus cada 15 minutos",
  "nodes": [
    {
      "parameters": {
        "interval": [15],
        "unit": "minutes"
      },
      "name": "Every 15 Minutes",
      "type": "n8n-nodes-base.interval",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "http://prometheus:9090/-/healthy",
        "method": "GET",
        "responseFormat": "text"
      },
      "name": "Check Prometheus",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [450, 300]
    }
  ],
  "connections": {
    "Every 15 Minutes": {
      "main": [[{"node": "Check Prometheus", "type": "main", "index": 0}]]
    }
  },
  "active": true,
  "settings": {},
  "staticData": null,
  "pinData": {}
}
WORKFLOW_EOF
)

curl -s -X POST http://localhost:5678/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d "$WORKFLOW1" 2>/dev/null | jq -r '.id // empty' > /tmp/wf1.txt

if [ -s /tmp/wf1.txt ]; then
  WF1=$(cat /tmp/wf1.txt)
  echo "✓ Health Check workflow creado (ID: $WF1)"
else
  echo "⚠️ No se pudo crear (esperado si API tiene restricciones)"
fi

# Workflow 2: Manual Test
echo ""
echo "2️⃣ Creando 'Manual Test' workflow..."

WORKFLOW2=$(cat <<'WORKFLOW_EOF'
{
  "name": "Manual Test - Demo",
  "description": "Workflow de prueba manual",
  "nodes": [
    {
      "parameters": {},
      "name": "Manual Trigger",
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "functionCode": "return [{\"json\": {\"message\": \"✅ Workflow funcionando!\", \"timestamp\": new Date().toISOString()}}];"
      },
      "name": "Echo Message",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [450, 300]
    }
  ],
  "connections": {
    "Manual Trigger": {
      "main": [[{"node": "Echo Message", "type": "main", "index": 0}]]
    }
  },
  "active": false,
  "settings": {},
  "staticData": null,
  "pinData": {}
}
WORKFLOW_EOF
)

curl -s -X POST http://localhost:5678/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d "$WORKFLOW2" 2>/dev/null | jq -r '.id // empty' > /tmp/wf2.txt

if [ -s /tmp/wf2.txt ]; then
  WF2=$(cat /tmp/wf2.txt)
  echo "✓ Manual Test workflow creado (ID: $WF2)"
else
  echo "⚠️ No se pudo crear (esperado si API tiene restricciones)"
fi

echo ""
echo "✨ Workflows inyectados (o en cola de creación)"
echo ""
echo "Verifica en: http://localhost:5678"
echo "Si no ves workflows, importa desde:"
echo "  observability/n8n/workflow-daily-report-template.json"
