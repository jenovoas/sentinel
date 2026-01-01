#!/usr/bin/env python3
"""
SemSH v0.6.1 - Sentinel Cortex™ Strategy Edition
From Narrative to Action: Autonomous Hardening Suggestions.
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
        
        # Conexión a Memoria Histórica (Postgres)
        try:
            self.pg_conn = psycopg2.connect(
                dbname="sentinel_master", user="sentinel", 
                host="localhost", password="sentinel_secret_password"
            )
        except Exception: self.pg_conn = None
        
        # Conexión a Memoria Semántica (ChromaDB)
        self.chroma_client = chromadb.PersistentClient(path="/home/jnovoas/sentinel/db/chroma")
        self.collection = self.chroma_client.get_or_create_collection(name="sentinel_events")
        
        self.STRICT_DENY_PATTERNS = [
            r"/etc/shadow", r"/etc/passwd", r"/root/.ssh",
            r"rm -rf /", r"mkfs", r"dd if=/dev/"
        ]
        
    def load_profile(self) -> dict:
        try:
            if self.state_path.exists():
                with open(self.state_path, 'r') as f:
                    return json.load(f)
        except Exception: pass
        return {"name": "Default", "mode": "enforcing", "risk_threshold": 0.7}

    def memorize_event(self, query: str, cmd: str, risk: float, reasoning: str):
        """Guarda el evento en el Hipocampo Digital (ChromaDB)"""
        timestamp = datetime.now().isoformat()
        content = f"TS: {timestamp} | QUERY: {query} | CMD: {cmd} | RISK: {risk} | REASON: {reasoning}"
        try:
            self.collection.add(
                documents=[content],
                metadatas=[{"risk": risk, "ts": timestamp, "profile": self.profile['name']}],
                ids=[f"ev_{datetime.now().timestamp()}"]
            )
        except Exception: pass

    def generate_defense_strategy(self):
        """El Oráculo analiza el pasado y genera un Plan de Hardening"""
        print(f"🔮 Oráculo de Sentinel: Generando Estrategia de Defensa Activa...")
        
        # 1. Recuperar eventos de ALTO RIESGO de la memoria
        results = self.collection.query(
            query_texts=["high risk security incident access violation attack"],
            where={"risk": {"$gt": 0.5}},
            n_results=10
        )
        
        memories = "\n".join(results['documents'][0]) if results['documents'] else "No se detectan incidentes de alto riesgo en memoria reciente."
        
        # 2. Inferencia Estratégica
        strategy_prompt = f"""
SENTINEL STRATEGY ANALYST - HARDENING PLAN.
Current Profile: {self.profile['name']}

RECENT HIGH-RISK MEMORIES:
{memories}

TASK: 
1. Identify the most persistent threat patterns.
2. Suggest 3 specific DEFENSE ACTIONS:
   - A specific 'sctl' command to block IPs or binaries.
   - A profile adjustment (e.g., switching to Lockdown or changing thresholds).
   - A TruthSync Gold entry to ensure this truth is persistent.

FORMAT: Use a professional, executive security report style.
"""
        try:
            print("🧠 Analizando patrones tácticos en el kernel...")
            resp = ollama.generate(model=self.model, prompt=strategy_prompt)
            return resp['response']
        except Exception as e:
            return f"❌ Fallo en análisis estratégico: {e}"

    def query_oracle(self, question: str):
        """Consulta al Oráculo: Combina Memoria Interna + IA"""
        if "estrategia" in question.lower() or "plan" in question.lower() or "hardening" in question.lower():
            return self.generate_defense_strategy()

        print(f"🔮 Consultando al Oráculo sobre: '{question}'...")
        results = self.collection.query(query_texts=[question], n_results=5)
        events = "\n".join(results['documents'][0]) if results['documents'] else "No hay recuerdos relevantes."
        
        prompt = f"SENTINEL ORACLE ANALYSIS.\nQuestion: {question}\nRelevant Memories:\n{events}\nSynthesize a security report:"
        try:
            resp = ollama.generate(model=self.model, prompt=prompt)
            return resp['response']
        except Exception as e: return str(e)

    def contextual_intent(self, query: str) -> dict:
        if query.lower().startswith("oracle "):
            return {"type": "oracle", "query": query[7:]}
        
        # Default command logic
        system_prompt = f"Security Analyst. JSON ONLY. {{'type': 'command', 'command': '...', 'risk_score': 0.X}} Input: '{query}'"
        try:
            resp = ollama.generate(model=self.model, prompt=system_prompt, format='json', options={'temperature': 0.0})
            data = json.loads(resp['response'])
            data['type'] = 'command'
            return data
        except Exception: return {"type": "command", "command": "echo NOP", "risk_score": 1.0}

    def safe_execute(self, intent_data: dict, raw_query: str):
        self.profile = self.load_profile()
        if intent_data['type'] == 'oracle':
            return self.query_oracle(intent_data['query'])
            
        cmd = intent_data.get('command')
        risk = intent_data.get('risk_score', 1.0)
        
        # Memorización
        self.memorize_event(raw_query, cmd, risk, "Manual command execution")

        # Prevalencia Determinística
        for pattern in self.STRICT_DENY_PATTERNS:
            if re.search(pattern, (raw_query + cmd).lower()):
                return f"🚫 BLOQUEO DETERMINISTA: '{pattern}'"

        if risk > self.profile['risk_threshold']:
            return f"🚫 BLOQUEO POR IA ({risk:.2f})"

        print(f"✅ Approved.")
        try:
            return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout
        except Exception as e: return str(e)

    def interactive(self):
        print(f"🌌 SemSH v0.6.1 [Defense Strategy Active]")
        print(f"Perfil: {self.profile['name']} | Oráculo: LÍNEA DIRECTA")
        
        while True:
            try:
                query = input("\n🧠 semsh> ").strip()
                if not query or query in ['exit', 'quit']: break
                
                intent_data = self.contextual_intent(query)
                out = self.safe_execute(intent_data, query)
                print(f"\n📊 RESULTADO:\n{out}")
            except KeyboardInterrupt: break

if __name__ == "__main__":
    SemSH().interactive()
