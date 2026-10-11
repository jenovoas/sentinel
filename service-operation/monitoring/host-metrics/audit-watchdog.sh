#!/bin/bash
set -euo pipefail

echo "🔍 Watchdog activo - Detectando exploits..."

if [[ $EUID -ne 0 ]]; then
  echo "[WARN] Se recomienda ejecutar como root para leer /var/log/audit/audit.log"
fi

LOG_FILE="/var/log/audit/audit.log"
if [[ ! -f "$LOG_FILE" ]]; then
  echo "[ERROR] No existe $LOG_FILE. ¿auditd está instalado y corriendo?"
  echo "Sugerencia: sudo systemctl status auditd"
  exit 1
fi

# Configuración de Pánico
THRESHOLD=100
WINDOW=60
COUNTER=0
LAST_RESET=$(date +%s)

tail -F "$LOG_FILE" | grep -E "(exec-watchdog|file-watchdog|ptrace-watchdog)" | while read -r line; do
  NOW=$(date +%s)
  
  # Reset del contador si el tiempo ha pasado
  if [ $((NOW - LAST_RESET)) -gt "$WINDOW" ]; then
    COUNTER=0
    LAST_RESET=$NOW
  fi

  echo "🚨 ALERTA: $(date): $line"
  
  if echo "$line" | grep -q "type=SYSCALL.*syscall=execve.*uid=[1-9]"; then
    ((COUNTER++))
    echo "💥 EXPLOIT DETECTADO [$COUNTER/$THRESHOLD]!"
    
    if [ "$COUNTER" -ge "$THRESHOLD" ]; then
      echo "🛑 ATAQUE MASIVO DETECTADO. ACTIVANDO PÁNICO..."
      echo "🔥 REINICIANDO SISTEMA POR SEGURIDAD..."
      /usr/sbin/reboot
    fi

    if command -v systemctl >/dev/null 2>&1; then
      sudo systemctl restart auditd || echo "[WARN] No se pudo reiniciar auditd"
    fi
  fi
done
