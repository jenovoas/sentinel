// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 💓 BIO-RESONANCE (SOUL VERIFIER) 💓
//!
//! Implementation of Axiom V: "Biocentrism".
//! Verifies that the operator is a biological entity via Chaos Theory.
//!
//! Based on EXP-019 protocols:
//! - Lyapunov Exponent (λ): Measures orbital divergence (Chaos).
//! - Shannon Entropy (H): Measures information density.

use crate::spa::SPA;
use crate::spa_math::SPAMath;

#[derive(Debug, Clone)]
pub struct BioMetrics {
    pub lyapunov: SPA,
    pub entropy: SPA,
    pub is_alive: bool,
}

pub struct SoulVerifier;

impl SoulVerifier {
    /// Analyzes a time-series signal (e.g., Heart Rhythm) for biological signatures.
    pub fn analyze(signal: &[SPA]) -> BioMetrics {
        let lyapunov = Self::calculate_lyapunov(signal);
        let entropy = Self::calculate_entropy(signal);

        // Validation Ranges (from EXP-019)
        // Lyapunov: 0.1 .. 2.5
        let l_min = SPA::new(0, 6, 0, 0, 0); // 0.1
        let l_max = SPA::new(2, 30, 0, 0, 0); // 2.5

        // Entropy: 0.5 .. 3.5
        let e_min = SPA::new(0, 30, 0, 0, 0); // 0.5
        let e_max = SPA::new(3, 30, 0, 0, 0); // 3.5

        let alive = lyapunov >= l_min && lyapunov <= l_max && entropy >= e_min && entropy <= e_max;

        BioMetrics {
            lyapunov,
            entropy,
            is_alive: alive,
        }
    }

    /// Calculates Lyapunov Exponent (λ)
    /// λ = (1/N) * Σ ln(|d2/d1|)
    fn calculate_lyapunov(signal: &[SPA]) -> SPA {
        if signal.len() < 3 {
            return SPA::zero();
        }

        let mut sum_div = SPA::zero();
        let mut count = SPA::zero();
        let threshold = SPA::new(0, 0, 0, 0, 1); // Epsilon (Fourths resolution)

        for i in 0..signal.len() - 2 {
            let d1 = (signal[i + 1] - signal[i]).abs();
            let d2 = (signal[i + 2] - signal[i + 1]).abs();

            if d1 > threshold {
                // d2 / d1
                // SPA division: (d2.raw * SCALE) / d1.raw
                // We can use the Div impl directly
                let ratio = d2 / d1;

                if ratio.to_raw() > 0 {
                    // ln(ratio)
                    let ln_val = SPAMath::ln(ratio).abs(); // Take abs magnitude of divergence
                    sum_div = sum_div + ln_val;
                    count = count + SPA::new(1, 0, 0, 0, 0);
                }
            }
        }

        if count.to_raw() == 0 {
            return SPA::zero();
        }

        // Average * Scaling Factor (0.5 from EXP-021)
        let avg = sum_div / count;
        let scale = SPA::new(0, 30, 0, 0, 0); // 0.5

        avg * scale
    }

    /// Calculates Shannon Entropy (H)
    /// H = -Σ p * ln(p)
    fn calculate_entropy(signal: &[SPA]) -> SPA {
        if signal.is_empty() {
            return SPA::zero();
        }

        // Quantize signal into buckets (simple histogram)
        // We assume signal is 0..100 roughly.
        // Bucket size = 1.0
        let mut counts = [0u32; 256]; // Max 256 buckets for simplicity
        let mut total = 0u32;

        for &val in signal {
            let _raw = val.to_raw();
            // Value assumed to be roughly 60..100.
            // Map to integer index: val.to_raw()
            let idx = val.to_raw() / SPA::SCALE_0;
            if (0..256).contains(&idx) {
                counts[idx as usize] += 1;
                total += 1;
            }
        }

        let mut entropy = SPA::zero();
        let total_spa = SPA::new(total as i64, 0, 0, 0, 0);

        for &c in &counts {
            if c > 0 {
                let p = SPA::new(c as i64, 0, 0, 0, 0) / total_spa;
                let ln_p = SPAMath::ln(p);
                // -p * ln(p)
                let term = p * ln_p;
                entropy = entropy - term; // Subtract negative value = add
            }
        }

        entropy
    }
}
