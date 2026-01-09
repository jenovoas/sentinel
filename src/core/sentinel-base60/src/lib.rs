//! # Sentinel Base-60 Mathematics Library
//! 
//! Pure sexagesimal (Base-60) arithmetic for Sentinel Cortex™.
//! 
//! ## AI Prime Directive Compliance
//! 
//! This library enforces **ZERO DECIMAL CONTAMINATION**:
//! - No `f32` or `f64` types allowed in construction
//! - All arithmetic is exact (no floating-point errors)
//! - Automatic normalization maintains canonical form
//! 
//! ## Example
//! 
//! ```
//! use sentinel_base60::S60;
//! 
//! // Create Base-60 values: [degrees; minutes, seconds, thirds, fourths]
//! let a = S60::new(&[0, 30, 0]);  // 30 minutes
//! let b = S60::new(&[0, 45, 0]);  // 45 minutes
//! let sum = a + b;                // 1 degree 15 minutes
//! 
//! assert_eq!(sum, S60::new(&[1, 15, 0]));
//! ```

#[macro_use]
pub mod macros;
pub mod types;

use std::fmt;
use std::ops::{Add, Sub, Mul, Div};

/// Error type for decimal contamination attempts
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DecimalContaminationError {
    message: String,
}

impl DecimalContaminationError {
    pub fn new(msg: impl Into<String>) -> Self {
        Self {
            message: msg.into(),
        }
    }
}

impl fmt::Display for DecimalContaminationError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "CRITICAL: {}", self.message)
    }
}

impl std::error::Error for DecimalContaminationError {}

/// Sexagesimal (Base-60) number representation.
/// 
/// Format: `[degrees, minutes, seconds, thirds, fourths, ...]`
/// 
/// Each component (except degrees) is automatically normalized to 0-59 range.
/// Degrees can be any value (positive or negative).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct S60 {
    components: Vec<i64>,
}

impl S60 {
    /// Create a new S60 value from components.
    /// 
    /// # Arguments
    /// 
    /// * `components` - Slice of i64 values representing [degrees, minutes, seconds, ...]
    /// 
    /// # Example
    /// 
    /// ```
    /// use sentinel_base60::S60;
    /// 
    /// let val = S60::new(&[10, 30, 45]);  // 10 degrees, 30 minutes, 45 seconds
    /// ```
    pub fn new(components: &[i64]) -> Self {
        let mut s60 = Self {
            components: components.to_vec(),
        };
        s60.normalize();
        s60
    }

    /// Create S60 from a single integer (degrees only).
    /// 
    /// # Example
    /// 
    /// ```
    /// use sentinel_base60::S60;
    /// 
    /// let val = S60::from_degrees(42);
    /// assert_eq!(val, S60::new(&[42, 0]));
    /// ```
    pub fn from_degrees(degrees: i64) -> Self {
        Self::new(&[degrees, 0])
    }

    /// **LEGACY IMPORT ONLY**: Convert decimal degrees to S60.
    /// 
    /// ⚠️ **WARNING**: This function accepts floats and should ONLY be used
    /// for importing legacy data. All new code must use integer-based construction.
    /// 
    /// # Arguments
    /// 
    /// * `decimal_val` - Decimal degrees value
    /// 
    /// # Example
    /// 
    /// ```
    /// use sentinel_base60::S60;
    /// 
    /// // ONLY for legacy data import!
    /// let val = S60::from_decimal_FOR_IMPORT_ONLY(10.5);
    /// // 10.5 degrees = 10 degrees, 30 minutes
    /// ```
    pub fn from_decimal_FOR_IMPORT_ONLY(decimal_val: f64) -> Self {
        let d = decimal_val.trunc() as i64;
        let mut rem = (decimal_val - decimal_val.trunc()) * 60.0;
        
        let m = rem.trunc() as i64;
        rem = (rem - rem.trunc()) * 60.0;
        
        let s = rem.trunc() as i64;
        rem = (rem - rem.trunc()) * 60.0;
        
        let t = rem.trunc() as i64;
        rem = (rem - rem.trunc()) * 60.0;
        
        let q = rem.trunc() as i64;
        
        Self::new(&[d, m, s, t, q])
    }

    /// Normalize components to canonical form.
    /// 
    /// Redistributes excess values (>= 60) upward via carry.
    /// Example: [0, 65, 0] becomes [1, 5, 0]
    fn normalize(&mut self) {
        if self.components.is_empty() {
            self.components = vec![0, 0];
            return;
        }

        // Ensure at least 2 components (degrees, minutes)
        if self.components.len() == 1 {
            self.components.push(0);
        }

        // Process from least significant to most significant
        for i in (1..self.components.len()).rev() {
            let val = self.components[i];
            let carry = val.div_euclid(60);
            let remainder = val.rem_euclid(60);
            
            self.components[i] = remainder;
            self.components[i - 1] += carry;
        }

        // Remove trailing zeros (except keep at least 2 components)
        while self.components.len() > 2 && self.components.last() == Some(&0) {
            self.components.pop();
        }
    }

    /// Get the number of components.
    pub fn len(&self) -> usize {
        self.components.len()
    }

    /// Check if empty (should never be true after construction).
    pub fn is_empty(&self) -> bool {
        self.components.is_empty()
    }

    /// Get a component by index.
    pub fn get(&self, index: usize) -> Option<i64> {
        self.components.get(index).copied()
    }

    /// Get degrees (first component).
    pub fn degrees(&self) -> i64 {
        self.components.get(0).copied().unwrap_or(0)
    }

    /// Get minutes (second component).
    pub fn minutes(&self) -> i64 {
        self.components.get(1).copied().unwrap_or(0)
    }

    /// Get seconds (third component).
    pub fn seconds(&self) -> i64 {
        self.components.get(2).copied().unwrap_or(0)
    }
}

// Display implementation: S60[DDD; MM, SS, TT, QQ]
impl fmt::Display for S60 {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if self.components.is_empty() {
            return write!(f, "S60[00; 00]");
        }

        let deg = self.components.get(0).copied().unwrap_or(0);
        
        if self.components.len() == 1 {
            return write!(f, "S60[{:03}; 00]", deg);
        }

        let sexagesimals: Vec<String> = self.components[1..]
            .iter()
            .map(|c| format!("{:02}", c))
            .collect();
        
        write!(f, "S60[{:03}; {}]", deg, sexagesimals.join(", "))
    }
}

// Addition: S60 + S60
impl Add for S60 {
    type Output = Self;

    fn add(self, other: Self) -> Self {
        let max_len = self.components.len().max(other.components.len());
        
        let mut result = Vec::with_capacity(max_len);
        for i in 0..max_len {
            let a = self.components.get(i).copied().unwrap_or(0);
            let b = other.components.get(i).copied().unwrap_or(0);
            result.push(a + b);
        }
        
        Self::new(&result)
    }
}

// Addition by reference
impl Add for &S60 {
    type Output = S60;

    fn add(self, other: Self) -> S60 {
        self.clone() + other.clone()
    }
}

// Subtraction: S60 - S60
impl Sub for S60 {
    type Output = Self;

    fn sub(self, other: Self) -> Self {
        let max_len = self.components.len().max(other.components.len());
        
        let mut result = Vec::with_capacity(max_len);
        for i in 0..max_len {
            let a = self.components.get(i).copied().unwrap_or(0);
            let b = other.components.get(i).copied().unwrap_or(0);
            result.push(a - b);
        }
        
        Self::new(&result)
    }
}

// Subtraction by reference
impl Sub for &S60 {
    type Output = S60;

    fn sub(self, other: Self) -> S60 {
        self.clone() - other.clone()
    }
}

// Scalar multiplication: S60 * i64
impl Mul<i64> for S60 {
    type Output = Self;

    fn mul(self, scalar: i64) -> Self {
        let result: Vec<i64> = self.components
            .iter()
            .map(|c| c * scalar)
            .collect();
        
        Self::new(&result)
    }
}

// Scalar multiplication by reference
impl Mul<i64> for &S60 {
    type Output = S60;

    fn mul(self, scalar: i64) -> S60 {
        self.clone() * scalar
    }
}

// Floor division: S60 / i64
impl Div<i64> for S60 {
    type Output = Self;

    fn div(self, divisor: i64) -> Self {
        if divisor == 0 {
            panic!("Division by zero");
        }

        let mut result_comps = Vec::new();
        let mut remainder: i64 = 0;

        for comp in &self.components {
            // Bring down current component + remainder from previous level (× 60)
            let val = comp + (remainder * 60);
            
            let res = val.div_euclid(divisor);
            remainder = val.rem_euclid(divisor);
            
            result_comps.push(res);
        }

        // If there's a remainder, we could expand to more precision levels
        // For now, we maintain the same precision as the input
        Self::new(&result_comps)
    }
}

// Floor division by reference
impl Div<i64> for &S60 {
    type Output = S60;

    fn div(self, divisor: i64) -> S60 {
        self.clone() / divisor
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_creation() {
        let val = S60::new(&[10, 30, 45]);
        assert_eq!(val.degrees(), 10);
        assert_eq!(val.minutes(), 30);
        assert_eq!(val.seconds(), 45);
    }

    #[test]
    fn test_normalization_carry() {
        // 65 seconds should become 1 minute 5 seconds
        let val = S60::new(&[0, 0, 65]);
        assert_eq!(val.degrees(), 0);
        assert_eq!(val.minutes(), 1);
        assert_eq!(val.seconds(), 5);
    }

    #[test]
    fn test_normalization_multiple_carries() {
        // 0 degrees, 65 minutes, 70 seconds
        // = 0 degrees, 66 minutes, 10 seconds (after first carry)
        // = 1 degree, 6 minutes, 10 seconds (after second carry)
        let val = S60::new(&[0, 65, 70]);
        assert_eq!(val.degrees(), 1);
        assert_eq!(val.minutes(), 6);
        assert_eq!(val.seconds(), 10);
    }

    #[test]
    fn test_addition() {
        let a = S60::new(&[0, 30, 0]);  // 30 minutes
        let b = S60::new(&[0, 45, 0]);  // 45 minutes
        let sum = a + b;
        
        assert_eq!(sum.degrees(), 1);
        assert_eq!(sum.minutes(), 15);
    }

    #[test]
    fn test_subtraction() {
        let a = S60::new(&[1, 15, 0]);  // 1 degree 15 minutes
        let b = S60::new(&[0, 30, 0]);  // 30 minutes
        let diff = a - b;
        
        assert_eq!(diff.degrees(), 0);
        assert_eq!(diff.minutes(), 45);
    }

    #[test]
    fn test_scalar_multiplication() {
        let val = S60::new(&[0, 10, 0]);  // 10 minutes
        let result = val * 6;              // 60 minutes = 1 degree
        
        assert_eq!(result.degrees(), 1);
        assert_eq!(result.minutes(), 0);
    }

    #[test]
    fn test_floor_division() {
        let val = S60::new(&[1, 0, 0]);  // 1 degree
        let result = val / 2;             // 0.5 degrees = 30 minutes
        
        assert_eq!(result.degrees(), 0);
        assert_eq!(result.minutes(), 30);
    }

    #[test]
    fn test_display() {
        let val = S60::new(&[10, 30, 45]);
        assert_eq!(format!("{}", val), "S60[010; 30, 45]");
    }
}
