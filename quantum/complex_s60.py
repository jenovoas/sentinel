#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️

"""
Complex Numbers in S60
======================
Representación de números complejos usando aritmética Base-60.

Un número complejo z = a + bi se representa como ComplexS60(real, imag)
donde real e imag son ambos S60.
"""

from quantum.yatra_core import S60
from quantum.yatra_math import S60Math

class ComplexS60:
    """
    Número complejo en aritmética S60.
    
    z = real + imag*i
    
    Soporta todas las operaciones complejas estándar.
    """
    
    def __init__(self, real: S60, imag: S60 = None):
        """
        Crea un número complejo.
        
        Args:
            real: Parte real (S60)
            imag: Parte imaginaria (S60), default 0
        """
        self.real = real if isinstance(real, S60) else S60(real)
        self.imag = imag if isinstance(imag, S60) else S60(imag if imag is not None else 0)
    
    def __add__(self, other):
        """Suma de complejos: (a+bi) + (c+di) = (a+c) + (b+d)i"""
        if isinstance(other, ComplexS60):
            return ComplexS60(self.real + other.real, self.imag + other.imag)
        elif isinstance(other, S60):
            return ComplexS60(self.real + other, self.imag)
        else:
            return NotImplemented
    
    def __sub__(self, other):
        """Resta de complejos."""
        if isinstance(other, ComplexS60):
            return ComplexS60(self.real - other.real, self.imag - other.imag)
        elif isinstance(other, S60):
            return ComplexS60(self.real - other, self.imag)
        else:
            return NotImplemented
    
    def __mul__(self, other):
        """
        Multiplicación de complejos:
        (a+bi)(c+di) = (ac-bd) + (ad+bc)i
        """
        if isinstance(other, ComplexS60):
            real_part = self.real * other.real - self.imag * other.imag
            imag_part = self.real * other.imag + self.imag * other.real
            return ComplexS60(real_part, imag_part)
        elif isinstance(other, S60):
            return ComplexS60(self.real * other, self.imag * other)
        else:
            return NotImplemented
    
    def __truediv__(self, other):
        """
        División de complejos:
        (a+bi)/(c+di) = [(ac+bd) + (bc-ad)i] / (c²+d²)
        """
        if isinstance(other, ComplexS60):
            denom = other.real * other.real + other.imag * other.imag
            real_part = (self.real * other.real + self.imag * other.imag) / denom
            imag_part = (self.imag * other.real - self.real * other.imag) / denom
            return ComplexS60(real_part, imag_part)
        elif isinstance(other, S60):
            return ComplexS60(self.real / other, self.imag / other)
        else:
            return NotImplemented
    
    def conjugate(self):
        """Conjugado complejo: (a+bi)* = a-bi"""
        return ComplexS60(self.real, -self.imag)
    
    def magnitude(self):
        """Magnitud: |a+bi| = √(a²+b²)"""
        return S60Math.sqrt(self.real * self.real + self.imag * self.imag)
    
    def phase(self):
        """Fase: arg(a+bi) = atan2(b, a)"""
        return S60Math.atan2(self.imag, self.real)
    
    def __abs__(self):
        """Valor absoluto (magnitud)."""
        return self.magnitude()
    
    def __eq__(self, other):
        """Igualdad de complejos."""
        if isinstance(other, ComplexS60):
            return self.real == other.real and self.imag == other.imag
        elif isinstance(other, S60):
            return self.real == other and self.imag == S60(0)
        else:
            return False
    
    def __repr__(self):
        """Representación string."""
        return f"ComplexS60({self.real}, {self.imag})"
    
    def __str__(self):
        """String legible."""
        if self.imag._value >= 0:
            return f"{self.real} + {self.imag}i"
        else:
            return f"{self.real} - {abs(self.imag)}i"
    
    @staticmethod
    def from_polar(magnitude: S60, phase: S60):
        """
        Crea un complejo desde forma polar.
        
        z = r * e^(iθ) = r*cos(θ) + i*r*sin(θ)
        
        Args:
            magnitude: Magnitud r
            phase: Fase θ (en grados)
        """
        real = magnitude * S60Math.cos(phase)
        imag = magnitude * S60Math.sin(phase)
        return ComplexS60(real, imag)
    
    @staticmethod
    def exp_i_theta(theta: S60):
        """
        Calcula e^(iθ) = cos(θ) + i*sin(θ)
        
        Args:
            theta: Ángulo en grados
        """
        return ComplexS60(S60Math.cos(theta), S60Math.sin(theta))


# Constantes útiles
I = ComplexS60(S60(0), S60(1))  # Unidad imaginaria
ONE = ComplexS60(S60(1), S60(0))  # Uno complejo
ZERO = ComplexS60(S60(0), S60(0))  # Cero complejo
