"""
Quantum Control Framework - Resource Adapters

Adapters for different infrastructure resources.
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
from .buffer import BufferResource
from .threads import ThreadPoolResource
from .memory import MemoryResource

__all__ = [
    'BufferResource',
    'ThreadPoolResource',
    'MemoryResource'
]
