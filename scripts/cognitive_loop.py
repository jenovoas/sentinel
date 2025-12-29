#!/usr/bin/env python3
"""
Guardian-Alpha Cognitive Loop
Monitors kernel events and uses AI to make security decisions.
Integrated with sentinel_core modules.
"""
import sys
import os

# Add sentinel to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sentinel_core.brain.inference import SentinelBrain
from sentinel_core.ebpf.map_manager import MapManager

TRACE_PIPE = "/sys/kernel/debug/tracing/trace_pipe"


def main():
    print("🧠 Guardian-Alpha Cognitive Loop Started...")
    print(f"📡 Monitoring: {TRACE_PIPE}")
    print("-" * 50)
    
    # Initialize AI Brain and Map Manager
    brain = SentinelBrain()
    map_manager = MapManager()

    try:
        with open(TRACE_PIPE, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if "Guardian [BLOCK]" in line:
                    # Extract filename
                    try:
                        parts = line.split("Unknown binary ")
                        if len(parts) > 1:
                            filename = parts[1].strip()
                            
                            print(f"🔍 [Monitor] Detectado bloqueo: {filename}")
                            
                            # Use real AI Brain
                            should_allow = brain.analyze_threat(filename)
                            
                            if should_allow:
                                print(f"🛡️  [Brain] Decisión: PERMITIR '{filename}'")
                                if map_manager.whitelist_binary(filename):
                                    print(f"✅ [Kernel] Whitelist actualizada.")
                                else:
                                    print(f"❌ [Kernel] Error actualizando whitelist")
                            else:
                                print(f"🚫 [Brain] Decisión: BLOQUEO CONFIRMADO para '{filename}'")
                    except Exception as e:
                        print(f"⚠️ Error parsing line: {e}")
    except PermissionError:
        print("❌ Error: Requires root permissions to read trace_pipe.")
        print("Run with: sudo python3 cognitive_loop.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Cognitive Loop stopped by user.")


if __name__ == "__main__":
    main()
