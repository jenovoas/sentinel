// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/quantum/bio_resonator.rs
//! BioResonator: Bio-Quantum Coherence Engine
//!
//! Translates biological events (keyboard/mouse) into quantum coherence states.

use crate::math::s60::S60;
use std::time::Instant;

/// Bio-Quantum Resonator
pub struct BioResonator {
    /// Current coherence level [0.0, 1.0] in S60
    pub coherence: S60,
    /// Decay factor per tick (entropy)
    decay_factor: S60,
    /// Gain per biological pulse
    pulse_gain: S60,
    /// Threshold for portal opening (0.9 = 90%)
    threshold_portal: S60,
    /// Last biological event timestamp
    last_pulse: Instant,
    /// Dead Man's Switch threshold (ms)
    dead_man_threshold_ms: u64,
}

impl BioResonator {
    pub fn new() -> Self {
        BioResonator {
            coherence: S60::zero(),
            decay_factor: S60::new(0, 0, 5, 0, 0).unwrap(),
            pulse_gain: S60::new(0, 5, 0, 0, 0).unwrap(),
            threshold_portal: S60::new(0, 54, 0, 0, 0).unwrap(),
            last_pulse: Instant::now(),
            dead_man_threshold_ms: 30_000,
        }
    }

    pub fn inject_bio_pulse(&mut self) {
        self.coherence = self.coherence + self.pulse_gain;
        if self.coherence > S60::one() {
            self.coherence = S60::one();
        }
        self.last_pulse = Instant::now();
    }

    pub fn tick_entropy(&mut self) {
        if self.coherence > S60::zero() {
            self.coherence = self.coherence - self.decay_factor;
            if self.coherence < S60::zero() {
                self.coherence = S60::zero();
            }
        }
    }

    pub fn is_portal_open(&self) -> bool { self.coherence >= self.threshold_portal }
    pub fn is_pilot_present(&self) -> bool { self.last_pulse.elapsed().as_millis() < self.dead_man_threshold_ms as u128 }
    pub fn get_coherence_raw(&self) -> i64 { self.coherence.to_base_units() }
    pub fn time_since_pulse_ms(&self) -> u64 { self.last_pulse.elapsed().as_millis() as u64 }
    pub fn reset(&mut self) { self.coherence = S60::zero(); }
}

impl Default for BioResonator {
    fn default() -> Self { Self::new() }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;
    use std::time::Duration;

    #[test]
    fn test_bio_accumulation() {
        let mut bio = BioResonator::new();
        for _ in 0..12 { bio.inject_bio_pulse(); }
        assert!(bio.is_portal_open());
    }
}
