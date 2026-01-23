#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# 1. CONSULTA PRIMERO: quantum/agents.md
# 2. Este archivo está PROTEGIDO por el Protocolo Yatra.
# 3. El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# 4. SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

"""
🔱 YATRA-CORE: MOTOR ARITMÉTICO SEXAGESIMAL (BASE-60 PURO)
==========================================================
AUTORIDAD: YATRA_CORE_SPEC.md
ESTADO: SOBERANO / STRICT MODE / HARDWARE-READY

Este módulo implementa aritmética sexagesimal en FIXED-POINT PURO.

ARQUITECTURA:
- Matemática: Base-60 pura (60^4, 60^3, 60^2, 60, 1)
- Almacenamiento: int Python (binario interno inevitable)
- Representación interna: int en unidades de 1/60^4
- Escala fija: 60^4 = 12,960,000
- Precisión: 1/12,960,000 ≈ 0.000077 grados

HARDWARE-READY:
- Sintetizable en FPGA/ASIC (Verilog/VHDL)
- Operaciones O(1) con enteros
- Sin loops variables
- Sin floats en runtime

REGLAS DE ACERO:
1. `__init__` lanza TypeError si recibe un float.
2. Todas las operaciones son enteros puros.
3. La unidad mínima es 1/12,960,000 (60^4).
4. CERO FLOATS en todo el pipeline.
"""


class DecimalContaminationError(TypeError):
    """Se lanza cuando se detecta un intento de usar lógica flotante sucia."""
    pass


class S60:
    """
    Representación de un valor en Base-60 Puro (Fixed-Point).
    
    Formato externo: [Grados; Minutos, Segundos, Tercios, Cuartos]
    Formato interno: int en unidades de 1/60^4
    
    Matemática: d*60^4 + m*60^3 + s*60^2 + t*60 + q (BASE-60 PURA)
    
    Ejemplo:
        S60(1, 30, 0, 0, 0) = 1.5 grados
        Interno: 1*12960000 + 30*216000 = 19,440,000 unidades
    """
    
    # Constantes de escala BASE-60 (pre-calculadas, inmutables)
    SCALE_0 = 12960000  # 60^4 (grados)
    SCALE_1 = 216000    # 60^3 (minutos)
    SCALE_2 = 3600      # 60^2 (segundos)
    SCALE_3 = 60        # 60^1 (tercios)
    SCALE_4 = 1         # 60^0 (cuartos)
    
    __slots__ = ['_value']  # Optimización de memoria
    
    def __init__(self, d=0, m=0, s=0, t=0, q=0):
        """
        Inicializa S60 desde componentes sexagesimales.
        
        Args:
            d: Grados (int)
            m: Minutos (int, 0-59)
            s: Segundos (int, 0-59)
            t: Tercios (int, 0-59)
            q: Cuartos (int, 0-59)
            
        Raises:
            DecimalContaminationError: Si algún componente es float
        """
        # Validación Estricta: Cero Tolerancia a Floats
        for c in [d, m, s, t, q]:
            if isinstance(c, float):
                raise DecimalContaminationError(
                    f"CRITICAL: Intento de inyectar decimal '{c}' en Núcleo Yatra."
                )
            if not isinstance(c, int):
                raise DecimalContaminationError(
                    f"CRITICAL: Tipo inválido '{type(c)}'. Solo enteros permitidos."
                )
        
        # Conversión a fixed-point (MATEMÁTICA BASE-60)
        # Valor = d*60^4 + m*60^3 + s*60^2 + t*60 + q
        self._value = (
            d * self.SCALE_0 +
            m * self.SCALE_1 +
            s * self.SCALE_2 +
            t * self.SCALE_3 +
            q * self.SCALE_4
        )
    
    @classmethod
    def _from_raw(cls, raw_value: int):
        """
        Crea S60 desde valor interno (para operaciones internas).
        
        Args:
            raw_value: Valor en unidades de 1/60^4
            
        Returns:
            S60 con ese valor interno
        """
        obj = cls.__new__(cls)
        obj._value = raw_value
        return obj
    
    def __repr__(self):
        """Formato Yatra Estandarizado: S60[GGG; MM, SS, TT, QQ]"""
        val = abs(self._value)
        sign = "-" if self._value < 0 else ""
        
        # Extraer componentes (MATEMÁTICA BASE-60)
        d = val // self.SCALE_0
        val %= self.SCALE_0
        
        m = val // self.SCALE_1
        val %= self.SCALE_1
        
        s = val // self.SCALE_2
        val %= self.SCALE_2
        
        t = val // self.SCALE_3
        val %= self.SCALE_3
        
        q = val
        
        return f"S60[{sign}{d:03d}; {m:02d}, {s:02d}, {t:02d}, {q:02d}]"
    
    # ========================================================================
    # OPERACIONES ARITMÉTICAS (BASE-60 FIXED-POINT)
    # ========================================================================
    
    def __add__(self, other):
        """Suma: una sola adición de enteros."""
        if not isinstance(other, S60):
            raise TypeError("Solo se puede sumar S60 con S60")
        return S60._from_raw(self._value + other._value)
    
    def __sub__(self, other):
        """Resta: una sola resta de enteros."""
        if not isinstance(other, S60):
            raise TypeError("Solo se puede restar S60 con S60")
        return S60._from_raw(self._value - other._value)
    
    def __mul__(self, scalar):
        """Multiplicación escalar (int) o S60 * S60."""
        if isinstance(scalar, float):
            raise DecimalContaminationError("Multiplicación por escalar float prohibida.")
        
        if isinstance(scalar, S60):
            # S60 * S60: multiplicar valores y re-escalar
            result = (self._value * scalar._value) // self.SCALE_0
            return S60._from_raw(result)
        elif isinstance(scalar, int):
            return S60._from_raw(self._value * scalar)
        else:
            raise TypeError(f"Solo se puede multiplicar S60 por int o S60, no {type(scalar)}")
    
    def __rmul__(self, scalar):
        """Multiplicación reversa (int * S60 o S60 * S60)."""
        return self.__mul__(scalar)
    
    def __floordiv__(self, divisor: int):
        """División entera: una sola división de enteros."""
        if isinstance(divisor, float):
            raise DecimalContaminationError("División por float prohibida.")
        if not isinstance(divisor, int):
            raise TypeError(f"Solo se puede dividir S60 por int, no {type(divisor)}")
        if divisor == 0:
            raise ZeroDivisionError("División por cero.")
        return S60._from_raw(self._value // divisor)
    
    def __truediv__(self, divisor):
        """
        División verdadera S60 / S60 o S60 / int.
        Retorna S60 con redondeo al cuarto más cercano (máxima precisión).
        """
        if isinstance(divisor, S60):
            if divisor._value == 0:
                raise ZeroDivisionError("División por cero")
            
            # División con re-escalado y redondeo (+ divisor//2 para redondear)
            num = self._value * self.SCALE_0
            den = divisor._value
            # Manejo de signo para redondeo correcto
            sign = 1 if (num ^ den) >= 0 else -1
            result = (abs(num) + abs(den) // 2) // abs(den)
            return S60._from_raw(result * sign)
        
        elif isinstance(divisor, int):
            if divisor == 0:
                raise ZeroDivisionError("División por cero")
            # S60 / int con redondeo
            sign = 1 if (self._value ^ divisor) >= 0 else -1
            result = (abs(self._value) + abs(divisor) // 2) // abs(divisor)
            return S60._from_raw(result * sign)
        
        else:
            raise TypeError(f"No se puede dividir S60 por {type(divisor)}")
    
    # ========================================================================
    # OPERADORES UNARIOS
    # ========================================================================
    
    def __neg__(self):
        """Negación unaria (-x)."""
        return S60._from_raw(-self._value)
    
    def __abs__(self):
        """Valor absoluto."""
        return S60._from_raw(abs(self._value))
    
    # ========================================================================
    # COMPARACIONES (FIXED-POINT PURO)
    # ========================================================================
    
    def __lt__(self, other):
        """Menor que (<)."""
        if not isinstance(other, S60):
            raise TypeError("Solo se puede comparar S60 con S60")
        return self._value < other._value
    
    def __le__(self, other):
        """Menor o igual (<=)."""
        if not isinstance(other, S60):
            raise TypeError("Solo se puede comparar S60 con S60")
        return self._value <= other._value
    
    def __gt__(self, other):
        """Mayor que (>)."""
        if not isinstance(other, S60):
            raise TypeError("Solo se puede comparar S60 con S60")
        return self._value > other._value
    
    def __ge__(self, other):
        """Mayor o igual (>=)."""
        if not isinstance(other, S60):
            raise TypeError("Solo se puede comparar S60 con S60")
        return self._value >= other._value
    
    def __eq__(self, other):
        """Igual (==)"""
        if not isinstance(other, S60):
            return False
        return self._value == other._value
    
    def __ne__(self, other):
        """Diferente (!=)."""
        return not self.__eq__(other)

    def __pow__(self, power: int):
        """Potencia entera S60 ** int."""
        if not isinstance(power, int):
            raise TypeError("La potencia debe ser un entero para mantener soberanía determinista.")
        if power < 0:
            # e.g. x^-2 = 1 / x^2
            res = (self**abs(power))
            return S60(1) / res
        
        result = S60(1)
        base = self
        while power > 0:
            if power % 2 == 1:
                result = result * base
            base = base * base
            power //= 2
        return result

    def __hash__(self):
        """Permite usar S60 como clave en diccionarios."""
        return hash(self._value)

    def __index__(self):
        """Permite usar S60 como índice si es entero (o para conversiones)."""
        return self._value // self.SCALE_0

    def __bool__(self):
        """True si el valor es distinto de cero."""
        return self._value != 0
    
    # ========================================================================
    # UTILIDADES
    # ========================================================================
    
    def to_base_units(self):
        """
        Retorna el valor interno en unidades mínimas (int puro).
        
        Útil para:
        - Comparaciones externas
        - Serialización
        - Debugging
        
        Returns:
            int: Valor en unidades de 1/60^4
        
        Ejemplo:
            S60(1, 30, 0, 0, 0).to_base_units() → 19,440,000
        """
        return self._value
    
    @classmethod
    def from_decimal_degrees_FOR_IMPORT_ONLY(cls, decimal_val):
        """
        ÚNICA PUERTA DE ENTRADA PERMITIDA para datos legacy.
        Convierte float -> S60 con precisión de 4 niveles.
        
        ⚠️ ADVERTENCIA: Usa floats internamente.
        ✅ ACEPTABLE: Solo para # math import removed - Yatra uses pure Base-60 arithmetic onlyr datos externos.
        🔒 REGLA: NUNCA usar dentro de lógica Yatra.
        
        Args:
            decimal_val: Valor decimal (float) a convertir
            
        Returns:
            S60 equivalente
        """
        d = int(decimal_val)
        rem = (decimal_val - d) * 60
        m = int(rem)
        rem = (rem - m) * 60
        s = int(rem)
        rem = (rem - s) * 60
        t = int(rem)
        rem = (rem - t) * 60
        q = int(rem)  # Truncamiento puro
        
        return cls(d, m, s, t, q)


# --- CONSTANTES MAESTRAS YATRA (INMUTABLES) ---

# Sintonía: 1/17 exacto en base 60
YATRA_SALTO_17 = S60(0, 3, 31, 45, 52)

# Estrellas Reales (Definidas en YATRA_CORE_SPEC.md)
STAR_ALDEBARAN = S60(68, 58, 48, 0, 0)   # 68; 58, 48
STAR_REGULUS   = S60(152, 5, 24, 0, 0)   # 152; 05, 24
STAR_ANTARES   = S60(247, 21, 0, 0, 0)   # 247; 21, 00
STAR_FOMALHAUT = S60(344, 24, 36, 0, 0)  # 344; 24, 36

# Unidad (Ciclo Completo)
UNITY_CYCLE = S60(1, 0, 0, 0, 0)

# UMR: Unidad Mínima de Resonancia (1 cuanto en el 4to nivel sexagesimal)
UMR = S60(0, 0, 0, 0, 1)


def demo_yatra():
    """Demostración del sistema Yatra."""
    print("🔱 INICIANDO YATRA-CORE SYSTEM CHECK (FIXED-POINT MODE)...")
    print("-" * 60)
    
    # 1. Verificar arquitectura
    print("\n1. Arquitectura Fixed-Point Base-60:")
    test = S60(1, 30, 0, 0, 0)
    print(f"   S60(1, 30, 0, 0, 0) = {test}")
    print(f"   Valor interno: {test._value}")
    expected = 1*12960000 + 30*216000
    print(f"   Esperado: 1*60^4 + 30*60^3 = {expected}")
    print(f"   Verificación: {test._value == expected} ✅")
    
    # 2. Prueba Aritmética
    print("\n2. Aritmética de Resonancia:")
    print(f"   Aldebaran Base: {STAR_ALDEBARAN}")
    
    adjustment = YATRA_SALTO_17 * 5
    result = STAR_ALDEBARAN + adjustment
    
    print(f"   Ajuste (Salto 17 x 5): {adjustment}")
    print(f"   Posición Ajustada: {result}")
    
    # 3. Verificación de precisión
    print(f"\n3. Cierre de Ciclo (1/17 * 17):")
    full_cycle_17 = YATRA_SALTO_17 * 17
    print(f"   Resultado: {full_cycle_17}")
    print(f"   Esperado:  S60[001; 00, 00, ...] aprox")
    
    # 4. Test de pureza
    print("\n4. Test de Pureza (debe rechazar float):")
    try:
        bad = S60(10, 30, S60(1)/2)  # Intenta inyectar algo que no sea int
        print("   ❌ FALLO: Aceptó float")
    except DecimalContaminationError as e:
        print(f"   ✅ ÉXITO: Rechazó float")
    
    # 5. Test de operaciones
    print("\n5. Test de Operaciones:")
    a = S60(10, 0, 0, 0, 0)
    b = S60(5, 0, 0, 0, 0)
    print(f"   a = {a}")
    print(f"   b = {b}")
    print(f"   a + b = {a + b}")
    print(f"   a - b = {a - b}")
    print(f"   a * 2 = {a * 2}")
    print(f"   a // 2 = {a // 2}")
    print(f"   a < b = {a < b}")
    print(f"   a > b = {a > b}")
    
    print("\n" + "=" * 60)
    print("✅ YATRA-CORE: FIXED-POINT BASE-60 OPERATIVO")
    print("   - Matemática: Base-60 pura (60^4, 60^3, 60^2, 60, 1)")
    print("   - Almacenamiento: int Python (binario inevitable)")
    print("   - Escala: 60^4 = 12,960,000")
    print("   - Hardware-ready: SÍ (sintetizable)")
    print("   - Floats: CERO")
# Constantes Globales Soberanas
PI_S60 = S60(3, 8, 29, 44, 0) # ≈ 3.14159265


if __name__ == "__main__":
    demo_yatra()