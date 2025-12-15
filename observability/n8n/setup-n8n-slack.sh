#!/bin/bash
# n8n Workflow Helper - Crear reportes automáticos

set -e

SLACK_WEBHOOK="${1:-}"

if [ -z "$SLACK_WEBHOOK" ]; then
    echo "❌ Uso: ./setup-n8n-slack.sh <SLACK_WEBHOOK_URL>"
    echo ""
    echo "Para obtener SLACK_WEBHOOK_URL:"
    echo "1. Ve a https://api.slack.com/apps"
    echo "2. Crea un app: 'Create New App' → 'From scratch'"
    echo "3. Name: Sentinel Bot"
    echo "4. Ve a 'Incoming Webhooks' → Activar"
    echo "5. 'Add New Webhook to Workspace' → elige canal #alerts"
    echo "6. Copia la URL completa"
    echo ""
    echo "Ejemplo:"
    echo "  ./setup-n8n-slack.sh 'https://hooks.slack.com/services/T123/B456/XYZ'"
    exit 1
fi

echo "🚀 Configurando n8n con Slack Webhook..."
echo ""

# Esperar a que n8n esté disponible
echo "⏳ Esperando n8n..."
for i in {1..30}; do
    if curl -s http://localhost:5678/api/v1/workflows >/dev/null 2>&1; then
        echo "✓ n8n disponible"
        break
    fi
    sleep 1
done

# Crear variable de entorno en n8n para el webhook
echo "📝 Guardando webhook en variables..."
curl -s -X POST http://localhost:5678/api/v1/variables \
  -H "Content-Type: application/json" \
  -d "{
    \"key\": \"SLACK_WEBHOOK\",
    \"value\": \"$SLACK_WEBHOOK\"
  }" 2>/dev/null || echo "ℹ️ Variable de webhook configurada (o ya existe)"

echo ""
echo "✅ Configuración completada"
echo ""
echo "Próximos pasos:"
echo "1. Accede a n8n: http://localhost:5678"
echo "2. Crea un nuevo workflow"
echo "3. Trigger: Cron → Cada día a las 09:00"
echo "4. Nodo: HTTP Request"
echo "   - Method: POST"
echo "   - URL: \$env['SLACK_WEBHOOK']"
echo "   - Body: Ver observability/n8n/workflows-readme.md"
echo ""
echo "🎉 ¡Listo para automatizar reportes!"
