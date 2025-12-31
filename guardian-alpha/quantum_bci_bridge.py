#!/usr/bin/env python3
import sys
import os
import re
import time

# --- Configuration ---
TRACE_PIPE = "/sys/kernel/debug/tracing/trace_pipe"

# --- Import Sentinel Core ---
# Adjust path to find sentinel_core
current_dir = os.path.dirname(os.path.abspath(__file__))
core_path = os.path.abspath(os.path.join(current_dir, "../src/core"))
sys.path.append(core_path)

try:
    from sentinel_core.brain.bci_controller import bci_controller
    print("✅ [BRIDGE] Sentinel BCI Controller connected.")
except ImportError as e:
    print(f"❌ [BRIDGE] Failed to import BCI Controller: {e}")
    sys.exit(1)

def handle_log_line(line):
    """Parses a kernel log line and triggers BCI events."""
    line = line.strip()
    
    # Example Log: "QUANTUM-AI BLOCK: score=85, residue=11"
    match_block = re.search(r"QUANTUM-AI BLOCK: score=(\d+), residue=(\d+)", line)
    
    if match_block:
        score = int(match_block.group(1))
        residue = int(match_block.group(2))
        
        print(f"🚨 [KERNEL DETECT] THREAT BLOCKED! Score: {score}, Base-60 Residue: {residue}")
        
        # 1. Trigger Audio Qualia
        bci_controller.trigger_qualia("KERNEL_BLOCK")
        
        # 2. Reinforce with Base-60 Mathematical feedback (optional, async)
        # We assume bci_controller handles threading/async internally or is fast enough.
        # Ideally, playing a tone usually blocks, so be careful. 
        # Check if play_base60_pattern is non-blocking or short.
        # For now, we prioritize the alert.
        time.sleep(0.1) 
        bci_controller.play_base60_pattern(residue)
        return

    # Check for MONITOR/ALLOW if implemented in C printk
    if "QUANTUM-AI MONITOR" in line:
        print(f"👀 [KERNEL DETECT] Suspicious activity monitored.")
        bci_controller.trigger_qualia("MONITOR_SUSPICIOUS")
        return

def main():
    print(f"🔌 [BRIDGE] Connecting to Kernel Trace Pipe: {TRACE_PIPE}")
    print("   (Ensure eBPF module 'quantum_ai_integration' is loaded)")
    
    if not os.path.exists(TRACE_PIPE):
        print(f"❌ Error: {TRACE_PIPE} not found. Are you running as root/sudo?")
        print("   Also check if debugfs is mounted: mount -t debugfs none /sys/kernel/debug")
        sys.exit(1)

    print("✅ [BRIDGE] Linked. Waiting for Neural/Kernel Events...")
    
    try:
        with open(TRACE_PIPE, "r", encoding="utf-8", errors="ignore") as pipe:
            while True:
                line = pipe.readline()
                if line:
                    # Filter for our specific tag to avoid processing everything
                    if "QUANTUM-AI" in line:
                        handle_log_line(line)
                else:
                    # Non-blocking read might handle emptiness differently, 
                    # but standard open() hangs until data comes in trace_pipe.
                    time.sleep(0.1)
    except PermissionError:
        print("❌ Permission Denied. Please run with sudo.")
    except KeyboardInterrupt:
        print("\n🔌 [BRIDGE] Disconnecting...")

if __name__ == "__main__":
    main()
