// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/security/bio_resonance.rs
//! BIO-RESONANCE ENGINE (The Human Anchor)
//!
//! Ports the "Soul Verifier" logic to PURE Base-60 (60^4 accuracy).

use crate::math::harmonic_logic::{HarmonicProcessor, HarmonicState, LogicState};
use me60os_core::spa::SPA as S60;

#[allow(dead_code)]
const PULSE_PERIOD_SEC: i64 = 17;
#[allow(dead_code)]
const CYCLE_DURATION_SEC: i64 = 68;

pub struct ResonanceEngine {
    npu: HarmonicProcessor,
    last_pulse_timestamp: u64,
    current_coherence: S60,
    entropy_rate: S60,
}

impl Default for ResonanceEngine {
    fn default() -> Self {
        Self::new()
    }
}

impl ResonanceEngine {
    pub fn new() -> Self {
        ResonanceEngine {
            npu: HarmonicProcessor::new(),
            last_pulse_timestamp: 0,
            current_coherence: S60::zero(), // Start at zero, require "Charging"
            entropy_rate: S60::from_raw(S60::SCALE_0 / 100), // 1% decay per tick
        }
    }

    /// Explicitly inject a biological pulse (Human activity)
    pub fn inject_pulse(&mut self, _timestamp: u64) {
        let bonus = S60::from_raw(S60::SCALE_0 / 10); // +10% coherence per pulse
        let new_coherence = self.current_coherence + bonus;
        
        // Clamp to 1.0
        if new_coherence > S60::one() {
            self.current_coherence = S60::one();
        } else {
            self.current_coherence = new_coherence;
        }
        
        tracing::debug!("PULSE INJECTED. New Coherence: {:?}", self.current_coherence);
    }

    /// Decay coherence (Entropy)
    pub fn tick_entropy(&mut self) {
        if self.current_coherence > S60::zero() {
            let next = self.current_coherence - self.entropy_rate;
            if next < S60::zero() {
                self.current_coherence = S60::zero();
            } else {
                self.current_coherence = next;
            }
        }
    }

    /// Check if the system is "Coherent" enough to execute (Portal check)
    pub fn is_coherent(&self) -> bool {
        // Portal opens at 90% (S60: 54/60)
        let threshold = S60::new(0, 54, 0, 0, 0); 
        self.current_coherence >= threshold
    }

    pub fn verify_pulse(&mut self, timestamp: u64) -> (bool, LogicState) {
        // Base verification logic using HarmonicProcessor
        let input_state = HarmonicState {
            ratio: self.current_coherence,
            phase: S60::zero(),
            energy: 100,
        };

        let verdict = self.npu.process_signal(input_state);
        let is_valid = match verdict {
            LogicState::Unison | LogicState::True | LogicState::Reference => self.is_coherent(),
            _ => false,
        };

        self.last_pulse_timestamp = timestamp;
        (is_valid, verdict)
    }

    pub fn get_coherence_raw(&self) -> i64 {
        self.current_coherence.to_raw()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_perfect_pulse() {
        let mut engine = ResonanceEngine::new();
        // Cargar el motor al estado coherente (>90%) con pulsos biológicos
        for i in 0..10 {
            engine.inject_pulse(100 + i);
        }
        let (valid, state) = engine.verify_pulse(117);
        assert!(valid, "Engine debía estar cargado y validar correctamente a >90%");
        // Validacion S60 Logica pura
        assert_eq!(state, LogicState::Unison);
    }
}
