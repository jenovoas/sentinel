# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
import sys
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
    assert buf.efficiency.to_raw() == 0
    buf.record_portal(3)
    assert buf.efficiency.to_raw() == 12_960_000
    buf.record_overflow()
    assert buf.efficiency.to_raw() == 9_720_000

    print("\n=== Testing phi SOMA ===")
    phi17 = me60os_core.QuantumSchedulerCore.static_phi(
        me60os_core.SPA._from_raw(17 * 12_960_000)
    ).to_raw()
    phi85 = me60os_core.QuantumSchedulerCore.static_phi(
        me60os_core.SPA._from_raw(8 * 12_960_000 + 6_480_000)
    ).to_raw()
    assert isinstance(phi17, int)
    assert isinstance(phi85, int)
    phase = me60os_core.SPA._from_raw(17 * 12_960_000)
    assert isinstance(me60os_core.QuantumSchedulerCore.is_portal_open(phase), bool)
    cycle_later = me60os_core.SPA._from_raw(phase.to_raw() + 68 * 12_960_000)
    assert me60os_core.QuantumSchedulerCore.is_portal_open(phase) == me60os_core.QuantumSchedulerCore.is_portal_open(cycle_later)

    print("\n=== Testing AnomalyDetector SOMA ===")
    scale = 12_960_000
    detector = me60os_core.AnomalyDetectorCore(20, 3 * scale)
    for _ in range(20):
        detector.analyze_metrics(
            (50 * scale, 50 * scale), (1000, 30 * scale), (10, 0), (1_000_000_000, 4_000_000_000)
        )
    assert not detector.is_learning
    anomalies = detector.analyze_metrics(
        (95 * scale, 95 * scale),
        (5_000_000, 99 * scale),
        (80, 10),
        (3_800_000_000, 4_000_000_000),
    )
    assert anomalies
    assert all(isinstance(item["metric_value_raw"], int) for item in anomalies)
    assert all(isinstance(item["threshold_value_raw"], int) for item in anomalies)
