// src/security/soul_verifier_s60_production.rs
//! PRODUCTION Biometric Verifier - Pure Base-60 (S60) Implementation
//!
//! CRITICAL: This module is designed for PHYSICAL MODEL deployment.
//! All mathematics use exact Base-60 arithmetic to prevent:
//! - Thermal noise from floating-point operations
//! - Precision errors that could cause hardware failure
//! - Pseudo-random number generation (uses real entropy)
//!
//! AXIOM I COMPLIANCE: FLOAT = DEATH for physical models

use crate::math::s60::{S60Error, S60};
use crate::math::s60_math::{fft_s60, q_factor_s60};
// use crate::security::rbac_biological::BiologicalRole;
use crate::security::soul_verifier_s60::{calculate_lyapunov_s60, chaos_entropy_s60};
use serde::{Deserialize, Serialize};
use sha3::{Digest, Sha3_512};
use std::fs::File;
use std::io::Read;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct LivenessChallenge {
    pub nonce: u64,
    pub light_sequence: Vec<u8>,
    pub timestamp: i64,
    pub user_id: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct BiometricProof {
    /// Lyapunov exponent in Base-60 (range: 0.1-2.5 for humans)
    pub lyapunov_exp: S60,

    /// Chaos entropy in Base-60 (range: 0.5-3.5 for living beings)
    pub chaos_entropy: S60,

    /// Q-Factor in Base-60 (signal quality: >10 = clean, <5 = synthetic)
    pub q_factor: S60,

    /// Light response correlation (not implemented, returns 0)
    pub response_correlation: S60,

    /// SHA3-512 hash of biometric signature
    pub biometric_hash: String,

    /// Unix timestamp of verification
    pub timestamp: i64,
}

#[derive(Debug)]
pub enum BiometricError {
    StaleChallenge,
    NoLivingSource,
    UnknownIdentity(String),
    InsufficientSignal,
    EntropyError(String),
}

pub struct BiometricVerifier {
    challenge_seq: Vec<u8>,
}

impl BiometricVerifier {
    pub fn new() -> Self {
        Self {
            challenge_seq: vec![255, 0, 255], // Red-Blue-Red (simplified)
        }
    }

    /// Generate challenge with REAL entropy (no rand::random)
    pub fn generate_challenge(&self, user_id: &str) -> LivenessChallenge {
        let nonce = self.generate_real_entropy_nonce();

        LivenessChallenge {
            nonce,
            light_sequence: self.challenge_seq.clone(),
            timestamp: chrono::Utc::now().timestamp(),
            user_id: user_id.to_string(),
        }
    }

    fn generate_real_entropy_nonce(&self) -> u64 {
        match File::open("/dev/urandom") {
            Ok(mut file) => {
                let mut buffer = [0u8; 8];
                if file.read_exact(&mut buffer).is_ok() {
                    u64::from_le_bytes(buffer)
                } else {
                    self.fallback_nonce()
                }
            }
            Err(_) => self.fallback_nonce(),
        }
    }

    fn fallback_nonce(&self) -> u64 {
        use std::time::{SystemTime, UNIX_EPOCH};

        let ts = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos() as u64;

        ts ^ (std::process::id() as u64)
    }

    /// Verify biometric liveness from rPPG signal - PURE S60
    pub fn verify_liveness(
        &self,
        rppg_signal: &[S60],
        challenge: &LivenessChallenge,
    ) -> Result<BiometricProof, BiometricError> {
        // 1. Verify timestamp freshness (<30s)
        let now = chrono::Utc::now().timestamp();
        if (now - challenge.timestamp) > 30 {
            return Err(BiometricError::StaleChallenge);
        }

        // 2. Calculate Lyapunov exponent (chaos measure) in S60
        let lyapunov = calculate_lyapunov_s60(rppg_signal);

        // 3. Calculate Shannon entropy in S60
        let entropy = chaos_entropy_s60(rppg_signal);

        // 4. Calculate Q-Factor (signal quality) in S60
        let q_factor = self.calculate_q_factor_s60(rppg_signal);

        // 5. Light correlation (NOT IMPLEMENTED - requires physical sensor)
        let light_response = S60::ZERO;

        tracing::debug!(
            "Biometric metrics: Lyapunov={}, Entropy={}, Q-Factor={}",
            lyapunov,
            entropy,
            q_factor
        );

        // 6. Compute biometric hash (SHA3-512 of signal + nonce)
        let biometric_hash_str =
            self.compute_biometric_hash_s60(rppg_signal, &challenge.nonce.to_le_bytes());

        // 8. Validate ranges (S60 pure, no float conversion)
        let min_lyap = S60::from_raw(S60::SCALE_0 / 10); // 0.1
        let max_lyap = S60::from_raw((S60::SCALE_0 * 5) / 2); // 2.5
        let min_entr = S60::from_raw(S60::SCALE_0 / 2); // 0.5
        let min_q = S60::from_raw(S60::SCALE_0 * 5); // 5.0 (minimum acceptable Q)

        if lyapunov < min_lyap || lyapunov > max_lyap {
            tracing::warn!("Lyapunov out of range: {}", lyapunov);
            return Err(BiometricError::NoLivingSource);
        }

        if entropy < min_entr {
            tracing::warn!("Entropy too low: {}", entropy);
            return Err(BiometricError::NoLivingSource);
        }

        if q_factor < min_q {
            tracing::warn!("Q-Factor too low: {}", q_factor);
            return Err(BiometricError::NoLivingSource);
        }

        Ok(BiometricProof {
            lyapunov_exp: lyapunov,
            chaos_entropy: entropy,
            q_factor,
            response_correlation: light_response,
            biometric_hash: biometric_hash_str,
            timestamp: now,
        })
    }

    fn calculate_q_factor_s60(&self, rppg_signal: &[S60]) -> S60 {
        // Ensure signal length is power of 2 for FFT
        let signal_len = rppg_signal.len();
        let fft_len = signal_len.next_power_of_two().min(256);

        let mut padded_signal: Vec<S60> = rppg_signal.iter().take(fft_len).copied().collect();
        while padded_signal.len() < fft_len {
            padded_signal.push(S60::ZERO);
        }

        let spectrum = match fft_s60(&padded_signal) {
            Ok(spec) => spec,
            Err(_) => return S60::ZERO,
        };

        let sample_rate = S60::from_raw(S60::SCALE_0 * 60);

        match q_factor_s60(&spectrum, sample_rate) {
            Ok(q) => q,
            Err(_) => S60::ZERO,
        }
    }

    fn compute_biometric_hash_s60(&self, rppg: &[S60], nonce: &[u8]) -> String {
        let mut hasher = Sha3_512::new();
        for val in rppg {
            let units: i64 = val.to_base_units();
            hasher.update(units.to_le_bytes());
        }
        hasher.update(nonce);
        let hash = hasher.finalize();
        hex::encode(hash)
    }
}

impl Default for BiometricVerifier {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_valid_human_signal_s60() {
        let verifier = BiometricVerifier::new();
        let user_id = "jnovoas";
        let challenge = verifier.generate_challenge(user_id);

        let signal: Vec<S60> = (0..100)
            .map(|i| {
                let base = S60::new(60 + (i as i32 % 40), 0, 0, 0, 0).unwrap();
                let variation = S60::new(0, ((i * 7) % 60) as u8, 0, 0, 0).unwrap();
                base + variation
            })
            .collect();

        let result = verifier.verify_liveness(&signal, &challenge);
        assert!(result.is_ok(), "Valid S60 signal should be accepted");
    }

    // Additional tests corresponding to the original ones
    #[test]
    fn test_reject_static_signal_s60() {
        let verifier = BiometricVerifier::new();
        let challenge = verifier.generate_challenge("jnovoas");

        // Static signal (no variation)
        let signal = vec![S60::new(60, 30, 0, 0, 0).unwrap(); 100];

        let result = verifier.verify_liveness(&signal, &challenge);

        assert!(result.is_err(), "Static signal should be rejected");
    }

    #[test]
    fn test_soul_hash_deterministic() {
        let verifier = BiometricVerifier::new();

        let signal = vec![S60::new(60, 30, 15, 0, 0).unwrap(); 10];
        let nonce = [1, 2, 3, 4, 5, 6, 7, 8];

        let hash1 = verifier.compute_biometric_hash_s60(&signal, &nonce);
        let hash2 = verifier.compute_biometric_hash_s60(&signal, &nonce);

        assert_eq!(hash1, hash2, "Hash should be deterministic");
        assert_eq!(hash1.len(), 128, "SHA3-512 should produce 128 hex chars");
    }
}
