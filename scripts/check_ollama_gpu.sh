#!/bin/bash
# Ollama GPU Diagnostic Script
# Quick health check for Ollama + GPU setup

set -e

echo "🔍 Sentinel AI - Ollama GPU Diagnostic"
echo "========================================"
echo ""

# Check GPU
echo "🎮 GPU Information:"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total,memory.used,driver_version --format=csv,noheader
    echo ""
else
    echo "❌ nvidia-smi not found - GPU not available"
    exit 1
fi

# Check Ollama service
echo "🔍 Ollama Service Status:"
if systemctl is-active --quiet ollama; then
    echo "✅ Service: ACTIVE"
    systemctl status ollama | grep "Active:"
else
    echo "❌ Service: INACTIVE"
    echo "   Run: sudo systemctl start ollama"
    exit 1
fi
echo ""

# Check GPU offloading in logs
echo "🔍 GPU Offloading (last 20 lines):"
journalctl -u ollama -n 20 --no-pager | grep -i "offloaded\|cuda\|vram\|gpu" | tail -5 || echo "⚠️  No GPU offloading logs found"
echo ""

# Check available models
echo "🔍 Installed Models:"
ollama list
echo ""

# Quick performance test
echo "🧪 Quick Performance Test:"
echo "   Prompt: 'What is 2+2?'"
echo "   Starting..."
START_TIME=$(date +%s.%N)
RESPONSE=$(ollama run llama3.2:3b "What is 2+2? Answer in one word." 2>&1)
END_TIME=$(date +%s.%N)
LATENCY=$(echo "$END_TIME - $START_TIME" | bc)

echo "   Response: $RESPONSE"
echo "   Latency: ${LATENCY}s"
echo ""

# Evaluate performance
if (( $(echo "$LATENCY < 3.0" | bc -l) )); then
    echo "✅ Performance: GOOD (GPU likely active)"
elif (( $(echo "$LATENCY < 10.0" | bc -l) )); then
    echo "⚠️  Performance: MODERATE (check GPU usage)"
else
    echo "❌ Performance: POOR (GPU may not be active)"
fi
echo ""

# Check VRAM usage
echo "🔍 Current VRAM Usage:"
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader
echo ""

# Summary
echo "========================================"
echo "✅ Diagnostic Complete"
echo ""
echo "📝 Next Steps:"
echo "   - View full logs: journalctl -u ollama -f"
echo "   - Monitor VRAM: watch -n 1 nvidia-smi"
echo "   - Run benchmarks: python backend/benchmarks/bench_ollama_gpu.py"
echo ""
