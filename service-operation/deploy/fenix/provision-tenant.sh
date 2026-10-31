#!/usr/bin/env bash
# Orquesta el alta/baja de un tenant: AD (Fenix) + org/mapping Grafana (Marte).
# Uso: provision-tenant.sh <tenant-id> [--admin <usuario>]... [--project <project-id>]...
#      provision-tenant.sh <tenant-id> --remove
# No crea el tenant/membresías en PostgreSQL: eso lo hace el portal y luego llama aquí.
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Ejecutar como root" >&2; exit 1; }
[ "$#" -ge 1 ] || { echo "Uso: $0 <tenant-id> [--admin ...] [--project ...] | --remove" >&2; exit 1; }

TENANT_ID="$1"
shift

if [ "${1:-}" = "--remove" ]; then
  ssh -i /home/jnovoas/.ssh/id_ed25519 -p 4222 \
    -o BatchMode=yes -o StrictHostKeyChecking=accept-new \
    -o UserKnownHostsFile=/home/jnovoas/.ssh/known_hosts \
    jnovoas@marte \
    "sudo -n /opt/sentinel-marte/grafana/provision-tenant.sh '$TENANT_ID' --remove"
  echo "Tenant ${TENANT_ID}: mapping, dashboard y datasource de Grafana eliminados; org conservada."
  exit 0
fi

/usr/local/sbin/provision-tenant-ad.sh "$TENANT_ID" "$@"

ssh -i /home/jnovoas/.ssh/id_ed25519 -p 4222 \
  -o BatchMode=yes -o StrictHostKeyChecking=accept-new \
  -o UserKnownHostsFile=/home/jnovoas/.ssh/known_hosts \
  jnovoas@marte \
  "sudo -n /opt/sentinel-marte/grafana/provision-tenant.sh '$TENANT_ID'"

echo "Tenant ${TENANT_ID}: AD y Grafana provisionados."
