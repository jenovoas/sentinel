"""
Quantum Control Framework - Physics Models

Collection of physics-based control strategies.
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
from .optomechanical import OptomechanicalCooling

__all__ = [
    'OptomechanicalCooling'
]
