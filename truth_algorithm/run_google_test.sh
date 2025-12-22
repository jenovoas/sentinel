#!/bin/bash
# Script para ejecutar test de Google con credenciales
# ====================================================
# IMPORTANTE: Edita este archivo y pon tu API key real

# Activar entorno virtual
source venv_google/bin/activate

# Configurar credenciales (EDITA AQUÍ)
API_KEY="TU_API_KEY_REAL_AQUI"  # ← Pon tu API key aquí
CX_ID="80b08c4835fa24341"

# Ejecutar test
echo "🔍 Ejecutando test de Google Search API..."
echo ""
python test_google_simple.py "$API_KEY" "$CX_ID"

# Desactivar entorno
deactivate
