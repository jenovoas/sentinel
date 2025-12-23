#!/usr/bin/env bash
set -euo pipefail

API_URL="http://localhost:8000/api/v1/ai/query"
PROMPT="Escribe una línea que diga: Hola desde Sentinel (prueba automática)."

echo "🧪 Testing AI endpoint: $API_URL"

response=$(curl --silent --fail -X POST "$API_URL" -H 'Content-Type: application/json' -d "{\"prompt\": \"$PROMPT\", \"max_tokens\": 50, \"temperature\": 0.3}") || {
  echo "❌ Request failed. Ensure backend and Ollama are up."
  exit 1
}

echo "✅ Response:"
echo "$response" | jq '.' 2>/dev/null || echo "$response"
