// src/quantum/bio_resonator.rs
//! BioResonator: Bio-Quantum Coherence Engine
//!
//! Translates biological events (keyboard/mouse) into quantum coherence states.
//! Implements the Bio-Centrism axiom (V) - The operator is the clock.

use crate::math::s60::S60;
use std::time::Instant;

/// Bio-Quantum Resonator
///
/// Maintains coherence state based on operator presence.
/// Implements Dead Man's Switch for emergency shutdown.
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
    /// Create new BioResonator with default parameters
    pub fn new() -> Self {
        BioResonator {
            coherence: S60::ZERO,

            // Decay: 0;0,5,0,0 = 5 arcseconds per tick (slow entropy)
            // This means: ~1 arcminute per 12 ticks @ 41Hz = ~0.3s to decay fully if idle
            decay_factor: S60::new(0, 0, 5, 0, 0).unwrap(),

            // Gain: 0;5,0,0,0 = 5 arcminutes per pulse
            // This means: 12 pulses to reach full coherence
            pulse_gain: S60::new(0, 5, 0, 0, 0).unwrap(),

            // Portal threshold: 0;54,0,0,0 = 90% coherence (54/60 arcminutes)
            threshold_portal: S60::new(0, 54, 0, 0, 0).unwrap(),

            last_pulse: Instant::now(),

            // Dead Man's Switch: 30 seconds without pulse = pilot absent
            dead_man_threshold_ms: 30_000,
        }
    }

    /// Inject biological pulse (called from Python FFI on keyboard/mouse event)
    pub fn inject_bio_pulse(&mut self) {
        self.coherence = self.coherence + self.pulse_gain;

        // Clamp to S60::ONE (1;0,0,0,0) = maximum coherence
        if self.coherence > S60::ONE {
            self.coherence = S60::ONE;
        }

        // Update timestamp
        self.last_pulse = Instant::now();
    }

    /// Apply entropy decay (called by TimeCrystal each tick @ ~41Hz)
    pub fn tick_entropy(&mut self) {
        if self.coherence > S60::ZERO {
            self.coherence = self.coherence - self.decay_factor;

            // Floor at zero
            if self.coherence < S60::ZERO {
                self.coherence = S60::ZERO;
            }
        }
    }

    /// Check if bio-portal is open (coherence >= 90%)
    pub fn is_portal_open(&self) -> bool {
        self.coherence >= self.threshold_portal
    }

    /// Check if pilot is present (Dead Man's Switch)
    pub fn is_pilot_present(&self) -> bool {
        self.last_pulse.elapsed().as_millis() < self.dead_man_threshold_ms as u128
    }

    /// Get raw coherence value (for FFI/telemetry)
    pub fn get_coherence_raw(&self) -> i64 {
        self.coherence.to_base_units()
    }

    /// Get normalized coherence [0.0, 1.0] (for visualization)
    ///
    /// NOTE: This uses f64 ONLY for GUI display. Internal logic is S60 pure.
    pub fn get_coherence_normalized(&self) -> f64 {
        (self.coherence.to_base_units() as f64) / (S60::ONE.to_base_units() as f64)
    }

    /// Get time since last pulse (ms)
    pub fn time_since_pulse_ms(&self) -> u64 {
        self.last_pulse.elapsed().as_millis() as u64
    }

    /// Reset coherence to zero (emergency/manual reset)
    pub fn reset(&mut self) {
        self.coherence = S60::ZERO;
    }
}

impl Default for BioResonator {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;
    use std::time::Duration;

    #[test]
    fn test_bio_resonator_pulse_accumulation() {
        let mut bio = BioResonator::new();

        // Initially zero
        assert_eq!(bio.coherence, S60::ZERO);
        assert!(!bio.is_portal_open());

        // Inject 12 pulses (should reach ~100% with gain of 5 arcminutes each)
        for _ in 0..12 {
            bio.inject_bio_pulse();
        }

        // Should be at or near ONE
        assert!(bio.coherence >= bio.threshold_portal);
        assert!(bio.is_portal_open());
    }

    #[test]
    fn test_entropy_decay() {
        let mut bio = BioResonator::new();

        // Charge to full
        for _ in 0..15 {
            bio.inject_bio_pulse();
        }

        let initial = bio.coherence;

        // Apply decay
        for _ in 0..100 {
            bio.tick_entropy();
        }

        // Should have decayed
        assert!(bio.coherence < initial);
    }

    #[test]
    fn test_dead_man_switch() {
        let mut bio = BioResonator::new();
        bio.dead_man_threshold_ms = 100; // 100ms threshold for testing

        // Initially present
        assert!(bio.is_pilot_present());

        // Wait beyond threshold
        thread::sleep(Duration::from_millis(150));

        // Should be absent
        assert!(!bio.is_pilot_present());

        // Inject pulse
        bio.inject_bio_pulse();

        // Should be present again
        assert!(bio.is_pilot_present());
    }

    #[test]
    fn test_portal_threshold() {
        let mut bio = BioResonator::new();

        // Not open initially
        assert!(!bio.is_portal_open());

        // Inject pulses until portal opens
        for _ in 0..12 {
            bio.inject_bio_pulse();

            if bio.is_portal_open() {
                // Portal opened - coherence should be >= 90%
                let norm = bio.get_coherence_normalized();
                assert!(norm >= 0.9, "Portal opened at {}%", norm * 100.0);
                break;
            }
        }

        assert!(bio.is_portal_open());
    }
}
