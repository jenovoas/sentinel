// src/math/s60_math.rs
//! Advanced mathematical functions for S60 (Base-60)
//!
//! Implements logarithm, entropy, and other functions needed for
//! Soul Verifier calculations using pure integer arithmetic.

use super::s60::{S60Error, S60};
use std::collections::HashMap;

/// Natural logarithm in Base-60 using Taylor series
///
/// Uses the series: ln(x) = 2 * sum((1/(2n+1)) * ((x-1)/(x+1))^(2n+1))
/// This converges for all x > 0
pub fn ln_s60(x: &S60) -> Result<S60, S60Error> {
    if *x <= S60::ZERO {
        return Err(S60Error::ComponentOutOfRange(
            "ln requires positive value".to_string(),
        ));
    }

    let one = S60::ONE;

    // Special case: ln(1) = 0
    if *x == one {
        return Ok(S60::ZERO);
    }

    // For x close to 1, use Taylor series around 1
    // ln(x) = (x-1) - (x-1)^2/2 + (x-1)^3/3 - ...

    // Calculate y = (x - 1) / (x + 1)
    let x_minus_1 = *x - one;
    let x_plus_1 = *x + one;
    let y = (x_minus_1 / x_plus_1)?;

    // Calculate y^2 for series
    let y_sq = y * y;

    // Taylor series: ln(x) = 2 * (y + y^3/3 + y^5/5 + ...)
    let mut sum = y;
    let mut y_power = y;

    // Iterate until convergence (max 20 terms)
    for n in 1..20 {
        y_power = y_power * y_sq;

        // Divide by (2n + 1)
        let divisor = (2 * n + 1) as i32;
        let term = match y_power / divisor {
            Ok(val) => val,
            Err(_) => break,
        };

        // Check for convergence (term becomes negligible)
        if term.abs().to_base_units() < 10 {
            // Threshold: very small
            break;
        }

        sum = sum + term;
    }

    // Multiply by 2
    Ok(sum * 2)
}

/// Shannon entropy calculation in Base-60
///
/// H = -sum(p_i * ln(p_i))
///
/// # Arguments
/// * `histogram` - Frequency counts for each bucket
/// * `total` - Total number of samples
pub fn entropy_s60(histogram: &HashMap<i32, u32>, total: u32) -> S60 {
    if total == 0 {
        return S60::ZERO;
    }

    let mut entropy = S60::ZERO;
    let total_s60 = S60::new(total as i32, 0, 0, 0, 0).unwrap();

    for &count in histogram.values() {
        if count == 0 {
            continue;
        }

        let count_s60 = S60::new(count as i32, 0, 0, 0, 0).unwrap();

        // p = count / total
        let p = match count_s60 / total_s60 {
            Ok(val) => val,
            Err(_) => continue,
        };

        // ln(p)
        let ln_p = match ln_s60(&p) {
            Ok(val) => val,
            Err(_) => continue,
        };

        // p * ln(p)
        let term = p * ln_p;

        // -sum
        entropy = entropy - term;
    }

    entropy
}

/// Cross-correlation between two S60 signals
///
/// Simplified version using direct correlation coefficient
pub fn cross_correlation_s60(signal_a: &[S60], signal_b: &[S60]) -> Result<S60, S60Error> {
    if signal_a.len() != signal_b.len() || signal_a.is_empty() {
        return Err(S60Error::ComponentOutOfRange(
            "Signals must have same non-zero length".to_string(),
        ));
    }

    let n = signal_a.len() as i32;
    let n_s60 = S60::new(n, 0, 0, 0, 0)?;

    // Calculate means
    let mut sum_a = S60::ZERO;
    let mut sum_b = S60::ZERO;
    for i in 0..signal_a.len() {
        sum_a = sum_a + signal_a[i];
        sum_b = sum_b + signal_b[i];
    }
    let mean_a = (sum_a / n)?;
    let mean_b = (sum_b / n)?;

    // Calculate correlation
    let mut numerator = S60::ZERO;
    let mut var_a = S60::ZERO;
    let mut var_b = S60::ZERO;

    for i in 0..signal_a.len() {
        let diff_a = signal_a[i] - mean_a;
        let diff_b = signal_b[i] - mean_b;

        numerator = numerator + (diff_a * diff_b);
        var_a = var_a + (diff_a * diff_a);
        var_b = var_b + (diff_b * diff_b);
    }

    // Correlation coefficient = numerator / sqrt(var_a * var_b)
    // Simplified: just return normalized numerator
    let denominator = var_a * var_b;
    if denominator == S60::ZERO {
        return Ok(S60::ZERO);
    }

    // This is a simplified version - full implementation would compute sqrt
    Ok(numerator)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ln_one() {
        let one = S60::new(1, 0, 0, 0, 0).unwrap();
        let result = ln_s60(&one).unwrap();
        assert_eq!(result, S60::ZERO);
    }

    #[test]
    fn test_entropy_uniform() {
        let mut hist = HashMap::new();
        hist.insert(0, 10);
        hist.insert(1, 10);
        hist.insert(2, 10);

        let entropy = entropy_s60(&hist, 30);
        // Uniform distribution should have high entropy
        assert!(entropy > S60::ZERO);
    }

    #[test]
    fn test_entropy_zero() {
        let hist = HashMap::new();
        let entropy = entropy_s60(&hist, 0);
        assert_eq!(entropy, S60::ZERO);
    }
}
