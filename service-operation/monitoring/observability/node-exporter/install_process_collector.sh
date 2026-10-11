#!/bin/bash
# Instala y habilita el daemon de colección de métricas de procesos
set -euo pipefail

SERVICE_SRC="/home/jnovoas/sentinel/systemd/process-memory-collector.service"
SERVICE_DST="/etc/systemd/system/process-memory-collector.service"
SCRIPT_PATH="/home/jnovoas/sentinel/observability/node-exporter/process-memory-daemon.sh"

if [[ $EUID -ne 0 ]]; then
  echo "[ERROR] Ejecuta como root: sudo $0"
  exit 1
fi

if [[ ! -f "$SCRIPT_PATH" ]]; then
  echo "[ERROR] No existe $SCRIPT_PATH"
  exit 1
fi

if [[ ! -f "$SERVICE_SRC" ]]; then
  echo "[ERROR] No existe $SERVICE_SRC"
  exit 1
fi

cp "$SERVICE_SRC" "$SERVICE_DST"
chmod 644 "$SERVICE_DST"

systemctl daemon-reload
systemctl enable --now process-memory-collector.service

systemctl status process-memory-collector.service --no-pager || true

echo "[OK] Daemon de colección de procesos instalado y habilitado."
echo "Logs: journalctl -u process-memory-collector -f"
