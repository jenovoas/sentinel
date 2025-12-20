#!/usr/bin/env python3
"""
Guardian-Alpha Watchdog Service

Sends heartbeat to /dev/watchdog every 10 seconds.
If this process dies, kernel will reboot the system.

This proves "Physical Resilience" - security tied to hardware.
"""

import time
import os
import sys
import fcntl
import struct

WATCHDOG_DEVICE = "/dev/watchdog"
HEARTBEAT_INTERVAL = 10  # seconds

def setup_watchdog():
    """Open watchdog device and configure timeout"""
    try:
        wd = os.open(WATCHDOG_DEVICE, os.O_WRONLY)
        
        # Set timeout to 30 seconds
        WDIOC_SETTIMEOUT = 0x80045706
        timeout = struct.pack('I', 30)
        fcntl.ioctl(wd, WDIOC_SETTIMEOUT, timeout)
        
        print(f"✅ Watchdog configured: 30s timeout")
        return wd
    except Exception as e:
        print(f"❌ Failed to open watchdog: {e}")
        print(f"ℹ️  Watchdog may not be available on this system")
        print(f"ℹ️  This is OK for POC - demonstrates the concept")
        return None

def send_heartbeat(wd):
    """Send heartbeat to watchdog"""
    if wd is None:
        return True
    
    try:
        os.write(wd, b'\x00')
        return True
    except Exception as e:
        print(f"❌ Failed to send heartbeat: {e}")
        return False

def main():
    print("🐕 Starting Guardian-Alpha Watchdog Service...")
    print("")
    
    wd = setup_watchdog()
    
    if wd:
        print(f"💓 Sending heartbeat every {HEARTBEAT_INTERVAL}s")
        print("⚠️  If this process dies, system will reboot in 30s")
    else:
        print(f"💓 Simulating heartbeat every {HEARTBEAT_INTERVAL}s (watchdog not available)")
    
    print("")
    
    try:
        while True:
            if send_heartbeat(wd):
                print(f"💓 Heartbeat sent at {time.strftime('%H:%M:%S')}")
            else:
                print("❌ Heartbeat failed - system will reboot!")
                break
            
            time.sleep(HEARTBEAT_INTERVAL)
    except KeyboardInterrupt:
        print("\n🛑 Stopping watchdog service...")
        if wd:
            # Write 'V' to disable watchdog before exit
            os.write(wd, b'V')
            os.close(wd)
            print("✅ Watchdog disabled")
        else:
            print("✅ Service stopped")

if __name__ == "__main__":
    main()
