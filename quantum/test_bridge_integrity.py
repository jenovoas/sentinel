#!/usr/bin/env python3
# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# ═════════════════════════════════════════════════════════════════════════════
# 🧪 P1.3 — Test de integridad del puente Py<->Rust (me60os_core)
#
# Verifica el contrato del binding tras la purga YATRA (f5086315, 2026-01-06) y
# el refactor Base-60 (69e53327, 2026-09-30):
#   1. Import del módulo nativo compilado (me60os_core.so).
#   2. Todas las clases exportadas en #[pymodule] existen.
#   3. PAI-60 divide exacta: (10°)/3 = 3°20' vía SPA raw.
#   4. SPA no re-introduce float por la puerta del puente (to_raw entero).
#
# Ejecución (requiere el .so construido):
#   cargo build -p me60os --features extension-module
#   cp target/debug/libme60os_core.so target/me60os_core.so
#   PYTHONPATH=target python3 -m pytest quantum/test_bridge_integrity.py -q
#   # o directamente: PYTHONPATH=target python3 quantum/test_bridge_integrity.py
# ═════════════════════════════════════════════════════════════════════════════

import sys
import os
import unittest

# Localizar el .so: preferir env DE60OS_SO_DIR, luego target/ del repo hermano
_SO_DIR = os.environ.get("ME60OS_SO_DIR")
if not _SO_DIR:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidate = os.path.join(root, "target")
    _SO_DIR = candidate if os.path.exists(os.path.join(candidate, "me60os_core.so")) else "/tmp/opencode"
for _p in (_SO_DIR, os.path.dirname(os.path.abspath(__file__))):
    if _p not in sys.path:
        sys.path.insert(0, _p)


class TestBridgeIntegrity(unittest.TestCase):
    """Puente Py<->Rust debe existir, exportar y calcular exacto."""

    @classmethod
    def setUpClass(cls):
        try:
            import me60os_core
        except ImportError as e:
            raise unittest.SkipTest(
                f"me60os_core no construido (cargo build --features extension-module): {e}"
            ) from e
        cls.S = me60os_core

    def test_clases_exportadas(self):
        # Contrato #[pymodule] en me-60os-core/src/lib.rs.
        esperadas = {
            "SPA", "SPAMath", "ComplexSPA", "ResonantMatrix", "PySharedBuffer",
            "IsochronousOscillator", "IsochronousClock", "OptomechanicalCooler",
            "S60PID", "HexagonalController",
            "QuantumSchedulerCore", "QuantumBuffer", "QuantumSchedulerDaemon",
            "AnomalyDetectorCore", "GuardianLsm", "ScvEngine", "py_pai60_divide",
        }
        faltantes = esperadas - set(x for x in dir(self.S) if not x.startswith("_"))
        self.assertFalse(faltantes, f"clases faltantes en el puente: {faltantes}")

    def test_pai60_divide_exact(self):
        # 10° / 3 = 3°20' exacto (Plimpton 322, tabla recíproca babilónica).
        ten = self.S.SPA(10, 0, 0, 0, 0)
        res = self.S.py_pai60_divide(ten.to_raw(), 3)
        self.assertIsNotNone(res, "3 es denominador regular (5-smooth)")
        esperado = self.S.SPA(3, 20, 0, 0, 0).to_raw()
        self.assertEqual(res, esperado, "10/3 debe ser 3;20 exacto")

    def test_spa_raw_es_entero(self):
        # YATRA: el puente no deja entrar float; to_raw siempre int.
        spa = self.S.SPA(1, 30, 0, 0, 0)
        self.assertIsInstance(spa.to_raw(), int)

    def test_wrapper_yatra_core_carga(self):
        # quantum/yatra_core.py automatiza: import wrapper no debe romper el puente.
        aquí = os.path.dirname(os.path.abspath(__file__))
        if aquí not in sys.path:
            sys.path.insert(0, aquí)
        import yatra_core  # noqa: F401
        self.assertEqual(str(yatra_core.PI_S60), "SPA[003; 08, 29, 44, 00]")


if __name__ == "__main__":
    unittest.main(verbosity=2)
