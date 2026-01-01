#!/bin/bash
# Sentinel Cortex - Global SemSH Deployment Script
# Usage: ./deploy_semsh.sh

echo "🌌 Deploying Sentinel Semantic Shell (SemSH) globally..."

# Get absolute path of source
SRC_PATH="$(pwd)/sem_shell.py"
BIN_PATH="/usr/local/bin/semsh"

if [ ! -f "$SRC_PATH" ]; then
    echo "❌ Error: sem_shell.py not found in current directory."
    exit 1
fi

echo "🔹 Source: $SRC_PATH"
echo "🔹 Target: $BIN_PATH"

# Remove existing link/file if present
if [ -f "$BIN_PATH" ] || [ -L "$BIN_PATH" ]; then
    echo "🔸 Removing existing deployment..."
    sudo rm -f "$BIN_PATH"
fi

# Create symlink
echo "🔸 Creating symlink..."
sudo ln -s "$SRC_PATH" "$BIN_PATH"

# Ensure executable
sudo chmod +x "$SRC_PATH"

# Add alias to .bashrc if not present
if ! grep -q "alias sem=" ~/.bashrc; then
    echo "🔸 Adding 'sem' alias to ~/.bashrc"
    echo 'alias sem="semsh"' >> ~/.bashrc
else
    echo "✅ Alias 'sem' already exists in ~/.bashrc"
fi

if ! grep -q "alias sem=" ~/.zshrc; then
    echo "🔸 Adding 'sem' alias to ~/.zshrc"
    echo 'alias sem="semsh"' >> ~/.zshrc
else
    echo "✅ Alias 'sem' already exists in ~/.zshrc"
fi

echo ""
echo "✅ DEPLOYMENT COMPLETE"
echo "👉 Run 'source ~/.bashrc' or 'source ~/.zshrc' to refresh aliases."
echo "👉 Try it: sem dashboard"
