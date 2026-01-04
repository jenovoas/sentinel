#!/bin/bash
# SENTINEL OMNI LAUNCHER
# Levanta todo el stack: Ollama Check -> Backend -> Frontend

echo "🌌 Iniciando Protocolo Sentinel OMNI..."

# 1. Verificar IA (Ollama)
if curl -s http://127.0.0.1:11434/api/tags > /dev/null; then
    echo "✅ IA Core (Ollama): ONLINE"
else
    echo "⚠️  IA Core (Ollama): OFFLINE. Intentando iniciar..."
    ollama serve &
    sleep 5
fi

# 2. Reiniciar Backend
echo "🔄 Reiniciando Backend..."
sudo systemctl restart sentinel-backend.service
sleep 2
if systemctl is-active --quiet sentinel-backend.service; then
    echo "✅ Backend (FastAPI): ONLINE (Port 8000)"
else
    echo "❌ Backend: FALLÓ al iniciar. Revisa 'journalctl -u sentinel-backend'"
fi

# 3. Iniciar Frontend (si no está corriendo ya)
# Matamos instancias previas para limpiar
pkill -f "next-server" || true
pkill -f "next start" || true

echo "🚀 Iniciando Frontend..."
cd /home/jnovoas/sentinel/frontend
# Usamos nohup para que siga corriendo si cerramos la terminal
nohup npm run dev > frontend.log 2>&1 &
echo "✅ Frontend (Next.js): INICIANDO... (Port 3000)"

echo "---------------------------------------------------"
echo "✨ SISTEMA COMPLETAMENTE OPERATIVO"
echo "👉 Accede al Dashboard: http://localhost:3000/quantum"
echo "---------------------------------------------------"
