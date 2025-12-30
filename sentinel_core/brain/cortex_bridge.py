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
                source TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _log_evidence(self, pid, path, allow):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO evidence (pid, path, allow, source) VALUES (?, ?, ?, ?)",
                     (pid, path, 1 if allow else 0, "AI_BRAIN"))
        conn.commit()
        conn.close()

    def start(self):
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(SOCKET_PATH)
        # Allow any user to connect to the socket (init runs as root, but let's be safe)
        os.chmod(SOCKET_PATH, 0o666)
        server.listen(5)

        print(f"🌲 [CortexBridge] Escuchando en {SOCKET_PATH}...")

        try:
            while True:
                conn, _ = server.accept()
                try:
                    data = conn.recv(4096)
                    if not data:
                        continue
                    
                    request = json.loads(data.decode('utf-8'))
                    pid = request.get("pid")
                    path = request.get("path")

                    allow = self.brain.analyze_threat(path)
                    
                    # Log the decision to forensics
                    self._log_evidence(pid, path, allow)

                    response = json.dumps({"allow": allow})
                    conn.sendall(response.encode('utf-8'))
                except Exception as e:
                    print(f"⚠️ [CortexBridge] Error procesando solicitud: {e}")
                finally:
                    conn.close()
        finally:
            server.close()
            if os.path.exists(SOCKET_PATH):
                os.remove(SOCKET_PATH)

if __name__ == "__main__":
    bridge = CortexBridge()
    bridge.start()
