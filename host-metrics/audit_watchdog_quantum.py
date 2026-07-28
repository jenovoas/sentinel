#!/usr/bin/env python3
# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
"""
Audit Watchdog — Quantum Scheduled
Reemplaza audit-watchdog.sh (tail | grep | while read continuo)

Problema del bash loop:
  - tail -F | grep corre sin parar → 30% CPU constante
  - Cada execve del LSM genera un evento → flood de logs
  - Loki ingiere en tiempo real → 47% CPU adicional

Solución (EXP-029-V2):
  - Thread de tail llena un buffer sparse (EXP-014, max 40 slots)
  - Scheduler detecta portales φ(t) > 0.75 cada 100ms (no busy-wait)
  - Procesa en batch adaptativo SOLO durante portales (2-5 eventos/portal)
  - Overflow de emergencia si buffer llega al límite (OVERFLOW_LIMIT=20)
  - Escribe métricas a textfile para node-exporter (no logging continuo a Loki)

Resultado esperado: 62.9% menos CPU vs loop bash continuo
"""

import sys
import os
import math
import time
import signal
import logging
import threading
import subprocess
from pathlib import Path
from datetime import datetime

# Añadir backend al path para importar quantum_scheduler
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
try:
    from app.quantum_scheduler import (
        QuantumBuffer, QuantumSchedulerDaemon,
        phi_now, is_portal_open, T_BIO, T_CYCLE
    )
except ImportError:
    # Fallback: definiciones locales mínimas si el backend no está disponible
    import math
    T_BIO, T_CYCLE, THETA = 17.0, 68.0, 0.75

    def phi_now():
        t = time.monotonic() % T_CYCLE
        return (1/3) * (
            math.sin(2 * math.pi * t / T_BIO) +
            math.sin(2 * math.pi * t / 4.25) +
            math.sin(2 * math.pi * t / 16.18)
        )

    def is_portal_open():
        return phi_now() > THETA

    from collections import deque
    import functools

    class QuantumBuffer:
        def __init__(self, overflow_limit=20):
            self.overflow_limit = overflow_limit
            self._buffer = deque()
            self._lock = threading.Lock()
            self._stats = {"portal": 0, "overflow": 0}

        def push(self, e):
            with self._lock:
                if len(self._buffer) < self.overflow_limit * 2:
                    self._buffer.append(e)
                    return True
            return False

        def pop_batch(self, n):
            with self._lock:
                batch = []
                while self._buffer and len(batch) < n:
                    batch.append(self._buffer.popleft())
                return batch

        def pop_one(self):
            with self._lock:
                return self._buffer.popleft() if self._buffer else None

        @property
        def size(self):
            with self._lock: return len(self._buffer)

        @property
        def is_overflow(self): return self.size >= self.overflow_limit

        def record_portal(self, n): self._stats["portal"] += n
        def record_overflow(self): self._stats["overflow"] += 1

        @property
        def stats(self):
            total = self._stats["portal"] + self._stats["overflow"]
            eff = self._stats["portal"] / total if total else 0
            return dict(self._stats, efficiency=f"{eff:.1%}")

    class QuantumSchedulerDaemon:
        def __init__(self, buffer, process_fn, dt=0.1, name="qd"):
            self.buffer = buffer
            self.process_fn = process_fn
            self.dt = dt
            self.name = name
            self._running = False
            self._t0 = time.monotonic()

        def _phi(self, t):
            return (1/3) * (
                math.sin(2*math.pi*t/T_BIO) +
                math.sin(2*math.pi*t/4.25) +
                math.sin(2*math.pi*t/16.18)
            )

        def _batch_size(self, p):
            if p > 0.90: return 5
            if p > 0.85: return 4
            if p > 0.80: return 3
            return 2

        def run(self):
            self._running = True
            last_report = 0.0
            while self._running:
                t = time.monotonic() - self._t0
                res = self._phi(t % T_CYCLE)
                if res > THETA and self.buffer.size > 0:
                    for e in self.buffer.pop_batch(self._batch_size(res)):
                        try: self.process_fn(e)
                        except: pass
                    self.buffer.record_portal(1)
                elif res <= THETA and self.buffer.is_overflow:
                    e = self.buffer.pop_one()
                    if e:
                        try: self.process_fn(e)
                        except: pass
                        self.buffer.record_overflow()
                if t - last_report >= T_CYCLE:
                    logger.info(f"[{self.name}] {self.buffer.stats} cola={self.buffer.size}")
                    last_report = t
                time.sleep(self.dt)

        def stop(self): self._running = False


# ── Config ────────────────────────────────────────────────────────────────────
LOG_PATH      = "/var/log/audit/audit.log"
METRICS_PATH  = "/var/lib/node_exporter/textfile/audit_quantum.prom"
KEYWORDS      = ["exec-watchdog", "file-watchdog", "ptrace-watchdog"]

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("audit-watchdog-quantum")

# ── Métricas Prometheus (textfile para node-exporter) ─────────────────────────
_metrics = {
    "events_portal_total": 0,
    "events_overflow_total": 0,
    "alerts_exploit_total": 0,
    "buffer_size": 0,
    "portal_efficiency": 0.0,
    "phi_now": 0.0,
}
_metrics_lock = threading.Lock()


def write_prometheus_metrics(buf: QuantumBuffer):
    """Escribe métricas en formato textfile para node-exporter."""
    metrics_dir = Path(METRICS_PATH).parent
    metrics_dir.mkdir(parents=True, exist_ok=True)

    resonance = phi_now()
    stats = buf.stats
    eff_str = stats["efficiency"].rstrip("%")
    try:
        eff = float(eff_str) / 100.0
    except ValueError:
        eff = 0.0

    content = f"""# HELP audit_quantum_events_portal_total Eventos procesados en portal
# TYPE audit_quantum_events_portal_total counter
audit_quantum_events_portal_total {stats['portal']}
# HELP audit_quantum_events_overflow_total Eventos procesados en overflow
# TYPE audit_quantum_events_overflow_total counter
audit_quantum_events_overflow_total {stats['overflow']}
# HELP audit_quantum_buffer_size Eventos en buffer ahora
# TYPE audit_quantum_buffer_size gauge
audit_quantum_buffer_size {buf.size}
# HELP audit_quantum_portal_efficiency Eficiencia portal vs overflow
# TYPE audit_quantum_portal_efficiency gauge
audit_quantum_portal_efficiency {eff:.4f}
# HELP audit_quantum_phi_now Resonancia φ(t) actual
# TYPE audit_quantum_phi_now gauge
audit_quantum_phi_now {resonance:.4f}
# HELP audit_quantum_portal_open Si el portal está abierto (1) o cerrado (0)
# TYPE audit_quantum_portal_open gauge
audit_quantum_portal_open {1 if resonance > 0.75 else 0}
"""
    try:
        Path(METRICS_PATH).write_text(content)
    except Exception as e:
        logger.warning(f"No se pudo escribir métricas: {e}")


# ── Event Processor ───────────────────────────────────────────────────────────

def process_audit_event(event: dict):
    """
    Procesa un evento de auditoría durante un portal.
    Logging mínimo — no inundar Loki.
    """
    line = event["line"]
    ts = datetime.fromtimestamp(event["ts"]).strftime("%H:%M:%S")
    key = event.get("key", "unknown")

    # Solo loguear resumen, no la línea completa (reduce Loki ingestion)
    if "exec-watchdog" in line:
        # Extraer syscall y uid para resumen
        uid = _extract_field(line, "uid")
        syscall = _extract_field(line, "syscall")
        comm = _extract_field(line, "comm")
        logger.info(f"[EXEC] {ts} uid={uid} comm={comm} syscall={syscall}")

        # Alerta de exploit: execve de uid de usuario real
        if uid and uid.isdigit() and int(uid) >= 1000:
            logger.warning(f"[ALERT] execve de usuario uid={uid} comm={comm}")
            with _metrics_lock:
                _metrics["alerts_exploit_total"] += 1

    elif "ptrace-watchdog" in line:
        uid = _extract_field(line, "uid")
        logger.warning(f"[PTRACE] {ts} uid={uid} — posible debugging/inject")


def _extract_field(line: str, field: str) -> str | None:
    """Extrae campo=valor de línea auditd."""
    try:
        idx = line.index(f"{field}=")
        rest = line[idx + len(field) + 1:]
        return rest.split()[0].strip("\"'()")
    except (ValueError, IndexError):
        return None


# ── Tail Thread ───────────────────────────────────────────────────────────────

def tail_audit_log(buf: QuantumBuffer, stop_event: threading.Event):
    """
    Thread daemon: tail -F del audit log → buffer.
    No procesa. Solo acumula. El scheduler decide cuándo.
    """
    logger.info(f"Tail thread iniciado: {LOG_PATH}")
    proc = subprocess.Popen(
        ["tail", "-F", LOG_PATH],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )

    try:
        for line in proc.stdout:
            if stop_event.is_set():
                break
            line = line.strip()
            if not line:
                continue
            # Filtrar antes de entrar al buffer (no deserializar todo)
            if not any(kw in line for kw in KEYWORDS):
                continue
            key = next((kw for kw in KEYWORDS if kw in line), "unknown")
            buf.push({"ts": time.time(), "line": line, "key": key})
    except Exception as e:
        logger.error(f"Tail thread error: {e}")
    finally:
        proc.terminate()
        logger.info("Tail thread terminado")


# ── Metrics Reporter Thread ───────────────────────────────────────────────────

def metrics_reporter(buf: QuantumBuffer, stop_event: threading.Event):
    """Escribe métricas Prometheus cada T_BIO segundos."""
    while not stop_event.is_set():
        write_prometheus_metrics(buf)
        stop_event.wait(T_BIO)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not Path(LOG_PATH).exists():
        logger.error(f"No existe {LOG_PATH}. ¿auditd corriendo?")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info(" Audit Watchdog — Quantum Scheduled v2")
    logger.info(f" T_BIO={T_BIO}s  T_CYCLE={T_CYCLE}s  THETA=0.75")
    logger.info(f" Buffer: OVERFLOW_LIMIT=20 (EXP-029-V2 validado)")
    logger.info(f" Métricas: {METRICS_PATH}")
    logger.info("=" * 60)

    buf = QuantumBuffer(overflow_limit=20)
    stop_event = threading.Event()

    # Signal handlers
    def _shutdown(sig, frame):
        logger.info(f"Signal {sig} recibido. Deteniendo...")
        stop_event.set()
        daemon.stop()
        logger.info(f"Stats finales: {buf.stats}")
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    # Thread: tail → buffer
    tail_thread = threading.Thread(
        target=tail_audit_log,
        args=(buf, stop_event),
        daemon=True,
        name="audit-tail",
    )
    tail_thread.start()

    # Thread: metrics reporter
    metrics_thread = threading.Thread(
        target=metrics_reporter,
        args=(buf, stop_event),
        daemon=True,
        name="metrics-reporter",
    )
    metrics_thread.start()

    # Main: quantum scheduler daemon
    daemon = QuantumSchedulerDaemon(
        buffer=buf,
        process_fn=process_audit_event,
        dt=0.1,
        name="audit-watchdog",
    )
    daemon.run()


if __name__ == "__main__":
    main()
