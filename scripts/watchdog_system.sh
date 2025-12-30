#!/bin/bash
# Sentinel Hardware Watchdog System
# Periodically "kicks" the hardware watchdog to indicate the system is alive.

WATCHDOG_DEV="/dev/watchdog"
INTERVAL=30

echo "[sentinel-watchdog] Starting hardware watchdog supervisor..."

if [ ! -c "$WATCHDOG_DEV" ]; then
    echo "[error] Watchdog device $WATCHDOG_DEV not found!"
    exit 1
fi

while true; do
    # Write a character to the watchdog device to reset the timer
    echo -n "V" > "$WATCHDOG_DEV"
    # echo "[sentinel-watchdog] Watchdog kicked at $(date)"
    sleep "$INTERVAL"
done
