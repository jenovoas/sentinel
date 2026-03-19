// src/quantum/portal_detector.rs
//! Portal Detector - Penta-Resonance Convergence
//!
//! Implements the algorithm from EXP-028 to detect "portals" (harmonic convergence windows)
//! across multiple resonance layers using pure S60 arithmetic.

use crate::math::s60::S60;
use crate::math::s60_math::sin_s60;

/// Portal Detector - Detects harmonic convergence across 5 layers
///
/// Layers:
/// 1. Bio: Human pulse rhythm (~17s period)
/// 2. Crystal: TimeCrystalClock rhythm (~4.25s period, 17/4)
/// 3. Venus: Planetary resonance (~16.18s, Phi-based)
/// 4. System: Salto-17 correction (68s implicit)
/// 5. Geoglyphs: Static anchor (implicit)
///
/// A "portal" occurs when layers 1-3 simultaneously peak (amplitude > threshold)
pub struct PortalDetector {
    /// Bio layer period (17 seconds)
    period_bio: S60,
    /// Crystal layer period (4.25 seconds = 17/4)
    period_crystal: S60,
    /// Venus layer period (16.18 seconds, Phi-based)
    period_venus: S60,
    /// Portal threshold (0.75 = 45 minutes in S60)
    threshold: S60,
}

impl PortalDetector {
    /// Create new PortalDetector with standard periods
    pub fn new() -> Self {
        PortalDetector {
            // T_bio = 17;0,0,0,0 (17 seconds exactly)
            period_bio: S60::from_int(17),

            // T_crystal = 4;15,0,0,0 (4.25s = 4 + 15/60 seconds)
            period_crystal: S60::new(4, 15, 0, 0, 0).unwrap(),

            // T_venus = 16;10,48,0,0 (16.18s ≈ 16 + 10/60 + 48/3600)
            period_venus: S60::new(16, 10, 48, 0, 0).unwrap(),

            // Threshold for portal detection: 0.75 (45/60)
            threshold: S60::new(0, 45, 0, 0, 0).unwrap(),
        }
    }

    /// Calculate penta-resonance value at time t
    ///
    /// Returns combined resonance value in range [-1, 1]
    /// Formula: (sin(2π*t/T_bio) + sin(2π*t/T_crystal) + sin(2π*t/T_venus)) / 3
    pub fn calculate_resonance(&self, t: S60) -> S60 {
        let two_pi = S60::two_pi();

        // Phase for each layer: φ = 2π * t / T
        // Division returns Result, unwrap to ZERO on error (division by zero protection)
        let phase_bio = sin_s60(((two_pi * t) / self.period_bio).unwrap_or(S60::ZERO));
        let phase_crystal = sin_s60(((two_pi * t) / self.period_crystal).unwrap_or(S60::ZERO));
        let phase_venus = sin_s60(((two_pi * t) / self.period_venus).unwrap_or(S60::ZERO));

        // Average of 3 layers
        let sum = phase_bio + phase_crystal + phase_venus;
        let three = S60::from_int(3);

        (sum / three).unwrap_or(S60::ZERO)
    }

    /// Check if portal is open at time t
    pub fn is_portal_open(&self, t: S60) -> bool {
        let resonance = self.calculate_resonance(t);
        resonance > self.threshold
    }

    /// Get individual layer phases (for telemetry/debugging)
    pub fn get_layer_phases(&self, t: S60) -> (S60, S60, S60) {
        let two_pi = S60::two_pi();

        let phase_bio = sin_s60(((two_pi * t) / self.period_bio).unwrap_or(S60::ZERO));
        let phase_crystal = sin_s60(((two_pi * t) / self.period_crystal).unwrap_or(S60::ZERO));
        let phase_venus = sin_s60(((two_pi * t) / self.period_venus).unwrap_or(S60::ZERO));

        (phase_bio, phase_crystal, phase_venus)
    }

    /// Get portal intensity (resonance value if open, else 0)
    pub fn get_portal_intensity(&self, t: S60) -> S60 {
        let resonance = self.calculate_resonance(t);
        if resonance > self.threshold {
            resonance
        } else {
            S60::zero()
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_portal_detector_creation() {
        let detector = PortalDetector::new();
        assert_eq!(detector.period_bio, S60::from_int(17));
    }

    #[test]
    fn test_resonance_at_zero() {
        let detector = PortalDetector::new();
        let t_zero = S60::zero();
        let resonance = detector.calculate_resonance(t_zero);
        // At t=0, all sins should be 0
        assert_eq!(resonance.to_base_units(), 0);
    }
}
