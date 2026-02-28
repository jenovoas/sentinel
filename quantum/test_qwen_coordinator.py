#!/usr/bin/env python3
"""
Test de integración: Qwen Coordinator con telemetría real desde Redis.
No usa datos inventados — lee el estado actual del enjambre.
"""
import urllib.request
import json
import time
import sys
import redis

LLM_HOST = "10.10.10.50:11434"
API_GENERATE = f"http://{LLM_HOST}/api/generate"
API_TAGS = f"http://{LLM_HOST}/api/tags"
REDIS_HOST = "10.10.10.2"
REDIS_PORT = 6379


def get_qwen_model():
    try:
        req = urllib.request.Request(API_TAGS, method="GET")
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode())
            for model in data.get('models', []):
                name = model.get('name', '')
                if 'qwen' in name.lower():
                    return name
            if data.get('models'):
                return data['models'][0]['name']
    except Exception as e:
        print(f"Error conectando a Ollama ({LLM_HOST}): {e}")
    return None


def get_real_telemetry(r: redis.Redis) -> str:
    """Lee el estado real del enjambre desde Redis."""
    lines = []

    # Estado del cristal
    phase = r.get("swarm:crystal:phase") or "UNKNOWN"
    coherence = r.get("swarm:crystal:coherence") or "0"
    lines.append(f"[CRYSTAL BRAIN]")
    lines.append(f"- phase: {phase} | coherence: {coherence}")

    # Nodos
    for node in ["sentinel", "fenix", "kingu", "centurion", "llm"]:
        data = r.hgetall(f"swarm:crystal:node:{node}")
        if data:
            lines.append(f"- {node}: phase={data.get('phase','?')} coherence={data.get('coherence','?')}")

    # Tareas activas
    pending = r.get("swarm:tasks:pending") or "0"
    running = r.get("swarm:tasks:running_count") or "0"
    lines.append(f"\n[TAREAS]")
    lines.append(f"- pending: {pending} | running: {running}")

    # Infraestructura conocida
    infra_log = r.lrange("swarm:infra:log", -5, -1)
    if infra_log:
        lines.append(f"\n[EVENTOS INFRA RECIENTES]")
        for entry in infra_log:
            lines.append(f"- {entry}")

    return "\n".join(lines)


def test_swarm_coordination(model_name: str, r: redis.Redis) -> bool:
    """
    Envía telemetría real al LLM y verifica que la respuesta es JSON válido
    con los campos esperados: 'analisis' y 'tareas'.
    Retorna True si el test pasa.
    """
    print(f"\n=== Test coordinación Qwen: {model_name} ===")

    telemetry = get_real_telemetry(r)
    print(f"Telemetría capturada:\n{telemetry}\n")

    system_prompt = (
        "Eres el Arquitecto de Coordinación del Enjambre Sentinel. "
        "Analiza la telemetría y responde ÚNICAMENTE con JSON válido:\n"
        '{"analisis": "diagnostico", "tareas": [{"agente": "nombre", "accion": "orden"}]}'
    )
    prompt = f"TELEMETRÍA ACTUAL:\n{telemetry}\n\nGenera plan de acción."

    payload = {
        "model": model_name,
        "system": system_prompt,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }

    start = time.time()
    try:
        req = urllib.request.Request(
            API_GENERATE,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as res:
            raw = json.loads(res.read().decode())
            elapsed = time.time() - start
            print(f"Inferencia: {elapsed:.1f}s")

            response_text = raw.get("response", "")
            decision = json.loads(response_text)

            # Assertions reales
            assert "analisis" in decision, "Falta campo 'analisis' en respuesta"
            assert "tareas" in decision, "Falta campo 'tareas' en respuesta"
            assert isinstance(decision["tareas"], list), "'tareas' debe ser lista"
            assert len(decision["tareas"]) > 0, "'tareas' no puede estar vacía"

            print(f"PASS — analisis: {decision['analisis'][:80]}...")
            print(f"       tareas: {len(decision['tareas'])} órdenes generadas")
            return True

    except json.JSONDecodeError as e:
        print(f"FAIL — respuesta no es JSON válido: {e}")
        return False
    except AssertionError as e:
        print(f"FAIL — assertion: {e}")
        return False
    except Exception as e:
        print(f"ERROR — {e}")
        return False


if __name__ == "__main__":
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    try:
        r.ping()
    except Exception as e:
        print(f"Redis no disponible ({REDIS_HOST}:{REDIS_PORT}): {e}")
        sys.exit(1)

    model = get_qwen_model()
    if not model:
        print(f"No se pudo determinar modelo Qwen en {LLM_HOST}")
        sys.exit(1)

    passed = test_swarm_coordination(model, r)
    sys.exit(0 if passed else 1)
