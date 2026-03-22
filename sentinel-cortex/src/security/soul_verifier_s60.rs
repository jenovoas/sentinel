#![allow(dead_code)]
// src/security/soul_verifier_s60.rs
//! Base-60 implementations of Soul Verifier mathematical functions
//!
//! This module provides S60-based chaos theory calculations for biometric verification.

use crate::math::s60::S60;
use crate::math::SPAMath;
use std::collections::HashMap;

/// Calculate Lyapunov exponent in Base-60
pub fn calculate_lyapunov_s60(signal: &[S60]) -> S60 {
    if signal.len() < 2 {
        return S60::zero();
    }

    let mut sum_div = S60::zero();
    let mut count = 0;

    for i in 0..signal.len() - 2 {
        let d1 = (signal[i + 1] - signal[i]).abs();
        let d2 = (signal[i + 2] - signal[i + 1]).abs();

        let threshold = S60::from_raw(S60::SCALE_0 / 10000); // 0.0001
        if d1 > threshold {
            let ratio = d2.div_safe(d1).unwrap_or(S60::zero());
            if ratio > S60::zero() {
                let ln_ratio = SPAMath::ln(ratio);
                sum_div = sum_div + ln_ratio.abs();
                count += 1;
            }
        }
    }

    if count == 0 {
        return S60::zero();
    }

    let count_s60 = S60::from_int(count as i64);
    let raw_lambda = sum_div.div_safe(count_s60).unwrap_or(S60::zero());

    let half = S60::from_raw(S60::SCALE_0 / 2); // 0.5
    let scaled = raw_lambda * half;

    let min = S60::from_raw(S60::SCALE_0 / 10); // 0.1
    let max = S60::from_raw((S60::SCALE_0 * 5) / 2); // 2.5
    scaled.clamp(min, max)
}

/// Calculate Shannon entropy in Base-60
pub fn chaos_entropy_s60(signal: &[S60]) -> S60 {
    if signal.is_empty() {
        return S60::zero();
    }

    let mut counts: HashMap<i64, u32> = HashMap::new();
    for val in signal {
        let bucket = (val.to_raw() * 100) / S60::SCALE_0;
        *counts.entry(bucket).or_insert(0) += 1;
    }

    let total = signal.len();
    let total_s60 = S60::from_int(total as i64);

    let mut entropy = S60::zero();
    for &count in counts.values() {
        if count == 0 { continue; }
        let count_s60 = S60::from_int(count as i64);
        let p = count_s60.div_safe(total_s60).unwrap_or(S60::zero());
        if p == S60::zero() { continue; }
        
        let ln_p = SPAMath::ln(p);
        entropy = entropy - (p * ln_p);
    }
    entropy
}

/// Square root using Newton's method in Base-60
pub fn sqrt_s60(x: &S60) -> S60 {
    if *x <= S60::zero() {
        return S60::zero();
    }

    let two = S60::from_int(2);
    let mut guess = x.div_safe(two).unwrap_or(S60::one());

    for _ in 0..15 {
        let x_div_guess = x.div_safe(guess).unwrap_or(guess);
        let new_guess = (guess + x_div_guess).div_safe(two).unwrap_or(guess);
        if (new_guess - guess).abs().to_raw() < 100 {
            return new_guess;
        }
        guess = new_guess;
    }
    guess
}

/// Autocorrelation at lag k
fn autocorrelation_s60(signal: &[S60], lag: usize) -> S60 {
    if lag >= signal.len() {
        return S60::zero();
    }
    let n = signal.len() - lag;
    let mut sum = S60::zero();
    for i in 0..n {
        sum = sum + (signal[i] * signal[i + lag]);
    }
    let n_s60 = S60::from_int(n as i64);
    sum.div_safe(n_s60).unwrap_or(S60::zero())
}

/// Find dominant frequency using autocorrelation
fn find_dominant_frequency_s60(signal: &[S60]) -> S60 {
    if signal.len() < 4 {
        return S60::one();
    }
    let mut max_corr = S60::zero();
    let mut period = 1;
    for lag in 1..signal.len() / 2 {
        let corr = autocorrelation_s60(signal, lag);
        if corr > max_corr {
            max_corr = corr;
            period = lag;
        }
    }
    let period_s60 = S60::from_int(period as i64);
    S60::one().div_safe(period_s60).unwrap_or(S60::one())
}

/// Calculate bandwidth using standard deviation
fn calculate_bandwidth_s60(signal: &[S60]) -> S60 {
    if signal.is_empty() { return S60::one(); }
    let sum: S60 = signal.iter().fold(S60::zero(), |acc, &x| acc + x);
    let n_s60 = S60::from_int(signal.len() as i64);
    let mean = sum.div_safe(n_s60).unwrap_or(S60::one());

    let var_sum: S60 = signal.iter().map(|&x| (x - mean) * (x - mean)).fold(S60::zero(), |acc, x| acc + x);
    let variance = var_sum.div_safe(n_s60).unwrap_or(S60::one());
    sqrt_s60(&variance)
}

/// Calculate Q-Factor in Base-60
pub fn calculate_q_factor_s60(signal: &[S60]) -> S60 {
    if signal.len() < 10 { return S60::from_int(5); }
    let f0 = find_dominant_frequency_s60(signal);
    let bandwidth = calculate_bandwidth_s60(signal);
    if bandwidth == S60::zero() { return S60::from_int(5); }
    let q = f0.div_safe(bandwidth).unwrap_or(S60::from_int(5));
    q.clamp(S60::from_int(2), S60::from_int(8))
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_sqrt_s60() {
        let four = S60::from_int(4);
        let result = sqrt_s60(&four);
        assert!((result - S60::from_int(2)).abs().to_raw() < 1000);
    }
}
