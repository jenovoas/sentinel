#!/usr/bin/env python3
"""
SemSH v0.6.0 - Sentinel Cortex™ Digital Hippocampus Edition
Harmony: Internal Memory (ChromaDB) + External Intel (SearXNG) + Kernel Truth (TruthSync)
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
        
        # 1. Conexión a Memoria Histórica (Postgres)
        try:
            self.pg_conn = psycopg2.connect(
                dbname="sentinel_master", user="sentinel", 
                host="localhost", password="sentinel_secret_password"
            )
        except Exception: self.pg_conn = None
        
        # 2. Conexión a Memoria Semántica (ChromaDB - El Hipocampo)
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
            # En producción usaríamos embeddings de Ollama, 
            # aquí usamos el default de Chroma (SentenceTransformers) para agilidad.
            self.collection.add(
                documents=[content],
                metadatas=[{"risk": risk, "ts": timestamp, "profile": self.profile['name']}],
                ids=[f"ev_{datetime.now().timestamp()}"]
            )
        except Exception as e:
            print(f"⚠️ Fallo en memorización: {e}")

    def query_oracle(self, question: str):
        """Consulta al Oráculo: Combina Memoria Interna + IA"""
        print(f"🔮 Consultando al Oráculo de Sentinel sobre: '{question}'...")
        
        # 1. Recuperar eventos relevantes de ChromaDB
        results = self.collection.query(
            query_texts=[question],
            n_results=5
        )
        
        events = "\n".join(results['documents'][0]) if results['documents'] else "No hay recuerdos previos."
        
        # 2. Razonamiento tipo Perplexity
        oracle_prompt = f"""
SENTINEL ORACLE - INTERNAL MEMORY ANALYSIS.
User is asking: {question}

I have retrieved these relevant memories from the system history:
{events}

Current Profile: {self.profile['name']}

Task: Provide a synthesis of what has happened. Identify patterns, 
security risks, or anomalies based ONLY on these memories.
"""
        try:
            print("🧠 La IA está recorriendo tus recuerdos digitales...")
            resp = ollama.generate(model=self.model, prompt=oracle_prompt)
            return resp['response']
        except Exception as e:
            return f"❌ El Oráculo está confundido: {e}"

    def sovereign_verify(self, context: str):
        """Búsqueda web para de-noising"""
        try:
            resp = requests.get(self.searxng_url, params={'q': context, 'format': 'json'}, timeout=10)
            results = resp.json().get('results', [])[:3]
            intel = "\n".join([r.get('content', '') for r in results])
            
            prompt = f"Analyze this security context via web intel:\n{intel}\nContext: {context}"
            return ollama.generate(model=self.model, prompt=prompt)['response']
        except Exception: return "Error en SSS."

    def contextual_intent(self, query: str) -> dict:
        # Detectar comandos del Oráculo
        if query.lower().startswith("oracle "):
            return {"type": "oracle", "query": query[7:]}
        
        system_prompt = f"Security Analyst. JSON ONLY. {{'type': 'command', 'command': '...', 'risk_score': 0.X, 'reasoning': '...'}} Input: '{query}'"
        try:
            resp = ollama.generate(model=self.model, prompt=system_prompt, format='json')
            data = json.loads(resp['response'])
            data['type'] = 'command'
            return data
        except Exception: return {"type": "command", "command": "echo NOP", "risk_score": 1.0, "reasoning": "FailSafe"}

    def safe_execute(self, intent_data: dict, raw_query: str):
        self.profile = self.load_profile()
        
        if intent_data['type'] == 'oracle':
            return self.query_oracle(intent_data['query'])
            
        cmd = intent_data.get('command')
        risk = intent_data.get('risk_score', 1.0)
        reasoning = intent_data.get('reasoning', '')

        # Memorización automática
        self.memorize_event(raw_query, cmd, risk, reasoning)

        # Prevalencia Determínistica
        for pattern in self.STRICT_DENY_PATTERNS:
            if re.search(pattern, (raw_query + cmd).lower()):
                return f"🚫 BLOQUEO DETERMINISTA: '{pattern}'"

        if risk > self.profile['risk_threshold']:
            return f"🚫 BLOQUEO POR IA ({risk:.2f})"

        print(f"✅ Executing...")
        try:
            return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout
        except Exception as e: return str(e)

    def interactive(self):
        print(f"🌌 SemSH v0.6.0 [Oracle Edition: ChromaDB Integrated]")
        print(f"Perfil: {self.profile['name']} | Memoria: ACTIVA")
        
        while True:
            try:
                query = input("\n🧠 semsh> ").strip()
                if not query or query in ['exit', 'quit']: break
                
                intent_data = self.contextual_intent(query)
                out = self.safe_execute(intent_data, query)
                print(f"\n📊 RESULTADO:\n{out[:800]}...")
            except KeyboardInterrupt: break

if __name__ == "__main__":
    SemSH().interactive()
