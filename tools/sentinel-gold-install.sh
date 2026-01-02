#!/bin/bash
# 🛡️ Sentinel Cortex v2.0 - Master Gold Installer
# Objetivo: Provisionamiento automático para VMware/Cloud

set -euo pipefail
IFS=$'\n\t'
echo "🚀 Iniciando Instalación Automática de Sentinel Cortex..."

# 1. Preparacin del Sistema
sudo apt-get update && sudo apt-get install -y \
    curl git docker.io docker-compose-v2 python3-venv \
    python3-pip jq xorriso systemd-container

# 2. Configuracin de Docker & Red
REAL_USER=${SUDO_USER:-$USER}
sudo systemctl enable --now docker
sudo usermod -aG docker "$REAL_USER"

# 3. Preparacin del Directorio de Trabajo
INSTALL_DIR="/opt/sentinel"
if [ ! -d "$INSTALL_DIR" ]; then
    echo "❌ Error: No se encuentra el directorio $INSTALL_DIR"
    exit 1
fi
cd "$INSTALL_DIR"
echo "📍 Directorio de trabajo: $PWD"

# 4. Entorno de IA (Ollama)
echo "🧠 Configurando Ollama y Modelos..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
fi
sudo systemctl enable ollama
sudo systemctl start ollama || true

# Esperar a que el servicio est listo
for i in {1..10}; do
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "✅ Ollama est listo."
        break
    fi
    echo "Wait for Ollama..."
    sleep 3
done

echo "📥 Descargando modelo llama3.2:3b (esto puede tardar)..."
ollama pull llama3.2:3b || echo "⚠️ Falló el pull inicial, se intentará en el primer arranque."

# 5. Entorno Python & Memoria Semntica
echo "🧬 Inicializando Hipocampo Digital..."
python3 -m venv .venv
# Asegurar permisos para el usuario real
sudo chown -R "$REAL_USER:$REAL_USER" "$INSTALL_DIR"
sudo -u "$REAL_USER" "$INSTALL_DIR/.venv/bin/pip" install ollama chromadb requests psycopg2-binary numpy

# 6. Despliegue de Infraestructura Core
echo "🏗️ Levantando Stack de Contenedores (Soberana)..."
# Ejecutar como el usuario real para que docker guarde sockets/contextos correctamente
sudo -u "$REAL_USER" docker compose -f docker-compose.core.yml up -d

# 7. Finalizacin
echo "✅ SENTINEL CORTEX INSTALADO CON XITO."
