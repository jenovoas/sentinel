# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

try:
    import me60os_core
except (ImportError, Exception):
    me60os_core = None


@pytest.mark.skipif(me60os_core is None, reason="me60os_core native module not available or incompatible ABI")
def test_soma_migration():
    print("=== Testing QuantumBuffer SOMA ===")
    buf = me60os_core.QuantumBuffer(20)
    print("Buffer is overflowing:", buf.is_overflow)
    buf.push("event1")
    buf.push("event2")
    print("Buffer size:", buf.size)
    print("Buffer efficiency:", buf.efficiency)

    print("\n=== Testing phi SOMA ===")
    t_raw = int(round(17.0 * 12_960_000))
    s60_t = me60os_core.SPA._from_raw(t_raw)
    phi17 = me60os_core.QuantumSchedulerCore.static_phi(s60_t).to_raw() / 12_960_000.0
    print("phi(17.0) =", phi17)

    t_raw = int(round(8.5 * 12_960_000))
    s60_t = me60os_core.SPA._from_raw(t_raw)
    phi85 = me60os_core.QuantumSchedulerCore.static_phi(s60_t).to_raw() / 12_960_000.0
    print("phi(8.5) =", phi85)

    print("\n=== Testing AnomalyDetector SOMA ===")
    detector = me60os_core.AnomalyDetectorCore(10, 3.0)

    # Send some normal metrics
    for i in range(10):
        detector.analyze_metrics(
            50.0, 50.0, 1000.0, 30.0, 10, 0, 1000.0, 4000.0
        )
    print("Detector finished learning?", not detector.is_learning)

    # Send an anomaly
    raw_anomalies = detector.analyze_metrics(
        95.0, 95.0, 5000000.0, 99.0, 80, 10, 3800.0, 4000.0
    )

    print(f"Detected {len(raw_anomalies)} anomalies!")
    for a in raw_anomalies:
        print(f"- {a['anomaly_type']} (Severity {a['severity']}): {a['title']}")
