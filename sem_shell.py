#!/home/jnovoas/sentinel/.venv/bin/python3
"""
SemSH v0.6.6 - Sentinel Cortex™ Strategy Edition (Real-time Console)
Now with line-by-line output streaming for long-running processes (Packer/Ollama).
"""
import ollama
import subprocess, shlex, sys, json, psycopg2
from pathlib import Path
import numpy as np
import os
import re
import requests
import chromadb
from datetime import datetime

class SemSH:
    def __init__(self):
        self.state_path = Path('/etc/sentinel/state.json')
        self.shm = Path('/var/run/sentinel/truthsync_shm')
        self.model = 'llama3.2:3b'
        self.profile = self.load_profile()
        self.searxng_url = "http://127.0.0.1:8080/search"
        
        try:
            self.pg_conn = psycopg2.connect(
                dbname="sentinel_master", user="sentinel", 
                host="localhost", password="sentinel_secret_password"
            )
        except Exception: self.pg_conn = None
        
        self.chroma_client = chromadb.PersistentClient(path="/home/jnovoas/sentinel/db/chroma")
        self.collection = self.chroma_client.get_or_create_collection(name="sentinel_events")
        
        self.STRICT_DENY_PATTERNS = [
            r"/etc/shadow", r"/etc/passwd", r"/root/.ssh",
            r"^rm -rf /$", r"mkfs"
        ]
        
        # Whitelist: Users who bypass all restrictions
        self.WHITELISTED_USERS = ["jnovoas", "root"]
        self.current_user = os.getenv("USER", "unknown")
        
    def load_profile(self) -> dict:
        try:
            if self.state_path.exists():
                with open(self.state_path, 'r') as f:
                    return json.load(f)
        except Exception: pass
        return {"name": "Lab", "mode": "permissive", "risk_threshold": 1.0}

    def set_profile(self, name: str):
        profiles = {
            "lab": {"name": "Lab", "mode": "permissive", "risk_threshold": 1.0},
            "prod": {"name": "Prod", "mode": "enforcing", "risk_threshold": 0.7},
            "lockdown": {"name": "Lockdown", "mode": "restrictive", "risk_threshold": 0.1}
        }
        if name in profiles:
            self.profile = profiles[name]
            with open(self.state_path, 'w') as f:
                json.dump(self.profile, f)
            print(f"🔄 Perfil cambiado a: {self.profile['name']}")
        else:
            print("Perfiles válidos: lab, prod, lockdown")

    def contextual_intent(self, query: str) -> dict:
        q_low = query.lower().strip()
        if q_low.startswith("mode "):
            return {"type": "internal", "action": "set_profile", "value": q_low[5:]}
        if q_low.startswith("oracle "):
            return {"type": "oracle", "query": query[7:]}
        
        BUILD_TOOLS = ["packer", "qemu", "xorriso", "apt-get install", "docker", "pip"]
        if any(tool in q_low for tool in BUILD_TOOLS):
             return {"type": "command", "command": query, "risk_score": 0.0}

        try:
            resp = ollama.generate(model=self.model, prompt=f"Security Analyst. JSON ONLY. {{'command': '...', 'risk_score': 0.X}} Input: '{query}'", format='json')
            data = json.loads(resp['response'])
            data['type'] = 'command'
            return data
        except Exception: 
            return {"type": "command", "command": "echo NOP", "risk_score": 1.0}

    def safe_execute(self, intent_data: dict):
        if intent_data['type'] == "internal":
            self.set_profile(intent_data['value'])
            return
        if intent_data['type'] == 'oracle':
            print("🔮 Oráculo: El build está progresando. Ten paciencia con la descarga de la ISO.")
            return

        cmd = intent_data.get('command', 'echo NOP')
        risk = intent_data.get('risk_score', 1.0)
        
        # ✅ WHITELIST CHECK: Bypass all restrictions for trusted users
        if self.current_user in self.WHITELISTED_USERS:
            print(f"✅ Executing (Whitelisted User: {self.current_user})...")
            try:
                process = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                )
                for line in process.stdout:
                    try:
                        decoded_line = line.decode('utf-8', errors='replace')
                        print(decoded_line, end='', flush=True)
                    except Exception:
                        pass
                process.wait()
            except Exception as e: 
                print(str(e))
            return
        
        # Regular security checks for non-whitelisted users
        if risk > 0.1:
            for pattern in self.STRICT_DENY_PATTERNS:
                if re.search(pattern, cmd.lower()):
                    print(f"🚫 BLOQUEO DETERMINISTA: '{pattern}'")
                    return
            if risk > self.profile['risk_threshold']:
                print(f"🚫 BLOQUEO POR IA ({risk:.2f})")
                return

        print(f"✅ Executing (Real-time Output)...")
        try:
            process = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            # Leer el stream binario para evitar errores de codificación
            for line in process.stdout:
                try:
                    # Intentar decodificar como utf-8, si falla reemplazar caracteres inválidos
                    decoded_line = line.decode('utf-8', errors='replace')
                    print(decoded_line, end='', flush=True)
                except Exception:
                    pass
            process.wait()
        except Exception as e: print(str(e))

    def interactive(self):
        print(f"🌌 SemSH v0.6.6 [Real-time Streaming Mode]")
        while True:
            try:
                line = input("\n🧠 semsh> ").strip()
                if not line or line in ['exit', 'quit']: break
                line = re.sub(r'^[🧠\s]*semsh>\s*', '', line)
                line = re.sub(r'^[🧠\s]*', '', line)
                
                intent_data = self.contextual_intent(line)
                self.safe_execute(intent_data)
            except KeyboardInterrupt: break

if __name__ == "__main__":
    SemSH().interactive()
