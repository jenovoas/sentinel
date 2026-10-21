#!/bin/bash
# sentinel-health.sh — chequeo unificado de fénix (reemplaza startup.sh obsoleto
# y healthcheck.sh orientado al stack viejo).
# Cubre: servicios OpenRC sentinel-*, stack docker, endpoints HTTP, eBPF
# (links+pins), verificador y recursos. Sale 0 solo si todo está OK.
# Uso: scripts/sentinel-health.sh [--quiet]

QUIET=0
[ "${1:-}" = "--quiet" ] && QUIET=1
ok=0; fail=0
say() { [ "$QUIET" -eq 0 ] && echo "$1"; }
pass() { ok=$((ok+1)); say "  ✅ $1"; }
miss() { fail=$((fail+1)); say "  ❌ $1"; }

say "== OpenRC (sentinel-*) =="
for s in $(rc-service -l 2>/dev/null | grep '^sentinel-'); do
    if rc-service "$s" status >/dev/null 2>&1; then pass "$s started"; else miss "$s NO started"; fi
done

say "== Docker stack =="
if sudo docker ps --format '{{.Names}}' 2>/dev/null | grep -q sentinel-postgres; then
    n=$(sudo docker ps --format '{{.Names}}' 2>/dev/null | grep -c sentinel-)
    pass "contenedores sentinel Up: $n"
else
    miss "stack sentinel caído"
fi

say "== Endpoints =="
probe() { # probe <url> <nombre> [codigo]
    code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$1" 2>/dev/null)
    if [ "$code" = "${3:-200}" ]; then pass "$2 ($code)"; else miss "$2 (HTTP $code)"; fi
}
probe "http://127.0.0.1:8000/api/v1/ai/health" "cortex /ai/health"
probe "http://127.0.0.1:8000/api/v1/lattice/hologram" "cortex /hologram"
probe "http://127.0.0.1:8010/health" "orchestrator /health" 401
probe "http://127.0.0.1:3000/api/health" "grafana /api/health"
# Loki comparte :3100 del host con el frontend; se sondea dentro del contenedor.
if sudo docker exec sentinel-loki wget -q -O - "http://127.0.0.1:3100/loki/api/v1/query?query=%7Bjob%3D%22syslog%22%7D&limit=1" 2>/dev/null | grep -q '"status":"success"'; then
    pass "loki query instantánea"
else
    miss "loki query instantánea"
fi
say "== eBPF =="
links=$(sudo bpftool link show 2>/dev/null | grep -c "lsm \|xdp \|tc ")
[ "$links" -ge 5 ] && pass "links BPF activos: $links" || miss "links BPF: $links (esperado >=5)"
[ -e /sys/fs/bpf/cortex_events ] && pass "pin cortex_events" || miss "pin cortex_events ausente"
[ -e /sys/fs/bpf/sentinel/whitelist_map ] && pass "pin whitelist_map" || miss "pin whitelist_map ausente"

say "== Verificador (último ciclo) =="
last=$(sudo tail -n 1 /var/log/sentinel/verifier.log 2>/dev/null)
if echo "$last" | grep -qE '"fail": ?0'; then
    pass "verificador $(echo "$last" | grep -oE '"ok": ?[0-9]+' | head -n 1)[fails 0]"
else
    miss "verificador: $(echo "$last" | grep -oE '"ok": ?[0-9]+,"fail": ?[0-9]+' | head -c 40)"
fi

say "== Recursos =="
load=$(cut -d' ' -f1 /proc/loadavg)
disk=$(df / 2>/dev/null | awk 'NR==2{gsub(/%/,"",$5); print $5}')
say "  load=$load disk=${disk}%"
[ "${disk:-100}" -lt 85 ] && pass "disco <85%" || miss "disco >=85%"

say "== Resultado: OK=$ok FAIL=$fail =="
[ "$fail" -eq 0 ]
