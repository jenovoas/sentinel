#!/usr/bin/env python3
import sys
import time
import subprocess
import binascii

# Configuration
TRACE_PIPE = "/sys/kernel/debug/tracing/trace_pipe"
MAP_PATH = "/sys/fs/bpf/guardian_alpha/whitelist_map"

print("🧠 Guardian-Alpha Cognitive Loop Started...")
print(f"📡 Monitoring: {TRACE_PIPE}")
print(f"🗺️  Map Target: {MAP_PATH}")
print("-" * 50)

def string_to_hex(s):
    # Convert string to hex representation for bpftool
    # Key is char[256], so we need to pad with zeros if necessary or just provide the bytes
    # bpftool expects space-separated hex bytes
    return " ".join("{:02x}".format(ord(c)) for c in s) + " 00"

def update_whitelist(filename):
    print(f"⚡ AI [ACTION]: Whitelisting '{filename}'...")
    
    # Construct hex key (null terminated)
    # The map key size is 256 bytes. Bpftool might need full padding?
    # Usually bpftool handles variable length if we don't specify full size?
    # No, for fixed size keys, we must provide full size or it fits.
    # Let's try sending just the string bytes first, usually works if key matches.
    # Wait, for 'bpftool map update', we usually need exact key size.
    # We will pad with zeros to 256 bytes just to be safe.
    
    hex_key = string_to_hex(filename)
    # Padding loop (256 bytes total, minus existing chars and null terminator)
    current_len = len(filename) + 1
    padding = " 00" * (256 - current_len)
    full_hex_key = hex_key + padding
    
    cmd = [
        "sudo", "bpftool", "map", "update", "pinned", MAP_PATH,
        "key", "hex", *full_hex_key.split(),
        "value", "hex", "01"
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        print(f"✅ AI [SUCCESS]: '{filename}' added to Dynamic Whitelist")
    except subprocess.CalledProcessError as e:
        print(f"❌ AI [ERROR]: Failed to update map: {e}")

def ai_decision(filename):
    """
    Simulated AI Decision Engine.
    Real world: Call Ollama/GPT-4.
    PoC: Static pattern analysis.
    """
    print(f"🤔 AI [ANALYSIS]: Analyzing block event for '{filename}'...")
    time.sleep(0.5) # Simulate inference latency
    
    if "safe" in filename or "deploy" in filename:
        print(f"🛡️  AI [DECISION]: ALLOW. Context implies legitimate operation.")
        return True
    elif "malware" in filename or "attack" in filename:
        print(f"🚫 AI [DECISION]: BLOCK CONFIRMED. Threat detected.")
        return False
    else:
        print(f"⚖️  AI [DECISION]: UNCERTAIN. Maintaining default block.")
        return False

def monitor_loop():
    try:
        with open(TRACE_PIPE, "r", encoding="utf-8", errors="ignore") as f:
            while True:
                line = f.readline()
                if not line:
                    continue
                
                # Filter for Guardian Logs
                if "Guardian [BLOCK]" in line:
                    # Line format example: ... bpf_trace_printk: Guardian [BLOCK]: Unknown binary ./safe_script.sh
                    # Extract filename
                    try:
                        parts = line.split("Unknown binary ")
                        if len(parts) > 1:
                            filename = parts[1].strip()
                            
                            # Trigger AI Logic
                            should_allow = ai_decision(filename)
                            if should_allow:
                                update_whitelist(filename)
                    except Exception as e:
                        print(f"Error parsing line: {e}")
                        
    except PermissionError:
        print("❌ Error: Need sudo privileges to read trace_pipe")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Loop stopped.")

if __name__ == "__main__":
    monitor_loop()
