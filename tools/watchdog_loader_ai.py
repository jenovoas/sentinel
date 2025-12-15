import os
import time
import json
import requests
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

N8N_URL = os.getenv("N8N_URL", "http://localhost:5678")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "8"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "30"))
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))
WORKFLOWS_DIR = os.getenv("WORKFLOWS_DIR", str(Path(__file__).parent.parent / "docker/n8n/workflows"))
AI_ENABLED = os.getenv("AI_ENABLED", "true").lower() == "true"

HEADERS = {"Content-Type": "application/json"}
if N8N_API_KEY:
    HEADERS["X-N8N-API-KEY"] = N8N_API_KEY

def enrich_with_ai(workflow_json, workflow_path):
    """Enriquece un workflow con sugerencias de IA"""
    if not AI_ENABLED:
        return workflow_json
    
    try:
        # Generar descripción con IA (con protección contra bucles)
        prompt = f"Describe brevemente este workflow n8n y sugiere mejoras. Workflow name: {workflow_json.get('name', 'sin nombre')}"
        
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "num_predict": OLLAMA_NUM_PREDICT,
                "temperature": OLLAMA_TEMPERATURE,
                "stream": False
            },
            timeout=OLLAMA_TIMEOUT
        )
        
        if response.status_code == 200:
            ai_response = response.json().get("response", "")
            print(f"   🤖 IA insights: {ai_response[:100]}...")
            
            # Agregar metadata de IA al workflow
            if "settings" not in workflow_json:
                workflow_json["settings"] = {}
            
            workflow_json["settings"]["ai_enriched"] = True
            workflow_json["settings"]["ai_model"] = OLLAMA_MODEL
            
            return workflow_json
    except Exception as e:
        print(f"   ⚠️ IA enriquecimiento falló: {e}")
    
    return workflow_json


class WorkflowHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".json"):
            try:
                # Esperar a que el archivo se escriba completamente
                time.sleep(0.5)
                with open(event.src_path, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                
                # Enriquecer con IA si está habilitado
                if AI_ENABLED:
                    print(f"   🧠 Enriqueciendo con IA ({OLLAMA_MODEL})...")
                    payload = enrich_with_ai(payload, event.src_path)
                
                r = requests.post(f"{N8N_URL}/api/v1/workflows", headers=HEADERS, json=payload, timeout=10)
                status_icon = "✅" if r.status_code == 200 else "⚠️"
                print(f"{status_icon} [watchdog] POST {event.src_path} -> {r.status_code}")
            except Exception as e:
                print(f"❌ [watchdog] Error procesando {event.src_path}: {e}")


def main():
    Path(WORKFLOWS_DIR).mkdir(parents=True, exist_ok=True)
    print(f"[watchdog] Observando: {WORKFLOWS_DIR}")
    print(f"[watchdog] N8N: {N8N_URL}, API_KEY set: {'yes' if N8N_API_KEY else 'no'}")
    print(f"[watchdog] AI: {'✅ ENABLED' if AI_ENABLED else '❌ DISABLED'}")
    if AI_ENABLED:
        print(f"[watchdog] Ollama: {OLLAMA_URL}, Modelo: {OLLAMA_MODEL}")

    obs = Observer()
    handler = WorkflowHandler()
    obs.schedule(handler, WORKFLOWS_DIR, recursive=False)
    obs.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()

if __name__ == "__main__":
    main()
