// src/math/s60.rs
//! Base-60 Fixed-Point Arithmetic (Yatra Protocol)
//!
//! Pure integer implementation of sexagesimal mathematics.
//! Equivalent to Python's yatra_core.py but in Rust for performance.
//!
//! Internal representation: i64 in units of 1/60^4
//! Scale: 60^4 = 12,960,000
//!
//! NO FLOATS ALLOWED - Yatra Protocol Enforcement

use serde::{Deserialize, Serialize};
use std::fmt;
use std::ops::{Add, Div, Mul, Neg, Sub};

/// Base-60 fixed-point number
///
/// Format: [d; m, s, t, q] where:
/// - d: degrees (any integer)
/// - m, s, t, q: 0-59 (minutes, seconds, thirds, fourths)
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct S60 {
    value: i64, // Internal value in units of 1/60^4
}

#[derive(Debug, Clone)]
pub enum S60Error {
    ComponentOutOfRange(String),
    DivisionByZero,
    Overflow,
}

impl fmt::Display for S60Error {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            S60Error::ComponentOutOfRange(msg) => write!(f, "Component out of range: {}", msg),
            S60Error::DivisionByZero => write!(f, "Division by zero"),
            S60Error::Overflow => write!(f, "Arithmetic overflow"),
        }
    }
}

impl std::error::Error for S60Error {}

impl S60 {
    // Base-60 scale constants (pre-calculated, immutable)
    pub const SCALE_0: i64 = 12_960_000; // 60^4 (degrees)
    pub const SCALE_1: i64 = 216_000; // 60^3 (minutes)
    pub const SCALE_2: i64 = 3_600; // 60^2 (seconds)
    pub const SCALE_3: i64 = 60; // 60^1 (thirds)
    pub const SCALE_4: i64 = 1; // 60^0 (fourths)

    /// Create S60 from sexagesimal components
    ///
    /// # Arguments
    /// * `d` - Degrees (any integer)
    /// * `m` - Minutes (0-59)
    /// * `s` - Seconds (0-59)
    /// * `t` - Thirds (0-59)
    /// * `q` - Fourths (0-59)
    pub fn new(d: i32, m: u8, s: u8, t: u8, q: u8) -> Result<Self, S60Error> {
        // Validate sub-degree components are in range [0, 59]
        if m >= 60 {
            return Err(S60Error::ComponentOutOfRange(format!("Minutes: {}", m)));
        }
        if s >= 60 {
            return Err(S60Error::ComponentOutOfRange(format!("Seconds: {}", s)));
        }
        if t >= 60 {
            return Err(S60Error::ComponentOutOfRange(format!("Thirds: {}", t)));
        }
        if q >= 60 {
            return Err(S60Error::ComponentOutOfRange(format!("Fourths: {}", q)));
        }

        // Calculate internal value (BASE-60 PURE MATH)
        let value = (d as i64) * Self::SCALE_0
            + (m as i64) * Self::SCALE_1
            + (s as i64) * Self::SCALE_2
            + (t as i64) * Self::SCALE_3
            + (q as i64) * Self::SCALE_4;

        Ok(S60 { value })
    }

    /// Create S60 from raw internal value (for internal use)
    pub(crate) fn from_raw(value: i64) -> Self {
        S60 { value }
    }

    /// Get internal value in base units
    pub fn to_base_units(&self) -> i64 {
        self.value
    }

    /// Extract sexagesimal components
    /// Returns (d, m, s, t, q)
    pub fn to_components(&self) -> (i32, u8, u8, u8, u8) {
        let mut val = self.value.abs();
        let sign = if self.value < 0 { -1 } else { 1 };

        let d = (val / Self::SCALE_0) as i32 * sign;
        val %= Self::SCALE_0;

        let m = (val / Self::SCALE_1) as u8;
        val %= Self::SCALE_1;

        let s = (val / Self::SCALE_2) as u8;
        val %= Self::SCALE_2;

        let t = (val / Self::SCALE_3) as u8;
        val %= Self::SCALE_3;

        let q = val as u8;

        (d, m, s, t, q)
    }

    /// Absolute value
    pub fn abs(&self) -> Self {
        S60 {
            value: self.value.abs(),
        }
    }

    /// Clamp value between min and max
    pub fn clamp(&self, min: S60, max: S60) -> S60 {
        if self.value < min.value {
            min
        } else if self.value > max.value {
            max
        } else {
            *self
        }
    }

    /// Zero constant
    pub const ZERO: S60 = S60 { value: 0 };

    /// One constant (1 degree)
    pub const ONE: S60 = S60 {
        value: Self::SCALE_0,
    };
}

// Arithmetic Operations

impl Add for S60 {
    type Output = S60;

    fn add(self, other: S60) -> S60 {
        S60 {
            value: self.value + other.value,
        }
    }
}

impl Sub for S60 {
    type Output = S60;

    fn sub(self, other: S60) -> S60 {
        S60 {
            value: self.value - other.value,
        }
    }
}

impl Mul<i32> for S60 {
    type Output = S60;

    fn mul(self, scalar: i32) -> S60 {
        S60 {
            value: self.value * (scalar as i64),
        }
    }
}

impl Mul<S60> for S60 {
    type Output = S60;

    /// S60 * S60: multiply and re-scale
    fn mul(self, other: S60) -> S60 {
        let result = (self.value * other.value) / Self::SCALE_0;
        S60 { value: result }
    }
}

impl Div<i32> for S60 {
    type Output = Result<S60, S60Error>;

    fn div(self, divisor: i32) -> Result<S60, S60Error> {
        if divisor == 0 {
            return Err(S60Error::DivisionByZero);
        }
        Ok(S60 {
            value: self.value / (divisor as i64),
        })
    }
}

impl Div<S60> for S60 {
    type Output = Result<S60, S60Error>;

    /// S60 / S60: divide with re-scaling and rounding
    fn div(self, divisor: S60) -> Result<S60, S60Error> {
        if divisor.value == 0 {
            return Err(S60Error::DivisionByZero);
        }

        let num = self.value * Self::SCALE_0;
        let den = divisor.value;

        // Rounding: add half divisor before dividing
        let sign = if (num ^ den) >= 0 { 1 } else { -1 };
        let result = (num.abs() + den.abs() / 2) / den.abs();

        Ok(S60 {
            value: result * sign,
        })
    }
}

impl Neg for S60 {
    type Output = S60;

    fn neg(self) -> S60 {
        S60 { value: -self.value }
    }
}

// Display

impl fmt::Display for S60 {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let (d, m, s, t, q) = self.to_components();
        let sign = if d < 0 { "-" } else { "" };
        write!(
            f,
            "S60[{}{:03}; {:02}, {:02}, {:02}, {:02}]",
            sign,
            d.abs(),
            m,
            s,
            t,
            q
        )
    }
}

// Serialization for API compatibility

impl Serialize for S60 {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        serializer.serialize_str(&self.to_string())
    }
}

impl<'de> Deserialize<'de> for S60 {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        let s = String::deserialize(deserializer)?;
        // Parse "S60[ddd; mm, ss, tt, qq]" format
        // For now, just return zero (implement parser if needed)
        Ok(S60::ZERO)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_construction() {
        let a = S60::new(10, 0, 0, 0, 0).unwrap();
        assert_eq!(a.value, 10 * S60::SCALE_0);
    }

    #[test]
    fn test_arithmetic() {
        let a = S60::new(10, 0, 0, 0, 0).unwrap();
        let b = S60::new(5, 0, 0, 0, 0).unwrap();

        let sum = a + b;
        assert_eq!(sum, S60::new(15, 0, 0, 0, 0).unwrap());

        let diff = a - b;
        assert_eq!(diff, S60::new(5, 0, 0, 0, 0).unwrap());

        let prod = a * 2;
        assert_eq!(prod, S60::new(20, 0, 0, 0, 0).unwrap());
    }

    #[test]
    fn test_component_validation() {
        assert!(S60::new(0, 60, 0, 0, 0).is_err());
        assert!(S60::new(0, 0, 60, 0, 0).is_err());
        assert!(S60::new(0, 0, 0, 60, 0).is_err());
        assert!(S60::new(0, 0, 0, 0, 60).is_err());
    }

    #[test]
    fn test_to_components() {
        let a = S60::new(1, 30, 0, 0, 0).unwrap();
        let (d, m, s, t, q) = a.to_components();
        assert_eq!((d, m, s, t, q), (1, 30, 0, 0, 0));
    }

    #[test]
    fn test_comparison() {
        let a = S60::new(10, 0, 0, 0, 0).unwrap();
        let b = S60::new(5, 0, 0, 0, 0).unwrap();
        assert!(a > b);
        assert!(b < a);
    }
}
