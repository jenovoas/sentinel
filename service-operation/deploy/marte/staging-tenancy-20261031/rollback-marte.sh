#!/usr/bin/env bash
# Restaura la configuración previa a la multitenancy de Mimir/Loki en Marte.
set -euo pipefail
BASE=/opt/sentinel-marte
STAGE=$BASE/staging/tenancy-20261031

[ "$(id -u)" -eq 0 ] || { echo "Ejecutar con sudo" >&2; exit 1; }

install -m 644 -o root -g root "$STAGE/backup/mimir.yml" "$BASE/mimir.yml"
install -m 644 -o root -g root "$STAGE/backup/loki.yml" "$BASE/loki.yml"
install -m 644 -o root -g root "$STAGE/backup/datasources.yml" "$BASE/grafana/datasources.yml"
install -m 644 -o root -g root "$STAGE/backup/alloy-marte.alloy" "$BASE/alloy-marte.alloy"

(cd "$BASE" && docker compose up -d --force-recreate alloy loki mimir grafana >/dev/null)

for _ in $(seq 1 30); do
  curl -fsS http://10.88.0.6:3100/ready >/dev/null 2>&1 && break
  sleep 1
done
curl -fsS http://10.88.0.6:3100/loki/api/v1/labels >/dev/null
curl -fsS http://10.88.0.6:3000/api/health >/dev/null

echo "Rollback Marte OK: Loki sin auth y Mimir single-tenant."
