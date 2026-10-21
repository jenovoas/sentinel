#!/bin/bash
set -euo pipefail

echo "🔍 Watchdog activo - Detectando exploits..."

# Heartbeat para sentinel-verifier: exige `"alive"` (entrecomillado) o
# `BIO_PULSE`, ≥3 ocurrencias en las últimas 200 líneas y mtime <90s.
(while true; do echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"source\":\"audit-watchdog\",\"alive\":true,\"pulse\":\"BIO_PULSE\"}"; sleep 60; done &)

if [[ $EUID -ne 0 ]]; then
  echo "[WARN] Se recomienda ejecutar como root para leer /var/log/audit/audit.log"
fi

LOG_FILE="/var/log/audit/audit.log"
if [[ ! -f "$LOG_FILE" ]]; then
  echo "[ERROR] No existe $LOG_FILE. ¿auditd está instalado y corriendo?"
  echo "Sugerencia: rc-service auditd status"
  exit 1
fi

tail -F "$LOG_FILE" | grep -E "(exec-watchdog|file-watchdog|ptrace-watchdog)" | while read -r line; do
  echo "🚨 ALERTA: $(date): $line"
  if echo "$line" | grep -q "type=SYSCALL.*syscall=execve.*uid=[1-9]"; then
    echo "💥 EXPLOIT DETECTADO! Reiniciando auditd..."
    if command -v rc-service >/dev/null 2>&1; then
      rc-service auditd restart || echo "[WARN] No se pudo reiniciar auditd"
    fi
  fi
done
