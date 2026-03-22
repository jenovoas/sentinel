// src/security/bio_resonance.rs
//! BIO-RESONANCE ENGINE (The Human Anchor)
//!
//! Ports the "Soul Verifier" logic to PURE Base-60 (60^4 accuracy).

use crate::math::harmonic_logic::{HarmonicProcessor, HarmonicState, LogicState};
use me60os_core::spa::SPA as S60;

const PULSE_PERIOD_SEC: i64 = 17;
#[allow(dead_code)]
const CYCLE_DURATION_SEC: i64 = 68;

pub struct ResonanceEngine {
    npu: HarmonicProcessor,
    last_pulse_timestamp: u64,
    current_coherence: S60,
}

impl ResonanceEngine {
    pub fn new() -> Self {
        ResonanceEngine {
            npu: HarmonicProcessor::new(),
            last_pulse_timestamp: 0,
            current_coherence: S60::one(),
        }
    }

    pub fn verify_pulse(&mut self, timestamp: u64) -> (bool, LogicState) {
        if self.last_pulse_timestamp == 0 {
            self.last_pulse_timestamp = timestamp;
            self.current_coherence = S60::one();
            return (true, LogicState::Unison);
        }

        let interval = timestamp.saturating_sub(self.last_pulse_timestamp);
        self.last_pulse_timestamp = timestamp;

        let interval_s60 = S60::from_int(interval as i64);
        let period_s60 = S60::from_int(PULSE_PERIOD_SEC);

        let ratio_s60 = interval_s60.div_safe(period_s60).unwrap_or(S60::zero());
        self.current_coherence = ratio_s60;

        let input_state = HarmonicState {
            ratio: ratio_s60,
            phase: S60::zero(),
            energy: 100,
        };

        let verdict = self.npu.process_signal(input_state);
        let is_valid = match verdict {
            LogicState::Unison | LogicState::True | LogicState::Reference => true,
            _ => false,
        };

        (is_valid, verdict)
    }

    #[allow(dead_code)]
    pub fn get_coherence_raw(&self) -> i64 {
        self.current_coherence.to_raw()
    }

    #[allow(dead_code)]
    pub fn apply_quantum_correction(&self, system_time_sec: u64) -> S60 {
        let remainder = system_time_sec % CYCLE_DURATION_SEC as u64;
        let remainder_s60 = S60::from_int(remainder as i64);
        let duration_s60 = S60::from_int(CYCLE_DURATION_SEC);

        let cycle_phase = remainder_s60.div_safe(duration_s60).unwrap_or(S60::zero());

        let threshold_high = S60::from_raw(99 * S60::SCALE_0 / 100);
        let threshold_low = S60::from_raw(S60::SCALE_0 / 100);

        if cycle_phase > threshold_high || cycle_phase < threshold_low {
            return S60::zero();
        }
        cycle_phase
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_perfect_pulse() {
        let mut engine = ResonanceEngine::new();
        engine.verify_pulse(100);
        let (valid, state) = engine.verify_pulse(117);
        assert!(valid);
        assert_eq!(state, LogicState::Unison);
    }
}
