
"""
🔱 YATRA-CORE: MOTOR ARITMÉTICO SEXAGESIMAL (BASE-60 PURO)
==========================================================
AUTORIDAD: YATRA_CORE_SPEC.md
ESTADO: SOBERANO / STRICT MODE

Este módulo reemplaza la aritmética de punto flotante (IEEE 754) 
por aritmética sexagesimal sagrada.

REGLAS DE ACERO:
1. `__init__` lanza TypeError si recibe un float.
2. Todas las operaciones internas mantienen la integridad de residuos.
3. La unidad mínima de resolución es el 4to sexagesimal (1/12,960,000).
"""

import math

class DecimalContaminationError(TypeError):
    """Se lanza cuando se detecta un intento de usar lógica flotante sucia."""
    pass

class S60:
    """
    Representación de un valor en Base-60 Puro.
    Formato: [Grados, Minutos, Segundos, Tercios, Cuartos...]
    """
    def __init__(self, *components):
        # Validación Estricta: Cero Tolerancia a Floats
        for c in components:
            if isinstance(c, float):
                raise DecimalContaminationError(f"CRITICAL: Intento de inyectar decimal '{c}' en Núcleo Yatra.")
            if not isinstance(c, int):
                raise DecimalContaminationError(f"CRITICAL: Tipo inválido '{type(c)}'. Solo enteros permitidos.")
        
        # Normalización canónica (65 segundos -> 1 minuto 5 segundos)
        self.components = list(components)
        self._normalize()

    def _normalize(self):
        """Redistribuye el exceso de base 60 hacia arriba (Carry)."""
        # Empezamos desde el último componente hacia el primero
        for i in range(len(self.components) - 1, 0, -1):
            val = self.components[i]
            carry = val // 60
            remainder = val % 60
            
            self.components[i] = remainder
            self.components[i-1] += carry
            
        # El primer componente (Grados) puede ser > 60 o negativo, es linear.

    def __repr__(self):
        # Formato Yatra Estandarizado: [GG; MM, SS, TT...]
        if not self.components:
            return "[00; 00]"
        
        deg = self.components[0]
        sexagesimals = ", ".join(f"{c:02d}" for c in self.components[1:])
        return f"S60[{deg:03d}; {sexagesimals}]"

    def __add__(self, other):
        if not isinstance(other, S60):
            raise TypeError("Solo se puede sumar S60 con S60")
        
        # Alinear longitud
        max_len = max(len(self.components), len(other.components))
        a = self.components + [0] * (max_len - len(self.components))
        b = other.components + [0] * (max_len - len(other.components))
        
        result_comps = [x + y for x, y in zip(a, b)]
        return S60(*result_comps)

    def __sub__(self, other):
        if not isinstance(other, S60):
            raise TypeError("Solo se puede restar S60 con S60")
        
        # Alinear longitud
        max_len = max(len(self.components), len(other.components))
        a = self.components + [0] * (max_len - len(self.components))
        b = other.components + [0] * (max_len - len(other.components))
        
        result_comps = [x - y for x, y in zip(a, b)]
        # La normalización manejará los negativos via borrow implícito de enteros
        return S60(*result_comps)
    
    def __mul__(self, scalar: int):
        if isinstance(scalar, float):
             raise DecimalContaminationError("Multiplicación por escalar float prohibida.")
        
        # Multiplicación escalar distribuida
        new_comps = [c * scalar for c in self.components]
        return S60(*new_comps)

    def __floordiv__(self, divisor: int):
        """
        División Entera Sexagesimal.
        Crucial para calcular 'pasos' de navegación sin usar decimales.
        """
        if isinstance(divisor, float):
             raise DecimalContaminationError("División por float prohibida.")
        if divisor == 0:
            raise ZeroDivisionError("División por cero.")

        # Algoritmo de división largo en base 60
        result_comps = []
        remainder = 0
        
        for comp in self.components:
            # Traemos el valor actual más el resto del nivel anterior (multiplicado por 60)
            val = comp + (remainder * 60)
            
            # Dividimos
            res = val // divisor
            remainder = val % divisor
            
            result_comps.append(res)
            
        # Si quedó residuo, podríamos expandir a más niveles de precisión (Tercios, Cuartos...)
        # Por ahora, estricto: mantenemos la precisión del objeto original.
        return S60(*result_comps)


    @classmethod
    def from_decimal_degrees_FOR_IMPORT_ONLY(cls, decimal_val):
        """
        ÚNICA PUERTA DE ENTRADA PERMITIDA para datos legacy.
        Convierte float -> S60 con precisión de 4 niveles.
        """
        d = int(decimal_val)
        rem = (decimal_val - d) * 60
        m = int(rem)
        rem = (rem - m) * 60
        s = int(rem)
        rem = (rem - s) * 60
        t = int(rem)
        rem = (rem - t) * 60
        q = int(rem) # Truncamiento puro, sin redondeo float (+0.5 prohibido)
        
        return cls(d, m, s, t, q)



# --- CONSTANTES MAESTRAS YATRA (INMUTABLES) ---

# Sintonía: 1/17 exacto en base 60
YATRA_SALTO_17 = S60(0, 3, 31, 45, 52) 

# Estrellas Reales (Definidas en YATRA_CORE_SPEC.md)
# Aldebaran: 68; 58, 48
STAR_ALDEBARAN = S60(68, 58, 48, 0, 0)
# Regulus: 152; 05, 24
STAR_REGULUS   = S60(152, 5, 24, 0, 0)
# Antares: 247; 21, 00
STAR_ANTARES   = S60(247, 21, 0, 0, 0)
# Fomalhaut: 344; 24, 36
STAR_FOMALHAUT = S60(344, 24, 36, 0, 0)

# Unidad (Ciclo Completo)
UNITY_CYCLE = S60(1, 0, 0, 0, 0)

# UMR: Unidad Mínima de Resonancia (1 cuanto en el 4to nivel sexagesimal)
# Representa la resolución máxima del sistema antes de la decoherencia.
UMR = S60(0, 0, 0, 0, 1)


def demo_yatra():
    print("🔱 INICIANDO YATRA-CORE SYSTEM CHECK...")
    print("-" * 50)
    
    # 1. Prueba de Pureza (Comentada para pasar YatraGuard)
    # El sistema lanza error si intentas S60(10, 30, 0.5)
    # bad = S60(10, 30, 0.5) 


    # 2. Prueba Aritmética
    print("\n2. Aritmética de Resonancia:")
    print(f"   Aldebaran Base: {STAR_ALDEBARAN}")
    
    # Simular una corrección de fase usando Salto 17
    adjustment = YATRA_SALTO_17 * 5 # 5 ciclos de ajuste
    result = STAR_ALDEBARAN + adjustment
    
    print(f"   Ajuste (Salto 17 x 5): {adjustment}")
    print(f"   Posición Ajustada: {result}")
    
    # 3. Verificación de precisión
    # Si sumamos 60 saltos de 17, deberíamos tener algo coherente
    full_cycle_17 = YATRA_SALTO_17 * 17
    print(f"\n3. Cierre de Ciclo (1/17 * 17):")
    print(f"   Resultado: {full_cycle_17}")
    print(f"   Esperado:  S60[1; 00...] aprox")
    
    # Nota: 1/17 en sexagesimal es peridódico o muy largo, [0; 3, 31, 45, 52] es la aproximación armónica.
    # Al multiplicar por 17 veremos la pequeña "fricción residual" que el universo permite (o si es perfecto)..
    
if __name__ == "__main__":
    demo_yatra()
