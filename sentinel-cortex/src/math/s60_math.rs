// src/math/s60_math.rs
//! Advanced mathematical functions for S60 (Base-60)
//!
//! Implements logarithm, entropy, and other functions needed for
//! Soul Verifier calculations using pure integer arithmetic.

use super::s60::{S60Error, S60};
use std::collections::HashMap;

/// Natural logarithm in Base-60 using Taylor series (IMPROVED)
///
/// Uses the series: ln(x) = 2 * sum((1/(2n+1)) * ((x-1)/(x+1))^(2n+1))
/// This converges for all x > 0
///
/// Improvements:
/// - 20 terms instead of 10 for better precision
/// - Range scaling to [0.5, 2] for faster convergence
/// - ln(2) constant for accurate scaling
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

    // Transform to range [0.5, 2] for better convergence
    let mut y = *x;
    let mut scale_factor = 0i32;

    // ln(2) ≈ 0.693147... = S60[000; 41, 34, 50] in sexagesimal
    // Calculated as: 693147 * SCALE_0 / 1000000
    let ln_2 = S60::from_raw(693147 * S60::SCALE_0 / 1000000);

    let two = S60::from_raw(S60::SCALE_0 * 2);
    let half = S60::from_raw(S60::SCALE_0 / 2);

    // Scale down if y > 2
    while y > two {
        // S60 division returns Result, so ? works
        y = (y / two)?;
        scale_factor += 1;
    }

    // Scale up if y < 0.5
    while y < half {
        // S60 mult returns S60, not Result, so ? is INVALID
        // We must change y = y * two
        y = y * two;
        scale_factor -= 1;
    }

    // Now y is in [0.5, 2] - optimal range for Taylor series

    // Calculate z = (y - 1) / (y + 1)
    let y_minus_1 = y - one;
    let y_plus_1 = y + one;
    let z = (y_minus_1 / y_plus_1)?;

    // Calculate z^2 for series
    let z_sq = z * z;

    // Taylor series: ln(y) = 2 * (z + z^3/3 + z^5/5 + z^7/7 + ...)
    let mut sum = z;
    let mut z_power = z;

    // Iterate 20 terms (was 10 before) for better precision
    for n in 1..20 {
        z_power = z_power * z_sq;

        // Divide by (2n + 1)
        let divisor_val = 2 * n + 1;
        let divisor_s60 = S60::new(divisor_val as i32, 0, 0, 0, 0).unwrap();
        let term = match z_power / divisor_s60 {
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
    let two = S60::new(2, 0, 0, 0, 0).unwrap();
    let mut result = sum * two;

    // Add back the scaling: ln(x) = ln(y) + scale_factor * ln(2)
    if scale_factor != 0 {
        let scale_s60 = S60::from_raw(scale_factor as i64 * S60::SCALE_0);
        let correction = scale_s60 * ln_2;
        result = result + correction;
    }

    Ok(result)
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

/// Complex number representation in S60 (for FFT)
#[derive(Debug, Clone, Copy)]
pub struct ComplexS60 {
    pub real: S60,
    pub imag: S60,
}

impl ComplexS60 {
    pub fn new(real: S60, imag: S60) -> Self {
        ComplexS60 { real, imag }
    }

    pub fn zero() -> Self {
        ComplexS60 {
            real: S60::ZERO,
            imag: S60::ZERO,
        }
    }

    /// Magnitude squared (avoids sqrt for efficiency)
    pub fn magnitude_squared(&self) -> S60 {
        self.real * self.real + self.imag * self.imag
    }

    /// Complex multiplication
    pub fn mul(&self, other: &ComplexS60) -> ComplexS60 {
        ComplexS60 {
            real: self.real * other.real - self.imag * other.imag,
            imag: self.real * other.imag + self.imag * other.real,
        }
    }

    /// Complex addition
    pub fn add(&self, other: &ComplexS60) -> ComplexS60 {
        ComplexS60 {
            real: self.real + other.real,
            imag: self.imag + other.imag,
        }
    }

    /// Complex subtraction
    pub fn sub(&self, other: &ComplexS60) -> ComplexS60 {
        ComplexS60 {
            real: self.real - other.real,
            imag: self.imag - other.imag,
        }
    }
}

/// Fast Fourier Transform (FFT) in Base-60
///
/// Implements the Cooley-Tukey algorithm for power-of-2 sized inputs.
/// Uses pure S60 arithmetic for complex number operations.
///
/// # Arguments
/// * `signal` - Input signal (must be power of 2 length)
///
/// # Returns
/// * `Vec<ComplexS60>` - Frequency domain representation
///
/// # Panics
/// * If signal length is not a power of 2
pub fn fft_s60(signal: &[S60]) -> Result<Vec<ComplexS60>, S60Error> {
    let n = signal.len();

    // Check if n is power of 2
    if n == 0 || (n & (n - 1)) != 0 {
        return Err(S60Error::ComponentOutOfRange(
            "FFT requires power-of-2 length".to_string(),
        ));
    }

    // Convert real signal to complex
    let mut data: Vec<ComplexS60> = signal
        .iter()
        .map(|&x| ComplexS60::new(x, S60::ZERO))
        .collect();

    // Bit-reversal permutation
    let mut j = 0;
    for i in 1..n {
        let mut bit = n >> 1;
        while j >= bit {
            j -= bit;
            bit >>= 1;
        }
        j += bit;
        if i < j {
            data.swap(i, j);
        }
    }

    // Cooley-Tukey FFT
    let mut size = 2;
    while size <= n {
        let half_size = size / 2;

        // Twiddle factor step
        // w = exp(-2πi/size) in S60
        // For Base-60, we use approximations of sin/cos

        for i in (0..n).step_by(size) {
            for k in 0..half_size {
                // Calculate twiddle factor: w = exp(-2πi * k / size) = cos(θ) - i·sin(θ)
                // con θ = 2π * k / size (en radianes, representación S60).
                //
                // Bug 1.7 fix: antes se usaba cos(θ) ≈ 1 - θ²/2 y sin(θ) ≈ θ
                // (Taylor a 1-2 términos). Para θ = π/2 (k = size/4) eso da
                // cos ≈ -0.234 (verdadero: 0) y sin ≈ 1.57 (verdadero: 1). El FFT
                // quedaba roto para señales con energía en frecuencias no triviales.
                // Ahora usamos sin_s60 (7 términos + rango reducido) y derivamos
                // cos(θ) = sin(θ + π/2) para mantener consistencia aritmética.

                // π ≈ 3.141592... = S60[3; 8, 29, 44]
                let pi = S60::from_raw(3141592 * S60::SCALE_0 / 1000000);
                let two = S60::from_raw(S60::SCALE_0 * 2);
                let size_s60 = S60::from_raw(size as i64 * S60::SCALE_0);

                let theta = match (two * pi * S60::from_raw(k as i64 * S60::SCALE_0)) / size_s60 {
                    Ok(val) => val,
                    Err(_) => continue,
                };

                // sin(θ) con Taylor mejorado (Bug 1.6 fix)
                let sin_theta = sin_s60(theta);

                // cos(θ) = sin(θ + π/2)
                let theta_plus_pi_2 = theta + S60::from_raw(pi.to_base_units() / 2);
                let cos_theta = sin_s60(theta_plus_pi_2);

                // w = cos(θ) - i·sin(θ) (signo negativo en el imaginario para FFT directa)
                let twiddle = ComplexS60::new(cos_theta, -sin_theta);

                let t = data[i + k + half_size].mul(&twiddle);
                let u = data[i + k];

                data[i + k] = u.add(&t);
                data[i + k + half_size] = u.sub(&t);
            }
        }

        size *= 2;
    }

    Ok(data)
}

/// Inverse FFT (IFFT) in Base-60
///
/// Converts frequency domain back to time domain.
pub fn ifft_s60(spectrum: &[ComplexS60]) -> Result<Vec<S60>, S60Error> {
    let n = spectrum.len();

    // Conjugate the input
    let mut conjugated: Vec<ComplexS60> = spectrum
        .iter()
        .map(|c| ComplexS60::new(c.real, -c.imag))
        .collect();

    // Apply FFT to conjugated data
    // (This is a placeholder - full implementation would recursively call FFT)

    // Conjugate the output and scale by 1/n
    let n_s60 = S60::from_raw(n as i64 * S60::SCALE_0);
    let result: Vec<S60> = conjugated
        .iter()
        .map(|c| match c.real / n_s60 {
            Ok(val) => val,
            Err(_) => S60::ZERO,
        })
        .collect();

    Ok(result)
}

/// Q-Factor (Quality Factor) in Base-60
///
/// Measures the "purity" of a resonance peak in the frequency spectrum.
/// Q = f₀ / Δf, where:
/// - f₀ = center frequency (peak)
/// - Δf = bandwidth at -3dB (half-power points)
///
/// Higher Q = sharper resonance (better signal quality)
/// Lower Q = broader resonance (noisy signal)
///
/// # Arguments
/// * `spectrum` - FFT output (frequency domain)
/// * `sample_rate` - Sampling rate in Hz (as S60)
///
/// # Returns
/// * `S60` - Q-Factor value
///
/// # Application
/// Used in soul_verifier to assess biometric signal quality:
/// - Q > 10 (S60[10;0]) = Clean human signal
/// - Q < 5 (S60[5;0]) = Noisy/synthetic signal
pub fn q_factor_s60(spectrum: &[ComplexS60], sample_rate: S60) -> Result<S60, S60Error> {
    if spectrum.is_empty() {
        return Err(S60Error::ComponentOutOfRange("Empty spectrum".to_string()));
    }

    let n = spectrum.len();

    // Find peak frequency (f₀)
    let mut peak_idx = 0;
    let mut peak_magnitude = S60::ZERO;

    // Only search first half (positive frequencies)
    for i in 0..(n / 2) {
        let mag = spectrum[i].magnitude_squared();
        if mag > peak_magnitude {
            peak_magnitude = mag;
            peak_idx = i;
        }
    }

    if peak_magnitude == S60::ZERO {
        return Ok(S60::ZERO); // No signal
    }

    // Calculate -3dB threshold (half power)
    // -3dB = 10^(-3/10) ≈ 0.5 (half power)
    let half_power = match peak_magnitude / S60::from_raw(S60::SCALE_0 * 2) {
        Ok(val) => val,
        Err(_) => return Ok(S60::ZERO),
    };

    // Find bandwidth: frequencies where power drops to half_power
    let mut f_low_idx = peak_idx;
    let mut f_high_idx = peak_idx;

    // Search left for lower -3dB point
    for i in (0..peak_idx).rev() {
        if spectrum[i].magnitude_squared() < half_power {
            f_low_idx = i;
            break;
        }
    }

    // Search right for upper -3dB point
    for i in (peak_idx + 1)..(n / 2) {
        if spectrum[i].magnitude_squared() < half_power {
            f_high_idx = i;
            break;
        }
    }

    // Convert indices to frequencies (in S60)
    // f = (index / N) * sample_rate
    let n_s60 = S60::from_raw(n as i64 * S60::SCALE_0);

    let f0_idx = S60::from_raw(peak_idx as i64 * S60::SCALE_0);
    let f_low_idx_s60 = S60::from_raw(f_low_idx as i64 * S60::SCALE_0);
    let f_high_idx_s60 = S60::from_raw(f_high_idx as i64 * S60::SCALE_0);

    let f0 = match f0_idx / n_s60 {
        Ok(ratio) => ratio * sample_rate,
        Err(_) => return Ok(S60::ZERO),
    };
    let f_low = match f_low_idx_s60 / n_s60 {
        Ok(ratio) => ratio * sample_rate,
        Err(_) => return Ok(S60::ZERO),
    };
    let f_high = match f_high_idx_s60 / n_s60 {
        Ok(ratio) => ratio * sample_rate,
        Err(_) => return Ok(S60::ZERO),
    };

    // Bandwidth Δf = f_high - f_low
    let bandwidth = f_high - f_low;

    if bandwidth == S60::ZERO {
        // Perfect resonance (infinite Q)
        return Ok(S60::from_raw(S60::SCALE_0 * 1000)); // Cap at 1000
    }

    // Q = f₀ / Δf
    let q_factor = (f0 / bandwidth)?;

    Ok(q_factor)
}

/// Cross-correlation between two S60 signals (IMPROVED)
///
/// Now includes proper sqrt computation for correlation coefficient
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
    let mean_a = (sum_a / n_s60)?;
    let mean_b = (sum_b / n_s60)?;

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
    let denominator = var_a * var_b;
    if denominator == S60::ZERO {
        return Ok(S60::ZERO);
    }

    // Compute sqrt using Newton-Raphson method
    let sqrt_denom = sqrt_s60(&denominator)?;

    Ok((numerator / sqrt_denom)?)
}

/// Square root in S60 using Newton-Raphson method
///
/// Iteratively computes sqrt(x) using: x_{n+1} = (x_n + a/x_n) / 2
pub fn sqrt_s60(x: &S60) -> Result<S60, S60Error> {
    if *x < S60::ZERO {
        return Err(S60Error::ComponentOutOfRange(
            "sqrt requires non-negative value".to_string(),
        ));
    }

    if *x == S60::ZERO {
        return Ok(S60::ZERO);
    }

    // Initial guess: x / 2
    let two = S60::from_raw(S60::SCALE_0 * 2);
    let mut guess = (*x / two)?;

    // Newton-Raphson iterations (10 iterations for convergence)
    for _ in 0..10 {
        let x_div_guess = (*x / guess)?;
        let new_guess = ((guess + x_div_guess) / two)?;

        // Check for convergence
        let diff = (new_guess - guess).abs();
        if diff.to_base_units() < 10 {
            // Converged
            return Ok(new_guess);
        }

        guess = new_guess;
    }

    Ok(guess)
}

/// Sine function in S60 using Taylor series
///
/// Implements sin(x) = x - x³/3! + x⁵/5! - x⁷/7! + x⁹/9! - x¹¹/11! + x¹³/13!
/// Input x should be in radians (S60 representation)
///
/// # Arguments
/// * `x` - Angle in radians (as S60)
///
/// # Returns
/// * `S60` - sin(x) in range [-1, 1]
///
/// # Notes
/// - Bug 1.6 fix: antes usaba 5 términos y reducía x solo a [0, 2π]. Para x cercano
///   a π (cerca del borde del rango de convergencia del Taylor), el error del
///   término x¹¹/11! ≈ 6.4e2/4e7 ≈ 1.6e-5 → ~3240 raw SPA, mayor que el umbral
///   declarado. Ahora:
///   1) Se reduce x a (-π, π] restando/restableciendo 2π simétricamente (la serie
///      converge mejor cerca del 0, donde los términos se hacen pequeños).
///   2) Se aumentan los términos a 7 (hasta x¹³/13!) para cerrar el error < 100 raw.
pub fn sin_s60(x: S60) -> S60 {
    // Normaliza x a (-π, π] restando/restableciendo 2π simétricamente
    // (antes era a [0, 2π] que deja a x=π en el borde, donde el Taylor diverge más).
    let two_pi = S60::two_pi();
    let pi = S60::from_raw(S60::SCALE_0 * 3 + S60::SCALE_1 * 8 + S60::SCALE_2 * 29 + S60::SCALE_3 * 44);

    let mut angle = x;
    // Traer a (-2π, 2π] primero
    while angle > two_pi {
        angle = angle - two_pi;
    }
    while angle <= -(two_pi) {
        angle = angle + two_pi;
    }
    // Y ahora a (-π, π]: si > π, restar 2π; si <= -π, sumar 2π
    while angle > pi {
        angle = angle - two_pi;
    }
    while angle <= -(pi) {
        angle = angle + two_pi;
    }

    // Taylor series: sin(x) = x - x³/3! + x⁵/5! - x⁷/7! + x⁹/9! - x¹¹/11! + x¹³/13!
    let x_sq = angle * angle; // x²

    // Term 1: x
    let mut result = angle;
    let mut term = angle;

    // Term 2: -x³/3! = -x³/6
    term = term * x_sq;
    if let Ok(val) = term / S60::from_int(6) {
        result = result - val;
    }

    // Term 3: +x⁵/5! = +x⁵/120
    term = term * x_sq;
    if let Ok(val) = term / S60::from_int(120) {
        result = result + val;
    }

    // Term 4: -x⁷/7! = -x⁷/5040
    term = term * x_sq;
    if let Ok(val) = term / S60::from_int(5040) {
        result = result - val;
    }

    // Term 5: +x⁹/9! = +x⁹/362880
    term = term * x_sq;
    if let Ok(val) = term / S60::from_int(362880) {
        result = result + val;
    }

    // Bug 1.6 fix: añadir términos 11 y 13 para reducir el error al borde
    // Term 6: -x¹¹/11! = -x¹¹/39916800
    term = term * x_sq;
    if let Ok(val) = term / S60::from_int(39_916_800i32) {
        result = result - val;
    }

    // Term 7: +x¹³/13! = +x¹³/6227020800  (13! > i32::MAX, se construye con from_raw)
    term = term * x_sq;
    let fact_13 = S60::from_raw(6_227_020_800i64 * S60::SCALE_0);
    if let Ok(val) = term / fact_13 {
        result = result + val;
    }

    result
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
    fn test_ln_two_precision() {
        // ln(2) = 0.693147...
        let two = S60::new(2, 0, 0, 0, 0).unwrap();
        let result = ln_s60(&two).unwrap();

        // Expected: 0.693147 = S60[000; 41, 34, 50]
        let expected = S60::from_raw(693147 * S60::SCALE_0 / 1000000);
        let diff = (result - expected).abs();

        // Error should be < 0.001
        assert!(
            diff.to_base_units() < 1000,
            "ln(2) error too large: {} vs {}",
            result.to_base_units(),
            expected.to_base_units()
        );
    }

    #[test]
    fn test_ln_large_number() {
        // ln(10) ≈ 2.302585
        let ten = S60::new(10, 0, 0, 0, 0).unwrap();
        let result = ln_s60(&ten).unwrap();

        // Should be around 2.3
        assert!(result.to_base_units() > S60::SCALE_0 * 2); // > 2.0
        assert!(result.to_base_units() < S60::SCALE_0 * 3); // < 3.0
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
