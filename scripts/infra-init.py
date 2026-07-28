#!/usr/bin/env python3
# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.

"""
INFRA-INIT — Bootstrap del Inventario Esperado (Should-Be State)
================================================================
Carga en Redis los servicios y contenedores que *deberían* estar corriendo
en cada nodo del clúster MycNet/Sentinel, según el diseño arquitectónico.

Uso inicial:
  ./infra_init.py
"""

import os
import sys
import redis

# ─────────────────────────────────────────── CONFIGURACIÓN ────────

REDIS_HOST = os.environ.get("REDIS_HOST", "10.10.10.2")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))

# Define la topología autoritativa de SecurePenguin / MycNet:
# Mapea Node -> [servicios_systemd o contenedores_podman]
TOPOLOGY = {
    # Nodo Maestro / Observabilidad
    "sentinel": [
        "samba-ad-dc",            # BDC (podman)
        "pdns",                   # PowerDNS (podman)
        "guardian-alpha",         # LSM eBPF Daemon (systemd)
        "postgres",               # Base de datos global (podman)
        "redis",                  # Inventario / Event Bus (podman o systemd)
        "grafana",                # Dashboard observability (podman)
        "prometheus",             # Métricas push/scraped (podman)
        "loki",                   # Agregador de logs / bitácora (podman)
        "sentinel-crystal-master" # Daemon de sincronización cuántica (systemd)
    ],
    
    # Nodo Borde / Orquestación LLM
    "fenix": [
        "traefik",                # Reverse Proxy ingress (docker)
        "n8n",                    # Oráculo lógico / truthsync webhook (docker)
        "guacamole",              # Acceso remoto (docker)
        "swarm-dispatcher",       # Despachador de IA (systemd)
        "claude-code"             # Agente persistente fenix (systemd/bg)
    ],
    
    # Nodo Identidad Primaria (PDC)
    "kingu": [
        "samba-ad-dc",            # PDC autoritativo (docker)
        "pdns",                   # PowerDNS (docker)
        "sentinel-crystal-master" # Replica Daemon (systemd)
    ],
    
    # Nodo SOA / Legacy
    "centurion": [
        "mailcow",                # SOA / Correo (docker-compose)
        "pdns",                   # DNS esclavo mail (docker)
        "sssd"                    # Sincronización identidad Unix (systemd)
    ],
    
    # Nodos BKP / LLM workers
    "llm": [
        "ollama"                  # Inferencia tensorial directa (systemd/podman)
    ]
}

def init_inventory():
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.ping()
    except redis.ConnectionError as e:
        print(f"⚠️ No se pudo conectar a Redis ({REDIS_HOST}:{REDIS_PORT}): {e}")
        sys.exit(1)
        
    print("🚀 Iniciando Bootstrap del Inventario Esperado...")
    
    for node, services in TOPOLOGY.items():
        key = f"swarm:infra:expected:{node}"
        
        # Primero limpiamos el inventario viejo de ese nodo
        r.delete(key)
        
        # Agregamos los servicios oficiales
        if services:
            r.sadd(key, *services)
            print(f"✅ Nodo '{node}': {len(services)} servicios registrados.")
        else:
            print(f"ℹ️ Nodo '{node}': sin servicios definidos.")
            
    print("\n📦 Bootstrap completado exitosamente.")
    print("El infra-scanner de cada nodo ahora validará contra este estado (Should-Be).")

if __name__ == "__main__":
    init_inventory()
