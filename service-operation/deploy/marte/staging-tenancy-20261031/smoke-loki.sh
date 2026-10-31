#!/usr/bin/env bash
set -uo pipefail
NAME=loki-tenancy-test
VOL=loki_tenancy_test
CFG=/opt/sentinel-marte/staging/tenancy-20261031/new/loki.yml

docker rm -f "$NAME" >/dev/null 2>&1 || true
docker volume rm "$VOL" >/dev/null 2>&1 || true
docker volume create "$VOL" >/dev/null
docker run -d --name "$NAME" --network sentinel_marte_observability \
  -v "$CFG:/etc/loki/loki.yml:ro" \
  -v "$VOL:/loki" \
  grafana/loki:3.7.0 -config.file=/etc/loki/loki.yml >/dev/null

ready=""
for _ in $(seq 1 30); do
  ready=$(docker run --rm --network sentinel_marte_observability postgres:16-alpine \
    sh -c 'wget -qO- http://loki-tenancy-test:3100/ready 2>/dev/null' || true)
  [ -n "$ready" ] && break
  sleep 1
done
echo "loki_ready=$ready"

code_no=$(docker run --rm --network sentinel_marte_observability postgres:16-alpine \
  sh -c 'wget -qO- http://loki-tenancy-test:3100/loki/api/v1/labels >/dev/null 2>&1 && echo 200 || echo 401')
code_yes=$(docker run --rm --network sentinel_marte_observability postgres:16-alpine \
  sh -c 'wget -qO- --header="X-Scope-OrgID: fake" http://loki-tenancy-test:3100/loki/api/v1/labels >/dev/null 2>&1 && echo 200 || echo fail')
echo "loki_without_header=$code_no loki_with_header=$code_yes"
docker logs --tail 15 "$NAME" 2>&1 | tail -15
docker rm -f "$NAME" >/dev/null 2>&1 || true
docker volume rm "$VOL" >/dev/null 2>&1 || true
