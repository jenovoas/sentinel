#!/usr/bin/env python3
import socket
import json
import sqlite3
import os
import sys

# Ensure project root is in path for direct execution
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from .inference import SentinelBrain
except ImportError:
    # Fallback for direct execution 
    from sentinel_core.brain.inference import SentinelBrain

SOCKET_PATH = "/tmp/sentinel_cortex.sock"
DB_PATH = "/home/jnovoas/sentinel/forensics/evidence.db"

class CortexBridge:
    def __init__(self):
        self.brain = SentinelBrain()
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                pid INTEGER,
                path TEXT,
                allow BOOLEAN,
                source TEXT,
                details TEXT,
                score REAL
            )
        """)
        
        # Schema Migration: Add columns if they missed the initial creation
        try:
            conn.execute("ALTER TABLE evidence ADD COLUMN details TEXT")
        except sqlite3.OperationalError:
            pass # Column likely exists
            
        try:
            conn.execute("ALTER TABLE evidence ADD COLUMN score REAL")
        except sqlite3.OperationalError:
            pass # Column likely exists

        conn.commit()
        conn.close()

    def _sanitize_telemetry(self, text):
        import re
        if not text:
            return "N/A"
        # 1. Remove HTML tags (XSS Prevention)
        clean = re.sub(r'<.*?>', '', str(text))
        # 2. Limit character range (ASCII focus)
        clean = "".join(i for i in clean if ord(i) < 128)
        # 3. Truncate long payloads (Dashboard stability)
        return clean[:200]

    def _log_evidence(self, pid, path, allow, source="AI_BRAIN", details=None, score=None):
        clean_path = self._sanitize_telemetry(path)
        clean_details = self._sanitize_telemetry(details)
        
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO evidence (pid, path, allow, source, details, score) VALUES (?, ?, ?, ?, ?, ?)",
                     (pid, clean_path, 1 if allow else 0, source, clean_details, score))
        conn.commit()
        conn.close()

    def _relay_to_n8n(self, payload):
        import urllib.request
        import json
        url = os.getenv("N8N_THREAT_WEBHOOK", "http://localhost:5678/webhook/threat-autopsy")
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), 
                                       headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=5) as response:
                print(f"📡 [CortexBridge] Relé n8n exitoso: {response.status}")
        except Exception as e:
            print(f"⚠️ [CortexBridge] Error relé n8n: {e}")

    def start(self):
        print(f"🌲 [CortexBridge] Connecting to Quantum Tunnel at {SOCKET_PATH}...")
        
        # Retry loop for connection
        import time
        connected = False
        while not connected:
            try:
                self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.sock.connect(SOCKET_PATH)
                connected = True
                print(f"📡 [CortexBridge] Connected to Sentinel Kernel (QEMU Bridge).")
            except Exception as e:
                print(f"⏳ [CortexBridge] Waiting for Sentinel Kernel... ({e})")
                time.sleep(2)

        # Spawn listener thread
        import threading
        listener = threading.Thread(target=self.listen_loop, daemon=True)
        listener.start()

        # Enter Command Loop
        self.command_loop()

    def listen_loop(self):
        try:
            self.buffer = ""
            while True:
                data = self.sock.recv(4096)
                if not data:
                    print("\n⚠️ [CortexBridge] Connection closed by Kernel.")
                    os._exit(1) # Exit main thread too
                
                # Append new data to buffer
                self.buffer += data.decode('utf-8', errors='ignore')
                
                # Check if we have a complete newline-terminated message
                while '\n' in self.buffer:
                    line, self.buffer = self.buffer.split('\n', 1)
                    line = line.strip()
                    if not line: continue
                    
                    try:
                        request = json.loads(line)
                        pid = request.get("pid")
                        
                        # Handle ThreatReport vs RiskCheck
                        if "score" in request:
                            # This is a ThreatReport from The Hunter
                            score = request.get("score")
                            details = request.get("details", "No details")
                            print(f"\n🏹 [CortexBridge] REPORTE DE CAZA: PID {pid}, Score {score}")
                            
                            self._log_evidence(pid, "N/A", False, source="HUNTER", details=details, score=score)
                            self._relay_to_n8n({
                                "event": "THREAT_NEUTRALIZED",
                                "pid": pid,
                                "score": score,
                                "details": details,
                                "status": "Inmunidad Preservada"
                            })
                        else:
                             pass

                    except json.JSONDecodeError:
                        print(f"⚠️ [CortexBridge] Incomplete/Malformed JSON (buffering): {line[:50]}...")
                    except Exception as e:
                         print(f"⚠️ [CortexBridge] Error processing request: {e}")
        finally:
             pass

    def command_loop(self):
        print("💻 [CortexBridge] Command Link Active. Type 'block <IP>' to filter traffic.")
        while True:
            try:
                cmd = input("FAIL-SAFE> ")
                if cmd.startswith("block "):
                    ip = cmd.split(" ")[1]
                    # Format: BrainResponse JSON
                    payload = json.dumps({"allow": True, "block_ip": ip}) + "\n"
                    self.sock.sendall(payload.encode('utf-8'))
                    print(f"🛡️ [CortexBridge] Sent BLOCK command for {ip}")
                elif cmd == "exit":
                    break
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")
        self.sock.close()

if __name__ == "__main__":
    bridge = CortexBridge()
    bridge.start()
