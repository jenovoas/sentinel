import math
import numpy as np

class S60:
    """
    Representación Soberana de números en Base-60.
    Impide la contaminación decimal al obligar a definir valores como Grados, Minutos y Segundos.
    """
    def __init__(self, degrees=0, minutes=0, seconds=0.0):
        self.d = degrees
        self.m = minutes
        self.s = seconds
        # Valor flotante interno solo para compatibilidad física final, pero protegido
        self._value = self.d + (self.m / 60.0) + (self.s / 3600.0)

    def __repr__(self):
        return f"S60[{self.d}; {self.m}, {self.s:.2f}]"

    def __float__(self):
        return self._value

    def __add__(self, other):
        if isinstance(other, S60):
            return S60_from_float(self._value + other._value)
        return S60_from_float(self._value + other)

    def __sub__(self, other):
        if isinstance(other, S60):
            return S60_from_float(self._value - other._value)
        return S60_from_float(self._value - other)

    def __mul__(self, other):
        val = other._value if isinstance(other, S60) else other
        return S60_from_float(self._value * val)

    def __truediv__(self, other):
        val = other._value if isinstance(other, S60) else other
        if val == 0: return S60(0)
        return S60_from_float(self._value / val)

    def to_harmonic(self):
        """Devuelve el valor normalizado para cálculos de resonancia"""
        return self._value

def S60_from_float(val):
    """Convierte un decimal contaminado de vuelta a la pureza S60"""
    d = int(val)
    rem_m = (abs(val) - abs(d)) * 60.0
    m = int(round(rem_m, 10))
    s = (rem_m - m) * 60.0
    # Ajuste de desbordamiento de redondeo
    if m >= 60:
        d += 1; m -= 60
    # Manejo de negativos
    if val < 0 and d == 0:
        if m != 0: m = -m
        elif s != 0: s = -s
    return S60(d, m, s)

# --- CONSTANTES SAGRADAS ---
PHI = S60(1, 37, 4.92) # Aprox 1.618... en sexagesimal
ZERO = S60(0, 0, 0)
ONE = S60(1, 0, 0)
PI_S60 = S60(3, 8, 29.7) # Pi babilónico

class SovereignLUT:
    """
    Tabla de Búsqueda Soberana para Trigonometría Base-60.
    Elimina la necesidad de np.sin/np.cos en tiempo de ejecución.
    Resolución: 1 segundo de arco (1,296,000 entradas).
    """
    _sin_table = None
    _cos_table = None
    _initialized = False

    @classmethod
    def initialize(cls):
        if cls._initialized: return
        # Generamos la tabla usando numpy para velocidad de carga (solo una vez)
        # pero con lógica soberana de 360*60*60 segundos
        total_seconds = 360 * 3600
        angles = np.linspace(0, 2*np.pi, total_seconds, endpoint=False)
        cls._sin_table = np.sin(angles)
        cls._cos_table = np.cos(angles)
        cls._initialized = True
        print(f"✅ SovereignLUT: 1,296,000 segundos sintonizados en Base-60.")

    @classmethod
    def get_sin_cos(cls, angle_s60: S60):
        """Devuelve (sin, cos) para un ángulo S60 indexando la tabla"""
        if not cls._initialized: cls.initialize()
        # Normalizar a 0-359
        d = angle_s60.d % 360
        m = angle_s60.m
        s = int(round(angle_s60.s))
        
        idx = d * 3600 + m * 60 + s
        if idx >= 1296000: idx = 0 # Wrap around
        return cls._sin_table[idx], cls._cos_table[idx]

# Inicializar al cargar el módulo
SovereignLUT.initialize()

class SovereignPhysics:
    @staticmethod
    def resonant_force(error_s60: S60, gain: S60) -> float:
        """
        Calcula fuerza basada en resonancia armónica, no en vectores lineales.
        F = Error * Ganancia (Todo en dominio S60)
        """
        return error_s60.to_harmonic() * gain.to_harmonic()

    @staticmethod
    def zpe_damping(velocity: float) -> float:
        """Amortiguamiento de Mercurio purificado"""
        # 3 + 14/60 = 3.2333... cercano a 2*PHI
        damping_const = S60(3, 14, 0).to_harmonic()
        return -velocity * damping_const
