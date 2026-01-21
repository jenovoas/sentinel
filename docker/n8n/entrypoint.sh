#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# ENTRYPOINT WRAPPER para n8n
# ═══════════════════════════════════════════════════════════════
#
# ESTRATEGIA:
# 1. Iniciar n8n en background (&)
# 2. Esperar a que n8n esté listo
# 3. Inyectar workflows via API
# 4. Traer n8n a foreground para que Docker lo vea

set -e

echo "🚀 Iniciando n8n con workflow auto-injection..."

# Iniciar n8n en background
n8n start &
N8N_PID=$!

echo "📦 n8n iniciado con PID: $N8N_PID"

# Ejecutar el script de inicialización en background
# Esto no bloquea el proceso principal
/usr/local/bin/init-workflows.sh &

# Esperar a que n8n termine (mantiene el contenedor vivo)
wait $N8N_PID
