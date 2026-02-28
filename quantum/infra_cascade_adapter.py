#!/usr/bin/env python3
import os
import sys
import redis
import time
import json
import socket
import logging

# YATRA LOCKED: Zero floats, only S60 integers
CLUSTER_NODES = ["kingu", "sentinel", "centurion", "fenix", "llm"]

# Incorporamos la ruta pura de Sentinel Quantum
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from ai_buffer_cascade import AIBufferCascade
from yatra_core import S60
from hexagonal_control import HexagonalController

class InfraCascadeAdapter:
    def __init__(self, redis_host='10.10.10.2'):
        self.r = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)
        # Inicializamos Hexagonal y Cascade genuinos
        self.hex_ctrl = HexagonalController(size=7)
        self.cascade = AIBufferCascade(self.hex_ctrl)
        self.logger = logging.getLogger("InfraCascade")
        logging.basicConfig(level=logging.INFO)

    def container_event_to_rift(self, event: dict):
        node = event.get('node', 'unknown')
        try:
            node_idx = CLUSTER_NODES.index(node)
        except ValueError:
            node_idx = 99
        
        # Consideramos un reinicio de servicio como una friccion +1
        # Omitimos floats, pura suma de tensores indexados
        return (node_idx, 1)

    def publish_prediction(self, node: str, result: dict):
        payload = {
            'future_coherence': str(result['future_coherence_target']),
            'vimana_ready': str(result['vimana_ready']),
            'memory_strength': str(result['memory_strength']),
            'timestamp': int(time.time()),
        }
        self.r.hset(f"swarm:infra:predictions:{node}", mapping=payload)
        self.logger.info(f"YATRA Predicted {node} -> {payload}")

    def run_daemon(self):
        self.logger.info("📡 Iniciando Sentinel Infra Predictor (YATRA S60)")
        last_id = "0-0"
        while True:
            try:
                # XREAD bloqueante por 5 segundos
                streams = self.r.xread({"swarm:infra:log": last_id}, count=10, block=5000)
                if streams:
                    for stream_name, messages in streams:
                        for message_id, event in messages:
                            last_id = message_id
                            
                            # Procesamos solo si es un fallo o reinicio
                            if event.get('old_state') != event.get('new_state'):
                                node = event.get('node', 'sentinel')
                                rift = self.container_event_to_rift(event)
                                
                                # Simulacion QHC (YATRA)
                                result = self.cascade.cascade_buffer(rift)
                                self.publish_prediction(node, result)
                                
            except redis.exceptions.ConnectionError:
                self.logger.error("Pierde conexion Redis. Reintentando...")
                time.sleep(5)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Falla de procesamiento de bloque log: {e}")
                time.sleep(2)

if __name__ == "__main__":
    adapter = InfraCascadeAdapter()
    adapter.run_daemon()
