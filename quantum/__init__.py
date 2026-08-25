# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

"""
Sentinel Quantum Package - __init__.py

Provides easy imports for all quantum simulators.
"""

# Version info
# REVIEW: versión corregida (antes era "1.S60(0,0,0)" — string literal inválido)
__version__ = "1.0.0"
__author__ = "Jaime Novoa"
__project__ = "Sentinel Cortex™"

# Core quantum simulator
try:
    from .core_simulator import QuantumCircuit, QuantumGates, QubitState
    _CORE_AVAILABLE = True
except ImportError:
    _CORE_AVAILABLE = False

# Optomechanical simulator
try:
    from .optomechanical_simulator import (
        MembraneParameters,
        OpticalParameters,
        OptomechanicalSystem,
        QuantumRiftDetector,
    )
    _OPTO_AVAILABLE = True
except ImportError:
    _OPTO_AVAILABLE = False

# Advanced quantum core
try:
    from .sentinel_quantum_core import SentinelConfig, SentinelQAOA, SentinelQuantumCore, SentinelVQE
    from .sentinel_quantum_core import SentinelRiftDetector as AdvancedRiftDetector
    _ADVANCED_AVAILABLE = True
except ImportError:
    _ADVANCED_AVAILABLE = False

# Lightweight version (always try to import)
try:
    from .quantum_lite import QuantumResourceManager, SentinelQuantumLite, demo_rift_detection
    _LITE_AVAILABLE = True
except ImportError:
    _LITE_AVAILABLE = False


def check_installation():
    """Check which modules are available."""
    print("Sentinel Quantum Package Status:")
    print(f"  Core Simulator: {'✅' if _CORE_AVAILABLE else '❌'}")
    print(f"  Optomechanical: {'✅' if _OPTO_AVAILABLE else '❌'}")
    print(f"  Advanced Core:  {'✅' if _ADVANCED_AVAILABLE else '❌'}")
    print(f"  Lite Version:   {'✅' if _LITE_AVAILABLE else '❌'}")

    if not any([_CORE_AVAILABLE, _OPTO_AVAILABLE, _ADVANCED_AVAILABLE, _LITE_AVAILABLE]):
        print("\n⚠️ No hay módulos Yatra operativos. Verificar integridad de yatra_core.py.")


def quick_start():
    """Run a quick demo to verify installation."""
    print("🚀 Sentinel Quantum Quick Start\n")

    if _LITE_AVAILABLE:
        print("Running lightweight demo (safe for laptops)...")
        from .quantum_lite import demo_rift_detection
        demo_rift_detection(n_membranes=2, n_levels=4)
    elif _CORE_AVAILABLE:
        print("Running core simulator demo...")
        from .core_simulator import QuantumCircuit
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)
        print(f"Bell state created: {qc.get_statevector()}")
    else:
        print("❌ No hay simuladores soberanos disponibles. Verifique Yatra Core.")


# Convenience imports
__all__ = [
    # Core
    'QubitState', 'QuantumGates', 'QuantumCircuit',
    # Optomechanical
    'MembraneParameters', 'OpticalParameters', 'OptomechanicalSystem',
    # Advanced
    'SentinelConfig', 'SentinelQuantumCore', 'SentinelQAOA', 'SentinelVQE',
    # Lite
    'QuantumResourceManager', 'SentinelQuantumLite', 'demo_rift_detection',
    # Utilities
    'check_installation', 'quick_start'
]
