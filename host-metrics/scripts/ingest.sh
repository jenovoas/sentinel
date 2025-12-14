#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
CONFIG="$ROOT_DIR/config.yaml"
CSV_PATH="$ROOT_DIR/data/metrics.csv"
URL="http://localhost:8000/api/v1/dashboard/status"

mkdir -p "$ROOT_DIR/data"

# Create CSV header if file not exists
if [ ! -f "$CSV_PATH" ]; then
  echo "timestamp,cpu_percent,mem_percent,gpu_percent,net_bytes_sent,net_bytes_recv,wifi_ssid,wifi_signal" > "$CSV_PATH"
fi

# Fetch JSON and append CSV row
resp=$(curl -s "$URL")
if [ -z "$resp" ]; then
  echo "Error: no response from backend" >&2
  exit 1
fi

# Parse fields with jq
timestamp=$(echo "$resp" | jq -r '.timestamp')
cpu=$(echo "$resp" | jq -r '.system.cpu_percent // 0')
mem=$(echo "$resp" | jq -r '.system.mem_percent // 0')
gpu=$(echo "$resp" | jq -r '.gpu.gpu_percent // 0')
sent=$(echo "$resp" | jq -r '.network.net_bytes_sent // 0')
recv=$(echo "$resp" | jq -r '.network.net_bytes_recv // 0')
ssid=$(echo "$resp" | jq -r '.network.wifi.ssid // ""')
signal=$(echo "$resp" | jq -r '.network.wifi.signal // 0')

# Append CSV line
printf "%s,%s,%s,%s,%s,%s,%s,%s\n" "$timestamp" "$cpu" "$mem" "$gpu" "$sent" "$recv" "$ssid" "$signal" >> "$CSV_PATH"

echo "✓ Sample ingested into $CSV_PATH"
