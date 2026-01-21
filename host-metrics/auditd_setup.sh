#!/bin/bash
# Setup de auditd y reglas watchdog (Arch/Manjaro)
set -euo pipefail

if ! command -v pacman >/dev/null 2>&1; then
  echo "[ERROR] Este script está pensado para Arch/Manjaro (pacman). Usa tu gestor de paquetes equivalente."
  exit 1
fi

if [[ $EUID -ne 0 ]]; then
  echo "[ERROR] Ejecuta como root: sudo $0"
  exit 1
fi

echo "Instalando audit..."
pacman -Sy --noconfirm audit

echo "Habilitando y arrancando auditd..."
systemctl enable --now auditd

# Reglas básicas watchdog
echo "Aplicando reglas watchdog..."
auditctl -a always,exit -F arch=b64 -S execve -k exec-watchdog
auditctl -a always,exit -F arch=b64 -S open -F success=0 -k file-watchdog
auditctl -a always,exit -F arch=b64 -S ptrace -k ptrace-watchdog

# Mostrar estado
augenrules --load || true
ausearch -k exec-watchdog -ts recent || true

echo "Listo. Ejecuta watchdog: host-metrics/audit-watchdog.sh"
