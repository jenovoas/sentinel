#!/bin/bash
# Sentinel Core Launcher with Trace Pipe Access
# This script solves the permission issue by using sudo only for trace_pipe reading

echo "🛡️  [Launcher] Iniciando Sentinel Core con permisos adecuados..."

# Start tailing trace_pipe with sudo and pipe to our Python monitor
sudo tail -f /sys/kernel/debug/tracing/trace_pipe | python3 -c "
import sys
import os
sys.path.insert(0, os.path.expanduser('~/sentinel'))

from sentinel_core.brain.inference import SentinelBrain
from sentinel_core.ebpf.map_manager import MapManager

print('🧠 [SentinelBrain] Conectando a Ollama Local: phi3:mini')
brain = SentinelBrain()
map_manager = MapManager()

print('📡 [Monitor] Escuchando eventos desde trace_pipe...')

for line in sys.stdin:
    if 'Guardian [BLOCK]' in line:
        try:
            parts = line.split('Unknown binary ')
            if len(parts) > 1:
                filename = parts[1].strip()
                print(f'🔍 [Monitor] Detectado bloqueo: {filename}')
                
                should_allow = brain.analyze_threat(filename)
                
                if should_allow:
                    print(f'🛡️  [Brain] Decisión: PERMITIR \"{filename}\"')
                    if map_manager.whitelist_binary(filename):
                        print(f'✅ [Kernel] Whitelist actualizada.')
                else:
                    print(f'🚫 [Brain] Decisión: BLOQUEO CONFIRMADO para \"{filename}\"')
        except Exception as e:
            print(f'⚠️ [Monitor] Error: {e}')
"
