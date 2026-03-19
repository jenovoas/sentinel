#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# ------------------------------------------------------------
# SENTINEL TELEMETRY BRIDGE (WATCHDOG)
# ------------------------------------------------------------
# Puente observacional desacoplado para el Quantum Lattice Engine.
# 
# Integraciones:
# 1. Prometheus: Exposición de métricas (Custom HTTP Server)
# 2. AIOps Shield: Sanitización de logs en tiempo real
# 3. Forensic WAL: Registro inmutable de eventos críticos
# 4. TruthSync: Validación de anomalías con el Oráculo
# ------------------------------------------------------------

import time
import json
import csv
import os
import sys
import glob
import threading
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any, List

try:
    import redis
    import redis.asyncio as aioredis
except ImportError:
    redis = None
    aioredis = None


# Core Integrations
from quantum.yatra_core import S60
from backend.app.services.aiops_shield import AIOpsShield, ThreatLevel
from backend.app.core.forensic_wal import ForensicWAL
from quantum.truthsync_verification import TruthSyncClient

# --- 1. Custom Prometheus Exporter (No external deps) ---
class PrometheusRegistry:
    def __init__(self):
        self._metrics = {}
    
    def gauge(self, name, help_text, value=0.0):
        self._metrics[name] = {"type": "gauge", "help": help_text, "value": value}
    
    def counter(self, name, help_text, value=0.0):
        if name not in self._metrics:
            self._metrics[name] = {"type": "counter", "help": help_text, "value": 0.0}
        self._metrics[name]["value"] += value
        
    def set(self, name, value):
        if name in self._metrics:
            self._metrics[name]["value"] = value

    def inc(self, name, amount=1.0):
        if name in self._metrics:
            self._metrics[name]["value"] += amount

    def generate_output(self):
        lines = []
        for name, data in self._metrics.items():
            lines.append(f"# HELP {name} {data['help']}")
            lines.append(f"# TYPE {name} {data['type']}")
            lines.append(f"{name} {data['value']}")
        return "\n".join(lines).encode('utf-8')

# Global Registry
REGISTRY = PrometheusRegistry()

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; version=0.0.4')
            self.end_headers()
            self.wfile.write(REGISTRY.generate_output())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return # Silent logging to avoid console spam

# --- 2. Log Watcher & Processor ---
class TelemetryBridge:
    def __init__(self, port=8000):
        self.port = port
        self.running = False
        
        # Redis Pub/Sub (Async)
        self.redis_client = None
        self.pubsub = None
        if aioredis:
            self.redis_client = aioredis.from_url(f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}")

        # Integrations
        self.shield = AIOpsShield()
        self.truthsync = TruthSyncClient()
        self.wal = ForensicWAL(base_path=Path(log_dir) / "wal_storage")
        
        # Init Metrics
        self._init_metrics()
        
    def _init_metrics(self):
        REGISTRY.gauge("sentinel_coherence_ratio", "Resonance coherence (0-1)")
        REGISTRY.gauge("sentinel_energy_total", "Total system energy")
        REGISTRY.gauge("sentinel_drift_seconds", "Temporal drift from Time Crystal")
        REGISTRY.counter("sentinel_ticks_total", "Total simulation ticks processed")
        REGISTRY.counter("sentinel_threats_detected", "Threats blocked by AIOpsShield")
        REGISTRY.counter("sentinel_truthsync_alerts", "Anomalies reported to TruthSync")

    async def _process_row(self, row: Dict[str, str]):
        """Procesa una fila del CSV"""
        tick = int(row['tick'])
        
        # Reconstrucción Pura desde valor raw
        energy_s60 = S60._from_raw(int(row['energy_total_raw']))
        coherence_s60 = S60._from_raw(int(row['coherence_raw']))
        drift_s60 = S60._from_raw(int(row['drift_raw']))
        
        # 1. Update Metrics
        # La conversión a float se hace en el último momento, solo para Prometheus.
        REGISTRY.set("sentinel_energy_total", energy_s60.to_float())
        REGISTRY.set("sentinel_coherence_ratio", coherence_s60.to_float())
        REGISTRY.set("sentinel_drift_seconds", drift_s60.to_float())
        REGISTRY.inc("sentinel_ticks_total")
        
        # 2. AIOps Shield Sanitization (Simulada sobre el contenido raw)
        # En producción, esto analizaría logs de texto libre. Aquí validamos estructura.
        log_payload = f"TICK:{tick} E_RAW:{energy_s60.to_raw()} C_RAW:{coherence_s60.to_raw()}"
        sanitization = self.shield.sanitize(log_payload)
        
        if sanitization.threat_level != ThreatLevel.SAFE:
            print(f"🛡️ [SHIELD] Threat Blocked: {sanitization.patterns_detected}")
            REGISTRY.inc("sentinel_threats_detected")
            
            # 3. Forensic WAL (Loguear ataque)
            await self.wal.write({
                "type": "THREAT_DETECTED",
                "tick": tick,
                "ThreatLevel": sanitization.threat_level.value,
                "payload": log_payload
            })
            return

        # 4. TruthSync Validation (Si coherencia baja peligrosamente)
        # Umbral Soberano: 0.9 = 54/60 = S60(0, 54, 0)
        THRESHOLD_COHERENCE = S60(0, 54, 0)

        if coherence_s60 < THRESHOLD_COHERENCE:
            # Usamos float solo para display en el log
            print(f"⚖️ [TRUTHSYNC] Low Coherence ({coherence_s60}). Validating...")
            
            # Call TruthSync Oracle
            is_valid = self.truthsync.verify_data("COHERENCE_CHECK", {
                "tick": tick,
                "coherence_raw": coherence_s60.to_raw(),
                "energy_raw": energy_s60.to_raw()
            })
            
            if not is_valid:
                 REGISTRY.inc("sentinel_truthsync_alerts")
                 # Log crítico inmutable
                 await self.wal.write({
                    "type": "TRUTHSYNC_REJECTION",
                    "tick": tick,
                    "reason": "Coherence anomaly rejected by Oracle"
                 })

    async def _watch_loop(self):
        if not self.redis_client or not self.pubsub:
            print("❌ Telemetry Bridge: Redis no disponible. El Watchdog no puede iniciar.")
            return

        print("👀 Watchdog Loop Started. Escuchando en 'sentinel:telemetry:stream'...")
        
        while self.running:
            try:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message['data']:
                    # Decodificar el payload JSON del mensaje de Redis
                    row = json.loads(message['data'])
                    await self._process_row(row)
            except Exception as e:
                if not isinstance(e, asyncio.TimeoutError):
                     print(f"⚠️ Watchdog Error: {e}")

    def start(self):
        self.running = True
        
        # Start Prometheus Server
        server_thread = threading.Thread(target=self._run_server, daemon=True)
        server_thread.start()
        
        # Start Async Watchdog
        asyncio.run(self.main_async_loop())

    def _run_server(self):
        print(f"📡 Prometheus Metrics active at port {self.port}")
        httpd = HTTPServer(('localhost', self.port), MetricsHandler)
        while self.running:
            httpd.handle_request()

    async def main_async_loop(self):
        if self.redis_client:
            async with self.redis_client.pubsub() as pubsub:
                self.pubsub = pubsub
                await self.pubsub.subscribe("sentinel:telemetry:stream")
                await self._watch_loop()
        

    def stop(self):
        self.running = False
        if self.pubsub:
            self.pubsub.unsubscribe()
        print("🛑 Telemetry Bridge Stopped")

if __name__ == "__main__":
    bridge = TelemetryBridge()
    bridge.start()
