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

@dataclass(frozen=True)
class S60:
    """Representación Base-60 (grados; minutos, segundos, tercios, cuartos)."""
    d: int  # grados
    m: int  # minutos
    s: int  # segundos
    t: int  # tercios
    q: int  # cuartos
    
    def __str__(self) -> str:
        return f"S60[{self.d:03d}; {self.m:02d}, {self.s:02d}, {self.t:02d}, {self.q:02d}]"

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
        output = subprocess.check_output(["batctl", "n"], text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando batctl: {e}", file=sys.stderr)
        return []
    
    neighbors = []
    for line in output.strip().split('\n')[1:]:  # Skip header
        if not line.strip():
            continue
        
        parts = line.split()
        if len(parts) >= 4:
            neighbor = {
                "neighbor": parts[0],
                "last_seen": parts[1],
                "tq": int(parts[3])  # TQ value
            }
            neighbors.append(neighbor)
    
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
    
    if not neighbors:
        print(json.dumps({"error": "No neighbors found"}, indent=2))
        return 1
    
    coherence_dec = compute_coherence(neighbors)
    coherence_s60 = dec_to_s60(coherence_dec)
    
    # Target coherence: 0.85 = S60[000; 51, ...]
    target_s60 = dec_to_s60(0.85)
    success = coherence_dec >= 0.85
    
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
    sys.exit(main())
