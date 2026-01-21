#!/bin/bash
# Script para exponer métricas de procesos a Node Exporter (textfile collector)
# Se ejecuta cada 60 segundos y genera prom file

OUTPUT_DIR="${1:-/var/lib/node_exporter/textfile_collector}"
PROM_FILE="$OUTPUT_DIR/processes.prom"

mkdir -p "$OUTPUT_DIR"

{
  echo "# HELP process_memory_rss_bytes RSS memory per process"
  echo "# TYPE process_memory_rss_bytes gauge"
  
  for proc_dir in /proc/[0-9]*; do
    pid=$(basename "$proc_dir")
    if [[ -r "$proc_dir/status" ]]; then
      name=$(grep "^Name:" "$proc_dir/status" 2>/dev/null | awk '{print $2}' | head -1)
      rss=$(grep "^VmRSS:" "$proc_dir/status" 2>/dev/null | awk '{print $2}' | head -1)
      if [[ -n "$rss" && -n "$name" ]]; then
        # Convertir KB a bytes
        rss_bytes=$((rss * 1024))
        echo "process_memory_rss_bytes{pid=\"$pid\",name=\"$name\"} $rss_bytes"
      fi
    fi
  done
} > "$PROM_FILE.tmp"

mv "$PROM_FILE.tmp" "$PROM_FILE"
