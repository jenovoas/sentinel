#!/usr/bin/env bash
# Aplica multitenancy de Mimir/Loki en Marte con rollback preparado.
# Requisito previo: Fenix Alloy ya envía X-Scope-OrgID (ver apply-fenix-alloy.sh).
set -euo pipefail
BASE=/opt/sentinel-marte
STAGE=$BASE/staging/tenancy-20261031

[ "$(id -u)" -eq 0 ] || { echo "Ejecutar con sudo" >&2; exit 1; }
[ -f "$STAGE/new/loki.yml" ] || { echo "Falta staging en $STAGE" >&2; exit 1; }

# El rollback solo es válido si los backups coinciden con el estado vivo actual.
for pair in \
  "backup/mimir.yml:$BASE/mimir.yml" \
  "backup/loki.yml:$BASE/loki.yml" \
  "backup/datasources.yml:$BASE/grafana/datasources.yml" \
  "backup/alloy-marte.alloy:$BASE/alloy-marte.alloy"; do
  src="${pair%%:*}"
  dst="${pair#*:}"
  cmp -s "$STAGE/$src" "$dst" || {
    echo "Backup no coincide con $dst; refresca $STAGE/backup antes de aplicar." >&2
    exit 1
  }
done

if ! sudo -H -u jnovoas ssh -o BatchMode=yes -o ConnectTimeout=5 fenix \
  "grep -q 'X-Scope-OrgID' /home/jnovoas/proyectos/sentinel/service-operation/deploy/marte/alloy-fenix.alloy"; then
  echo "ERROR: ejecuta primero apply-fenix-alloy.sh (Alloy Fenix debe enviar X-Scope-OrgID)." >&2
  exit 1
fi

echo "[1/4] Alloy Marte con header; Loki aún sin auth"
install -m 644 -o root -g root "$STAGE/new/alloy-marte.alloy" "$BASE/alloy-marte.alloy"
(cd "$BASE" && docker compose up -d --force-recreate alloy >/dev/null)
sleep 3

echo "[2/4] Loki auth_enabled=true"
install -m 644 -o root -g root "$STAGE/new/loki.yml" "$BASE/loki.yml"
(cd "$BASE" && docker compose up -d --force-recreate loki >/dev/null)

echo "[3/4] Grafana datasources con X-Scope-OrgID"
install -m 644 -o root -g root "$STAGE/new/datasources.yml" "$BASE/grafana/datasources.yml"
(cd "$BASE" && docker compose up -d --force-recreate grafana >/dev/null)

echo "[4/4] Mimir multitenancy"
install -m 644 -o root -g root "$STAGE/new/mimir.yml" "$BASE/mimir.yml"
(cd "$BASE" && docker compose up -d --force-recreate mimir >/dev/null)

echo "Verificando..."
for _ in $(seq 1 30); do
  curl -fsS http://10.88.0.6:3100/ready >/dev/null 2>&1 && break
  sleep 1
done
code_no=$(curl -s -o /dev/null -w '%{http_code}' http://10.88.0.6:3100/loki/api/v1/labels)
code_yes=$(curl -s -o /dev/null -w '%{http_code}' -H 'X-Scope-OrgID: fake' http://10.88.0.6:3100/loki/api/v1/labels)
echo "Loki labels sin header=$code_no (esperado 401), con header=$code_yes (esperado 200)"
[ "$code_no" = "401" ] && [ "$code_yes" = "200" ] || {
  echo "Fallo Loki. Ejecuta: sudo $STAGE/rollback-marte.sh" >&2
  exit 1
}

mimir_code=$(docker run --rm --network sentinel_marte_observability postgres:16-alpine \
  sh -c 'wget -qO- --header="X-Scope-OrgID: anonymous" http://sentinel-marte-mimir:9009/prometheus/api/v1/labels >/dev/null && echo 200 || echo fail')
echo "Mimir labels con header=$mimir_code (esperado 200)"
[ "$mimir_code" = "200" ] || {
  echo "Fallo Mimir. Ejecuta: sudo $STAGE/rollback-marte.sh" >&2
  exit 1
}

ADMIN_PW="$(cat /etc/sentinel/grafana-admin-password)"
CURL_CFG="$(mktemp)"
trap 'rm -f "$CURL_CFG"' EXIT
printf 'user = "admin:%s"\n' "$ADMIN_PW" > "$CURL_CFG"
chmod 600 "$CURL_CFG"
for ds in loki mimir; do
  curl -fsS --config "$CURL_CFG" "http://10.88.0.6:3000/api/datasources/uid/$ds/health" >/dev/null
  echo "Grafana datasource $ds: healthy"
done
curl -fsS http://10.88.0.6:3000/api/health >/dev/null

echo "OK. Rollback: sudo $STAGE/rollback-marte.sh"
