#!/bin/bash

# ==============================================================================
# 🌌 SENTINEL QUANTUM MODE STARTUP SCRIPT
# ==============================================================================
# Propósito: Levantar SOLO lo necesario para la Matriz Cuántica (1000 Membranas).
# Optimizado para evitar sobrecalentamiento y apagados térmicos.
# ==============================================================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌌 Iniciando Protocolo de Emergencia Térmica: MODO QUANTUM ONLY${NC}"

# 1. DETENER TODOS LOS SERVICIOS INNECESARIOS
echo -e "\n${YELLOW}🔥 Deteniendo servicios pesados para enfriar CPU...${NC}"

# Detener contenedores Docker (Base de datos, Grafana, Prometheus, etc.)
if command -v docker &> /dev/null; then
    echo "   Stopping Docker containers..."
    docker stop $(docker ps -q) 2>/dev/null || true
fi

# Detener procesos de fondo de Sentinel
pkill -f "celery" || true
pkill -f "uvicorn" || true
pkill -f "next" || true
pkill -f "node" || true
pkill -f "ollama" || true 

echo -e "${GREEN}✅ Sistema enfriado. Memoria liberada.${NC}"

# 2. INICIAR BACKEND (Modo Ligero)
echo -e "\n${BLUE}🧠 Iniciando Cortex Core (Solo API)...${NC}"
cd /home/jnovoas/sentinel/backend

# Desactivar logs pesados y conexiones a DB innecesarias via ENV vars si fuera posible
# Iniciamos uvicorn directamente en background
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --log-level error > backend_quantum.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend activo (PID: $BACKEND_PID)${NC}"

# 3. INICIAR FRONTEND
echo -e "\n${BLUE}👁️ Iniciando Interfaz Visual (Next.js)...${NC}"
cd /home/jnovoas/sentinel/frontend

# Usamos 'dev' pero podríamos usar 'start' si hubiera build. 
# Asumimos dev por flexibilidad, pero limitamos la concurrencia si fuera posible (no fácil en npm)
nohup npm run dev > frontend_quantum.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend activo (PID: $FRONTEND_PID)${NC}"

# 4. MONITOR DE TEMPERATURA (Opcional, informativo)
echo -e "\n${YELLOW}⚠️  ADVERTENCIA: La simulación de 1000 membranas es INTENSIVA.${NC}"
echo -e "   Se ha desactivado la IA (Ollama) y la Base de Datos para ahorrar energía."
echo -e "   La interpretación de texto del Oráculo podría fallar, pero la FÍSICA funcionará."

echo -e "\n${GREEN}🚀 SISTEMA LISTO.${NC}"
echo -e "   Frontend: http://localhost:3000/quantum"
echo -e "   Backend:  http://localhost:8000/docs"
echo -e "\n   (Presiona Ctrl+C para detener todo)"

# Esperar a que el usuario cancele
trap "kill $BACKEND_PID $FRONTEND_PID; echo '🛑 Deteniendo todo...'; exit" SIGINT SIGTERM

wait
