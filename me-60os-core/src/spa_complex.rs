// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ BASE-60 COMPLEX ARITHMETIC - RUST CORE 🛡️
//!
//! Complex numbers using SPA fixed-point arithmetic.
//! Compliant with AI Prime Directives.

use crate::spa::SPA;
use crate::spa_math::SPAMath;
use std::ops::{Add, Div, Mul, Neg, Sub};

#[derive(Clone, Copy, Debug, PartialEq, Eq, Default)]
#[cfg_attr(
    feature = "extension-module",
    pyclass(module = "me60os_core", from_py_object)
)]
pub struct ComplexSPA {
    pub real: SPA,
    pub imag: SPA,
}

impl ComplexSPA {
    pub const fn new(real: SPA, imag: SPA) -> Self {
        Self { real, imag }
    }

    pub fn magnitude(&self) -> SPA {
        SPAMath::sqrt(self.real * self.real + self.imag * self.imag)
    }

    pub fn conjugate(&self) -> Self {
        Self::new(self.real, -self.imag)
    }

    pub fn exp_i_theta(phi: SPA) -> Self {
        Self::new(SPAMath::cos(phi), SPAMath::sin(phi))
    }
}

// --- ARITHMETIC ---

impl Add for ComplexSPA {
    type Output = Self;
    fn add(self, other: Self) -> Self {
        Self::new(self.real + other.real, self.imag + other.imag)
    }
}

impl Sub for ComplexSPA {
    type Output = Self;
    fn sub(self, other: Self) -> Self {
        Self::new(self.real - other.real, self.imag - other.imag)
    }
}

impl Mul for ComplexSPA {
    type Output = Self;
    fn mul(self, other: Self) -> Self {
        let r = (self.real * other.real) - (self.imag * other.imag);
        let i = (self.real * other.imag) + (self.imag * other.real);
        Self::new(r, i)
    }
}

impl Mul<SPA> for ComplexSPA {
    type Output = Self;
    fn mul(self, scalar: SPA) -> Self {
        Self::new(self.real * scalar, self.imag * scalar)
    }
}

impl Div<SPA> for ComplexSPA {
    type Output = Self;
    fn div(self, scalar: SPA) -> Self {
        Self::new(self.real / scalar, self.imag / scalar)
    }
}

impl Neg for ComplexSPA {
    type Output = Self;
    fn neg(self) -> Self {
        Self::new(-self.real, -self.imag)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_complex_add() {
        let a = ComplexSPA::new(SPA::new(1, 0, 0, 0, 0), SPA::new(0, 30, 0, 0, 0));
        let b = ComplexSPA::new(SPA::new(0, 45, 0, 0, 0), SPA::new(1, 15, 0, 0, 0));
        let sum = a + b;
        assert_eq!(sum.real, SPA::new(1, 45, 0, 0, 0));
        assert_eq!(sum.imag, SPA::new(1, 45, 0, 0, 0));
    }
}

// Constantes
pub const I: ComplexSPA = ComplexSPA::new(SPA::new(0, 0, 0, 0, 0), SPA::new(1, 0, 0, 0, 0));
pub const ONE: ComplexSPA = ComplexSPA::new(SPA::new(1, 0, 0, 0, 0), SPA::new(0, 0, 0, 0, 0));

// --- PYO3 PYTHON BINDINGS ---
#[cfg(feature = "extension-module")]
use pyo3::prelude::*;
#[cfg(feature = "extension-module")]
use pyo3::pyclass::CompareOp;

#[cfg(feature = "extension-module")]
#[pymethods]
impl ComplexSPA {
    #[new]
    #[pyo3(signature = (real=SPA::zero(), imag=SPA::zero()))]
    pub fn py_new(real: SPA, imag: SPA) -> PyResult<Self> {
        Ok(Self::new(real, imag))
    }

    #[getter]
    pub fn get_real(&self) -> SPA {
        self.real
    }

    #[getter]
    pub fn get_imag(&self) -> SPA {
        self.imag
    }

    pub fn __add__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        if let Ok(c) = other.extract::<ComplexSPA>() {
            Ok(*self + c)
        } else if let Ok(s) = other.extract::<SPA>() {
            Ok(Self::new(self.real + s, self.imag))
        } else {
            Err(pyo3::exceptions::PyTypeError::new_err(
                "Unsupported operand type for +",
            ))
        }
    }

    pub fn __sub__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        if let Ok(c) = other.extract::<ComplexSPA>() {
            Ok(*self - c)
        } else if let Ok(s) = other.extract::<SPA>() {
            Ok(Self::new(self.real - s, self.imag))
        } else {
            Err(pyo3::exceptions::PyTypeError::new_err(
                "Unsupported operand type for -",
            ))
        }
    }

    pub fn __mul__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        if let Ok(c) = other.extract::<ComplexSPA>() {
            Ok(*self * c)
        } else if let Ok(s) = other.extract::<SPA>() {
            Ok(*self * s)
        } else {
            Err(pyo3::exceptions::PyTypeError::new_err(
                "Unsupported operand type for *",
            ))
        }
    }

    pub fn __truediv__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        if let Ok(c) = other.extract::<ComplexSPA>() {
            let denom = c.real * c.real + c.imag * c.imag;
            let real_part = (self.real * c.real + self.imag * c.imag) / denom;
            let imag_part = (self.imag * c.real - self.real * c.imag) / denom;
            Ok(Self::new(real_part, imag_part))
        } else if let Ok(s) = other.extract::<SPA>() {
            Ok(*self / s)
        } else {
            Err(pyo3::exceptions::PyTypeError::new_err(
                "Unsupported operand type for /",
            ))
        }
    }

    pub fn __neg__(&self) -> Self {
        -*self
    }

    pub fn __abs__(&self) -> SPA {
        self.magnitude()
    }

    pub fn __richcmp__(&self, other: &Bound<'_, PyAny>, op: CompareOp) -> PyResult<bool> {
        match op {
            CompareOp::Eq => {
                if let Ok(c) = other.extract::<ComplexSPA>() {
                    Ok(self.real == c.real && self.imag == c.imag)
                } else if let Ok(s) = other.extract::<SPA>() {
                    Ok(self.real == s && self.imag.to_raw() == 0)
                } else {
                    Ok(false)
                }
            }
            CompareOp::Ne => {
                if let Ok(c) = other.extract::<ComplexSPA>() {
                    Ok(self.real != c.real || self.imag != c.imag)
                } else if let Ok(s) = other.extract::<SPA>() {
                    Ok(self.real != s || self.imag.to_raw() != 0)
                } else {
                    Ok(true)
                }
            }
            _ => Err(pyo3::exceptions::PyTypeError::new_err(
                "Comparison not supported for ComplexSPA",
            )),
        }
    }

    pub fn __repr__(&self) -> String {
        format!("ComplexSPA({}, {})", self.real, self.imag)
    }

    pub fn __str__(&self) -> String {
        if self.imag.to_raw() >= 0 {
            format!("{} + {}i", self.real, self.imag)
        } else {
            format!("{} - {}i", self.real, self.imag.abs())
        }
    }

    pub fn py_conjugate(&self) -> Self {
        self.conjugate()
    }

    pub fn py_magnitude(&self) -> SPA {
        self.magnitude()
    }

    // Phase implies atan2. Not strictly impl since there is no SPAMath::atan2 native yet.
    // For now, it will raise NotImplemented if called from Python wrapper.

    #[staticmethod]
    pub fn py_from_polar(magnitude: SPA, phase: SPA) -> Self {
        let real = magnitude * SPAMath::cos(phase);
        let imag = magnitude * SPAMath::sin(phase);
        Self::new(real, imag)
    }

    #[staticmethod]
    pub fn py_exp_i_theta(theta: SPA) -> Self {
        Self::exp_i_theta(theta)
    }
}
