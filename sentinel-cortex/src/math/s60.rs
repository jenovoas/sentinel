// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/math/s60.rs
//! S60: Sovereign Base-60 Fixed-Point Arithmetic
//!
//! Implements strict Base-60 math to adhere to Axiom I.
//! Precision: 1 Degree = 60 Minutes = 3600 Seconds = 216,000 Tertia = 12,960,000 Quarta
//!
//! Internal Representation: i64 representing "Quarta" (1/12,960,000 of a Unit)
//! Scale matches SPA (me-60os-core/src/spa.rs). Exact precision for 10;5,6,5 patterns,
//! harmonic ratios, and full 60⁴ sexagesimal arithmetic.
//!
//! ## References
//! - [P-RES] Novoa, J. (2026). *Investigación: Aritmética Sexagesimal como Base de Sistemas.*
//!   `docs/02_ciencia_y_quantum/RESEARCH_es.md` — tipo S60 base, escala 60⁴ = 12,960,000 quartas.
//! - [EXT-MAN] Mansfield, D. F. & Wildberger, N. J. (2017).
//!   *Plimpton 322 is Babylonian exact sexagesimal trigonometry.* Historia Mathematica.
//!   https://doi.org/10.1016/j.hm.2017.08.001 — fundamento histórico de la aritmética exacta base-60.

#![allow(dead_code)]

use serde::{Deserialize, Serialize};
use std::fmt;
use std::ops::{Add, Div, Mul, Neg, Sub};

#[derive(Debug, Clone)]
pub enum S60Error {
    Overflow,
    DivisionByZero,
    ComponentOutOfRange(String),
}

/// The Holy S60 Type
/// Value is stored in "Quarta" (fourth sexagesimal place)
/// 1 Unit = 60^4 = 12,960,000 Quarta
/// Matches SPA scale from me-60os-core/src/spa.rs — zero-incompatibility eliminated.
#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
pub struct S60 {
    pub _value: i64,
}

impl S60 {
    // Scales — aligned with SPA (60⁴)
    pub const SCALE_0: i64 = 12_960_000; // 60^4 — 1.0
    pub const SCALE_1: i64 = 216_000;    // 60^3 — 1/60 (Minute)
    pub const SCALE_2: i64 = 3_600;      // 60^2 — 1/3600 (Second)
    pub const SCALE_3: i64 = 60;         // 60^1 — 1/216000 (Tertia)
    pub const SCALE_4: i64 = 1;          // 60^0 — 1/12960000 (Quarta)

    pub const ZERO: S60 = S60 { _value: 0 };
    pub const ONE: S60 = S60 { _value: 12_960_000 };

    /// Create new S60 from components
    /// d: Degrees (Units)
    /// m: Minutes (1/60)
    /// s: Seconds (1/3600)
    /// t: Tertia (1/216000)
    /// q: Quarta (1/12960000)
    pub fn new(d: i32, m: u8, s: u8, t: u8, q: u8) -> Result<Self, S60Error> {
        if m >= 60 || s >= 60 || t >= 60 || q >= 60 {
            return Err(S60Error::ComponentOutOfRange(
                "Sexagesimal components must be < 60".into(),
            ));
        }

        let total = (d as i64 * Self::SCALE_0)
            + (m as i64 * Self::SCALE_1)
            + (s as i64 * Self::SCALE_2)
            + (t as i64 * Self::SCALE_3)
            + (q as i64 * Self::SCALE_4);

        Ok(S60 {
            _value: total,
        })
    }

    /// Raw constructor (Internal use only)
    pub fn from_raw(raw: i64) -> Self {
        S60 { _value: raw }
    }

    pub fn to_base_units(&self) -> i64 {
        self._value
    }

    pub fn abs(&self) -> Self {
        S60 {
            _value: self._value.abs(),
        }
    }

    /// Convenience: S60::zero()
    pub fn zero() -> Self {
        S60::ZERO
    }

    /// Convenience: S60::one()
    pub fn one() -> Self {
        S60::ONE
    }

    /// Create S60 from integer (e.g., S60::from_int(3) = 3;0,0,0,0)
    pub fn from_int(i: i32) -> Self {
        S60 {
            _value: (i as i64) * S60::SCALE_0,
        }
    }

    /// Common constant: 2π (6.283185307... ≈ 6;16,59,28,0)
    /// Matches SPA::TWO_PI exactly.
    pub fn two_pi() -> Self {
        S60::new(6, 16, 59, 28, 0).unwrap()
    }

    /// Create S60 from base units (tertia)
    pub fn from_base_units(raw: i64) -> Self {
        S60 { _value: raw }
    }

    /// Get components (for display/telemetry) — 4 sexagesimal places
    pub fn to_components(&self) -> (i32, u8, u8, u8, u8) {
        let sign = if self._value < 0 { -1 } else { 1 };
        let abs_val = self._value.abs();

        let d = (abs_val / S60::SCALE_0) as i32 * sign;
        let rem_d = abs_val % S60::SCALE_0;

        let m = (rem_d / S60::SCALE_1) as u8;
        let rem_m = rem_d % S60::SCALE_1;

        let s = (rem_m / S60::SCALE_2) as u8;
        let rem_s = rem_m % S60::SCALE_2;

        let t = (rem_s / S60::SCALE_3) as u8;
        let q = (rem_s % S60::SCALE_3) as u8;

        (d, m, s, t, q)
    }
}

// FORMATTING (Sexagesimal Output — 4 places, matching SPA)
impl fmt::Debug for S60 {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let sign = if self._value < 0 { "-" } else { "" };
        let abs_val = self._value.abs();

        let d = abs_val / S60::SCALE_0;
        let rem_d = abs_val % S60::SCALE_0;

        let m = (rem_d / S60::SCALE_1) as u8;
        let rem_m = rem_d % S60::SCALE_1;

        let s = (rem_m / S60::SCALE_2) as u8;
        let rem_s = rem_m % S60::SCALE_2;

        let t = (rem_s / S60::SCALE_3) as u8;
        let q = (rem_s % S60::SCALE_3) as u8;

        write!(f, "S60[{}{}; {:02}, {:02}, {:02}, {:02}]", sign, d, m, s, t, q)
    }
}

impl fmt::Display for S60 {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        fmt::Debug::fmt(self, f)
    }
}

// ARITHMETIC OPERATORS

impl Add for S60 {
    type Output = S60;
    fn add(self, other: S60) -> S60 {
        S60 {
            _value: self._value + other._value,
        }
    }
}

impl Sub for S60 {
    type Output = S60;
    fn sub(self, other: S60) -> S60 {
        S60 {
            _value: self._value - other._value,
        }
    }
}

impl Mul for S60 {
    type Output = S60;
    fn mul(self, other: S60) -> S60 {
        // Multiply: (A/S * B/S) = (A*B)/(S*S). We want result/S.
        // So we do (A*B)/S.
        // Use i128 to prevent overflow during intermediate calc
        let product = (self._value as i128 * other._value as i128) / S60::SCALE_0 as i128;
        S60 {
            _value: product as i64,
        }
    }
}

impl Div for S60 {
    type Output = Result<S60, S60Error>;
    fn div(self, other: S60) -> Result<S60, S60Error> {
        if other._value == 0 {
            return Err(S60Error::DivisionByZero);
        }
        // Division: (A/S) / (B/S) = A/B. We want result/S.
        // So we do (A * S) / B.
        let scaled_numerator = self._value as i128 * S60::SCALE_0 as i128;
        let quotient = scaled_numerator / other._value as i128;
        Ok(S60 {
            _value: quotient as i64,
        })
    }
}

impl Neg for S60 {
    type Output = S60;
    fn neg(self) -> S60 {
        S60 {
            _value: -self._value,
        }
    }
}
