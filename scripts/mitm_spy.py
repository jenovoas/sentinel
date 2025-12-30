#!/usr/bin/env python3
import socket
import threading
import os
import sys
import select

# Configuration
REAL_KERNEL_SOCKET = "/tmp/sentinel_cortex.sock" # QEMU listens here
FAKE_KERNEL_SOCKET = "/tmp/sentinel_spy.sock"   # Bridge connects here

def main():
    # 1. Setup Spy Server (Fake Kernel)
    if os.path.exists(FAKE_KERNEL_SOCKET):
        os.remove(FAKE_KERNEL_SOCKET)
    
    spy_server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    spy_server.bind(FAKE_KERNEL_SOCKET)
    spy_server.listen(1)
    
    print(f"🕵️  [SPY] Listening on {FAKE_KERNEL_SOCKET} (Bridge should connect here)")
    print(f"🔌 [SPY] Will forward to {REAL_KERNEL_SOCKET} (QEMU)")
    
    conn_bridge, _ = spy_server.accept()
    print("🕵️  [SPY] Bridge Connected!")
    
    # 2. Connect to Real Kernel (QEMU)
    try:
        conn_kernel = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        conn_kernel.connect(REAL_KERNEL_SOCKET)
        print("🕵️  [SPY] Connected to Real Kernel (QEMU)!")
    except Exception as e:
        print(f"❌ [SPY] Failed to connect to QEMU: {e}")
        conn_bridge.close()
        return

    # 3. Proxy Loop
    sockets = [conn_bridge, conn_kernel]
    
    try:
        while True:
            readable, _, _ = select.select(sockets, [], [])
            
            for s in readable:
                data = s.recv(4096)
                if not data:
                    print("🕵️  [SPY] Connection Closed.")
                    return
                
                if s is conn_kernel:
                    # Direction: Kernel (Init) -> Bridge
                    # This is where we expect PQC Hello and Encrypted Reports
                    print(f"\n[KERNEL -> BRIDGE] {len(data)} bytes")
                    print(f"RAW: {data}")
                    conn_bridge.sendall(data)
                else:
                    # Direction: Bridge -> Kernel
                    # This is where we expect PQC Auth or Commands
                    print(f"\n[BRIDGE -> KERNEL] {len(data)} bytes")
                    print(f"RAW: {data}")
                    conn_kernel.sendall(data)
                    
    except KeyboardInterrupt:
        print("\n🕵️  [SPY] Stopping.")
    finally:
        conn_kernel.close()
        conn_bridge.close()
        os.remove(FAKE_KERNEL_SOCKET)

if __name__ == "__main__":
    main()
