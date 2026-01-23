// src/math/s60.rs
//! S60: Sovereign Base-60 Fixed-Point Arithmetic
//!
//! Implements strict Base-60 math to adhere to Axiom I.
//! Precision: 1 Degree = 60 Minutes = 3600 Seconds = 216,000 Tertia
//!
//! Internal Representation: i64 representing "Tertia" (1/216,000 of a Unit)
//! This gives us exact precision for 10;5,6,5 patterns and harmonic ratios.

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
/// Value is stored in "Tertia" (Thirds)
/// 1 Unit = 60 * 60 * 60 = 216,000 Tertia
#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
pub struct S60 {
    pub _value: i64,
}

impl S60 {
    // Scales
    pub const SCALE_0: i64 = 216_000; // 1.0
    pub const SCALE_1: i64 = 3_600; // 1/60 (Minute)
    pub const SCALE_2: i64 = 60; // 1/3600 (Second)
    pub const SCALE_3: i64 = 1; // 1/216000 (Tertia)

    pub const ZERO: S60 = S60 { _value: 0 };
    pub const ONE: S60 = S60 { _value: 216_000 };

    /// Create new S60 from components
    /// d: Degrees (Units)
    /// m: Minutes (1/60)
    /// s: Seconds (1/3600)
    /// t: Tertia (1/216000)
    /// q: Quarta (ignored/rounded for now, or added if we expand)
    pub fn new(d: i32, m: u8, s: u8, t: u8, _q: u8) -> Result<Self, S60Error> {
        if m >= 60 || s >= 60 || t >= 60 {
            return Err(S60Error::ComponentOutOfRange(
                "Sexagesimal components must be < 60".into(),
            ));
        }

        let total_tertia = (d as i64 * Self::SCALE_0)
            + (m as i64 * Self::SCALE_1)
            + (s as i64 * Self::SCALE_2)
            + (t as i64 * Self::SCALE_3);

        Ok(S60 {
            _value: total_tertia,
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
}

// FORMATTING (Sexagesimal Output)
impl fmt::Debug for S60 {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let sign = if self._value < 0 { "-" } else { "" };
        let abs_val = self._value.abs();

        let d = abs_val / S60::SCALE_0;
        let rem_d = abs_val % S60::SCALE_0;

        let m = rem_d / S60::SCALE_1;
        let rem_m = rem_d % S60::SCALE_1;

        let s = rem_m / S60::SCALE_2;
        let t = rem_m % S60::SCALE_2;

        write!(f, "S60[{}{}; {:02}, {:02}, {:02}]", sign, d, m, s, t)
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
