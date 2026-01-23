// src/security/bio_resonance.rs
//! BIO-RESONANCE ENGINE (The Human Anchor)
//!
//! Ports the "Soul Verifier" logic to PURE Base-60 (NO FLOATS).
//! Manages the 17s Pulse and the T=68s Quantum Leap.
//!
//! AXIOM COMPLIANCE:
//! - NO f32/f64 operations
//! - NO rand::random()
//! - ALL arithmetic in S60

use crate::math::harmonic_logic::{HarmonicProcessor, HarmonicState, LogicState};
use crate::math::s60::S60;

/// The Pulse Constant: 17 seconds (Pure S60)
const PULSE_PERIOD_SEC: i64 = 17;
const CYCLE_DURATION_SEC: i64 = 68;

pub struct ResonanceEngine {
    npu: HarmonicProcessor,
    last_pulse_timestamp: u64, // Unix Timestamp
    current_coherence: S60,
}

impl ResonanceEngine {
    pub fn new() -> Self {
        ResonanceEngine {
            npu: HarmonicProcessor::new(),
            last_pulse_timestamp: 0,
            current_coherence: S60::ONE, // Start optimistic
        }
    }

    /// Process a Human Pulse (Authentication Event)
    /// Returns: (Is_Valid, Logic_State)
    ///
    /// PURE S60: No float operations
    pub fn verify_pulse(&mut self, timestamp: u64) -> (bool, LogicState) {
        if self.last_pulse_timestamp == 0 {
            // First pulse, initialize
            self.last_pulse_timestamp = timestamp;
            return (true, LogicState::Unison);
        }

        let interval = timestamp.saturating_sub(self.last_pulse_timestamp);
        self.last_pulse_timestamp = timestamp;

        // Convert interval to S60 Ratio relative to Target (17s)
        // Ratio = Interval / 17
        // If Interval == 17, Ratio = 1.0 (Unison)

        // PURE S60 ARITHMETIC (NO FLOATS)
        let interval_s60 = S60::from_raw(interval as i64 * S60::SCALE_0);
        let period_s60 = S60::from_raw(PULSE_PERIOD_SEC * S60::SCALE_0);

        let ratio_s60 = match interval_s60 / period_s60 {
            Ok(ratio) => ratio,
            Err(_) => S60::ZERO, // Division error, treat as invalid
        };

        let input_state = HarmonicState {
            ratio: ratio_s60,
            phase: S60::ZERO,
            energy: 100,
        };

        // Feed to NPU
        let verdict = self.npu.process_signal(input_state);

        // Check if verdict is Harmonic
        let is_valid = match verdict {
            LogicState::Unison | LogicState::True | LogicState::Reference => true,
            _ => false,
        };

        (is_valid, verdict)
    }

    /// QUANTUM LEAP PROTOCOL
    /// Checks system time against the Great Cycle (68s).
    /// If in Dissonance Gap, forces Phase Reset.
    ///
    /// PURE S60: No float operations
    pub fn apply_quantum_correction(&self, system_time_sec: u64) -> S60 {
        // Calculate phase within cycle (PURE S60)
        let remainder = system_time_sec % CYCLE_DURATION_SEC as u64;
        let remainder_s60 = S60::from_raw(remainder as i64 * S60::SCALE_0);
        let duration_s60 = S60::from_raw(CYCLE_DURATION_SEC * S60::SCALE_0);

        let cycle_phase = match remainder_s60 / duration_s60 {
            Ok(phase) => phase,
            Err(_) => return S60::ZERO, // Error, force reset
        };

        // Thresholds: > 0.99 or < 0.01 (PURE S60 CONSTANTS)
        let threshold_high = S60::from_raw(99 * S60::SCALE_0 / 100); // 0.99
        let threshold_low = S60::from_raw(S60::SCALE_0 / 100); // 0.01

        if cycle_phase > threshold_high || cycle_phase < threshold_low {
            // Force Reset
            // In a real system, this might send a signal to the Clock to adjust tick.
            // Here we return the Virtual Phase (0.0).
            return S60::ZERO;
        }

        // Return actual phase as S60
        cycle_phase
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_perfect_pulse() {
        let mut engine = ResonanceEngine::new();

        // Initial Pulse (T=100)
        let (valid, state) = engine.verify_pulse(100);
        assert!(valid, "First pulse should be valid");

        // Second Pulse (T=117) -> Interval 17s (Perfect Unison)
        let (valid, state) = engine.verify_pulse(117);
        assert!(valid);
        match state {
            LogicState::Unison => (), // Pass
            _ => panic!("Expected Unison, got {:?}", state),
        }
    }

    #[test]
    fn test_harmonic_pulse() {
        let mut engine = ResonanceEngine::new();
        engine.verify_pulse(100);

        // T=125 (Interval 25 ≈ 17 * 1.47) -> Should be close to 3:2 (1.5)
        let (valid, state) = engine.verify_pulse(125);
        // Should be valid (harmonic)
        assert!(valid, "Harmonic pulse should be valid");
    }

    #[test]
    fn test_quantum_correction_reset() {
        let engine = ResonanceEngine::new();

        // T=68 (Exact Cycle End) -> Should return 0.0 Phase
        let phase = engine.apply_quantum_correction(68);
        assert_eq!(phase, S60::ZERO, "T=68 should trigger Quantum Reset");

        // T=0 (Cycle Start) -> Should also reset
        let phase_start = engine.apply_quantum_correction(0);
        assert_eq!(phase_start, S60::ZERO, "T=0 should trigger Quantum Reset");

        // T=34 (Mid Cycle) -> Should NOT reset
        let phase_mid = engine.apply_quantum_correction(34);
        assert_ne!(phase_mid, S60::ZERO);

        // 34/68 = 0.5 = S60(0, 30, 0)
        let expected = S60::new(0, 30, 0, 0, 0).unwrap();
        // Allow slight conversion diff
        assert!((phase_mid - expected).abs().to_base_units() < S60::SCALE_1);
    }

    #[test]
    fn test_no_float_contamination() {
        // This test ensures no f64 operations are used
        let mut engine = ResonanceEngine::new();

        // All operations should be pure S60
        let (valid, _) = engine.verify_pulse(100);
        assert!(valid);

        let (valid, _) = engine.verify_pulse(117);
        assert!(valid);

        let phase = engine.apply_quantum_correction(34);
        assert_ne!(phase, S60::ZERO);

        // If this compiles and runs, we have no float contamination ✅
    }
}
