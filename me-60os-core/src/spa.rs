// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ BASE-60 FIXED-POINT: RUST CORE 🛡️
//!
//! Pure sexagesimal arithmetic for ME-60OS.
//! Implementation: Zero-allocation, fixed-point (60^4 scaling).
//! Compliant with AI Prime Directives: ZERO DECIMAL CONTAMINATION.
//!
//! REVIEW: wrapping_* reemplazado por checked_* para detectar overflow.
//!         to_raw() ya no clampea silenciosamente.
//!         two_pi() ahora es fn constante y consistente con SPAMath::TWO_PI.

use serde::{Deserialize, Serialize};
use std::fmt;
use std::ops::{Add, Div, Mul, Neg, Rem, Sub};

#[cfg(feature = "extension-module")]
use pyo3::prelude::*;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[cfg_attr(
    feature = "extension-module",
    pyclass(module = "me60os_core", eq, eq_int, from_py_object)
)]
pub enum SPAError {
    DivisionByZero,
}

impl std::fmt::Display for SPAError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            SPAError::DivisionByZero => write!(f, "SPA Division by zero"),
        }
    }
}

impl std::error::Error for SPAError {}

/// Sexagesimal (Base-60) Fixed-Point Number.
#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Default, Serialize, Deserialize)]
#[cfg_attr(
    feature = "extension-module",
    pyclass(module = "me60os_core", from_py_object)
)]
pub struct SPA {
    pub components: [i64; 5],
}

impl SPA {
    pub const SCALE_0: i64 = 12_960_000; // 60^4
    pub const SCALE_1: i64 = 216_000; // 60^3
    pub const SCALE_2: i64 = 3_600; // 60^2
    pub const SCALE_3: i64 = 60; // 60^1
    pub const SCALE_4: i64 = 1; // 60^0

    pub const ZERO: SPA = SPA { components: [0; 5] };
    pub const ONE: SPA = SPA {
        components: [1, 0, 0, 0, 0],
    };

    pub const fn new(d: i64, m: i64, s: i64, t: i64, q: i64) -> Self {
        Self {
            components: [d, m, s, t, q],
        }
    }

    pub fn from_raw(raw: i64) -> Self {
        let sign = if raw < 0 { -1 } else { 1 };
        let mut val = raw.abs();
        let q = val % 60;
        val /= 60;
        let t = val % 60;
        val /= 60;
        let s = val % 60;
        val /= 60;
        let m = val % 60;
        val /= 60;
        let d = val;
        Self {
            components: [d * sign, m * sign, s * sign, t * sign, q * sign],
        }
    }

    pub fn from_int(i: i64) -> Self {
        Self::from_raw(i * Self::SCALE_0)
    }
    pub fn from_base_units(raw: i64) -> Self {
        Self::from_raw(raw)
    }
    // REVIEW: consistente con SPAMath::TWO_PI (antes era 6,16,59,27,43 — off by 17 quartae)
    pub const TWO_PI: SPA = SPA::new(6, 16, 59, 28, 0);
    pub const fn two_pi() -> Self {
        Self::TWO_PI
    }
    pub const fn zero() -> Self {
        Self::ZERO
    }
    pub const fn one() -> Self {
        Self::ONE
    }
    pub fn abs(&self) -> Self {
        Self::from_raw(self.to_raw().abs())
    }

    pub fn to_raw(&self) -> i64 {
        let raw_128 = (self.components[0] as i128 * Self::SCALE_0 as i128)
            + (self.components[1] as i128 * Self::SCALE_1 as i128)
            + (self.components[2] as i128 * Self::SCALE_2 as i128)
            + (self.components[3] as i128 * Self::SCALE_3 as i128)
            + (self.components[4] as i128 * Self::SCALE_4 as i128);
        // REVIEW: se eliminó clamp silencioso — panic si overflow real (defense-in-depth)
        i64::try_from(raw_128).expect("SPA to_raw overflow: componentes exceden i64")
    }

    pub fn to_degrees(&self) -> i64 {
        self.components[0]
    }
    pub fn to_components(&self) -> [i64; 5] {
        self.components
    }
    pub fn from_legacy_tertia(tertia: i64) -> Self {
        Self::from_raw(tertia * 60)
    }
    pub fn to_legacy_tertia(&self) -> i64 {
        self.to_raw() / 60
    }
    pub fn from_decimal_for_import_only(decimal: f64) -> Self {
        let raw = (decimal * Self::SCALE_0 as f64).round() as i64;
        Self::from_raw(raw)
    }
}

// --- ARITHMETIC ---
// REVIEW: wrapping_* reemplazado por checked_* con panic explícito en overflow
//         para sistema de tiempo cuántico donde overflow = pérdida de coherencia
impl Add for SPA {
    type Output = Self;
    fn add(self, other: Self) -> Self {
        let raw = self
            .to_raw()
            .checked_add(other.to_raw())
            .expect("SPA overflow en add");
        Self::from_raw(raw)
    }
}

impl Sub for SPA {
    type Output = Self;
    fn sub(self, other: Self) -> Self {
        let raw = self
            .to_raw()
            .checked_sub(other.to_raw())
            .expect("SPA overflow en sub");
        Self::from_raw(raw)
    }
}

impl Mul<i64> for SPA {
    type Output = Self;
    fn mul(self, scalar: i64) -> Self {
        let raw = self
            .to_raw()
            .checked_mul(scalar)
            .expect("SPA overflow en mul escalar");
        Self::from_raw(raw)
    }
}

impl Mul for SPA {
    type Output = Self;
    fn mul(self, other: Self) -> Self {
        let v1 = self.to_raw() as i128;
        let v2 = other.to_raw() as i128;
        Self::from_raw(((v1 * v2) / Self::SCALE_0 as i128) as i64)
    }
}

impl Div<i64> for SPA {
    type Output = Self;
    fn div(self, divisor: i64) -> Self {
        if divisor == 0 {
            panic!("SPA Division by zero (scalar)");
        }
        Self::from_raw(self.to_raw() / divisor)
    }
}

impl Div for SPA {
    type Output = Self;
    fn div(self, other: Self) -> Self {
        let v2 = other.to_raw();
        if v2 == 0 {
            panic!("SPA Division by zero");
        }
        let v1 = self.to_raw() as i128;
        Self::from_raw(((v1 * Self::SCALE_0 as i128) / v2 as i128) as i64)
    }
}

impl SPA {
    pub fn div_safe(&self, other: Self) -> Result<Self, SPAError> {
        let v2 = other.to_raw();
        if v2 == 0 {
            return Err(SPAError::DivisionByZero);
        }
        let v1 = self.to_raw() as i128;
        Ok(Self::from_raw(
            ((v1 * Self::SCALE_0 as i128) / v2 as i128) as i64,
        ))
    }
}

impl Rem<i64> for SPA {
    type Output = Self;
    fn rem(self, rhs: i64) -> Self::Output {
        Self::from_raw(self.to_raw() % (rhs * Self::SCALE_0))
    }
}

impl Rem for SPA {
    type Output = Self;
    fn rem(self, rhs: Self) -> Self::Output {
        Self::from_raw(self.to_raw() % rhs.to_raw())
    }
}

impl Neg for SPA {
    type Output = Self;
    fn neg(self) -> Self {
        Self::from_raw(-self.to_raw())
    }
}

// --- FORMATTING ---
impl fmt::Display for SPA {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let raw = self.to_raw();
        let sign = if raw < 0 { "-" } else { "" };
        let c = self.abs().components;
        write!(
            f,
            "SPA[{}{:03}; {:02}, {:02}, {:02}, {:02}]",
            sign, c[0], c[1], c[2], c[3], c[4]
        )
    }
}

impl fmt::Debug for SPA {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self)
    }
}

#[cfg(feature = "extension-module")]
#[pymethods]
impl SPA {
    #[new]
    #[pyo3(signature = (d=0, m=0, s=0, t=0, q=0))]
    pub fn py_new(d: i64, m: i64, s: i64, t: i64, q: i64) -> PyResult<Self> {
        Ok(Self::new(d, m, s, t, q))
    }
    #[staticmethod]
    pub fn _from_raw(raw: i64) -> Self {
        Self::from_raw(raw)
    }
    pub fn to_base_units(&self) -> i64 {
        self.to_raw()
    }
    pub fn __repr__(&self) -> String {
        format!("{}", self)
    }
    pub fn __add__(&self, other: &SPA) -> Self {
        *self + *other
    }
    pub fn __sub__(&self, other: &SPA) -> Self {
        *self - *other
    }

    pub fn __mul__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        if let Ok(spa) = other.extract::<SPA>() {
            Ok(*self * spa)
        } else if let Ok(scalar) = other.extract::<i64>() {
            Ok(*self * scalar)
        } else {
            Err(pyo3::exceptions::PyTypeError::new_err(
                "Invalid multiplication",
            ))
        }
    }

    pub fn __truediv__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        let divisor_raw = if let Ok(spa) = other.extract::<SPA>() {
            spa.to_raw()
        } else if let Ok(scalar) = other.extract::<i64>() {
            scalar * Self::SCALE_0
        } else {
            return Err(pyo3::exceptions::PyTypeError::new_err(
                "Invalid division type",
            ));
        };

        if divisor_raw == 0 {
            return Err(pyo3::exceptions::PyZeroDivisionError::new_err(
                "SPA Division by zero",
            ));
        }

        // Compute directly to avoid trait Result vs SPA confusion here
        let v1 = self.to_raw() as i128;
        Ok(Self::from_raw(
            ((v1 * Self::SCALE_0 as i128) / divisor_raw as i128) as i64,
        ))
    }

    pub fn __neg__(&self) -> Self {
        -*self
    }
    pub fn __abs__(&self) -> Self {
        self.abs()
    }

    #[pyo3(name = "to_raw")]
    pub fn py_to_raw(&self) -> i64 {
        self.to_raw()
    }
}
