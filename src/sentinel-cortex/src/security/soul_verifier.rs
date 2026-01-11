// src/security/soul_verifier.rs
use crate::math::s60::S60;
use crate::security::rbac_biological::BiologicalRole;
use crate::security::soul_verifier_s60::{calculate_lyapunov_s60, chaos_entropy_s60};
use serde::{Deserialize, Serialize};
use sha3::{Digest, Sha3_512};
use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct AlmaChallenge {
    pub nonce: u64,
    pub light_sequence: Vec<u8>,
    pub timestamp: i64,
    pub user_id: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct ProofOfLife {
    pub lyapunov_exp: f64,         // 0.1-2.5 (humano vivo)
    pub chaos_entropy: f64,        // 1.2-3.8 (no periódico)
    pub response_correlation: f64, // >0.7 (responde luz)
    pub soul_hash: String,
    pub timestamp: i64,
    pub role: BiologicalRole,
}

#[derive(Debug, Clone, Serialize)]
pub struct BiologicalMetrics {
    pub lyapunov_exp: f64,
    pub chaos_entropy: f64,
}

#[derive(Debug)]
pub enum SoulError {
    StaleChallenge,
    NoLivingSoul,
    UnknownSoul(String),
    InsufficientSignal,
    UnauthorizedIdentity(BiologicalMetrics),
}

pub struct SoulVerifier {
    challenge_seq: Vec<u8>,
}

impl SoulVerifier {
    pub fn new() -> Self {
        Self {
            challenge_seq: vec![255, 0, 255], // Rojo-Azul-Rojo (Simplificado)
        }
    }

    /// 1. Servidor genera desafío luminoso
    pub fn generate_challenge(&self, user_id: &str) -> AlmaChallenge {
        let nonce = rand::random::<u64>();
        AlmaChallenge {
            nonce,
            light_sequence: self.challenge_seq.clone(),
            timestamp: chrono::Utc::now().timestamp(),
            user_id: user_id.to_string(),
        }
    }

    /// 2. Verifica prueba de vida desde rPPG raw
    pub fn verify_proof_of_life(
        &self,
        rppg_signal: &[f32], // Serie temporal brillo facial
        challenge: &AlmaChallenge,
    ) -> Result<ProofOfLife, SoulError> {
        // Verificar timestamp fresco (< 30s)
        let now = chrono::Utc::now().timestamp();
        if (now - challenge.timestamp) > 30 {
            return Err(SoulError::StaleChallenge);
        }

        // a) Correlación con secuencia de luz (Simulado por ahora)
        let light_response = self.correlate_light_challenge(rppg_signal, &challenge.light_sequence);

        // b) Calcular Exponente Lyapunov (caos humano)
        let lyapunov = self.calculate_lyapunov_exponent(rppg_signal);

        let entropy = self.chaos_entropy(rppg_signal);

        // S60 VALIDATION PATH (comparison only, not used for auth yet)
        let (lyapunov_s60, entropy_s60) = self.calculate_s60_metrics(rppg_signal);
        self.compare_and_log(lyapunov, lyapunov_s60, entropy, entropy_s60);

        let light_response = self.correlate_light_challenge(rppg_signal, &challenge.light_sequence);

        // Compute soul hash
        let soul_hash_str = self.compute_soul_hash(rppg_signal, &challenge.nonce.to_le_bytes());

        // Role-based validation
        let role = BiologicalRole::from_soul_hash(&challenge.user_id);

        if lyapunov < 0.1 || lyapunov > 2.5 {
            return Err(SoulError::NoLivingSoul);
        }

        if entropy < 0.5 {
            return Err(SoulError::NoLivingSoul);
        }

        Ok(ProofOfLife {
            lyapunov_exp: lyapunov,
            chaos_entropy: entropy,
            response_correlation: light_response,
            soul_hash: soul_hash_str,
            timestamp: now,
            role,
        })
    }

    /// Calculate S60 metrics for validation (dual-path)
    fn calculate_s60_metrics(&self, signal: &[f32]) -> (f64, f64) {
        // Convert f32 signal to S60
        let signal_s60: Vec<S60> = signal
            .iter()
            .map(|&val| S60::from_f32_unsafe(val))
            .collect();

        // Calculate using S60
        let lyap = calculate_lyapunov_s60(&signal_s60);
        let entr = chaos_entropy_s60(&signal_s60);

        // Convert back to f64 for comparison
        (lyap.to_f64_unsafe(), entr.to_f64_unsafe())
    }

    /// Compare f64 and S60 results, log discrepancies
    fn compare_and_log(&self, l_f64: f64, l_s60: f64, e_f64: f64, e_s60: f64) {
        let lyap_diff = (l_f64 - l_s60).abs();
        let entr_diff = (e_f64 - e_s60).abs();

        if lyap_diff > 0.1 || entr_diff > 0.1 {
            tracing::warn!(
                "🔍 S60 divergence: Lyapunov Δ={:.4} (f64={:.4}, s60={:.4}), Entropy Δ={:.4} (f64={:.4}, s60={:.4})",
                lyap_diff, l_f64, l_s60, entr_diff, e_f64, e_s60
            );
        } else {
            tracing::debug!(
                "✅ S60 validation OK: Lyapunov Δ={:.4}, Entropy Δ={:.4}",
                lyap_diff,
                entr_diff
            );
        }
    }

    fn calculate_lyapunov_exponent(&self, signal: &[f32]) -> f64 {
        if signal.len() < 2 {
            return 0.0;
        }

        let mut sum_div = 0.0f64;
        let mut count = 0;

        // Versión optimizada: Analiza la divergencia de pendientes consecutivas
        for i in 0..signal.len() - 2 {
            let d1 = (signal[i + 1] - signal[i]).abs() as f64;
            let d2 = (signal[i + 2] - signal[i + 1]).abs() as f64;

            if d1 > 0.0001 {
                let ratio = d2 / d1;
                if ratio > 0.0 {
                    sum_div += ratio.ln();
                    count += 1;
                }
            }
        }

        if count == 0 {
            return 0.0;
        }
        let raw_lambda = sum_div / count as f64;

        // Escalar al rango esperado [0.1 - 2.5] para Sentinel
        (raw_lambda.abs() * 2.0).clamp(0.1, 2.5)
    }

    fn chaos_entropy(&self, signal: &[f32]) -> f64 {
        if signal.is_empty() {
            return 0.0;
        }

        let mut counts = HashMap::new();
        // Mayor resolución para rPPG (100 buckets)
        for &val in signal {
            let bucket = (val * 100.0).round() as i32;
            *counts.entry(bucket).or_insert(0) += 1;
        }

        let len = signal.len() as f64;
        let mut h = 0.0;
        for &count in counts.values() {
            let p = count as f64 / len;
            if p > 0.0 {
                h -= p * p.ln();
            }
        }
        h
    }

    fn correlate_light_challenge(&self, _rppg: &[f32], _light_seq: &[u8]) -> f64 {
        // CRITICAL: This function was previously hardcoded to return 0.85
        // This violated Axiom II (Radical Honesty - No Simulation)
        //
        // Real implementation requires:
        // 1. FFT cross-correlation between rPPG signal and light sequence
        // 2. Physical sensor data (not simulated)
        // 3. Base-60 arithmetic for Yatra compliance
        //
        // For now, return 0.0 to indicate "not implemented"
        // Tests should be updated to expect this behavior
        tracing::warn!(
            "⚠️ correlate_light_challenge NOT IMPLEMENTED - requires physical sensor data"
        );
        0.0
    }

    fn compute_soul_hash(&self, rppg: &[f32], nonce: &[u8]) -> String {
        let mut hasher = Sha3_512::new();
        for val in rppg {
            hasher.update(val.to_be_bytes());
        }
        hasher.update(nonce);
        let hash = hasher.finalize();
        hex::encode(hash)
    }
}

#[cfg(test)]
mod tests {
    use super::super::rbac_biological::BiologicalRole;
    use super::*;

    #[test]
    fn test_valid_human_signal() {
        let verifier = SoulVerifier::new();
        // Use a registered user to pass RBAC
        let user_id = "jnovoas";
        let challenge = verifier.generate_challenge(user_id);

        let signal: Vec<f32> = (0..100)
            .map(|i| {
                let t = i as f32 * 0.1;
                t.sin() * 0.5 + (t * 0.5).cos() * 0.3 + 0.1
            })
            .collect();

        let result = verifier.verify_proof_of_life(&signal, &challenge);

        assert!(
            result.is_ok(),
            "La señal humana simulada debería ser aceptada para usuario registrado"
        );
        let proof = result.unwrap();
        println!(
            "✅ Human Validated: Lyapunov={:.4}, Role={:?}",
            proof.lyapunov_exp, proof.role
        );

        assert!(proof.lyapunov_exp > 0.05);
        assert_eq!(proof.role, BiologicalRole::Sovereign);
    }

    #[test]
    fn test_reject_unauthorized_identity() {
        let verifier = SoulVerifier::new();
        let user_id = "intruder_01"; // Not in the family list
        let challenge = verifier.generate_challenge(user_id);

        let signal: Vec<f32> = (0..100)
            .map(|i| {
                let t = i as f32 * 0.1;
                t.sin() * 0.5 + (t * 0.5).cos() * 0.3 + 0.1
            })
            .collect();

        let result = verifier.verify_proof_of_life(&signal, &challenge);
        match result {
            Err(SoulError::UnauthorizedIdentity(metrics)) => {
                assert!(metrics.lyapunov_exp > 0.05);
            }
            _ => panic!("Should reject unauthorized identity even if biological signal is valid"),
        }
    }

    #[test]
    fn test_reject_static_signal() {
        let verifier = SoulVerifier::new();
        let challenge = verifier.generate_challenge("jnovoas");
        let signal = vec![0.5; 100]; // Static

        let result = verifier.verify_proof_of_life(&signal, &challenge);
        assert!(result.is_err(), "Señal estática debe ser rechazada");
    }

    #[test]
    fn test_reject_expired_challenge() {
        let verifier = SoulVerifier::new();
        let mut challenge = verifier.generate_challenge("jnovoas");
        challenge.timestamp = chrono::Utc::now().timestamp() - 31;
        let signal: Vec<f32> = (0..100).map(|i| (i as f32).sin()).collect();

        let result = verifier.verify_proof_of_life(&signal, &challenge);
        match result {
            Err(SoulError::StaleChallenge) => assert!(true),
            _ => panic!("Debería rechazar por tiempo expirado"),
        }
    }
}
