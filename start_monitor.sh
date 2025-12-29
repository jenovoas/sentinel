#!/bin/bash
# Script para iniciar el Sentinel Monitor
# Este script debe ejecutarse en una terminal separada

echo "🛡️  [Sentinel] Iniciando Guardian Monitor..."
echo "=============================================="
echo ""
echo "Este monitor escuchará eventos del kernel y tomará decisiones con IA"
echo "Presiona Ctrl+C para detener"
echo ""

# Verificar que eBPF está cargado
if ! sudo bpftool prog show pinned /sys/fs/bpf/guardian_alpha/guardian_prog &>/dev/null; then
    echo "❌ Error: eBPF Guardian no está cargado"
    echo "Por favor ejecuta: cd ebpf && sudo ./load.sh"
    exit 1
fi

# Verificar que Ollama está corriendo
if ! pgrep -x "ollama" > /dev/null; then
    echo "⚠️  Warning: Ollama no parece estar corriendo"
    echo "Iniciando Ollama..."
    ollama serve &
    sleep 3
fi

# Verificar que el modelo llama3.2:3b está disponible
if ! ollama list | grep -q "llama3.2:3b"; then
    echo "⚠️  Warning: Modelo llama3.2:3b no encontrado"
    echo "Descargando modelo..."
    ollama pull llama3.2:3b
fi

echo "✅ Prerequisitos verificados"
echo ""
echo "🚀 Iniciando monitor..."
echo ""

# Iniciar el monitor
sudo python3 -m sentinel_core.main start
