#!/bin/bash
# 🤖 SENTINEL AI STACK INSTALLER (USER SPACE / LOCAL)
# -----------------------------------------------------------------------------
# Installs Ollama into /home/jnovoas/ollama_system to avoid filling Root Partition.
# -----------------------------------------------------------------------------

set -e

INSTALL_DIR="/home/jnovoas/ollama_system"
BIN_DIR="$INSTALL_DIR/bin"
LIB_DIR="$INSTALL_DIR/lib"
SERVICE_FILE="/etc/systemd/system/ollama.service"

echo "🦁 SENTINEL AI EXPANSION PROTOCOL (LOCAL INSTALL)"
echo "------------------------------------------------"

# 1. Download Official Bundle
echo "⬇️  Downloading Ollama Bundle..."
cd /tmp
curl -L https://ollama.com/download/ollama-linux-amd64.tgz -o ollama.tgz

# 2. Extract to /home (Where space exists)
echo "📦 Extracting to $INSTALL_DIR..."
# Ensure directories exist
mkdir -p "$BIN_DIR" "$LIB_DIR"

# Extract stripping the initial directory structure if needed, or just extract full
# The tarball usually has ./bin/ollama and ./lib/ollama...
tar -C "$INSTALL_DIR" -xzf ollama.tgz

echo "✅ Extraction Complete."

# 3. Setup User Service (Systemd) pointing to Local Binary
echo "⚙️  Configuring Service..."
# We need to cleanup old failed service if exists
if [ -f "$SERVICE_FILE" ]; then
    sudo systemctl stop ollama || true
fi

# Write custom service file
# Note: User needs sudo to write to systemd, but binary is in home
sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Ollama Service (Sentinel Local)
After=network-online.target

[Service]
ExecStart=$BIN_DIR/ollama serve
User=$USER
Group=$USER
Restart=always
RestartSec=3
Environment="PATH=$BIN_DIR:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="OLLAMA_MODELS=/home/jnovoas/.ollama/models"
Environment="OLLAMA_HOST=0.0.0.0"

[Install]
WantedBy=default.target
EOF

# 4. Reload and Start
echo "🔥 Activating Service..."
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl restart ollama

# 5. Wait for Pulse
echo "⏳ Waiting for API..."
sleep 5
if systemctl is-active --quiet ollama; then
    echo "✅ Service is RUNNING."
else
    echo "❌ Service failed to start. Check logs: journalctl -u ollama"
    exit 1
fi

# 6. Pull Model
MODEL="llama3.2:3b"
echo ""
echo "🧠 Injecting Neural Matrix ($MODEL)..."
# Use the local binary to pull
"$BIN_DIR/ollama" pull $MODEL

echo ""
echo "✅ AI STACK OPERATIONAL (LOCAL MODE)."
echo "   Binary: $BIN_DIR/ollama"
echo "   Models: ~/.ollama/models"
