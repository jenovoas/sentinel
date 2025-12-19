#!/bin/bash
# Script para mantener modelo Ollama en memoria permanentemente
# Evita la doble carga entre requests

echo "🔧 Configurando Ollama para mantener modelo en memoria..."
echo ""

# 1. Verificar que Ollama esté corriendo
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama no está corriendo"
    echo "   Ejecuta: docker-compose up -d ollama"
    exit 1
fi

echo "✅ Ollama está corriendo"
echo ""

# 2. Listar modelos disponibles
echo "📋 Modelos disponibles:"
curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | cut -d'"' -f4
echo ""

# 3. Precargar modelo con keep_alive permanente
MODEL="${1:-phi3:mini}"
echo "🚀 Precargando modelo: $MODEL"
echo "   (keep_alive: -1 = permanente)"
echo ""

curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$MODEL\",
    \"prompt\": \"warmup\",
    \"stream\": false,
    \"keep_alive\": -1
  }" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Modelo cargado en memoria (permanente)"
    echo ""
    echo "📊 Verificando estado:"
    curl -s http://localhost:11434/api/ps | grep -o '"name":"[^"]*"' | cut -d'"' -f4
    echo ""
    echo "✅ Configuración completa"
    echo ""
    echo "💡 El modelo permanecerá en memoria hasta reiniciar Ollama"
    echo "   Para liberar memoria: docker-compose restart ollama"
else
    echo "❌ Error al cargar modelo"
    echo "   Verifica que el modelo exista: ollama list"
    exit 1
fi
