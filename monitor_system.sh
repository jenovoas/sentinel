#!/bin/bash
while true; do
    MEM=$(free -m | awk '/Mem:/ { print $3 }')
    TOTAL=$(free -m | awk '/Mem:/ { print $2 }')
    PCT=$(( 100 * MEM / TOTAL ))
    echo "$(date): Memoria en uso: ${MEM}MB (${PCT}%)"
    if [ $PCT -gt 90 ]; then
        echo "🚨 ALERTA: Memoria crítica! Intentando liberar cache..."
        sync; sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"
    fi
    sleep 30
done
