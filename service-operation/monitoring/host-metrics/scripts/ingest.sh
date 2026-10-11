#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
CSV_PATH="$ROOT_DIR/data/metrics.csv"

mkdir -p "$ROOT_DIR/data"

# Create CSV header if file not exists
if [ ! -f "$CSV_PATH" ]; then
  echo "timestamp,cpu_percent,mem_percent,gpu_percent,net_bytes_sent,net_bytes_recv,wifi_ssid,wifi_signal" > "$CSV_PATH"
fi

# Timestamp in ISO8601
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")

# CPU usage (idle from top, calculate busy)
cpu_idle=$(top -bn1 | grep "Cpu(s)" | awk '{print $8}' | cut -d'%' -f1)
cpu=$(awk "BEGIN {printf \"%.1f\", 100 - $cpu_idle}")

# Memory usage (percentage)
mem=$(free | grep Mem | awk '{printf "%.1f", ($3/$2) * 100.0}')

# GPU usage (NVIDIA only, fallback to 0)
gpu=0
if command -v nvidia-smi &> /dev/null; then
  gpu=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null | head -n1 || echo "0")
fi

# Network bytes (accumulated from all interfaces)
sent=0
recv=0
for iface in /sys/class/net/*; do
  if [ -f "$iface/statistics/tx_bytes" ] && [ -f "$iface/statistics/rx_bytes" ]; then
    iface_name=$(basename "$iface")
    # Skip loopback and docker interfaces
    if [[ "$iface_name" != "lo" ]] && [[ "$iface_name" != docker* ]] && [[ "$iface_name" != veth* ]]; then
      sent=$((sent + $(cat "$iface/statistics/tx_bytes")))
      recv=$((recv + $(cat "$iface/statistics/rx_bytes")))
    fi
  fi
done

# WiFi info (nmcli preferred, iwconfig fallback)
ssid=""
signal=0
if command -v nmcli &> /dev/null; then
  wifi_info=$(nmcli -t -f active,ssid,signal dev wifi | grep "^sí" | head -n1)
  if [ -n "$wifi_info" ]; then
    ssid=$(echo "$wifi_info" | cut -d':' -f2)
    signal=$(echo "$wifi_info" | cut -d':' -f3)
  fi
elif command -v iwconfig &> /dev/null; then
  wifi_dev=$(iwconfig 2>/dev/null | grep -oP '^\w+(?=\s+IEEE)')
  if [ -n "$wifi_dev" ]; then
    ssid=$(iwconfig "$wifi_dev" 2>/dev/null | grep -oP 'ESSID:"\K[^"]+' || echo "")
    signal_dbm=$(iwconfig "$wifi_dev" 2>/dev/null | grep -oP 'Signal level=\K-?\d+' || echo "-100")
    # Convert dBm to approximate percentage (rough approximation)
    signal=$(awk "BEGIN {s = ($signal_dbm + 100) * 2; if (s < 0) s = 0; if (s > 100) s = 100; printf \"%.0f\", s}")
  fi
fi

# Append CSV line
printf "%s,%s,%s,%s,%s,%s,%s,%s\n" "$timestamp" "$cpu" "$mem" "$gpu" "$sent" "$recv" "$ssid" "$signal" >> "$CSV_PATH"

echo "✓ Host metrics ingested into $CSV_PATH"
