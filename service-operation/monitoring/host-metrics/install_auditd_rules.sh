#!/bin/bash
# Instala reglas persistentes de auditd en /etc/audit/rules.d/
set -euo pipefail

RULES_SRC="/home/jnovoas/sentinel/host-metrics/auditd_rules.conf"
RULES_DST="/etc/audit/rules.d/sentinel.rules"

if [[ $EUID -ne 0 ]]; then
  echo "[ERROR] Ejecuta como root: sudo $0"
  exit 1
fi

if [[ ! -f "$RULES_SRC" ]]; then
  echo "[ERROR] No existe $RULES_SRC"
  exit 1
fi

cp "$RULES_SRC" "$RULES_DST"
chmod 640 "$RULES_DST"

# Recargar reglas
if command -v augenrules >/dev/null 2>&1; then
  augenrules --load
else
  echo "[WARN] No se encontró augenrules; aplicando con auditctl"
  auditctl -R "$RULES_DST"
fi

# Verificar alguna regla aplicada
ausearch -k exec-watchdog -ts recent || true

echo "[OK] Reglas de auditd instaladas en $RULES_DST"
