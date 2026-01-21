import os
import time
import json
import requests
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

N8N_URL = os.getenv("N8N_URL", "http://localhost:5678")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")
WORKFLOWS_DIR = os.getenv("WORKFLOWS_DIR", str(Path(__file__).parent.parent / "docker/n8n/workflows"))

HEADERS = {"Content-Type": "application/json"}
if N8N_API_KEY:
    HEADERS["X-N8N-API-KEY"] = N8N_API_KEY

class WorkflowHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".json"):
            try:
                with open(event.src_path, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                r = requests.post(f"{N8N_URL}/api/v1/workflows", headers=HEADERS, json=payload, timeout=10)
                print(f"[watchdog] POST {event.src_path} -> {r.status_code}: {r.text[:120]}")
            except Exception as e:
                print(f"[watchdog] Error procesando {event.src_path}: {e}")

    def on_modified(self, event):
        # Opcional: re-publicar si cambia
        pass


def main():
    Path(WORKFLOWS_DIR).mkdir(parents=True, exist_ok=True)
    print(f"[watchdog] Observando: {WORKFLOWS_DIR}")
    print(f"[watchdog] N8N: {N8N_URL}, API_KEY set: {'yes' if N8N_API_KEY else 'no'}")

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
