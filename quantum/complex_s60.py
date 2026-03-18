#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# 1. Este archivo está PROTEGIDO por el Protocolo Yatra.
# 2. MIGRAGO A RUST: Ahora es un puente (wrapper) hacia `me-60os/src/spa_complex.rs`
# 3. Cualquier modificación debe hacerse en la librería nativa Rust.
# -------------------------------------------------------------------------------------

import sys
import os
from quantum.yatra_core import S60, DecimalContaminationError

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from me60os_core import ComplexSPA
except ImportError as e:
    print("CRITICAL: No se pudo importar la librería nativa Rust me60os_core.so")
    print(f"Error: {e}")
    sys.exit(1)

class ComplexS60:
    """Wrapper para operaciones complejas delegadas a Rust (ComplexSPA)."""
    
    def __init__(self, real, imag=None):
        if isinstance(real, ComplexSPA):
            self._z = real
        else:
            r = real if isinstance(real, S60) else S60(real)
            i = imag if isinstance(imag, S60) else S60(imag if imag is not None else 0)
            self._z = ComplexSPA(r, i)

    @property
    def real(self):
        return self._z.real

    @property
    def imag(self):
        return self._z.imag
    
    def __add__(self, other):
        if isinstance(other, ComplexS60):
            return ComplexS60(self._z + other._z)
        return ComplexS60(self._z + other)

    def __sub__(self, other):
        if isinstance(other, ComplexS60):
            return ComplexS60(self._z - other._z)
        return ComplexS60(self._z - other)

    def __mul__(self, other):
        if isinstance(other, ComplexS60):
            return ComplexS60(self._z * other._z)
        return ComplexS60(self._z * other)

    def __truediv__(self, other):
        if isinstance(other, ComplexS60):
            return ComplexS60(self._z / other._z)
        return ComplexS60(self._z / other)

    def __neg__(self):
        return ComplexS60(-self._z)

    def conjugate(self):
        return ComplexS60(self._z.py_conjugate())
    
    def magnitude(self):
        return self._z.py_magnitude()
        
    def __abs__(self):
        return self.magnitude()
    
    def __eq__(self, other):
        if isinstance(other, ComplexS60):
            return self._z == other._z
        return self._z == other

    def __repr__(self):
        return f"ComplexS60({self.real}, {self.imag})"
    
    def __str__(self):
        return str(self._z).replace("ComplexSPA", "ComplexS60")
        
    @staticmethod
    def from_polar(magnitude: S60, phase: S60):
        return ComplexS60(ComplexSPA.py_from_polar(magnitude, phase))
    
    @staticmethod
    def exp_i_theta(theta: S60):
        return ComplexS60(ComplexSPA.py_exp_i_theta(theta))


# Constantes útiles
I = ComplexS60(S60(0), S60(1))
ONE = ComplexS60(S60(1), S60(0))
ZERO = ComplexS60(S60(0), S60(0))

def demo_complex():
    print("🔱 COMPLEX S60: CHECKING NATIVE RUST DELEGATION...")
    c1 = ComplexS60(S60(2), S60(3))
    c2 = ComplexS60(S60(1), S60(1))
    
    print(f"c1 = {c1}")
    print(f"c2 = {c2}")
    print(f"c1 + c2 = {c1 + c2}")
    print(f"c1 * c2 = {c1 * c2}")
    print(f"|c1|    = {abs(c1)}")
    print("✅ DELEGACIÓN COMPLEJA NATICA EXITOSA")

if __name__ == "__main__":
    demo_complex()
