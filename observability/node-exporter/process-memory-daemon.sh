#!/bin/bash
# Ejecutar script de métricas de procesos cada 60 segundos
# Asumir que /var/lib/node_exporter/textfile_collector está montado o disponible en el host

SCRIPT="/home/jnovoas/sentinel/observability/node-exporter/process-memory.sh"
OUTPUT_DIR="/var/lib/node_exporter/textfile_collector"

mkdir -p "$OUTPUT_DIR"

while true; do
  "$SCRIPT" "$OUTPUT_DIR" 2>/dev/null || echo "[WARN] Error ejecutando $SCRIPT"
  sleep 60
done
