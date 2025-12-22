"""
Quantum Control Framework - Core Module

Universal quantum controller for infrastructure optimization.
"""

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

__version__ = '0.1.0'
