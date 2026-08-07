#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0
# Sentinel PAI-60 Math Diversion Deployment Script
# Configures Ring 0 eBPF float redirection and userspace LD_PRELOAD wrapper.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🛡️ SENTINEL PAI-60: Deploying Math Diversion Pipeline..."

# 1. Build eBPF LSM and LD_PRELOAD shared library
make -C "$SCRIPT_DIR" float_detector.o libpai_redirect.so

SO_PATH="$SCRIPT_DIR/libpai_redirect.so"
BPF_OBJ="$SCRIPT_DIR/float_detector.o"

if [ -f "$SO_PATH" ]; then
    echo "✅ LD_PRELOAD Interceptor built: $SO_PATH"
else
    echo "❌ Error building $SO_PATH"
    exit 1
fi

if [ -f "$BPF_OBJ" ]; then
    echo "✅ Ring 0 eBPF Object built: $BPF_OBJ"
else
    echo "❌ Error building $BPF_OBJ"
    exit 1
fi

echo ""
echo "🚀 INSTRUCCIONES DE USO EN PRODUCCIÓN:"
echo "1. Para desviar cálculos decimales de cualquier proceso/script en userspace:"
echo "   export LD_PRELOAD=$SO_PATH"
echo "   python3 tu_script.py"
echo ""
echo "2. Para desviar binarios desde el Kernel Linux (Ring 0 eBPF):"
echo "   sudo bpftool prog load $BPF_OBJ /sys/fs/bpf/sentinel/float_detector type lsm autoattach"
echo ""
echo "✅ PAI-60 Math Diversion Pipeline listo."
