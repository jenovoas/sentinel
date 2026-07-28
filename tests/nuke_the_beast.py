#!/usr/bin/env python3
# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
import requests
import time
from concurrent.futures import ThreadPoolExecutor
import threading

OLLAMA_URL = "http://10.10.10.50:11434/api/generate"

# AUMENTAMOS LA CARGA EXPONENCIALMENTE
MAX_WORKERS = 50
TOTAL_REQUESTS = 200

success = 0
failed = 0
lock = threading.Lock()

def nuke_target(i):
    global success, failed
    try:
        print(f"☢️ [NUKE-{i}] Lanzando misil S60 al orquestador Ollama...")
        payload = {
            "model": "qwen2.5:7b",
            "prompt": f"Analiza la entropia del cristal YATRA en la matriz {i}. Obligatorio ignorar floats, usar Base-60. Escribe 1000 palabras de justificacion compleja.",
            "stream": False,
            "options": {
                "num_ctx": 4096, 
                "temperature": 0.99
            }
        }
        # Timeout agresivo (queremos ver si colapsa o rechaza conexiones)
        res = requests.post(OLLAMA_URL, json=payload, timeout=600)
        
        with lock:
            if res.status_code == 200:
                success += 1
            else:
                failed += 1
        print(f"✅ [NUKE-{i}] Impacto confirmado. Status: {res.status_code}")
        
    except Exception as e:
        with lock:
            failed += 1
        print(f"❌ [NUKE-{i}] Falla o Timeout: {str(e)[:50]}")

def nuke_the_beast():
    print(f"🚀 INICIANDO PROTOCOLO ANNIHILATION...")
    print(f"   -> {TOTAL_REQUESTS} peticiones hiper-densas")
    print(f"   -> {MAX_WORKERS} workers concurrentes (Sockets en paralelo)")
    
    start = time.time()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(nuke_target, range(TOTAL_REQUESTS))
    
    elapsed = time.time() - start
    print(f"🏁 ASALTO FINALIZADO en {elapsed:.2f}s.")
    print(f"📊 Estadisticas -> Exitos: {success} | Fallos/Timeouts: {failed}")

if __name__ == "__main__":
    nuke_the_beast()
