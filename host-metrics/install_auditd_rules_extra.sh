#!/bin/bash
# Instala o quita reglas extra de auditd para laboratorio
set -euo pipefail

EXTRA_SRC="/home/jnovoas/sentinel/host-metrics/auditd_rules_extra.conf"
EXTRA_DST="/etc/audit/rules.d/sentinel-extra.rules"

usage() {
  echo "Uso: sudo $0 [install|remove]"
}

if [[ $EUID -ne 0 ]]; then
  echo "[ERROR] Ejecuta como root: sudo $0"
  exit 1
fi

ACTION=${1:-install}
case "$ACTION" in
  install)
    [[ -f "$EXTRA_SRC" ]] || { echo "[ERROR] No existe $EXTRA_SRC"; exit 1; }
    cp "$EXTRA_SRC" "$EXTRA_DST"
    chmod 640 "$EXTRA_DST"
    if command -v augenrules >/dev/null 2>&1; then
      augenrules --load
    else
      auditctl -R "$EXTRA_DST"
    fi
    echo "[OK] Reglas extra instaladas en $EXTRA_DST"
    ;;
  remove)
    rm -f "$EXTRA_DST"
    if command -v augenrules >/dev/null 2>&1; then
      augenrules --load
    else
      auditctl -D
    fi
    echo "[OK] Reglas extra removidas"
    ;;
  *)
    usage
    exit 1
    ;;
esac
