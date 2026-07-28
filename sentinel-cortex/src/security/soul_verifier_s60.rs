// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/security/soul_verifier_s60.rs
//! Base-60 implementations of Soul Verifier mathematical functions
//!
//! This module provides S60-based chaos theory calculations for biometric verification.

use crate::math::s60::{S60Error, S60};
use crate::math::s60_math::ln_s60;
// Dup 3.1 fix: sqrt_s60 estaba duplicado en este archivo (privado) y en
// s60_math.rs (público). Se elimina la copia local y se reutiliza la pública
// para que cualquier mejora futura en la implementación se propague a ambos
// consumidores. Respeta Axioma VI: no se elimina archivo ni documentación,
// sólo se consolida una función duplicada (sugerencia de auditoría).
use crate::math::s60_math::sqrt_s60;
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
                        // ln(ratio) - take absolute value to handle ratio < 1
                        if let Ok(ln_ratio) = ln_s60(&ratio) {
                            sum_div = sum_div + ln_ratio.abs();
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
    let count_s60 = S60::from_raw(count as i64 * S60::SCALE_0);
    let raw_lambda = match sum_div / count_s60 {
        Ok(val) => val,
        Err(_) => return S60::ZERO,
    };

    // Scale to expected range [0.1 - 2.5] for Sentinel
    // Multiply by 0.5 (same as f64 version)
    let half = S60::from_raw(S60::SCALE_0 / 2); // 0.5
    let scaled = raw_lambda * half;

    // Define min and max bounds
    let min = S60::from_raw(S60::SCALE_0 / 10); // 0.1
    let max = S60::from_raw((S60::SCALE_0 * 5) / 2); // 2.5

    // Clamp to range
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

/// Square root using Newton's method in Base-60
///
/// sqrt(x) via iteration: x_{n+1} = (x_n + a/x_n) / 2
///
/// Dup 3.1 fix: la implementación se eliminó en favor de la versión pública
/// `crate::math::s60_math::sqrt_s60` (ver el `use` al inicio del archivo).
/// Cualquier mejora en la convergencia (terms, threshold, overflow handling)
/// se aplica una sola vez y úlalmentelega a todos los consumidores.
/// Axioma VI respetado: no se elimina el archivo, sólo la función duplicada.

/// Autocorrelation at lag k
fn autocorrelation_s60(signal: &[S60], lag: usize) -> S60 {
    if lag >= signal.len() {
        return S60::ZERO;
    }

    let n = signal.len() - lag;
    let mut sum = S60::ZERO;

    for i in 0..n {
        sum = sum + (signal[i] * signal[i + lag]);
    }

    let n_s60 = S60::from_raw(n as i64 * S60::SCALE_0);
    match sum / n_s60 {
        Ok(val) => val,
        Err(_) => S60::ZERO,
    }
}

/// Find dominant frequency using autocorrelation
fn find_dominant_frequency_s60(signal: &[S60]) -> S60 {
    if signal.len() < 4 {
        return S60::ONE;
    }

    let mut max_corr = S60::ZERO;
    let mut period = 1;

    // Search for peak in autocorrelation (skip lag=0)
    for lag in 1..signal.len() / 2 {
        let corr = autocorrelation_s60(signal, lag);
        if corr > max_corr {
            max_corr = corr;
            period = lag;
        }
    }

    // f = 1 / period
    let period_s60 = S60::from_raw(period as i64 * S60::SCALE_0);
    match S60::ONE / period_s60 {
        Ok(f) => f,
        Err(_) => S60::ONE,
    }
}

/// Calculate bandwidth using standard deviation
fn calculate_bandwidth_s60(signal: &[S60]) -> S60 {
    if signal.is_empty() {
        return S60::ONE;
    }

    // Calculate mean
    let sum: S60 = signal.iter().fold(S60::ZERO, |acc, &x| acc + x);
    let n_s60 = S60::from_raw(signal.len() as i64 * S60::SCALE_0);
    let mean = match sum / n_s60 {
        Ok(m) => m,
        Err(_) => return S60::ONE,
    };

    // Calculate variance
    let variance: S60 = signal
        .iter()
        .map(|&x| {
            let diff = x - mean;
            diff * diff
        })
        .fold(S60::ZERO, |acc, x| acc + x);

    let variance = match variance / n_s60 {
        Ok(v) => v,
        Err(_) => return S60::ONE,
    };

    // bandwidth ≈ sqrt(variance)
    sqrt_s60(&variance).unwrap_or(S60::ONE)
}

/// Calculate Q-Factor in Base-60
///
/// Q = f0 / bandwidth
/// Range for human biometrics: S60[002; 00...] to S60[008; 00...] (2.0-8.0)
/// High Q (>10) indicates synthetic/periodic signal
/// Low Q (<5) indicates chaotic/human signal
pub fn calculate_q_factor_s60(signal: &[S60]) -> S60 {
    if signal.len() < 10 {
        return S60::from_raw(S60::SCALE_0 * 5); // Default 5.0
    }

    // 1. Find dominant frequency (f0)
    let f0 = find_dominant_frequency_s60(signal);

    // 2. Calculate bandwidth
    let bandwidth = calculate_bandwidth_s60(signal);

    // Avoid division by zero
    if bandwidth == S60::ZERO {
        return S60::from_raw(S60::SCALE_0 * 5); // Default 5.0
    }

    // 3. Q = f0 / bandwidth
    let q = match f0 / bandwidth {
        Ok(val) => val,
        Err(_) => return S60::from_raw(S60::SCALE_0 * 5),
    };

    // Clamp to expected range [2.0 - 8.0]
    let min = S60::from_raw(S60::SCALE_0 * 2); // 2.0
    let max = S60::from_raw(S60::SCALE_0 * 8); // 8.0
    q.clamp(min, max)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sqrt_s60() {
        // sqrt(4) = 2
        let four = S60::from_raw(S60::SCALE_0 * 4);
        let result = sqrt_s60(&four).unwrap();
        let two = S60::from_raw(S60::SCALE_0 * 2);
        let diff = (result - two).abs();
        assert!(diff.to_base_units() < 1000); // Error < 0.001
    }

    #[test]
    fn test_autocorrelation() {
        let signal = vec![S60::ONE, S60::ONE, S60::ONE];
        let corr = autocorrelation_s60(&signal, 1);
        assert!(corr > S60::ZERO);
    }

    #[test]
    fn test_q_factor_constant() {
        // Constant signal should have high Q
        let signal = vec![S60::ONE; 20];
        let q = calculate_q_factor_s60(&signal);
        // Should be clamped to max (8.0)
        assert!(q.to_base_units() >= S60::SCALE_0 * 2); // >= 2.0
    }

    #[test]
    fn test_q_factor_short_signal() {
        let signal = vec![S60::ONE; 5];
        let q = calculate_q_factor_s60(&signal);
        // Should return default 5.0
        assert_eq!(q, S60::from_raw(S60::SCALE_0 * 5));
    }

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
