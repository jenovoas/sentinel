#!/bin/bash
# Sentinel Pressure Injector - Simula una ráfaga de ejecuciones para estresar el Ringbuffer
echo "🚀 Iniciando ráfaga de presión (Quantum Pressure)..."
for i in {1..5000}; do
    /usr/bin/true & 
done
wait
echo "✅ Ráfaga de 5000 ejecuciones completada."
