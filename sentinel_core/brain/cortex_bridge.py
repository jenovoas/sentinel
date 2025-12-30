import os
import socket
import json
import sqlite3
from .inference import SentinelBrain

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
        
        # In the virtio-serial architecture, QEMU creates the socket server.
        # We must connect as a client.
        
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

        try:
            while True:
                data = self.sock.recv(4096)
                if not data:
                    print("⚠️ [CortexBridge] Connection closed by Kernel.")
                    break
                
                try:
                    # Handle multiple JSON objects in one stream (newline delimited)
                    buffer = data.decode('utf-8').strip()
                    for line in buffer.split('\n'):
                        if not line: continue
                        
                        request = json.loads(line)
                        pid = request.get("pid")
                        
                        # Handle ThreatReport vs RiskCheck
                        if "score" in request:
                            # This is a ThreatReport from The Hunter
                            score = request.get("score")
                            details = request.get("details", "No details")
                            print(f"🏹 [CortexBridge] REPORTE DE CAZA: PID {pid}, Score {score}")
                            
                            self._log_evidence(pid, "N/A", False, source="HUNTER", details=details, score=score)
                            self._relay_to_n8n({
                                "event": "THREAT_NEUTRALIZED",
                                "pid": pid,
                                "score": score,
                                "details": details,
                                "status": "Inmunidad Preservada"
                            })
                        else:
                             # Traditional RiskCheck (Not fully supported in unidirectional serial bridge yet)
                             pass

                except json.JSONDecodeError:
                    print(f"⚠️ [CortexBridge] Malformed JSON: {line}")
                except Exception as e:
                     print(f"⚠️ [CortexBridge] Error processing request: {e}")

        finally:
            self.sock.close()

if __name__ == "__main__":
    bridge = CortexBridge()
    bridge.start()
