#!/usr/bin/env bash
# Failover / Switch de tráfico Sentinel (Fenix <-> Marte) en Kingu Nginx.
# Uso: switch-backend-traffic.sh [fenix|marte|status]
# Ejecutar como root o vía sudo en Kingu.
set -euo pipefail

NGINX_SENTINEL_CONF="/etc/nginx/sites-available/sentinel.pinguinoseguro.cl"
if [ ! -f "$NGINX_SENTINEL_CONF" ]; then
  NGINX_SENTINEL_CONF="/etc/nginx/conf.d/sentinel.conf"
fi

show_status() {
  echo "=== Estado actual de upstream en Kingu ==="
  grep -E "proxy_pass http://10\.88\.0\." /etc/nginx/ -rn 2>/dev/null || true
}

ACTION="${1:-status}"

case "$ACTION" in
  status)
    show_status
    ;;
  marte)
    echo "Conmutando backend a Marte (10.88.0.6:8000)..."
    sed -i -E 's|proxy_pass http://10\.88\.0\.1:800[01]|proxy_pass http://10.88.0.6:8000|g' /etc/nginx/sites-enabled/*
    nginx -t
    systemctl reload nginx
    echo "Tráfico conmutado a Marte exitosamente."
    ;;
  fenix)
    echo "Restableciendo backend a Fenix (10.88.0.1)..."
    sed -i -E 's|proxy_pass http://10\.88\.0\.6:8000|proxy_pass http://10.88.0.1:8001|g' /etc/nginx/sites-enabled/*
    nginx -t
    systemctl reload nginx
    echo "Tráfico restablecido a Fenix exitosamente."
    ;;
  *)
    echo "Uso: $0 [fenix|marte|status]" >&2
    exit 1
    ;;
esac
