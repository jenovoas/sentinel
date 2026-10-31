#!/usr/bin/env bash
# Restaura Alloy de Fenix a la configuración previa.
set -euo pipefail
LIVE=/home/jnovoas/proyectos/sentinel/service-operation/deploy/marte/alloy-fenix.alloy
STAGE=/home/jnovoas/proyectos/sentinel/service-operation/deploy/marte/staging-tenancy-20261031

install -m 644 "$STAGE/backup/alloy-fenix.alloy" "$LIVE"
docker restart sentinel-fenix-alloy >/dev/null
sleep 2
docker logs --tail 5 sentinel-fenix-alloy 2>&1 | tail -5
echo "Rollback Alloy Fenix OK."
