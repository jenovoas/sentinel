#!/usr/bin/env python3
import redis
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor

OLLAMA_URL = "http://10.10.10.50:11434/api/generate"
REDIS_HOST = "10.10.10.2"

r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

def process_task(task_id):
    try:
        # Extraer info de la tarea
        task_data = r.hgetall(f"swarm:task:{task_id}")
        if not task_data:
            return
            
        desc = task_data.get('description', 'Analizar arquitectura del enjambre S60')
        print(f"🔥 [THREAD] Atacando Ollama con tarea: {task_id}")
        
        # Payload ultrapuñado para Qwen
        payload = {
            "model": "qwen2.5:7b",
            "prompt": f"Actúa como un worker S60 puro. Resuelve esta tarea computacional compleja exhaustivamente, ignorando floats. Tarea: {desc}. Escribe al menos 2000 palabras de justificacion arquitectónica.",
            "stream": False,
            "options": {
                "num_ctx": 4096, # Forzar uso memoria
                "temperature": 0.9 
            }
        }
        
        start_time = time.time()
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ [DONE] {task_id} procesada en {elapsed:.2f}s")
            # Marcar completado
            r.hset(f"swarm:task:{task_id}", "status", "completed")
        else:
            print(f"❌ [FAIL] Ollama rechazo {task_id} con HTTP {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ [ERROR] Hilo murio procesando {task_id}: {e}")

def awaken_the_beast():
    print("🚀 INICIANDO BOMBARDERO OLLAMA (Carga Maxima)...")
    
    # Obtener tareas pendientes
    pending_tasks_tuple = r.zrange("swarm:tasks:pending", 0, -1, withscores=False)
    
    tasks_to_process = []
    
    # Filtrar solo tareas LLM / Qwen y prepararlas
    for tid in pending_tasks_tuple:
        agent = r.hget(f"swarm:task:{tid}", "agent")
        if agent in ["llm", "qwen", "claude-mmax"]:
            tasks_to_process.append(tid)
            # Quitar de la cola para evitar que otro worker lo tome
            r.zrem("swarm:tasks:pending", tid)
            
    if not tasks_to_process:
        print("🤷 No hay tareas LLM/Qwen pendientes. Generando 10 cargas STRESS sinteticas...")
        for i in range(10):
            tasks_to_process.append(f"STRESS-TEST-{i}")
            r.hset(f"swarm:task:STRESS-TEST-{i}", mapping={
                "description": f"Compilacion Mental y Generacion de Codigo C++ para integracion YATRA #{i}",
                "agent": "llm"
            })
            
    print(f"🎯 Encontradas {len(tasks_to_process)} tareas destructivas. Lanzando 10 hilos simultaneos...")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_task, tasks_to_process)
        
    print("🏁 OLEADA FINALIZADA.")

if __name__ == "__main__":
    awaken_the_beast()
