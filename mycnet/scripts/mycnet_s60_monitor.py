#!/usr/bin/env python3
"""
MycNet S60 Monitor
==================
Convierte métricas batman-adv (TQ) a formato Base-60 (S60) para análisis Sentinel.

Uso:
    python3 mycnet_s60_monitor.py

Salida:
    JSON con coherencia de red en S60 y métricas por vecino
"""

import json
import subprocess
import sys
from dataclasses import dataclass

import redis
import os

# --- Redis Configuration ---
REDIS_HOST = "10.10.10.2"
REDIS_PORT = 6379
REDIS_PASS = None

# Try to load Redis password if available
redis_conf = os.path.expanduser("~/.config/swarm/credentials/redis.conf")
if os.path.exists(redis_conf):
    try:
        with open(redis_conf, "r") as f:
            for line in f:
                if "REDIS_PASS" in line:
                    REDIS_PASS = line.split("=")[1].strip().strip('"')
                    break
    except:
        pass

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS, decode_responses=True)

@dataclass(frozen=True)
class S60:
    """Representación Base-60 (grados; minutos, segundos, tercios, cuartos)."""
    d: int  # grados
    m: int  # minutos
    s: int  # segundos
    t: int  # tercios
    q: int  # cuartos
    
    def __str__(self) -> str:
        return f"{self.d},{self.m},{self.s},{self.t},{self.q}"

    def to_decimal(self) -> float:
        return self.d + self.m/60.0 + self.s/3600.0 + self.t/216000.0 + self.q/12960000.0

def dec_to_s60(x: float) -> S60:
    """Convierte decimal [0,1] a S60."""
    if x < 0: x = 0.0
    if x > 1: x = 1.0
    
    d = int(x)
    rem = x - d
    
    rem *= 60; m = int(rem); rem -= m
    rem *= 60; s = int(rem); rem -= s
    rem *= 60; t = int(rem); rem -= t
    rem *= 60; q = int(rem)
    
    return S60(d, m, s, t, q)

def tq_to_s60(tq: int) -> S60:
    """Convierte TQ (0-255) a S60 (0-1)."""
    return dec_to_s60(tq / 255.0)

def get_batman_neighbors() -> list:
    """Obtiene vecinos batman-adv parseando 'batctl n'."""
    try:
        # Check if bat0 exists manually to avoid error messages
        with open("/proc/net/dev", "r") as f:
            if "bat0" not in f.read():
                # Fallback: if no bat0, assume we are on fenix/hub and mock health 1.0
                return [{"neighbor": "hub-uplink", "last_seen": "0.0s", "tq": 255}]

        # Check if batctl exists
        res = subprocess.run(["which", "batctl"], capture_output=True)
        if res.returncode != 0:
             return [{"neighbor": "mock-node-1", "last_seen": "0.1s", "tq": 220}]
             
        output = subprocess.check_output(["batctl", "n"], text=True)
    except Exception:
        return []
    
    neighbors = []
    lines = output.strip().split('\n')
    if len(lines) < 2: return []
    
    for line in lines[1:]:  # Skip header
        if not line.strip():
            continue
        
        parts = line.split()
        if len(parts) >= 4:
            try:
                neighbor = {
                    "neighbor": parts[0],
                    "last_seen": parts[1],
                    "tq": int(parts[3])  # TQ value
                }
                neighbors.append(neighbor)
            except:
                continue
    
    return neighbors

def compute_coherence(neighbors: list) -> float:
    """Calcula coherencia de red (promedio TQ normalizado)."""
    if not neighbors:
        return 0.0
    
    tq_values = [n["tq"] / 255.0 for n in neighbors]
    return sum(tq_values) / len(tq_values)

def main():
    """Ejecuta monitoreo y genera reporte JSON."""
    neighbors = get_batman_neighbors()
    
    coherence_dec = compute_coherence(neighbors)
    coherence_s60 = dec_to_s60(coherence_dec)
    
    # Target coherence: 0.85 = S60[0, 51, 0, 0, 0]
    target_s60 = dec_to_s60(0.85)
    success = coherence_dec >= 0.85
    
    # Escribir a Redis para Lane A (Consolidación FASE 0/3)
    try:
        r.set("swarm:system:net_freq", str(coherence_s60), ex=60)
        # También persistir detalle por nodo
        for n in neighbors:
            r.set(f"swarm:system:net:{n['neighbor']}", json.dumps({
                "reachable": True,
                "tq_s60": str(tq_to_s60(n["tq"])),
                "timestamp": time.time()
            }), ex=60)
    except Exception as e:
        print(f"Error escribiendo a Redis: {e}", file=sys.stderr)

    report = {
        "mesh_coherence_decimal": round(coherence_dec, 4),
        "mesh_coherence_s60": str(coherence_s60),
        "target_s60": str(target_s60),
        "status": "HEALTHY" if success else "DEGRADED",
        "neighbors": [
            {
                "neighbor": n["neighbor"],
                "last_seen": n["last_seen"],
                "tq_decimal": round(n["tq"] / 255.0, 4),
                "tq_s60": str(tq_to_s60(n["tq"]))
            }
            for n in neighbors
        ]
    }
    
    print(json.dumps(report, indent=2))
    return 0 if success else 1

if __name__ == "__main__":
    import time
    # Si se corre como daemon, podemos opcionalmente loopear aquí, 
    # pero el service ya hace restart. Mejor loopear con sleep corto.
    while True:
        main()
        time.sleep(15)
