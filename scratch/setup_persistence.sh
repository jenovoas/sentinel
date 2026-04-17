#!/bin/bash
set -e

SERVICES=(
    "sentinel-postgres"
    "sentinel-redis"
    "sentinel-backend"
    "sentinel-nginx"
    "sentinel-frontend"
    "sentinel-prometheus"
    "sentinel-loki"
    "sentinel-promtail"
    "sentinel-grafana"
    "sentinel-node-exporter"
    "sentinel-postgres-exporter"
    "sentinel-redis-exporter"
    "sentinel-n8n"
    "sentinel-neural-guard"
)

echo "Generating systemd units for all Sentinel services..."
for SERVICE in "${SERVICES[@]}"; do
    echo "Processing $SERVICE..."
    podman generate systemd --new --name "$SERVICE" > ~/.config/systemd/user/container-"$SERVICE".service
done

echo "Reloading systemd..."
systemctl --user daemon-reload

echo "Enabling all Sentinel services..."
for SERVICE in "${SERVICES[@]}"; do
    systemctl --user enable container-"$SERVICE".service
done

# Ensure lingering is enabled for the user so services start without login
echo "Enabling linger for jnovoas..."
loginctl enable-linger jnovoas || echo "Warning: Could not enable linger. Ensure you have permissions."

echo "Stack persistence setup complete."
