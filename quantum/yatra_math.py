#!/usr/bin/env python3
# DEPRECATED: Migrated to sentinel-cortex/src/math/s60_math.rs
# Este archivo es un puente (wrapper) hacia Rust. La implementación real está en Rust.
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# 1. CONSULTA PRIMERO: quantum/agents.md
# 2. Este archivo está PROTEGIDO por el Protocolo Yatra.
# 3. MIGRAGO A RUST: Ahora es un puente (wrapper) hacia `me-60os/src/spa_math.rs`
# 4. Cualquier modificación de cálculo debe hacerse en la librería nativa Rust.
# -------------------------------------------------------------------------------------

import sys
import os
from yatra_core import S60, DecimalContaminationError

# Asegurar que el módulo nativo compilado (me60os_core.so) sea encontrado
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from me60os_core import SPAMath as S60MathNative
except ImportError as e:
    print("CRITICAL: No se pudo importar la librería nativa Rust me60os_core.so")
    print(f"Error: {e}")
    sys.exit(1)


# Importamos del núcleo nativo para evitar redundancias
class S60Math:
    """Wrapper para funciones matemáticas trascendentes procesadas en Rust nativo."""

    # Constantes maestras ahora inicializadas vía S60(Rust)
    PI = S60(3, 8, 29, 44, 0)
    TWO_PI = S60(6, 16, 59, 28, 0)
    PI_HALF = S60(1, 34, 14, 52, 0)

    DEG_TO_RAD_FACTOR = S60(0, 1, 2, 49, 12)  # PI / 180 ≈ 0.017453...

    @staticmethod
    def sin(angle_s60, precision_terms=10):
        """Calcula el seno del ángulo. Ignora precision_terms porque Rust maneja el Taylor series optimizado."""
        return S60MathNative.py_sin(angle_s60)

    @staticmethod
    def sin_fast(angle_s60):
        return S60MathNative.py_sin(angle_s60)

    @staticmethod
    def cos(angle_s60, precision_terms=10):
        """Calcula el coseno del ángulo. Taylor series en Rust."""
        return S60MathNative.py_cos(angle_s60)

    @staticmethod
    def cos_fast(angle_s60):
        return S60MathNative.py_cos(angle_s60)

    @staticmethod
    def sqrt(n_s60, iterations=12):
        """Raíz cuadrada vía Newton-Raphson rápido en Rust."""
        return S60MathNative.py_sqrt(n_s60)

    @staticmethod
    def exp(x_s60, precision_terms=12):
        """Exponencial taylor series en Rust."""
        return S60MathNative.py_exp(x_s60)

    @staticmethod
    def exp_fast(x_s60):
        return S60MathNative.py_exp(x_s60)

    @staticmethod
    def ln(x_s60, precision_terms=15):
        """Logaritmo natural en Rust."""
        return S60MathNative.py_ln(x_s60)

    @staticmethod
    def log2(x_s60):
        """log2 = ln(x) / ln(2). Realizado directamente con el wrapper en base a Rust."""
        ln_x = S60MathNative.py_ln(x_s60)
        # ln(2) * SCALE_0 = 8983187 (en Rust: LN_2)
        # log2 = (ln_x * (1/ln(2)))
        INV_LN2_RAW = 18698485
        res = getattr(ln_x, "to_base_units")() * INV_LN2_RAW // S60.SCALE_0
        return S60._from_raw(res)

    @staticmethod
    def log(x_s60, base=60):
        """Logaritmo en base 60 o cualquier otra entera"""
        ln_x = S60MathNative.py_ln(x_s60)
        if base == 60:
            LN60_RAW = 53062706  # Equivalente exacto a Rust SPAMath::LN_60
            res = getattr(ln_x, "to_base_units")() * S60.SCALE_0 // LN60_RAW
        else:
            ln_b = S60MathNative.py_ln(S60(base))
            res = (
                getattr(ln_x, "to_base_units")()
                * S60.SCALE_0
                // getattr(ln_b, "to_base_units")()
            )

        return S60._from_raw(res)

    @staticmethod
    def sin_cos(angle_s60, precision_terms=10):
        return S60MathNative.py_sin(angle_s60), S60MathNative.py_cos(angle_s60)

    @staticmethod
    def abs(x_s60):
        return abs(x_s60)

    @staticmethod
    def floor(x_s60):
        integer_part = x_s60.to_base_units() // S60.SCALE_0
        if x_s60.to_base_units() < 0 and (x_s60.to_base_units() % S60.SCALE_0) != 0:
            integer_part -= 1
        return S60(integer_part)

    @staticmethod
    def ceil(x_s60):
        integer_part = x_s60.to_base_units() // S60.SCALE_0
        if x_s60.to_base_units() > 0 and (x_s60.to_base_units() % S60.SCALE_0) != 0:
            integer_part += 1
        return S60(integer_part)

    @staticmethod
    def tensor_product(A, B):
        """
        Calcula el producto de Kronecker de dos matrices o vectores representados como listas.
        """
        # Caso 2D: List[List[S60]]
        if isinstance(A, list) and len(A) > 0 and isinstance(A[0], list):
            m, n = len(A), len(A[0])
            p, q = len(B), len(B[0])

            res = [
                [(A[i][j] * B[k][l]) for j in range(n) for l in range(q)]
                for i in range(m)
                for k in range(p)
            ]
            return res

        # Caso 1D: List[S60]
        elif isinstance(A, list):
            m = len(A)
            p = len(B)
            # Validación de tipos estricta para evitar contaminación
            if m > 0 and not isinstance(A[0], S60):
                raise TypeError("Tensor A must contain S60")
            if p > 0 and not isinstance(B[0], S60):
                raise TypeError("Tensor B must contain S60")

            res = [(A[i] * B[k]) for i in range(m) for k in range(p)]
            return res


# Alias de utilidad
def s60_abs(x):
    return abs(x)


def s60_compare(a, b):
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


def demo_math():
    print("🔱 YATRA MATH: CHECKING NATIVE RUST DELEGATION (sin / cos / exp / ln)...")
    angle = S60(30, 0, 0, 0, 0)
    print(f"sin(30°) = {S60Math.sin(angle)}")
    print(f"cos(30°) = {S60Math.cos(angle)}")
    num = S60(4, 0, 0, 0, 0)
    print(f"sqrt(4)  = {S60Math.sqrt(num)}")
    print(f"exp(1)   = {S60Math.exp(S60(1))}")
    print(f"ln(e)    = {S60Math.ln(S60Math.exp(S60(1)))}")
    print("✅ DELEGACIÓN NATICA EXITOSA")


if __name__ == "__main__":
    demo_math()
