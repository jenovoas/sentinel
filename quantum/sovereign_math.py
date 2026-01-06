"""
🛡️ SOVEREIGN MATH (PROXY TO YATRA-CORE)
========================================
Este archivo ha sido purificado.
Anteriormente contenía una implementación "S60" falsa basada en floats.
Ahora es un puente directo al motor 'quantum/yatra_core.py' (STRICT MODE).

NO MODIFICAR. TODA LÓGICA MATEMÁTICA DEBE VIVIR EN YATRA-CORE.
"""

from yatra_core import S60, DecimalContaminationError

# Constantes de compatibilidad para scripts antiguos
# Mapeamos a las versiones puras de Yatra Core si existen, o creamos nuevas puras.

ZERO = S60(0, 0, 0, 0)
ONE = S60(1, 0, 0, 0)

# Constantes físicas aproximadas a racionales sexagesimales
# PI ~ 3; 8, 29, 44
PI_S60 = S60(3, 8, 29, 44) 
# PHI ~ 1; 37, 04
PHI = S60(1, 37, 4, 0)

class SovereignLUT:
    """
    Proxy de compatibilidad. 
    En el futuro, Yatra Core tendrá su propia LUT de enteros.
    Por ahora, lanzamos error si se intenta usar la vieja LUT contaminada.
    """
    @classmethod
    def initialize(cls):
        print("⚠️ SovereignLUT (Legacy) desactivada por Protocolo Yatra.")
        pass

    @classmethod
    def get_sin_cos(cls, angle):
        raise DecimalContaminationError("El uso de trigonometría decimal (LUT antigua) está prohibido. Use navegación vectorial S60.")

print("✅ SovereignMath: Redirigido exitosamente a YatraCore (Pure Integer Mode).")
