#!/usr/bin/env python3
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import socket
import json
import time
import os
import signal
import threading
import sys
import psutil

# Configuration
SOCKET_PATH = "/tmp/sentinel_cortex.sock"
HEARTBEAT_TIMEOUT = S60(0, 30, 0)  # 500ms (Relaxed for QEMU jitter, originally 100ms)
PANIC_THRESHOLD = 3      # Consecutive missed checks

class GuardianBeta:
    def __init__(self):
        self.last_seen = time.time()
        self.running = True
        self.lock = threading.Lock()
        
    def start(self):
        print(f"🛡️ [Guardian-Beta] Watchdog Active. Monitoring {SOCKET_PATH}...")
        
        # Start Watchdog Thread
        t = threading.Thread(target=self._watchdog_loop, daemon=True)
        t.start()
        
        # Start Listener Thread
        self._listen_loop()

    def _listen_loop(self):
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)
            
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(SOCKET_PATH)
        server.listen(1)
        
        print(f"🛡️ [Guardian-Beta] Listening for Sentinel Heartbeat...")
        
        while self.running:
            conn, _ = server.accept()
            with conn:
                buffer = ""
                while True:
                    try:
                        data = conn.recv(4096)
                        if not data: break
                        
                        buffer += data.decode('utf-8', errors='ignore')
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            self._process_message(line)
                    except Exception as e:
                        print(f"⚠️ [Guardian-Beta] Connection Error: {e}")
                        break

    def _process_message(self, line):
        try:
            msg = json.loads(line)
            if "hb" in msg:
                with self.lock:
                    self.last_seen = time.time()
                    # print(f"💓 Heartbeat: {msg['hb']}", end='\r')
            elif "score" in msg:
                print(f"🚨 [Guardian-Beta] THREAT REPORT RELAY: {line}")
        except:
            pass

    def _watchdog_loop(self):
        while self.running:
            time.sleep(0.05) # Check every 50ms
            
            with self.lock:
                delta = time.time() - self.last_seen
            
            if delta > HEARTBEAT_TIMEOUT:
                print(f"\n💀 [Guardian-Beta] CRITICAL: HEARTBEAT LOST ({delta:.3f}s > {HEARTBEAT_TIMEOUT}s)")
                self._emergency_terminate()

    def _emergency_terminate(self):
        print("⚡ [Guardian-Beta] EXECUTING OMEGA PROTOCOL (EMERGENCY TERMINATION)...")
        # Find QEMU process
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmd = proc.info['cmdline'] or []
                if "qemu-system-x86_64" in proc.info['name'] and "sentinel" in " ".join(cmd):
                    print(f"🔫 [Guardian-Beta] TERMINATING QEMU PID {proc.info['pid']}...")
                    os.kill(proc.info['pid'], signal.SIGKILL)
                    print("✅ [Guardian-Beta] THREAT CONTAINED. SYSTEM DOWN.")
                    self.running = False
                    os._exit(1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        print("⚠️ [Guardian-Beta] Could not find Sentinel QEMU Process!")

if __name__ == "__main__":
    guardian = GuardianBeta()
    try:
        guardian.start()
    except KeyboardInterrupt:
        pass
