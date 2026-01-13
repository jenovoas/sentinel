#!/usr/bin/env python3
import time
import os
import sys
import subprocess
import requests

# Sentinel Verification Script: The Cascade
# 1. Start Cortex (Writes to 'cortex_primary' every 5s)
# 2. Start SubCortex/TruthSync (Reads 'cortex_primary', Writes 'subcortex_secondary')
# 3. Verify Buffers exist and contain data

def verify_cascade():
    print("🚀 [VERIFY] Starting Sentinel Cascade Verification...")
    
    # 1. Clean previous state
    subprocess.run(["rm", "-f", "/dev/shm/cortex_primary", "/dev/shm/subcortex_secondary"])
    
    # 2. Start Cortex
    print("🧠 [VERIFY] Launching Cortex...")
    cortex_log = open("/tmp/cortex_debug.log", "w")
    cortex_proc = subprocess.Popen(
        ["/home/jnovoas/dev/sentinel/.venv/bin/python3", "quantum/cortex_main.py", "--rust", "--gpu3gb"],
        cwd="/home/jnovoas/dev/sentinel",
        env={**os.environ, "PYTHONPATH": os.getcwd()},
        stdout=cortex_log,
        stderr=subprocess.STDOUT
    )
    
    # 3. Start TruthSync (SubCortex)
    print("🔮 [VERIFY] Launching TruthSync (SubCortex)...")
    debug_log = open("/tmp/truthsync_debug.log", "w")
    truth_proc = subprocess.Popen(
        ["/home/jnovoas/dev/sentinel/.venv/bin/python3", "truthsync-poc/truthsync_server.py"],
        cwd="/home/jnovoas/dev/sentinel",
        env={**os.environ, "PYTHONPATH": os.getcwd()},
        stdout=debug_log,
        stderr=subprocess.STDOUT
    )
    
    try:
        # Wait for Cortex initialization and at least one 'memory.store' (5 ticks = 5 seconds)
        print("⏳ [VERIFY] Waiting for system stabilization (10s)...")
        time.sleep(10)
        
        # Trigger TruthSync processing (to activate cascade read/write)
        # TruthSync server normally batches requests. We send one.
        print("⚡ [VERIFY] Triggering SubCortex Processing...")
        try:
            payload = {"text": "integrity_check", "metadata": {"pid": 0}}
            requests.post("http://localhost:8001/verify", json=payload, timeout=2)
            # Give it time to process batch
            time.sleep(1) 
        except Exception as e:
            print(f"⚠️ [VERIFY] TruthSync API Call Failed: {e}")

        # 4. Check Buffers
        print("\n🔍 [VERIFY] INSPECTING SHARED MEMORY:")
        
        # Cortex Primary
        if os.path.exists("/dev/shm/cortex_primary"):
            size = os.path.getsize("/dev/shm/cortex_primary")
            print(f"   ✅ 'cortex_primary' EXISTS. Size: {size} bytes")
        else:
            print("   ❌ 'cortex_primary' MISSING.")

        # SubCortex Secondary
        if os.path.exists("/dev/shm/subcortex_secondary"):
            size = os.path.getsize("/dev/shm/subcortex_secondary")
            print(f"   ✅ 'subcortex_secondary' EXISTS. Size: {size} bytes")
        else:
            print("   ❌ 'subcortex_secondary' MISSING (Cascade Broken).")
            
    finally:
        print("\n🛑 [VERIFY] Shutting down...")
        cortex_proc.terminate()
        truth_proc.terminate()
        try:
            cortex_proc.wait(timeout=5)
            truth_proc.wait(timeout=5)
        except:
            cortex_proc.kill()
            truth_proc.kill()

if __name__ == "__main__":
    verify_cascade()
