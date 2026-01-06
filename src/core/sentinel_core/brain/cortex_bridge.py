#!/usr/bin/env python3
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import socket
import json
import sqlite3
import os
import sys
import threading
import base64
import time

# Ensure project root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from . import tiny_crypto
except ImportError:
    # Direct execution fallback
    import tiny_crypto

SOCKET_PATH = "/tmp/sentinel_cortex.sock"
# SOCKET_PATH = "/tmp/sentinel_spy.sock" # Blackbox Test Mode
DB_PATH = "/home/jnovoas/sentinel/forensics/evidence.db"

class CortexBridge:
    def __init__(self):
        self._init_db()
        self.session_key = None
        self.sock = None
        self.lock = threading.Lock()

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
        try:
            conn.execute("ALTER TABLE evidence ADD COLUMN details TEXT")
        except sqlite3.OperationalError: pass
        try:
            conn.execute("ALTER TABLE evidence ADD COLUMN score REAL")
        except sqlite3.OperationalError: pass
        conn.commit()
        conn.close()

    def _log_evidence(self, pid, score, details):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO evidence (pid, score, details, source, allow) VALUES (?, ?, ?, ?, ?)",
                     (pid, score, details, "HUNTER_ENCRYPTED", 0))
        conn.commit()
        conn.close()

    def start(self):
        print(f"🌲 [CortexBridge] Connecting directly to Init Socket: {SOCKET_PATH}")
        while True:
            try:
                self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.sock.connect(SOCKET_PATH)
                print(f"📡 [CortexBridge] Connected to Sentinel Kernel.")
                break
            except Exception as e:
                print(f"⏳ [CortexBridge] Waiting for Sentinel Kernel... ({e})")
                time.sleep(2)

        listener = threading.Thread(target=self.listen_loop, daemon=True)
        listener.start()

        self.command_loop()

    def listen_loop(self):
        buffer = ""
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    print("\n⚠️ Connection lost.")
                    os._exit(1)
                
                # Debug Raw Data
                print(f"BYTE DUMP: {data}")
                
                buffer += data.decode('utf-8', errors='ignore')
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self.handle_message(line.strip())
            except Exception as e:
                print(f"Error in listener: {e}")
                break

    def handle_message(self, line):
        if not line: return
        try:
            msg = json.loads(line)
            msg_type = msg.get("type", "unknown")

            if msg_type == "pqc_hello":
                self.handle_handshake(msg["pk"])
            elif msg_type == "enc":
                self.handle_encrypted(msg["payload"])
            else:
                # Legacy/Plaintext Fallback
                self.process_payload(msg)

        except json.JSONDecodeError:
            pass 

    def handle_handshake(self, peer_pk_base64):
        print(f"🔐 [PQC] Handshake Request Received (Key: {peer_pk_base64[:10]}...)")
        
        # 1. Generate Ephemeral Keypair (b, B)
        my_secret, my_public = tiny_crypto.generate_keypair()
        
        # 2. Decode Peer's Public Key (A)
        peer_pk = base64.b64decode(peer_pk_base64)
        
        # 3. Compute Shared Secret (S = b * A)
        shared = tiny_crypto.shared_secret(my_secret, peer_pk)
        
        # 4. Derive Session Key (First 32 bytes)
        self.session_key = shared[:32]
        
        # 5. Send Auth (B)
        my_public_b64 = base64.b64encode(my_public).decode('utf-8')
        auth_msg = json.dumps({"type": "pqc_auth", "ct": my_public_b64}) + "\n"
        self.sock.sendall(auth_msg.encode('utf-8'))
        
        print("✅ [PQC] Secure Channel Established (X25519 + ChaCha20).")

    def handle_encrypted(self, payload_b64):
        if not self.session_key:
            print("⚠️ Encrypted message received but no session key!")
            return

        try:
            # decode format: nonce(12) + ct
            combined = base64.b64decode(payload_b64)
            nonce = combined[:12]
            ciphertext = combined[12:]
            
            plaintext = tiny_crypto.chacha20_aead_decrypt(self.session_key, nonce, ciphertext)
            if plaintext:
                inner_json = json.loads(plaintext.decode('utf-8'))
                self.process_payload(inner_json)
            else:
                print("⚠️ Decryption Failed (MAC Mismatch)")
        except Exception as e:
            print(f"Decryption Error: {e}")

    def process_payload(self, data):
        if "score" in data:
            print(f"🏹 [SECURE-REPORT] PID {data.get('pid')} - Score: {data.get('score')}")
            self._log_evidence(data.get('pid'), data.get('score'), data.get('details'))
        elif "hb" in data:
            # Heartbeats might come through encrypted now
            # print(f"💓 Secure Heartbeat: {data['hb']}", end='\r')
            pass

    def send_command_encrypted(self, cmd_data):
        json_bytes = json.dumps(cmd_data).encode('utf-8')
        if self.session_key:
            nonce = os.urandom(12)
            ciphertext_tag = tiny_crypto.chacha20_aead_encrypt(self.session_key, nonce, json_bytes)
            
            # combine nonce + ct_tag
            final = nonce + ciphertext_tag
            payload_b64 = base64.b64encode(final).decode('utf-8')
            
            wrapper = json.dumps({"type": "enc", "payload": payload_b64}) + "\n"
            self.sock.sendall(wrapper.encode('utf-8'))
        else:
            print("⚠️ Cannot send command: Session not established.")

    def command_loop(self):
        print("💻 Crypto-Link Active. Type 'block <IP>'")
        while True:
            try:
                cmd = input("> ")
                if cmd.startswith("block "):
                    ip = cmd.split(" ")[1]
                    self.send_command_encrypted({"allow": True, "block_ip": ip})
                    print("Sent Encrypted Block Command.")
            except:
                break

if __name__ == "__main__":
    bridge = CortexBridge()
    bridge.start()
