// src/security/soul_verifier.rs
use sha3::{Digest, Sha3_512};
use ndarray::{Array1, ArrayView1};
use std::collections::HashMap;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct AlmaChallenge {
    pub nonce: u64,
    pub light_sequence: Vec<u8>,
    pub timestamp: i64,
    pub user_id: String,
}

#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub enum SoulRole {
    Sovereign,
    Monitored,
    Guest,
    Unauthorized,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct SoulIdentity {
    pub name: String,
    pub role: SoulRole,
}

#[derive(Debug, Clone, Serialize)]
pub struct ProofOfLife {
    pub lyapunov_exp: f64,        // 0.1-2.5 (humano vivo)
    pub chaos_entropy: f64,       // 1.2-3.8 (no periódico)
    pub response_correlation: f64, // >0.7 (responde luz)
    pub soul_hash: String,
    pub timestamp: i64,
    pub identity: Option<SoulIdentity>,
}

#[derive(Debug)]
pub enum SoulError {
    StaleChallenge,
    NoLivingSoul,
    UnknownSoul(String),
    InsufficientSignal,
    UnauthorizedIdentity,
}

pub struct SoulVerifier {
    registered_souls: HashMap<String, SoulIdentity>, // UserID/Hash -> Identity
    challenge_seq: Vec<u8>,
}

impl SoulVerifier {
    pub fn new() -> Self {
        let mut souls = HashMap::new();
        
        // --- FAMILY REGISTRY (Simulated Hashes for MVP) ---
        // In production, keys would be the SHA3-512 Hash of their biological signature.
        // For now, we map UserID -> Identity to demonstrate RBAC logic.
        
        souls.insert("jnovoas".to_string(), SoulIdentity {
            name: "JNovoaS (Operator)".to_string(),
            role: SoulRole::Sovereign,
        });
        
         souls.insert("madre".to_string(), SoulIdentity {
            name: "Madre (Matriarch)".to_string(),
            role: SoulRole::Monitored,
        });

        souls.insert("cristian".to_string(), SoulIdentity {
            name: "Cristian (Strategist)".to_string(),
            role: SoulRole::Monitored,
        });

        souls.insert("diego".to_string(), SoulIdentity {
            name: "Diego (Guardian)".to_string(),
            role: SoulRole::Monitored,
        });
        
         souls.insert("madelin".to_string(), SoulIdentity {
            name: "Madelin (Sensitive)".to_string(),
            role: SoulRole::Monitored,
        });

        Self {
            registered_souls: souls,
            challenge_seq: vec![255, 0, 255], 
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
        rppg_signal: &[f32],  // Serie temporal brillo facial
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
        
        // c) Entropía caótica (no periódica, no random)
        let entropy = self.chaos_entropy(rppg_signal);
        
        // d) Hash biológico SHA3-512
        let soul_hash = self.compute_soul_hash(rppg_signal, &challenge.nonce.to_le_bytes());
        
        // e) Verificar umbrales de vida primero
        if lyapunov <= 0.05 || entropy <= 0.5 {
             return Err(SoulError::NoLivingSoul);
        }
        
        // f) Identificación y Control de Acceso (RBAC)
        // En el futuro: buscar soul_hash en registered_souls.
        // Ahora: usar user_id del challenge para simular el lookup.
        let identity = self.registered_souls.get(&challenge.user_id).cloned();
        
        // Si no está registrado o no es familia -> Rechazar (o Guest si implementáramos eso)
        if identity.is_none() {
             return Err(SoulError::UnauthorizedIdentity);
        }

        Ok(ProofOfLife {
            lyapunov_exp: lyapunov,
            chaos_entropy: entropy,
            response_correlation: light_response,
            soul_hash: soul_hash,
            timestamp: now,
            identity,
        })
    }

    fn calculate_lyapunov_exponent(&self, signal: &[f32]) -> f64 {
        // Implementación básica de estimación de caos (simulada math)
        // En producción usuaríamos algoritmo de Rosenstein
        let var = variance(signal);
        if var == 0.0 { return 0.0; }
        (var.ln().abs() % 2.5) // Fake pero determinista basado en señal
    }

    fn chaos_entropy(&self, signal: &[f32]) -> f64 {
        // Entropía de Shannon simplificada
       let mut counts = HashMap::new();
       for &val in signal {
           let bucket = (val * 10.0).round() as i32;
           *counts.entry(bucket).or_insert(0) += 1;
       }
       let len = signal.len() as f64;
       counts.values().fold(0.0, |acc, &count| {
           let p = count as f64 / len;
           acc - p * p.ln()
       })
    }

    fn correlate_light_challenge(&self, _rppg: &[f32], _light_seq: &[u8]) -> f64 {
        // Implementación futura: Correlación cruzada
        0.85 // Valor nominal de 'alta resonancia'
    }

    fn compute_soul_hash(&self, rppg: &[f32], nonce: &[u8]) -> String {
        let mut hasher = Sha3_512::new();
        // Convert f32 vec to bytes
        for val in rppg {
            hasher.update(val.to_be_bytes());
        }
        hasher.update(nonce);
        let hash = hasher.finalize();
        hex::encode(hash)
    }
}

fn variance(data: &[f32]) -> f64 {
    if data.is_empty() { return 0.0; }
    let mean = data.iter().sum::<f32>() as f64 / data.len() as f64;
    data.iter().map(|value| {
        let diff = mean - (*value as f64);
        diff * diff
    }).sum::<f64>() / data.len() as f64
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;
    use std::time::Duration;

    #[test]
    fn test_valid_human_signal() {
        let verifier = SoulVerifier::new();
        // Use a registered user to pass RBAC
        let user_id = "jnovoas"; 
        let challenge = verifier.generate_challenge(user_id);

        // Generar una señal "viva" (Seno + Ruido controlado)
        let signal: Vec<f32> = (0..100).map(|i| {
            let t = i as f32 * 0.1;
            t.sin() * 0.5 + (t * 0.5).cos() * 0.3 + 0.1
        }).collect();

        let result = verifier.verify_proof_of_life(&signal, &challenge);
        
        assert!(result.is_ok(), "La señal humana simulada debería ser aceptada para usuario registrado");
        let proof = result.unwrap();
        println!("✅ Human Validated: Lyapunov={:.4}, Identity={:?}", proof.lyapunov_exp, proof.identity);
        
        assert!(proof.lyapunov_exp > 0.05);
        assert_eq!(proof.identity.unwrap().role, SoulRole::Sovereign);
    }

    #[test]
    fn test_reject_static_signal() {
        let verifier = SoulVerifier::new();
        let challenge = verifier.generate_challenge("bot");

        // Señal plana (video congelado / foto)
        let signal = vec![0.5; 100];

        let result = verifier.verify_proof_of_life(&signal, &challenge);
        assert!(result.is_err(), "Señal estática debe ser rechazada");
    }

    #[test]
    fn test_reject_expired_challenge() {
        let verifier = SoulVerifier::new();
        let mut challenge = verifier.generate_challenge("sloth");
        
        // Manipular timestamp al pasado (-31s)
        challenge.timestamp = chrono::Utc::now().timestamp() - 31;
        
        // Señal válida
        let signal: Vec<f32> = (0..100).map(|i| (i as f32).sin()).collect();

        let result = verifier.verify_proof_of_life(&signal, &challenge);
        match result {
            Err(SoulError::StaleChallenge) => assert!(true),
            _ => panic!("Debería rechazar por tiempo expirado"),
        }
    }

    #[test]
    fn test_benchmark_verification_speed() {
        let verifier = SoulVerifier::new();
        let challenge = verifier.generate_challenge("bench_user");
        let signal: Vec<f32> = (0..300).map(|i| (i as f32 * 0.1).sin()).collect();

        let start = std::time::Instant::now();
        let iterations = 1000;
        
        for _ in 0..iterations {
            let _ = verifier.verify_proof_of_life(&signal, &challenge);
        }
        
        let duration = start.elapsed();
        println!("🚀 Benchmark: {} verificaciones en {:?}", iterations, duration);
        println!("⚡ Avg Time: {:?} per verification", duration / iterations);
        
        // Asegurar que es rápido (< 1ms por verify en release, <5ms en debug)
        assert!(duration.as_millis() < 5000, "La verificación es demasiado lenta");
    }
}
