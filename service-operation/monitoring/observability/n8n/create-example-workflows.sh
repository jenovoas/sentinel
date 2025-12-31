#!/bin/bash
# Script para crear workflows de ejemplo en n8n

echo "🤖 Creando workflows en n8n..."
sleep 2

# Workflow 1: Health Check Simple
echo ""
echo "1️⃣ Creando 'Health Check' workflow..."

curl -s -X POST http://localhost:5678/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Health Check - Simple",
    "active": true,
    "nodes": [
      {
        "id": "uuid-1",
        "name": "Every 15 Minutes",
        "type": "n8n-nodes-base.interval",
        "typeVersion": 1,
        "position": [250, 300],
        "parameters": {
          "interval": [15],
          "unit": "minutes"
        }
      },
      {
        "id": "uuid-2", 
        "name": "Ping Prometheus",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4,
        "position": [450, 300],
        "parameters": {
          "url": "http://prometheus:9090/-/healthy",
          "method": "GET"
        }
      }
    ],
    "connections": {
      "Every 15 Minutes": {
        "main": [[{"node": "Ping Prometheus", "type": "main", "index": 0}]]
      }
    },
    "settings": {}
  }' 2>/dev/null | jq -r '.id // "error"' | head -1

echo "✓ Workflow creado"

# Workflow 2: Manual Test
echo ""
echo "2️⃣ Creando 'Manual Test' workflow..."

curl -s -X POST http://localhost:5678/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Manual Test - Send Message",
    "active": false,
    "nodes": [
      {
        "id": "uuid-3",
        "name": "Manual Trigger",
        "type": "n8n-nodes-base.manualTrigger",
        "typeVersion": 1,
        "position": [250, 300],
        "parameters": {}
      },
      {
        "id": "uuid-4",
        "name": "Log Message",
        "type": "n8n-nodes-base.code",
        "typeVersion": 1,
        "position": [450, 300],
        "parameters": {
          "functionCode": "return [{\"json\": {\"message\": \"✅ Workflow funcionando\", \"time\": new Date().toISOString()}}];"
        }
      }
    ],
    "connections": {
      "Manual Trigger": {
        "main": [[{"node": "Log Message", "type": "main", "index": 0}]]
      }
    },
    "settings": {}
  }' 2>/dev/null | jq -r '.id // "error"' | head -1

echo "✓ Workflow creado"

echo ""
echo "✅ Workflows de ejemplo creados en n8n"
echo ""
echo "Próximos pasos:"
echo "1. Ve a http://localhost:5678"
echo "2. Ve a 'Workflows' en la sidebar"
echo "3. Verás 'Health Check - Simple' (activo) y 'Manual Test' (inactivo)"
echo "4. Para agregar Slack webhook:"
echo "   ./observability/n8n/setup-n8n-slack.sh 'YOUR_WEBHOOK_URL'"
