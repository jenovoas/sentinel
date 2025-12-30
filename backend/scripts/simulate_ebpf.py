import requests
import time
import json
import os
import sys

# Configuración
API_URL = os.getenv("SENTINEL_API_URL", "http://localhost:8000/api/v1/cortex/events")
TOKEN = os.getenv("SENTINEL_TOKEN", "sentinel-internal-ebpf-key-2025")

def send_event(event_type, data, source="guardian_alpha"):
    headers = {
        "Content-Type": "application/json",
        "X-Sentinel-Token": TOKEN
    }
    payload = {
        "event_type": event_type,
        "source": source,
        "data": data
    }
    
    print(f"📡 Enviando evento {event_type}...")
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 201:
            decision = response.json()
            print(f"✅ Respuesta recibida (ID: {decision['decision_id']})")
            print(f"   Decisión: {decision['decision_type']} (Confianza: {decision['confidence']:.2%})")
            print(f"   Razonamiento: {decision['reasoning']}")
            return decision
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"💥 Error de conexión: {e}")
    return None

def test_scenario_privilege_escalation():
    print("\n🔥 Escenario: Intento de Escalación de Privilegios")
    data = {
        "syscall": "setuid",
        "target_uid": 0,
        "uid": 1000,
        "user": "attacker_demo",
        "pid": 5566,
        "process_name": "sudo-exploit"
    }
    send_event("syscall", data)

def test_scenario_malicious_binary():
    print("\n🔥 Escenario: Ejecución de Binario en Directorio Temporal")
    data = {
        "syscall": "execve",
        "process_path": "/tmp/netcat-rev-shell",
        "user": "www-data",
        "uid": 33,
        "pid": 7788
    }
    send_event("syscall", data)

def test_scenario_data_exfiltration():
    print("\n🔥 Escenario: Exfiltración de Datos Masiva")
    data = {
        "event_type": "network",
        "dest_ip": "1.2.3.4",
        "dest_port": 1337,
        "bytes_sent": 100 * 1024 * 1024, # 100MB
        "protocol": "tcp",
        "is_external": True
    }
    send_event("network", data)

def test_telemetry_injection_attempt():
    print("\n🛡️ Probando mitigación AIOpsDoom (Inyección sin Token)")
    headers = {"Content-Type": "application/json"}
    payload = {"event_type": "syscall", "source": "fake_sensor", "data": {"msg": "i am hacker"}}
    
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 403:
        print("✅ ÉXITO: Intento de inyección bloqueado (403 Forbidden)")
    else:
        print(f"❌ FALLO: El sistema permitió la inyección ({response.status_code})")

if __name__ == "__main__":
    test_telemetry_injection_attempt()
    time.sleep(1)
    test_scenario_privilege_escalation()
    time.sleep(1)
    test_scenario_malicious_binary()
    time.sleep(1)
    test_scenario_data_exfiltration()
    print("\n🏁 Simulación completada.")
