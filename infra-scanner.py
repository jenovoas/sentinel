#!/usr/bin/env python3

"""
INFRA-SCANNER — Agente de Descubrimiento de Infraestructura
===========================================================
Escanea el estado del nodo (hardware, systemd, podman) y lo publica en Redis 
bajo el namespace `swarm:infra:*`. Si detecta desviaciones respecto al 
estado `expected`, emite un evento a la bitácora inmutable `swarm:infra:log`.

Uso:
  ./infra_scanner.py [--loop <segundos>]
"""

import os
import sys
import json
import time
import socket
import subprocess
import argparse
import redis
from datetime import datetime

# ─────────────────────────────────────────── CONFIGURACIÓN ────────

REDIS_HOST = os.environ.get("REDIS_HOST", "10.10.10.2")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))

NODE_NAME = socket.gethostname()

KEY_NODE     = f"swarm:infra:node:{NODE_NAME}"
KEY_EXPECTED = f"swarm:infra:expected:{NODE_NAME}"
STREAM_LOG   = "swarm:infra:log"

# ─────────────────────────────────────────── SCANNER ──────────────

class InfraScanner:
    def __init__(self):
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        try:
            self.redis.ping()
        except redis.ConnectionError as e:
            print(f"⚠️ No se pudo conectar a Redis en {REDIS_HOST}:{REDIS_PORT}: {e}")
            sys.exit(1)
            
        print(f"🔍 InfraScanner iniciado en nodo: {NODE_NAME}")
        self.expected_services = self._get_expected_services()
        
    def _get_expected_services(self) -> set:
        """Carga la lista de servicios esperados desde Redis."""
        expected = self.redis.smembers(KEY_EXPECTED)
        if not expected:
            # Fallback a defaults si no hay config
            defaults = {
                "sentinel": ["samba-ad-dc", "pdns", "guardian-alpha", "postgres", "redis", "grafana", "prometheus", "loki", "sentinel-crystal-master"],
                "fenix": ["traefik", "n8n", "guacamole", "swarm-dispatcher", "claude-code"],
                "kingu": ["samba-ad-dc", "pdns", "sentinel-crystal-master"],
                "centurion": ["mailcow", "pdns", "sssd"]
            }
            expected = set(defaults.get(NODE_NAME, []))
            
            # Poblar redis con el default para la próxima
            if expected:
                self.redis.sadd(KEY_EXPECTED, *expected)
                
        return expected

    def scan_node_hardware(self):
        """Escanea info básica del hardware/OS y actualiza el Hash del nodo."""
        try:
            # Obtener IP (asumiendo eth0 o similar con ruta por defecto)
            ip_output = subprocess.check_output(["ip", "route", "get", "1.1.1.1"], text=True)
            ip_pub = ip_output.split('src')[1].split()[0] if 'src' in ip_output else 'unknown'
            
            # Obtener uptime
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                
            # Obtener load avg
            with open('/proc/loadavg', 'r') as f:
                load = f.readline().split()[0]
                
            # Obtener RAM
            with open('/proc/meminfo', 'r') as f:
                mem_total = int(f.readline().split()[1]) // 1024 # MB
                
            kernel = subprocess.check_output(["uname", "-r"]).decode().strip()
            
        except Exception as e:
            print(f"⚠️ Error escaneando hardware: {e}")
            ip_pub = "unknown"
            uptime_seconds = 0
            load = "0"
            mem_total = 0
            kernel = "unknown"
            
        self.redis.hset(KEY_NODE, mapping={
            "ip_pub": ip_pub,
            "os": "linux",
            "kernel": kernel,
            "ram_mb": str(mem_total),
            "load_1m": load,
            "uptime_s": str(uptime_seconds),
            "last_seen": str(int(time.time())),
            "status": "online"
        })
        
        # Expirar la key si el nodo se cae (watchdog de 3x el intervalo)
        self.redis.expire(KEY_NODE, 900)

    def scan_systemd_services(self) -> dict:
        """Escanea estado de servicios systemd relevantes."""
        services_state = {}
        for svc in self.expected_services:
            # Verificamos si es un servicio systemd
            try:
                result = subprocess.run(["systemctl", "is-active", svc], capture_output=True, text=True)
                if result.returncode != 0:
                    result = subprocess.run(["systemctl", "is-active", f"{svc}.service"], capture_output=True, text=True)
                is_active = result.returncode == 0
                state = "active" if is_active else "inactive"
                
                # Ignorar si el servicio no existe o es un contenedor de compose
                if "unknown" in result.stdout.lower() and "inactive" in result.stdout.lower():
                    continue
                    
                services_state[svc] = {
                    "type": "systemd",
                    "state": state,
                    "expected": "active"
                }
            except Exception:
                pass
        return services_state

    def scan_podman_containers(self) -> dict:
        """Escanea contenedores usando docker o podman según esté disponible."""
        containers_state = {}
        try:
            # Detectar el motor (preferimos docker en fenix/centurion, podman en sentinel)
            # En Fenix ubuntu corre docker nativo.
            try:
                result_help = subprocess.check_output(["docker", "ps", "--help"], stderr=subprocess.STDOUT, text=True)
                if "podman" in result_help.lower():
                    motor = "podman"
                else:
                    motor = "docker"
            except (subprocess.CalledProcessError, FileNotFoundError):
                motor = "podman"
                
            use_sudo = ["sudo"] if motor == "podman" else [] # Docker suele estar en el grupo del usuario, podman rootless o sudo
            
            # Docker usa {{.RestartCount}}, Podman usa {{.Restarts}} si falla el primero
            if motor == "docker":
                cmd = use_sudo + [motor, "ps", "-a", "--format", "{{.Names}}|{{.State}}|{{.Image}}|{{.RestartCount}}"]
            else:
                # Fallback genérico para podman en Debian
                cmd = use_sudo + [motor, "ps", "-a", "--format", "{{.Names}}|{{.State}}|{{.Image}}"]
                
            result = subprocess.check_output(cmd, text=True)
            
            for line in result.strip().split('\n'):
                if not line: continue
                parts = line.split('|')
                if len(parts) >= 3:
                    name, state, image = parts[0], parts[1], parts[2]
                    restarts = parts[3] if len(parts) > 3 else "0"
                    
                    # Limpiamos nombres de compose (ej: sentinel_loki_1 -> loki)
                    clean_name = name
                    for expected in self.expected_services:
                        if expected in name:
                            clean_name = expected
                            break
                            
                    containers_state[clean_name] = {
                        "type": "podman",
                        "name": name,
                        "state": state.lower(),
                        "image": image,
                        "restarts": restarts,
                        "expected": "running" if clean_name in self.expected_services else "unknown"
                    }
        except Exception as e:
            print(f"⚠️ Error escaneando podman (¿requiere sudo?): {e}")
            
        return containers_state
        
    def audit_and_report(self, states: dict):
        """
        Compara el nuevo estado con el estado anterior en Redis.
        Si hay cambios, genera un evento de bitácora (XADD).
        """
        timestamp = str(int(time.time()))
        
        for name, current in states.items():
            key_svc = f"swarm:infra:svc:{NODE_NAME}:{name}"
            
            # Obtener estado anterior
            prev_state_str = self.redis.hget(key_svc, "state")
            prev_restarts_str = self.redis.hget(key_svc, "restarts")
            
            current_state = current.get("state", "unknown")
            current_restarts = current.get("restarts", "0")
            
            # Actualizar Hash en Redis
            mapping = {
                "type": current.get("type", "unknown"),
                "state": current_state,
                "restarts": current_restarts,
                "expected": current.get("expected", "unknown"),
                "last_check": timestamp
            }
            if "image" in current: mapping["image"] = current["image"]
            if "name" in current: mapping["container_name"] = current["name"]
            
            self.redis.hset(key_svc, mapping=mapping)
            
            # Analizar desviaciones para la bitácora
            event_type = None
            
            if prev_state_str and prev_state_str != current_state:
                event_type = "STATE_CHANGE"
            elif prev_restarts_str and prev_restarts_str != current_restarts:
                event_type = "CONTAINER_RESTART"
            elif not prev_state_str and current_state != "unknown":
                event_type = "SERVICE_DISCOVERED"
                
            if current_state != "running" and current_state != "active" and current.get("expected") in ["running", "active"]:
                if event_type != "STATE_CHANGE":  # Para no duplicar eventos si ya detectamos el cambio
                    # Solo enviar evento de fallo intermitentemente (no spam)
                    last_alert = self.redis.hget(key_svc, "last_alert")
                    if not last_alert or int(timestamp) - int(last_alert) > 3600:
                        event_type = "SERVICE_DOWN_ALERT"
                        self.redis.hset(key_svc, "last_alert", timestamp)
            
            if event_type:
                # Escribir en la bitácora S60 (Stream)
                log_entry = {
                    "node": NODE_NAME,
                    "agent": "infra-scanner",
                    "event_type": event_type,
                    "service": name,
                    "old_state": str(prev_state_str),
                    "new_state": current_state,
                    "restarts": str(current_restarts),
                    "timestamp": timestamp
                }
                self.redis.xadd(STREAM_LOG, log_entry)
                print(f"📝 Bitácora: [{NODE_NAME}] {name} -> {event_type} ({current_state})")


    def run_scan(self):
        """Ejecuta un ciclo completo de escaneo y reporte."""
        print(f"--- Escaneo iniciado: {datetime.now()} ---")
        
        self.expected_services = self._get_expected_services()
        self.scan_node_hardware()
        
        all_states = {}
        all_states.update(self.scan_systemd_services())
        all_states.update(self.scan_podman_containers())
        
        self.audit_and_report(all_states)
        print("✅ Escaneo completado.\n")


# ─────────────────────────────────────────── ENTRY POINT ──────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scanner de Infraestructura SecurePenguin")
    parser.add_argument("--loop", type=int, help="Ejecutar en bucle cada N segundos")
    args = parser.parse_args()
    
    scanner = InfraScanner()
    
    if args.loop:
        print(f"🔄 Modo Daemon: escaneando cada {args.loop} segundos")
        try:
            while True:
                scanner.run_scan()
                time.sleep(args.loop)
        except KeyboardInterrupt:
            print("\nDetenido.")
    else:
        scanner.run_scan()
