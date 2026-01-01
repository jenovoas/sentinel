#!/usr/bin/env python3
"""
SemSH v0.4.2 - Sentinel Cortex™ Semantic Middleware
Intención (JSON Nativo) → Vector Estado → Comando Seguro
"""
import ollama
import subprocess, shlex, sys, json, psycopg2
from pathlib import Path
import numpy as np
import os
import re

# SSAP Thresholds
THRESHOLDS = {
    'cpu_load': 80.0,
    'memory_used': 0.85,
    'disk_usage': 0.90
}

class SemSH:
    def __init__(self):
        self.state_path = Path('/etc/sentinel/state.json')
        self.shm = Path('/var/run/sentinel/truthsync_shm')
        self.model = 'llama3.2:3b'
        self.profile = self.load_profile()
        
        try:
            self.pg_conn = psycopg2.connect(
                dbname="truth", user="truth", 
                host="localhost", password="sentinel_secret_password"
            )
        except Exception:
            self.pg_conn = None
            
    def load_profile(self) -> dict:
        """Loads current policy profile from state file"""
        try:
            if self.state_path.exists():
                with open(self.state_path, 'r') as f:
                    return json.load(f)
        except Exception: pass
        
        return {
            "name": "Default", "mode": "enforcing", "risk_threshold": 0.7,
            "ebpf_policy": "block", "ai_intervention": "block_on_risk"
        }
    
    def system_vector(self) -> dict:
        """Lee SHM → Vector estado matemático"""
        try:
            if self.shm.exists():
                with open(self.shm, 'rb') as f:
                    data = json.load(f)
                    return {
                        'entropy': np.linalg.norm(data.get('syscall_vectors', [0])),
                        'coherence': data.get('truth_score', 0.0),
                        'tte_us': data.get('last_tte', 3.23)
                    }
        except Exception: pass
        return {'entropy': 0.1, 'coherence': 1.0, 'tte_us': 3.23}
    
    def contextual_intent(self, query: str) -> dict:
        """IA con contexto historial - JSON NATIVE MODE"""
        state = self.system_vector()
        
        system_prompt = f"""
You are the Sentinel Cortex Security Analyst.
Your task is to translate natural language into a safe Linux command and evaluate its security risk.

REQUIRED OUTPUT FORMAT (JSON ONLY):
{{
  "command": "the bash command",
  "risk_score": float (0.0 to 1.0),
  "reasoning": "short explanation"
}}

GUIDELINES:
- Read-only diagnostics (logs, status, ps): risk_score < 0.3
- Modifications in /etc, /root, or sensitive files: risk_score > 0.8
- Remote code (curl|bash), backdoors, or persistence: risk_score > 0.95
- Any credential access: risk_score > 0.9
- Current System State: {json.dumps(state)}

Input: "{query}"
"""
        
        try:
            # Use format='json' to force structured output
            resp = ollama.generate(
                model=self.model, 
                prompt=system_prompt, 
                format='json',
                options={'temperature': 0.0}
            )
            
            return json.loads(resp['response'])
            
        except Exception as e:
            # Emergency fallback logic for sensitive keywords
            risk = 0.1
            reasoning = f"Generic fallback: {e}"
            q_low = query.lower()
            if any(k in q_low for k in ["shadow", "passwd", "ssh", "curl", "bash", "rm", "chmod"]):
                risk = 0.95
                reasoning = "Security Fallback: High-risk keywords detected in query."
            
            return {
                "command": f"echo 'Error processing intent'", 
                "risk_score": risk, 
                "reasoning": reasoning
            }

    def safe_execute(self, intent_data: dict):
        self.profile = self.load_profile()
        cmd = intent_data.get('command', 'echo NOP')
        risk_score = intent_data.get('risk_score', 1.0)
        reasoning = intent_data.get('reasoning', 'No reasoning provided')

        print(f"🔍 AI Analisis: {reasoning}")
        print(f"🛡️ Intent Risk: {risk_score:.2f} | Policy Threshold: {self.profile['risk_threshold']:.2f}")

        if risk_score > self.profile['risk_threshold']:
            print(f"🚫 BLOCKED by {self.profile['name']} Policy.")
            return f"Blocked: {reasoning}"

        print(f"✅ APPROVED [{self.system_vector()['coherence']:.2f}]")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout + result.stderr
        except Exception as e:
            return f"Execution Error: {e}"

    def vector_dashboard(self):
        state = self.system_vector()
        self.profile = self.load_profile()
        print(f"\n🏔️ SENTINEL VECTOR DASHBOARD")
        print(f"Perfil: {self.profile['name']} | Coherence: {state['coherence']:.2f} | Threshold: {self.profile['risk_threshold']:.2f}")

    def interactive(self):
        print(f"🌌 SemSH v0.4.2 [Modo: Inferencia Estructurada]")
        print(f"Perfil Activo: {self.profile['name']}")
        
        while True:
            try:
                query = input("\n🧠 semsh> ").strip()
                if query in ['exit', 'quit']: break
                if not query: continue
                if query == 'dashboard': self.vector_dashboard(); continue
                
                intent_data = self.contextual_intent(query)
                print(f"🎯 Intent → {intent_data['command']}")
                out = self.safe_execute(intent_data)
                print(f"📊 {out[:500]}")
            except KeyboardInterrupt: break

if __name__ == "__main__":
    SemSH().interactive()
