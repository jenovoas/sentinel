// src/security/soul_verifier_s60.rs
//! Base-60 implementations of Soul Verifier mathematical functions
//!
//! This module provides S60-based chaos theory calculations for biometric verification.

use crate::math::s60::{S60Error, S60};
use crate::math::s60_math::ln_s60;
use std::collections::HashMap;

/// Calculate Lyapunov exponent in Base-60
///
/// Measures the rate of divergence of nearby trajectories in phase space.
/// Range for human biometrics: S60[000; 06...] to S60[002; 30...] (0.1-2.5)
pub fn calculate_lyapunov_s60(signal: &[S60]) -> S60 {
    if signal.len() < 2 {
        return S60::ZERO;
    }

    let mut sum_div = S60::ZERO;
    let mut count = 0;

    // Analyze divergence of consecutive slopes
    for i in 0..signal.len() - 2 {
        let d1 = (signal[i + 1] - signal[i]).abs();
        let d2 = (signal[i + 2] - signal[i + 1]).abs();

        // Threshold to avoid division by very small numbers
        let threshold = S60::from_raw(S60::SCALE_0 / 10000); // 0.0001

        if d1 > threshold {
            // Calculate ratio d2 / d1
            match d2 / d1 {
                Ok(ratio) => {
                    if ratio > S60::ZERO {
                        // ln(ratio)
                        if let Ok(ln_ratio) = ln_s60(&ratio) {
                            sum_div = sum_div + ln_ratio;
                            count += 1;
                        }
                    }
                }
                Err(_) => continue,
            }
        }
    }

    if count == 0 {
        return S60::ZERO;
    }

    // Average: sum / count
    let raw_lambda = match sum_div / count {
        Ok(val) => val,
        Err(_) => return S60::ZERO,
    };

    // Scale to expected range [0.1 - 2.5] for Sentinel
    // Multiply by 2 and clamp
    let scaled = raw_lambda.abs() * 2;

    let min = S60::from_raw(S60::SCALE_0 / 10); // 0.1
    let max = S60::from_raw(S60::SCALE_0 * 5 / 2); // 2.5

    scaled.clamp(min, max)
}

/// Calculate Shannon entropy in Base-60
///
/// H = -sum(p_i * ln(p_i))
/// Range for deterministic chaos: S60[000; 30...] to S60[003; 30...] (0.5-3.5)
pub fn chaos_entropy_s60(signal: &[S60]) -> S60 {
    if signal.is_empty() {
        return S60::ZERO;
    }

    // Create histogram with 100 buckets for resolution
    let mut counts: HashMap<i64, u32> = HashMap::new();

    for val in signal {
        // Bucket: multiply by 100 and round
        let bucket = (val.to_base_units() * 100) / S60::SCALE_0;
        *counts.entry(bucket).or_insert(0) += 1;
    }

    let total = signal.len();
    let total_s60 = S60::from_raw(total as i64 * S60::SCALE_0);

    let mut entropy = S60::ZERO;

    for &count in counts.values() {
        if count == 0 {
            continue;
        }

        let count_s60 = S60::from_raw(count as i64 * S60::SCALE_0);

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

        // -sum (subtract because we negate at the end)
        entropy = entropy - term;
    }

    entropy
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lyapunov_zero_signal() {
        let signal = vec![];
        let result = calculate_lyapunov_s60(&signal);
        assert_eq!(result, S60::ZERO);
    }

    #[test]
    fn test_lyapunov_constant_signal() {
        let signal = vec![S60::ONE; 10];
        let result = calculate_lyapunov_s60(&signal);
        // Constant signal should have low Lyapunov
        assert!(result.to_base_units() < S60::SCALE_0); // < 1.0
    }

    #[test]
    fn test_entropy_empty() {
        let signal = vec![];
        let result = chaos_entropy_s60(&signal);
        assert_eq!(result, S60::ZERO);
    }

    #[test]
    fn test_entropy_uniform() {
        // Uniform distribution should have high entropy
        let signal = vec![
            S60::from_raw(S60::SCALE_0),
            S60::from_raw(S60::SCALE_0 * 2),
            S60::from_raw(S60::SCALE_0 * 3),
        ];
        let result = chaos_entropy_s60(&signal);
        assert!(result > S60::ZERO);
    }
}
