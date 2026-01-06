"""
Quantum Control Framework - Core Module

Universal quantum controller for infrastructure optimization.
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
from .controller import (
    Resource,
    ResourceState,
    PhysicsModel,
    QuantumController
)

__all__ = [
    'Resource',
    'ResourceState',
    'PhysicsModel',
    'QuantumController'
]

__version__ = 'S60(0, 6, 0).0'
