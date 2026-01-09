#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# YATRA-MATH: MATEMÁTICAS SOBERANAS DERIVADAS (SIN TABLAS HARDCODED)
# -------------------------------------------------------------------------------------

from quantum.yatra_core import S60


class S60Math:
    """
    Implementación de funciones trascendentes mediante series de potencias puras.
    Evita el 'hardcoding' de tablas CORDIC para mantener la soberanía absoluta.
    """
    
    # Constantes derivadas
    # PI ≈ 3.14159265... -> S60[003; 08, 29, 44, 00]
    PI = S60(3, 8, 29, 44, 0)
    PI_HALF = S60(1, 34, 14, 52, 0)
    TWO_PI = S60(6, 16, 59, 28, 0)
    
    DEG_TO_RAD_FACTOR = S60(0, 1, 2, 49, 12) # PI / 180 ≈ 0.017453...
    
    @staticmethod
    def _normalize_to_pi_half(angle_s60):
        """
        Normaliza cualquier ángulo al primer cuadrante [0, PI/2]
        Retorna (ángulo_normalizado, signo_sin, signo_cos)
        """
        # 360 grados en unidades raw
        full_circle = 360 * S60.SCALE_0
        raw = angle_s60._value % full_circle
        if raw < 0: raw += full_circle
        
        deg = raw // S60.SCALE_0
        
        # Lógica de cuadrantes
        if deg <= 90:
            return S60._from_raw(raw), 1, 1
        elif deg <= 180:
            # 180 - x
            return S60._from_raw(180 * S60.SCALE_0 - raw), 1, -1
        elif deg <= 270:
            # x - 180
            return S60._from_raw(raw - 180 * S60.SCALE_0), -1, -1
        else:
            # 360 - x
            return S60._from_raw(360 * S60.SCALE_0 - raw), -1, 1

    @staticmethod
    def sin(angle_s60, precision_terms=10):
        """
        Calcula sin(x) mediante Serie de Taylor: x - x^3/3! + x^5/5! - ...
        No usa tablas. Deriva el valor puramente de la potencia y el factorial.
        """
        norm_angle, s_sin, _ = S60Math._normalize_to_pi_half(angle_s60)
        
        # Convertir a "radianes internos" (escalados por SCALE_0)
        # x = deg * (PI/180)
        # En fixed point: (deg_raw * factor_raw) // SCALE_0
        x = (norm_angle._value * S60Math.DEG_TO_RAD_FACTOR._value) // S60.SCALE_0
        
        res = x
        term = x
        x_sq = (x * x) // S60.SCALE_0
        
        for i in range(1, precision_terms):
            # Próximo término: term * (-x^2) / ((2i)*(2i+1))
            n = 2 * i
            denom = n * (n + 1)
            term = -(term * x_sq) // (S60.SCALE_0 * denom)
            
            if term == 0: break
            res += term
            
        return S60._from_raw(res * s_sin)

    @staticmethod
    def cos(angle_s60, precision_terms=10):
        """
        Calcula cos(x) mediante Serie de Taylor: 1 - x^2/2! + x^4/4! - ...
        """
        norm_angle, _, s_cos = S60Math._normalize_to_pi_half(angle_s60)
        
        x = (norm_angle._value * S60Math.DEG_TO_RAD_FACTOR._value) // S60.SCALE_0
        
        res = S60.SCALE_0
        term = S60.SCALE_0
        x_sq = (x * x) // S60.SCALE_0
        
        for i in range(1, precision_terms):
            # Próximo término: term * (-x^2) / ((2i-1)*(2i))
            n = 2 * i
            denom = (n - 1) * n
            term = -(term * x_sq) // (S60.SCALE_0 * denom)
            
            if term == 0: break
            res += term
            
        return S60._from_raw(res * s_cos)

    @staticmethod
    def sqrt(x_s60, iterations=12):
        """
        Calcula sqrt(x) mediante Herón / Newton-Raphson.
        """
        if x_s60._value < 0: raise ValueError("Math Domain Error: sqrt de negativo")
        if x_s60._value == 0: return S60(0)
        
        # Guess inicial (x/2 o algo proporcional)
        g = x_s60._value
        if g > S60.SCALE_0: g //= 2
        
        for _ in range(iterations):
            # g = (g + x/g) / 2
            # x/g escalado: (x_raw * SCALE) // g_raw
            div_part = (x_s60._value * S60.SCALE_0) // g
            g = (g + div_part) // 2
            
        return S60._from_raw(g)

    @staticmethod
    def exp(x_s60, precision_terms=12):
        """
        Calcula e^x mediante Serie de Taylor: 1 + x + x^2/2! + x^3/3! ...
        """
        x = x_s60._value
        res = S60.SCALE_0
        term = S60.SCALE_0
        
        for i in range(1, precision_terms):
            # Próximo término: term * x / i
            term = (term * x) // (S60.SCALE_0 * i)
            if term == 0: break
            res += term
            
        return S60._from_raw(res)

    @staticmethod
    def sin_cos(angle_s60, precision_terms=10):
        """
        Calcula sin(x) y cos(x) simultáneamente para mayor eficiencia.
        """
        return S60Math.sin(angle_s60, precision_terms), S60Math.cos(angle_s60, precision_terms)

    @staticmethod
    def tensor_product(A, B):
        """
        Calcula el producto de Kronecker de dos matrices o vectores representados como listas.
        """
        # Caso 2D: List[List[S60]]
        if isinstance(A, list) and len(A) > 0 and isinstance(A[0], list):
            m, n = len(A), len(A[0])
            p, q = len(B), len(B[0])
            
            res = [[(A[i][j] * B[k][l]) for j in range(n) for l in range(q)] 
                   for i in range(m) for k in range(p)]
            return res
        
        # Caso 1D: List[S60]
        elif isinstance(A, list):
            m = len(A)
            p = len(B)
            res = [(A[i] * B[k]) for i in range(m) for k in range(p)]
            return res
        
        return None


# Alias de utilidad para el sistema
def s60_abs(x): return abs(x)
def s60_compare(a, b):
    if a < b: return -1
    if a > b: return 1
    return 0
