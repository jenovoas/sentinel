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
import csv
import os
import sys
import glob
import threading
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any, List

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
    def __init__(self, log_dir="logs", port=8000):
        self.log_dir = log_dir
        self.port = port
        self.running = False
        
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

    def _get_latest_log_file(self):
        files = glob.glob(os.path.join(self.log_dir, "lattice_run_*.csv"))
        if not files: return None
        return max(files, key=os.path.getctime)

    def _parse_s60_repr(self, s60_str: str) -> float:
        """Parsea representación S60 string a float (Solo para métricas de display)."""
        # Formato: S60[int; d, m, s, t]
        try:
            # Extracción sucia pero efectiva para display
            clean = s60_str.replace("S60", "").strip("[]")
            parts = clean.split(";")
            integer = float(parts[0])
            fractionals = [float(x) for x in parts[1].split(",")]
            
            val = integer
            val += fractionals[0] / 60
            val += fractionals[1] / 3600
            val += fractionals[2] / 216000
            val += fractionals[3] / 12960000
            return val
        except:
            return 0.0

    async def _process_row(self, row: Dict[str, str]):
        """Procesa una fila del CSV"""
        tick = int(row['tick'])
        energy_str = row['energy_total']
        coherence_str = row['coherence']
        drift_str = row['drift']
        
        # 1. Update Metrics
        REGISTRY.set("sentinel_energy_total", self._parse_s60_repr(energy_str))
        REGISTRY.set("sentinel_coherence_ratio", self._parse_s60_repr(coherence_str))
        REGISTRY.set("sentinel_drift_seconds", self._parse_s60_repr(drift_str))
        REGISTRY.inc("sentinel_ticks_total")
        
        # 2. AIOps Shield Sanitization (Simulada sobre el contenido raw)
        # En producción, esto analizaría logs de texto libre. Aquí validamos estructura.
        log_payload = f"TICK:{tick} E:{energy_str} C:{coherence_str}"
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
        # Parseamos a S60 real para la lógica de control (Sovereign Logic)
        try:
             # Formato esperado: S60[int; d, m, s, t]
             # Usamos el parser de yatra_core si es posible, o reconstruimos
             # Para la lógica crítica, necesitamos precisión S60, no float.
             
             # Extraemos la parte entera y fraccional del string para reconstruir S60
             clean = coherence_str.replace("S60", "").strip("[]")
             parts = clean.split(";")
             integer_part = int(parts[0])
             frac_parts = [int(x) for x in parts[1].split(",")]
             
             coherence_s60 = S60(integer_part, frac_parts[0], frac_parts[1]) 
             # Nota: S60 constructor solo acepta 3 argumentos fraccionales principales en algunas versiones,
             # o si acepta más, los pasamos. Revisando yatra_core.py, __init__ toma (deg, min, sec).
             # Asumimos que los primeros 3 son suficientes para el umbral.
        except:
             # Fallback seguro: si falla el parseo estricto, asumimos estado seguro temporalmente o 0
             coherence_s60 = S60(0, 0, 0)

        # Umbral Soberano: 0.9 = 54/60 = S60(0, 54, 0)
        THRESHOLD_COHERENCE = S60(0, 54, 0)

        if coherence_s60 < THRESHOLD_COHERENCE:
            # Usamos float solo para display en el log
            print(f"⚖️ [TRUTHSYNC] Low Coherence ({coherence_str}). Validating...")
            
            # Call TruthSync Oracle
            is_valid = self.truthsync.verify_data("COHERENCE_CHECK", {
                "tick": tick,
                "coherence": coherence_str,
                "energy": energy_str
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
        print("👀 Watchdog Loop Started. Waiting for logs...")
        current_file = None
        f = None
        
        while self.running:
            latest = self._get_latest_log_file()
            
            if latest != current_file:
                if f: f.close()
                current_file = latest
                if current_file:
                    print(f"📂 Tracking new log file: {current_file}")
                    f = open(current_file, 'r')
                    # Skip header
                    f.readline()
                else:
                    await asyncio.sleep(1)
                    continue
            
            # Read new lines
            where = f.tell()
            line = f.readline()
            if not line:
                time.sleep(0.1)
                f.seek(where)
                await asyncio.sleep(0.1)
                continue
                
            # Parse line
            try:
                # Simple Manual CSV Parse to avoid csv.reader buffering issues on tail
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    # Remove quotes
                    cleaned = [p.strip('"') for p in parts]
                    row = {
                        "tick": cleaned[0],
                        "energy_total": cleaned[1],
                        "coherence": cleaned[2],
                        "drift": cleaned[3]
                    }
                    await self._process_row(row)
            except Exception as e:
                print(f"⚠️ Parse Error: {e}")
                
            await asyncio.sleep(0.01)

    def start(self):
        self.running = True
        
        # Start Prometheus Server
        server_thread = threading.Thread(target=self._run_server, daemon=True)
        server_thread.start()
        
        # Start Async Watchdog
        try:
            asyncio.run(self._watch_loop())
        except KeyboardInterrupt:
            self.stop()

    def _run_server(self):
        print(f"📡 Prometheus Metrics active at port {self.port}")
        httpd = HTTPServer(('localhost', self.port), MetricsHandler)
        httpd.serve_forever()

    def stop(self):
        self.running = False
        print("🛑 Telemetry Bridge Stopped")

if __name__ == "__main__":
    bridge = TelemetryBridge()
    bridge.start()
