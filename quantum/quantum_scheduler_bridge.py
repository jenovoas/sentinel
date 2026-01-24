# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

"""
Quantum Scheduler Bridge - Python Integration
Interacts with the Rust Quantum Scheduler via FFI/ctypes.

Features:
- Enqueue tasks with Python callbacks (CFUNCTYPE)
- Monitor scheduler efficiency
- Interface with BioResonator and PortalDetector

Author: Jaime Novoa (Migrated to Rust FFI)
"""

import ctypes
import os
import logging
from enum import IntEnum

# Configure logging
logger = logging.getLogger("QUANTUM_SCHEDULER")

# Load Rust Library
LIB_PATH = os.getenv("LIB_PATH")

if not LIB_PATH:
    # Assuming sentinel_core.so is in the python path or same directory
    LIB_PATH = os.path.join(os.path.dirname(__file__), "../sentinel-cortex/target/release/libsentinel_cortex.so")
    # Fallback for dev environment path
    if not os.path.exists(LIB_PATH):
        LIB_PATH = os.path.join(os.getcwd(), "sentinel-cortex/target/release/libsentinel_cortex.so")

try:
    lib = ctypes.CDLL(LIB_PATH)
    RUST_AVAILABLE = True
    logger.info(f"✅ Rust Quantum Core loaded from: {LIB_PATH}")
except OSError as e:
    logger.error(f"❌ Failed to load Rust Quantum Core: {e}")
    # Mock library for fallback/testing if Rust not built
    lib = None
    RUST_AVAILABLE = False

# -----------------------------------------------------------------------------
# Type Definitions
# -----------------------------------------------------------------------------

# C-compatible callback type: void callback(void)
CALLBACK_TYPE = ctypes.CFUNCTYPE(None)

class TaskType(IntEnum):
    ZPETune = 1
    BCISync = 2
    LatticeGC = 3
    BackupS60 = 4
    PhaseAlign = 5

# -----------------------------------------------------------------------------
# FFI Signatures
# -----------------------------------------------------------------------------

if RUST_AVAILABLE:
    # fn scheduler_enqueue(id: u64, task_type: u8, cost: u32, callback: extern "C" fn())
    lib.scheduler_enqueue.argtypes = [
        ctypes.c_uint64,  # id
        ctypes.c_uint8,   # task_type
        ctypes.c_uint32,  # cost
        CALLBACK_TYPE     # callback
    ]
    lib.scheduler_enqueue.restype = None

    # fn scheduler_tick(time_s60_raw: i64)
    lib.scheduler_tick.argtypes = [ctypes.c_int64]
    lib.scheduler_tick.restype = None

    # fn scheduler_get_efficiency() -> f64
    lib.scheduler_get_efficiency.argtypes = []
    lib.scheduler_get_efficiency.restype = ctypes.c_double

    # fn scheduler_reset_stats()
    lib.scheduler_reset_stats.argtypes = []
    lib.scheduler_reset_stats.restype = None

    # fn scheduler_queue_len() -> usize
    lib.scheduler_queue_len.argtypes = []
    lib.scheduler_queue_len.restype = ctypes.c_size_t

# -----------------------------------------------------------------------------
# Python Wrapper Class
# -----------------------------------------------------------------------------

class QuantumSchedulerBridge:
    """Interface to the Rust Quantum Scheduler."""

    def __init__(self):
        self.callbacks = [] # Keep references to prevent GC

    def enqueue(self, task_id: int, task_type: TaskType, cost: int, python_func):
        """
        Enqueue a Python function as a quantum task.
        
        Args:
            task_id: Unique ID
            task_type: Enum TaskType
            cost: Energy cost estimate
            python_func: Python callable to execute
        """
        if not RUST_AVAILABLE:
            logger.warning("Rust core unavailable - executing task immediately (fallback)")
            python_func()
            return

        # Create C callback wrapper
        c_callback = CALLBACK_TYPE(python_func)
        
        # IMPORTANT: We must keep a reference to c_callback, otherwise
        # Python's GC will collect it and Rust will crash when calling it.
        self.callbacks.append(c_callback)

        # Call Rust FFI
        lib.scheduler_enqueue(
            task_id,
            int(task_type),
            cost,
            c_callback
        )
        logger.debug(f"Enqueued task {task_id} ({task_type.name}) to Quantum Scheduler")

    def tick(self, time_s60_raw: int):
        """Advance scheduler clock (call at 41 Hz)."""
        if RUST_AVAILABLE:
            lib.scheduler_tick(time_s60_raw)

    def get_efficiency(self) -> float:
        """Get current adiabatic efficiency [0.0 - 1.0]."""
        if RUST_AVAILABLE:
            return lib.scheduler_get_efficiency()
        return 0.0

    def get_queue_len(self) -> int:
        if RUST_AVAILABLE:
            return lib.scheduler_queue_len()
        return 0

# Global singleton
scheduler = QuantumSchedulerBridge()
