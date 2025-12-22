"""
Quantum Control Framework - Resource Adapters

Adapters for different infrastructure resources.
"""

from .buffer import BufferResource
from .threads import ThreadPoolResource

__all__ = [
    'BufferResource',
    'ThreadPoolResource'
]
