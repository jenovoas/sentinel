#!/bin/bash

# Script de monitoreo del sistema para diagnosticar bloqueos
# Uso: ./monitor_system.sh

echo "=== MONITOR DEL SISTEMA ==="
echo "Presiona Ctrl+C para salir"
echo ""

while true; do
    clear
    echo "=== TEMPERATURA CPU ==="
    sensors | grep -E "Package|Core|temp1" | head -6
    
    echo ""
    echo "=== USO DE MEMORIA ==="
    free -h | grep -E "Mem:|Swap:"
    
    echo ""
    echo "=== PROCESOS MÁS PESADOS (Top 5) ==="
    ps aux --sort=-%mem | head -6 | awk '{printf "%-10s %5s %5s %s\n", $1, $3, $4, $11}'
    
    echo ""
    echo "=== CARGA DEL SISTEMA ==="
    uptime
    
    echo ""
    echo "Actualizado: $(date '+%H:%M:%S')"
    echo "Próxima actualización en 3 segundos..."
    
    sleep 3
done
