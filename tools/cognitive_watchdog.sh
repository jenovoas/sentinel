#!/bin/bash
# Sentinel Cognitive Watchdog
# Monitors AI memory usage and alerts if critical

THRESHOLD_MB=4096 # 4GB
CHECK_INTERVAL=10

while true; do
    # Get Ollama Memory Usage (RSS)
    MEM_ usage=$(ps -C ollama -o rss= | awk '{sum+=$1} END {print sum/1024}')
    
    if (( $(echo "$MEM_usage > $THRESHOLD_MB" | bc -l) )); then
        # Critical Alert via GUI Notification (notify-send)
        notify-send -u critical "🧠 COGNITIVE OVERLOAD" "AI Memory Usage: ${MEM_usage}MB. Sentinel throttling enabled."
        
        # Optional: Throttling Logic here (cgroups)
        # echo "20000" > /sys/fs/cgroup/memory/sentinel_ai/memory.limit_in_bytes
    fi
    
    sleep $CHECK_INTERVAL
done
