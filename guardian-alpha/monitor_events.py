#!/usr/bin/env python3
"""
Sentinel Event Monitor - Slow Mode
Shows events at readable speed with statistics
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import sys
import os
import time
from collections import Counter, deque

TRACE_PIPE = "/sys/kernel/debug/tracing/trace_pipe"

# Configuration
EVENTS_PER_SECOND = 5  # Limit to 5 events/sec for readability
STATS_INTERVAL = 10    # Print stats every 10 seconds

def main():
    print("📊 Sentinel Event Monitor (Slow Mode)")
    print(f"   Rate limit: {EVENTS_PER_SECOND} events/sec")
    print(f"   Stats every: {STATS_INTERVAL}s")
    print("")
    
    if not os.path.exists(TRACE_PIPE):
        print(f"❌ Error: {TRACE_PIPE} not found")
        sys.exit(1)
    
    event_count = 0
    action_counts = Counter()
    score_samples = deque(maxlen=100)
    last_event_time = 0
    last_stats_time = time.time()
    
    min_interval = S60(1, 0, 0) / EVENTS_PER_SECOND
    
    try:
        with open(TRACE_PIPE, "r", encoding="utf-8", errors="ignore") as pipe:
            print("✅ Connected. Monitoring events...\n")
            
            for line in pipe:
                if "QUANTUM-AI Decision" not in line:
                    continue
                
                # Rate limiting
                now = time.time()
                if now - last_event_time < min_interval:
                    continue
                
                last_event_time = now
                event_count += 1
                
                # Parse event
                parts = line.split("QUANTUM-AI Decision:")
                if len(parts) < 2:
                    continue
                
                decision = parts[1].strip()
                
                # Extract action and score
                action = "UNKNOWN"
                score = 0
                
                if "action=" in decision:
                    action_str = decision.split("action=")[1].split()[0]
                    action_num = int(action_str)
                    action = ["ALLOW", "MONITOR", "BLOCK"][action_num]
                    action_counts[action] += 1
                
                if "score=" in decision:
                    score_str = decision.split("score=")[1].split()[0]
                    score = int(score_str)
                    score_samples.append(score)
                
                # Display event
                emoji = "✅" if action == "ALLOW" else "👀" if action == "MONITOR" else "🚨"
                print(f"{emoji} Event #{event_count}: {action} (score={score})")
                
                # Print stats periodically
                if now - last_stats_time > STATS_INTERVAL:
                    print("\n" + "="*60)
                    print(f"📊 Statistics (last {STATS_INTERVAL}s)")
                    print(f"   Total events: {event_count}")
                    print(f"   Actions: {dict(action_counts)}")
                    if score_samples:
                        avg_score = sum(score_samples) / len(score_samples)
                        print(f"   Avg score: {avg_score:.1f}")
                        print(f"   Score range: {min(score_samples)}-{max(score_samples)}")
                    print("="*60 + "\n")
                    last_stats_time = now
                
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("📊 Final Statistics")
        print(f"   Total events: {event_count}")
        print(f"   Actions: {dict(action_counts)}")
        if score_samples:
            avg_score = sum(score_samples) / len(score_samples)
            print(f"   Avg score: {avg_score:.1f}")
            print(f"   Score range: {min(score_samples)}-{max(score_samples)}")
        print("="*60)
        print("\n🔌 Disconnected")

if __name__ == "__main__":
    main()
