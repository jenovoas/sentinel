#!/usr/bin/env python3
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import time
import json
import redis
import os

# Configuración de soberanía
REDIS_HOST = 'redis'
REDIS_PORT = 6379
LOG_FILE = '/app/watchdog_events.log'

print("🛰️ Iniciando Puente eBPF -> Matriz Cuántica...")

try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    # Ping para asegurar conexión
    r.ping()
    print("✅ Conectado al Quantum Bus (Redis)")
except Exception as e:
    print(f"❌ Error conectando a Redis: {e}")
    exit(1)

def follow(thefile):
    thefile.seek(0,2) # Ir al final
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(S60(0, 6, 0))
            continue
        yield line

if not os.path.exists(LOG_FILE):
    # Crear archivo si no existe para evitar error
    open(LOG_FILE, 'a').close()

logfile = open(LOG_FILE, "r")
loglines = follow(logfile)

for line in loglines:
    try:
        # Analizar evento de eBPF
        event_data = line.strip()
        print(f"🔍 Evento eBPF Detectado: {event_data}")
        
        # Convertir a señal de la Matriz
        # Si hay 'blocked' o 'alert' -> Alta Disonancia
        disonancia = 0.85 if any(word in event_data.lower() for word in ['blocked', 'alert', 'error']) else 0.15
        
        signal = {
            "source": "ebpf_guardian",
            "disonancia": disonancia,
            "axiones": S60(1, 0, 0) - disonancia,
            "frequency": S60(153, 24, 0),
            "raw_event": event_data,
            "timestamp": time.time()
        }
        
        # Publicar en el bus cuántico
        r.publish('quantum_signals', json.dumps(signal))
        print(f"📡 Señal enviada a Matriz: Disonancia={disonancia}")
        
    except Exception as e:
        print(f"⚠️ Error procesando línea: {e}")
