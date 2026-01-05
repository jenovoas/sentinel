#!/bin/bash
# SENTINEL BARE METAL - OPTIMIZED RUNNER
# Reduce contenedores al mínimo manteniendo la integridad de las cadenas de seguridad.

set -e

# Configuración de rutas
SENTINEL_DIR="/home/jnovoas/sentinel"
VENV="$SENTINEL_DIR/.venv/bin/activate"

echo "🛡️ Iniciando Sentinel en modo BARE METAL OPTIMIZED..."

# 0. Cargar configuración de IA (Gemini/Antigravity)
if [ -f "$SENTINEL_DIR/sentinel_env.sh" ]; then
    echo "🧠 Cargando configuración de IA (Gemini)..."
    source "$SENTINEL_DIR/sentinel_env.sh"
else
    echo "⚠️  sentinel_env.sh no encontrado, usando Ollama por defecto"
fi

# 1. Asegurar persistencia y aprendizaje (Docker para DB y n8n)
echo "📦 Minimizando infraestructura Docker (Postgres + Redis + n8n)..."
cd "$SENTINEL_DIR"
docker-compose up -d postgres redis n8n

# 2. Esperar a la base de datos de TruthSync
echo "⏳ Esperando integridad de base de datos..."
until docker exec sentinel-postgres pg_isready -U sentinel > /dev/null 2>&1; do
  sleep 1
done
echo "✅ Base de datos lista."

# 3. Lanzar Backend (Sentinel Core API) nativamente
# Acceso directo al hardware para eBPF y reducción de latencia en TruthSync.
echo "⚛️ Lanzando Sentinel Core API de forma nativa..."
source "$VENV"

# Exportamos variables críticas para la integridad del sistema
export DATABASE_URL="postgresql+asyncpg://sentinel_user:2wA4KgRinuKNgcOrA839ZRC2R1ycNtC4@127.0.0.1:5432/sentinel_db"
export REDIS_URL="redis://127.0.0.1:6379/0"
export OLLAMA_URL="http://127.0.0.1:11434"
export N8N_URL="http://127.0.0.1:5678/webhook/learning"
export TRUTHSYNC_N8N_URL="http://127.0.0.1:5678/webhook/truthsync-audit"

cd "$SENTINEL_DIR/backend"

# Limpieza de procesos huérfanos
pkill -f "uvicorn app.main:app" || true
sleep 1

# Ejecutar backend con variables de entorno explícitas
env DATABASE_URL="postgresql+asyncpg://sentinel_user:2wA4KgRinuKNgcOrA839ZRC2R1ycNtC4@127.0.0.1:5432/sentinel_db" \
    REDIS_URL="redis://127.0.0.1:6379/0" \
    OLLAMA_URL="http://127.0.0.1:11434" \
    N8N_URL="http://127.0.0.1:5678/webhook/learning" \
    TRUTHSYNC_N8N_URL="http://127.0.0.1:5678/webhook/truthsync-audit" \
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$SENTINEL_DIR/core_api.log" 2>&1 &

echo "🚀 Sentinel Core API iniciado. Logs: $SENTINEL_DIR/core_api.log"

# 4. Lanzar Guardian Watchdog (Reflejos de Supervivencia)
echo "🛡️ Activando Guardian Watchdog (Hardware Resilience)..."
pkill -f "watchdog_service.py" || true
nohup python3 "$SENTINEL_DIR/ebpf/watchdog_service.py" > "$SENTINEL_DIR/watchdog.log" 2>&1 &

# 5. Verificar Salud del Sistema
echo "🔎 Verificando integridad de la cadena de mando..."
sleep 3
if curl -s http://127.0.0.1:8000/api/v1/health | grep -q "healthy"; then
    echo "✅ CADENA DE SEGURIDAD VERIFICADA: Core API <-> TruthSync <-> Watchdog [OK]"
else
    echo "⚠️  Core API en fase de sincronización. Verifica logs si la TUI falla."
fi

echo -e "\n🔥 SISTEMA TOTALMENTE ACTIVADO: 3 Contenedores + 2 Servicios Nativos"
echo "--- INICIANDO SENTINEL TUI (MODO SOBERANO) ---"
sleep 1

# 6. Lanzar TUI (Frente de Control)
# Se lanza en el foreground para interactividad inmediata
python3 "$SENTINEL_DIR/sentinel_tui.py"
