#!/usr/bin/env bash
# Actualiza Alloy de Fenix para enviar X-Scope-OrgID=fake a Loki.
# Es seguro antes de activar auth en Loki: el header se ignora mientras auth_enabled=false.
set -euo pipefail
LIVE=/home/jnovoas/proyectos/sentinel/service-operation/deploy/marte/alloy-fenix.alloy
STAGE=/home/jnovoas/proyectos/sentinel/service-operation/deploy/marte/staging-tenancy-20261031

install -m 644 "$STAGE/new/alloy-fenix.alloy" "$LIVE"
docker restart sentinel-fenix-alloy >/dev/null
sleep 2
docker logs --tail 5 sentinel-fenix-alloy 2>&1 | tail -5
echo "Alloy Fenix actualizado. Verifica que siga enviando logs a Loki."
