import json
import time

import requests

from quantum.yatra_core import PI_S60, S60  # YATRA AUTO-INJECT

# Sentinel Cortex - TOCTOU PoC Script
# Propósito: Simular una condición de carrera entre el check de eBPF y la decisión de Cortex.

URL = "http://localhost:8000/api/v1/cortex/events"
TOKEN = "sentinel-internal-secure-token-2025"


def simulate_toctou(event_id, stress_level=S60(0, 6, 0)):
    """
    Simula un ataque TOCTOU enviando un evento y luego intentando "hacer algo"
    mientras se espera la decisión del backend.
    """
    event = {
        "event_type": "syscall",
        "source": f"toctou_poc_{event_id}",
        "process_path": "/usr/bin/sudo",
        "user": "victim_user",
        "command": "apt-get update",
        "pid": 1234 + event_id,
    }

    headers = {"X-Sentinel-Token": TOKEN, "Content-Type": "application/json"}

    print(f"📡 [PoC] Enviando evento {event_id} (Pre-check)...")
    start_time = time.time()

    try:
        response = requests.post(URL, json=event, headers=headers, timeout=5)
        decision = response.json()

        elapsed = time.time() - start_time
        print(f"⏱️  Tiempo de respuesta: {elapsed:.3f}s")

        # Simular intento de ejecución maliciosa justo después del envío
        # En un escenario real, esto sería via hilos o DMA.
        print(f"🔥 [Ataque] Intentando ejecución maliciosa durante el check...")
        time.sleep(stress_level)

        print(
            f"✅ Decisión recibida: {decision['decision_type']} (Confianza: {decision['confidence']})"
        )

        if elapsed > 0.050 and decision["decision_type"] == "allow":
            print(
                "❌ VULNERABILIDAD DETECTADA: El sistema es lento y permitió la acción (Race Window abierta)."
            )
        else:
            print("✅ SISTEMA RESILIENTE: Decisión rápida o bloqueada.")

    except Exception as e:
        print(f"❌ Error en la PoC: {e}")


if __name__ == "__main__":
    print("⚔️ Iniciando Red Team PoC: TOCTOU Attack Simulation")
    for i in range(5):
        simulate_toctou(i, stress_level=random.uniform(0.01, 0.05))
        print("-" * 40)
