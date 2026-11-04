# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
# DEPRECATED: Migrated to sentinel-cortex/src/quantum/quantum_scheduler.rs
# Este archivo se mantiene temporalmente por compatibilidad del backend API.
# La implementación activa está en Rust.

"""
Quantum Scheduler — Motor de Resonancia Armónica
Basado en EXP-029-V2 (94.4% eficiencia) + EXP-014 (sparse memory 99.9% reducción)

Principio: en sistemas bio-resonantes, el costo energético de una operación
depende del estado del sistema en el momento de ejecución.

  E_portal  = E₀          (resistencia R = 0, superconductor)
  E_cerrado = 3 × E₀      (resistencia R >> 0, modo resistivo)

Resultado validado: 62.9% ahorro energético vs scheduler tradicional.
"""

import logging
import time

logger = logging.getLogger("quantum_scheduler")

# ── Constantes SPA raw (60^4) ────────────────────────────────────────────────
SCALE_0 = 12_960_000
T_CYCLE_RAW = 68 * SCALE_0
THETA_RAW = 9_720_000


import sys
from pathlib import Path

# Agregar soporte me-60os (SOMA Rust Core)
try:
    import me60os_core
except ImportError:
    import sys

    sys.path.insert(0, str(Path(__file__).parent))
    try:
        import me60os_core
    except ImportError:
        logger.error(
            "No se pudo importar me60os_core. Asegúrese de que me60os_core.so esté en sys.path"
        )
        sys.exit(1)

# ── Resonance Engine (Delegado a SOMA/Rust) ───────────────────────────────────


def phi(t_raw: int) -> int:
    """Calcula phi para un tiempo expresado en unidades raw SPA."""
    value = me60os_core.SPA._from_raw(t_raw)
    return me60os_core.QuantumSchedulerCore.static_phi(value).to_raw()


def phi_now() -> int:
    t_raw = time.monotonic_ns() * SCALE_0 // 1_000_000_000
    return phi(t_raw % T_CYCLE_RAW)


def is_portal_open() -> bool:
    t_raw = time.monotonic_ns() * SCALE_0 // 1_000_000_000
    return me60os_core.QuantumSchedulerCore.is_portal_open(
        me60os_core.SPA._from_raw(t_raw)
    )


def adaptive_batch_size(resonance_raw: int) -> int:
    if resonance_raw > 90 * SCALE_0 // 100:
        return 5
    if resonance_raw > 85 * SCALE_0 // 100:
        return 4
    if resonance_raw > 80 * SCALE_0 // 100:
        return 3
    return 2


def milliseconds_to_next_portal(resolution_ms: int = 50) -> int:
    t0_raw = time.monotonic_ns() * SCALE_0 // 1_000_000_000 % T_CYCLE_RAW
    cycle_ms = 68_000
    steps = cycle_ms // resolution_ms
    for i in range(steps):
        t_raw = (t0_raw + i * resolution_ms * SCALE_0 // 1_000) % T_CYCLE_RAW
        if phi(t_raw) > THETA_RAW:
            return i * resolution_ms
    return cycle_ms


# ── Quantum Buffer y Daemon (EXP-014 + EXP-029-V2 delegado a SOMA) ────────────

QuantumBuffer = me60os_core.QuantumBuffer


def QuantumSchedulerDaemon(buffer, process_fn, dt_ms=100, name="quantum-daemon"):
    """Construye el daemon SOMA con intervalo entero en milisegundos."""
    return me60os_core.QuantumSchedulerDaemon(buffer, process_fn, dt_ms, name)
