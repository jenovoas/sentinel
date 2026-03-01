#!/usr/bin/env python3

# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

# bring_ebpf_to_matrix.py — Puente Resonante Dual (eBPF → Lattice Cuántica)
"""
BRING eBPF TO MATRIX — Pilar 0: El Umbral
==========================================
Transporta eventos del kernel (Guardian-Alpha LSM / Ring 0) al interior
de la Lattice Cuántica (AIBufferCascade / ResonantMatrix).

Conecta DOS memorias: el anillo del kernel y la memoria no-Markoviana.
También puede conectar DOS planetas: el bus local y un bus remoto via Redis.

Arquitectura:
    Guardian-Alpha LSM (Ring 0)
        │  watchdog_events.log  │  /sys/fs/bpf/cortex_events
        ▼                       ▼
    LogWatcher             RingReader           ← fuentes intercambiables
        │                       │
        └───────────┬───────────┘
                    ▼
            CortexEventS60        ← convierte RawCortexEvent a S60
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
    Lattice LOCAL       Lattice REMOTA         ← dos planetas
    (AIBufferCascade)   (Redis PUBLISH)
          │                   │
          └─────────┬─────────┘
                    ▼
          swarm:infra:log (XADD)              ← bitácora S60

Autor: Jaime Novoa (Ea-nasir) + Gemini (reconstrucción YATRA R1)
YATRA: Cero floats. Cero random. Cero numpy. Solo S60.
"""

import os
import sys
import time
import json
import redis
from typing import Optional, Dict, Any

from quantum.yatra_core import S60, PI_S60
from quantum.yatra_math import S60Math

# ─────────────────────────────────────────── CONSTANTES YATRA ─────
# Umbral de disonancia ALTA: equivale a lo que era 0.85
# 51/60 en escala S60 cruda (= 51 grados de disonancia)
DISONANCIA_ALTA       = S60(51, 0, 0)   # antes: 0.85
DISONANCIA_BAJA       = S60(9, 0, 0)    # antes: 0.15

# Frecuencia axiónica del sistema (153°24' en S60)
FREQ_AXIONICA         = S60(153, 24, 0)

# Heartbeat resonante: 17 segundos (pulso humano base-60)
TICK_17S              = S60(17, 0, 0)

# Umbral de coherencia soberana (42°30' = base de estabilidad)
COHERENCIA_SOBERANA   = S60(42, 30, 0)

# Tipos de evento (deben coincidir con cortex_events.h)
EVENT_FILE_BLOCKED    = 1
EVENT_EXEC_BLOCKED    = 2
EVENT_FILE_ALLOWED    = 3
EVENT_EXEC_ALLOWED    = 4
EVENT_NETWORK_BURST   = 5
EVENT_NETWORK_NORMAL  = 6

# Neuromapa hexagonal S60 (neuronas en la lattice)
NEURON_MAP = {
    EVENT_FILE_BLOCKED:   S60(0, 0, 0),    # Neurona 0: amenaza de archivo
    EVENT_EXEC_BLOCKED:   S60(64, 0, 0),   # Neurona 64: amenaza de ejecución
    EVENT_FILE_ALLOWED:   S60(128, 0, 0),  # Neurona 128: operación normal archivo
    EVENT_EXEC_ALLOWED:   S60(192, 0, 0),  # Neurona 192: ejecución normal
    EVENT_NETWORK_BURST:  S60(256, 0, 0),  # Neurona 256: anomalía de red
    EVENT_NETWORK_NORMAL: S60(320, 0, 0),  # Neurona 320: red normal
}

# ─────────────────────────────────────────── CONFIGURACIÓN ────────
REDIS_HOST   = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT   = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_REMOTE = os.environ.get("REDIS_REMOTE", None)   # IP del segundo planeta

LOG_FILE      = os.environ.get("EBPF_LOG", "/home/jnovoas/Dev/sentinel/ebpf/watchdog_events.log")
RINGBUF_PATH  = "/sys/fs/bpf/ai_guardian_maps/cortex_events"

STREAM_KEY   = "swarm:infra:log"
CHANNEL_LOCAL  = "quantum_signals"
CHANNEL_REMOTE = "quantum_signals"


# ─────────────────────────────────────────── STRUCT S60 CORTEX ────

class CortexEventS60:
    """
    Representación S60-pura de un CortexEvent del kernel.
    Sin floats. Sin strings para cálculo core.
    """
    __slots__ = (
        "timestamp_s60",   # S60: segundos del sistema en base-60
        "event_type",      # int: tipo de evento (1-6)
        "pid",             # int: PID del proceso
        "entropy_s60",     # S60: señal de entropía normalizada a base-60
        "severity",        # int: 0=LOW, 1=MED, 2=HIGH, 3=CRITICAL
        "neuron_s60",      # S60: coordenada de neurona en la lattice
        "disonancia_s60",  # S60: valor de disonancia (ex-float)
    )

    def __init__(
        self,
        timestamp_ns: int,
        event_type: int,
        pid: int,
        entropy_raw: int,
        severity: int,
    ):
        # Convertir nanosegundos a S60 (segundos enteros, sin división flotante)
        # timestamp_ns // 1_000_000_000 = segundos enteros
        ts_sec = timestamp_ns // 1_000_000_000
        self.timestamp_s60 = S60(ts_sec % 60, (ts_sec // 60) % 60, (ts_sec // 3600) % 60)

        self.event_type = event_type
        self.pid = pid

        # entropy_raw es un entero u64 del kernel (campo SPA raw value)
        # Normalizar a S60: tomar los 6 bits superiores como grados S60
        # Escalamos: entropy_raw // S60.SCALE => grados S60
        # S60.SCALE = 12_960_000 (60^4)
        S60_SCALE = 12_960_000
        entropy_degrees = (entropy_raw // S60_SCALE) % 60
        entropy_minutes = (entropy_raw % S60_SCALE) // (S60_SCALE // 60)
        self.entropy_s60 = S60(entropy_degrees, entropy_minutes % 60, 0)

        self.severity = severity

        # Neurona hexagonal en la lattice
        self.neuron_s60 = NEURON_MAP.get(event_type, S60(0, 0, 0))

        # Disonancia: eventos bloqueados o burst = ALTA, resto = BAJA
        # YATRA: sin condicional float — todo S60
        if event_type in (EVENT_FILE_BLOCKED, EVENT_EXEC_BLOCKED, EVENT_NETWORK_BURST):
            self.disonancia_s60 = DISONANCIA_ALTA
        else:
            self.disonancia_s60 = DISONANCIA_BAJA

    def to_axion(self) -> Dict[str, Any]:
        """
        Serializa el evento como un axión (señal cuántica) para el bus Redis.
        Usa strings S60 para serialización — el cálculo core ya fue completado.
        """
        return {
            "source":     "ebpf_guardian",
            "disonancia": str(self.disonancia_s60),
            "axiones":    str(S60(60, 0, 0) - self.disonancia_s60),
            "frequency":  str(FREQ_AXIONICA),
            "neuron":     str(self.neuron_s60),
            "entropy":    str(self.entropy_s60),
            "event_type": self.event_type,
            "pid":        self.pid,
            "severity":   self.severity,
            "timestamp":  str(self.timestamp_s60),
        }

    def to_rift_coords(self) -> tuple:
        """
        Proyecta el evento a coordenadas de rift hexagonal
        para AIBufferCascade.cascade_buffer().
        Coordenadas: (neurona_index, severidad_s60)
        """
        neuron_idx = int(str(self.neuron_s60).split("°")[0])
        return (neuron_idx, self.severity * int(str(DISONANCIA_ALTA).split("°")[0]))

    def to_infra_log_entry(self) -> Dict[str, str]:
        """
        Formato para XADD al stream swarm:infra:log.
        Todos los campos como strings para Redis Stream.
        """
        event_labels = {
            EVENT_FILE_BLOCKED: "FILE_BLOCKED",
            EVENT_EXEC_BLOCKED: "EXEC_BLOCKED",
            EVENT_FILE_ALLOWED: "FILE_ALLOWED",
            EVENT_EXEC_ALLOWED: "EXEC_ALLOWED",
            EVENT_NETWORK_BURST: "NETWORK_BURST",
            EVENT_NETWORK_NORMAL: "NETWORK_NORMAL",
        }
        return {
            "node":       "sentinel",
            "agent":      "bring_ebpf_to_matrix",
            "event_type": event_labels.get(self.event_type, "UNKNOWN"),
            "pid":        str(self.pid),
            "severity":   str(self.severity),
            "disonancia": str(self.disonancia_s60),
            "entropy":    str(self.entropy_s60),
            "neuron":     str(self.neuron_s60),
            "timestamp":  str(self.timestamp_s60),
        }


# ─────────────────────────────────────────── FUENTES DE EVENTOS ───

def follow_log(filepath: str):
    """
    Sigue un archivo de log línea por línea (tail -f S60-puro).
    Espera TICK_17S / 3 si no hay líneas nuevas (ciclo ~5.6s).
    """
    with open(filepath, "a"):   # crear si no existe
        pass

    with open(filepath, "r") as f:
        f.seek(0, 2)   # ir al final del archivo
        while True:
            line = f.readline()
            if not line:
                # Espera proporcional al tick-17 (sin float)
                time.sleep(int(str(TICK_17S).split("°")[0]) // 3 or 1)
                continue
            yield ("log", line.strip())


def parse_log_line(raw: str) -> Optional[CortexEventS60]:
    """
    Convierte una línea de watchdog_events.log en un CortexEventS60.
    Formato esperado: JSON con campos timestamp_ns, event_type, pid, entropy, severity.
    Si la línea no es JSON parseable, infiere el tipo por palabras clave.
    """
    try:
        data = json.loads(raw)
        return CortexEventS60(
            timestamp_ns = int(data.get("timestamp_ns", int(time.time()) * 1_000_000_000)),
            event_type   = int(data.get("event_type", EVENT_FILE_ALLOWED)),
            pid          = int(data.get("pid", 0)),
            entropy_raw  = int(data.get("entropy", 0)),
            severity     = int(data.get("severity", 0)),
        )
    except (json.JSONDecodeError, ValueError):
        # Inferencia por palabras clave (sin floats)
        lower = raw.lower()
        if any(w in lower for w in ("blocked", "alert", "error", "denied")):
            etype    = EVENT_EXEC_BLOCKED
            severity = 2
        elif "network" in lower and "burst" in lower:
            etype    = EVENT_NETWORK_BURST
            severity = 1
        else:
            etype    = EVENT_FILE_ALLOWED
            severity = 0

        return CortexEventS60(
            timestamp_ns = int(time.time()) * 1_000_000_000,
            event_type   = etype,
            pid          = 0,
            entropy_raw  = 0,
            severity     = severity,
        )


# ─────────────────────────────────────────── NÚCLEO DEL BRIDGE ────

class BringEbpfToMatrix:
    """
    Puente Resonante Dual.
    Conecta el ring-0 del kernel con dos instancias de la Lattice Cuántica:
      - LOCAL:  AIBufferCascade (proceso local, via Redis PUBLISH)
      - REMOTA: segundo nodo del enjambre (via Redis remoto PUBLISH)

    También escribe la bitácora en swarm:infra:log (XADD, inmutable).
    """

    def __init__(
        self,
        cascade=None,          # AIBufferCascade opcional (lattice local)
        redis_local=None,
        redis_remote=None,
    ):
        self.cascade = cascade

        # Bus local
        self.r_local = redis_local or self._connect_redis(REDIS_HOST, REDIS_PORT)

        # Bus remoto (segundo planeta) — opcional
        self.r_remote = redis_remote
        if REDIS_REMOTE and not redis_remote:
            try:
                self.r_remote = self._connect_redis(REDIS_REMOTE, REDIS_PORT)
                print(f"🌐 Segundo planeta conectado: {REDIS_REMOTE}")
            except Exception as e:
                print(f"⚠️ Sin conexión al segundo planeta: {e}")

        print("🛰️ Puente Resonante Dual activo")
        print(f"   Bus local:  {REDIS_HOST}:{REDIS_PORT}")
        print(f"   Bus remoto: {REDIS_REMOTE or 'no configurado'}")

    def _connect_redis(self, host: str, port: int) -> redis.Redis:
        r = redis.Redis(host=host, port=port, decode_responses=True)
        r.ping()
        return r

    def _publish_axion(self, event: CortexEventS60):
        """
        Publica el axión en los dos buses (local y remoto).
        Escribre en la bitácora S60.
        """
        axion = event.to_axion()
        payload = json.dumps(axion)

        # Bus local: canal quantum_signals
        self.r_local.publish(CHANNEL_LOCAL, payload)

        # Bitácora inmutable: swarm:infra:log (XADD)
        self.r_local.xadd(STREAM_KEY, event.to_infra_log_entry())

        # Bus remoto: segundo planeta
        if self.r_remote:
            try:
                self.r_remote.publish(CHANNEL_REMOTE, payload)
            except Exception as e:
                print(f"⚠️ Error enviando al segundo planeta: {e}")

        print(
            f"📡 Axión transmitido → neurona={axion['neuron']} "
            f"disonancia={axion['disonancia']} freq={axion['frequency']}"
        )

    def _feed_cascade(self, event: CortexEventS60):
        """
        Alimenta la AIBufferCascade local con el evento como rift.
        Solo si hay una instancia de cascade configurada.
        """
        if not self.cascade:
            return

        rift_coords = event.to_rift_coords()
        result = self.cascade.cascade_buffer(rift_coords)

        # Publicar predicción en Redis
        self.r_local.hset(
            f"swarm:infra:predictions:sentinel",
            mapping={
                "future_coherence":  str(result.get("future_coherence_target", COHERENCIA_SOBERANA)),
                "vimana_ready":      str(result.get("vimana_ready", False)),
                "memory_strength":   str(result.get("memory_strength", S60(0, 0, 0))),
                "current_coherence": str(result.get("current_coherence", COHERENCIA_SOBERANA)),
                "last_event_type":   str(event.event_type),
                "last_severity":     str(event.severity),
            }
        )

    def run_from_log(self, filepath: str = LOG_FILE):
        """
        Modo LOG: sigue watchdog_events.log y procesa cada línea.
        Funciona sin acceso a /sys/fs/bpf.
        """
        print(f"📜 Modo LOG activo: {filepath}")
        for _, raw in follow_log(filepath):
            if not raw:
                continue
            event = parse_log_line(raw)
            if event:
                self._publish_axion(event)
                self._feed_cascade(event)

    def run_from_redis_stream(self, stream: str = STREAM_KEY):
        """
        Modo STREAM: consume eventos ya almacenados en swarm:infra:log.
        Útil para re-procesar historia (Salto-17: backflow de información).
        Solo S60 en el cálculo; strings solo para Redis.
        """
        print(f"🔁 Modo STREAM activo (backflow): {stream}")
        last_id = "0"
        while True:
            entries = self.r_local.xread({stream: last_id}, count=10, block=1000)
            if not entries:
                continue
            for _, messages in entries:
                for msg_id, fields in messages:
                    last_id = msg_id
                    # Reconstruir CortexEventS60 desde el stream
                    try:
                        event = CortexEventS60(
                            timestamp_ns = int(time.time()) * 1_000_000_000,
                            event_type   = int(fields.get("event_type_raw", EVENT_FILE_ALLOWED)),
                            pid          = 0,
                            entropy_raw  = 0,
                            severity     = int(fields.get("severity", 0)),
                        )
                        self._feed_cascade(event)
                    except Exception as e:
                        print(f"⚠️ Error reprocessando evento: {e}")


# ─────────────────────────────────────────── ENTRY POINT ──────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Puente Resonante eBPF → Lattice Cuántica")
    parser.add_argument(
        "--mode",
        choices=["log", "stream"],
        default="log",
        help="Fuente de eventos: 'log' (watchdog) o 'stream' (Redis backflow)",
    )
    parser.add_argument("--log-file", default=LOG_FILE)
    parser.add_argument("--cascade", action="store_true", help="Activar AIBufferCascade local")
    args = parser.parse_args()

    cascade_instance = None
    if args.cascade:
        try:
            sys.path.append(os.path.dirname(__file__))
            from hexagonal_control import HexagonalController
            from ai_buffer_cascade import AIBufferCascade

            hx = HexagonalController(size=7)
            cascade_instance = AIBufferCascade(hx)
            print("✅ AIBufferCascade lattice activada")
        except ImportError as e:
            print(f"⚠️ AIBufferCascade no disponible: {e} — solo bus Redis")

    bridge = BringEbpfToMatrix(cascade=cascade_instance)

    try:
        if args.mode == "log":
            bridge.run_from_log(args.log_file)
        else:
            bridge.run_from_redis_stream()
    except KeyboardInterrupt:
        print("\n🔴 Puente detenido. Coherencia preservada.")
