#!/bin/bash
# Script para configurar Ollama keep_alive PERMANENTE
# Mantiene modelo en RAM indefinidamente (hasta reiniciar Ollama)

echo "🔧 Configurando Ollama keep_alive PERMANENTE..."
echo ""

# Modelo a mantener en RAM
MODEL="llama3.2:1b"

echo "📋 Opciones de keep_alive:"
echo "   -1  = PERMANENTE (nunca descarga, hasta reiniciar Ollama)"
echo "   0   = Descarga inmediatamente después de responder"
echo "   5m  = Mantiene 5 minutos"
echo "   1h  = Mantiene 1 hora"
echo "   24h = Mantiene 24 horas"
echo ""
echo "✅ Usando: keep_alive = -1 (PERMANENTE)"
echo ""

# Configurar keep_alive = -1 (permanente)
echo "🚀 Enviando configuración a Ollama..."
RESPONSE=$(curl -s http://localhost:11434/api/generate -d "{
  \"model\": \"$MODEL\",
  \"prompt\": \"Sistema iniciado. Modelo cargado en memoria.\",
  \"keep_alive\": -1,
  \"stream\": false
}")

if [ $? -eq 0 ]; then
    echo "✅ Modelo $MODEL configurado con keep_alive = -1 (PERMANENTE)"
    echo ""
    echo "📊 Esto significa:"
    echo "   ✓ El modelo permanecerá en RAM indefinidamente"
    echo "   ✓ NO se descargará entre requests"
    echo "   ✓ Latencias consistentes garantizadas"
    echo "   ✓ Solo se descarga si reinicias Ollama"
    echo ""
    echo "💾 Uso de RAM:"
    echo "   Modelo llama3.2:1b: ~1.3 GB VRAM"
    echo "   GTX 1050 disponible: 3 GB VRAM"
    echo "   Espacio restante: ~1.7 GB ✅"
    echo ""
    echo "🔍 Verificando modelos cargados..."
    curl -s http://localhost:11434/api/tags | python3 -m json.tool | grep -A 10 "name"
else
    echo "❌ Error al configurar keep_alive"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Verifica que Ollama esté corriendo:"
    echo "      systemctl status ollama"
    echo ""
    echo "   2. Si no está corriendo, inícialo:"
    echo "      systemctl start ollama"
    echo ""
    echo "   3. Verifica que el modelo esté descargado:"
    echo "      ollama list"
    exit 1
fi

echo ""
echo "✅ CONFIGURACIÓN COMPLETA"
echo ""
echo "🚀 Ahora puedes ejecutar benchmarks con latencia consistente:"
echo "   cd backend && python sentinel_global_benchmark.py"
echo ""
echo "📝 Nota: El modelo permanecerá en RAM hasta que:"
echo "   - Reinicies Ollama (systemctl restart ollama)"
echo "   - Reinicies el sistema"
echo "   - Cambies keep_alive manualmente"
