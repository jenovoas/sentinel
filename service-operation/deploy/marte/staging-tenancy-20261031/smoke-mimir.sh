#!/usr/bin/env bash
set -uo pipefail
NAME=mimir-tenancy-test
VOL=mimir_tenancy_test
CFG=/opt/sentinel-marte/staging/tenancy-20261031/new/mimir.yml

docker rm -f "$NAME" >/dev/null 2>&1 || true
docker volume rm "$VOL" >/dev/null 2>&1 || true
docker volume create "$VOL" >/dev/null
docker run -d --name "$NAME" --network sentinel_marte_observability \
  -v "$CFG:/etc/mimir/mimir.yml:ro" \
  -v "$VOL:/data/mimir" \
  grafana/mimir:3.2.3 -config.file=/etc/mimir/mimir.yml >/dev/null

ready=""
for _ in $(seq 1 30); do
  ready=$(docker run --rm --network sentinel_marte_observability postgres:16-alpine \
    sh -c 'wget -qO- http://mimir-tenancy-test:9009/ready 2>/dev/null' || true)
  [ -n "$ready" ] && break
  sleep 1
done
echo "mimir_ready=$ready"

code_no=$(docker run --rm --network sentinel_marte_observability postgres:16-alpine \
  sh -c 'wget -qO- http://mimir-tenancy-test:9009/prometheus/api/v1/labels >/dev/null 2>&1 && echo 200 || echo 401')
code_yes=$(docker run --rm --network sentinel_marte_observability postgres:16-alpine \
  sh -c 'wget -qO- --header="X-Scope-OrgID: anonymous" http://mimir-tenancy-test:9009/prometheus/api/v1/labels >/dev/null 2>&1 && echo 200 || echo fail')
echo "mimir_without_header=$code_no mimir_with_header=$code_yes"
docker logs --tail 20 "$NAME" 2>&1 | tail -20
docker rm -f "$NAME" >/dev/null 2>&1 || true
docker volume rm "$VOL" >/dev/null 2>&1 || true
