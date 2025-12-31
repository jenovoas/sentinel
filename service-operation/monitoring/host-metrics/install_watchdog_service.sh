#!/bin/bash
set -euo pipefail

SERVICE_SRC="/home/jnovoas/sentinel/systemd/audit-watchdog.service"
SERVICE_DST="/etc/systemd/system/audit-watchdog.service"
SCRIPT_PATH="/home/jnovoas/sentinel/host-metrics/audit-watchdog.sh"

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
systemctl enable --now audit-watchdog.service

systemctl status audit-watchdog.service --no-pager || true

echo "[OK] Servicio audit-watchdog instalado y habilitado. Logs: journalctl -u audit-watchdog -f"
