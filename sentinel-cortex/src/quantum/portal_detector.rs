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
            // 16.18 = 16 + 0.18
            // 0.18 * 60 = 10.8 minutes
            // 0.8 * 60 = 48 seconds
            period_venus: S60::new(16, 10, 48, 0, 0).unwrap(),

            // Threshold for portal detection: 0.75 (45/60)
            threshold: S60::new(0, 45, 0, 0, 0).unwrap(),
        }
    }

    /// Calculate penta-resonance value at time t
    ///
    /// Returns combined resonance value in range [-1, 1]
    /// Formula: (sin(2π*t/T_bio) + sin(2π*t/T_crystal) + sin(2π*t/T_venus)) / 3
    ///
    /// # Arguments
    /// * `t` - Current time (in seconds as S60)
    ///
    /// # Returns
    /// * `S60` - Resonance value, normalized to [-1, 1]
    pub fn calculate_resonance(&self, t: S60) -> S60 {
        let two_pi = S60::two_pi();

        // Phase for each layer: φ = 2π * t / T

        // Bio layer: φ_bio = sin(2π * t / T_bio)
        let phase_bio_arg = match (two_pi * t) / self.period_bio {
            Ok(val) => val,
            Err(_) => S60::zero(),
        };
        let phase_bio = sin_s60(phase_bio_arg);

        // Crystal layer: φ_crystal = sin(2π * t / T_crystal)
        let phase_crystal_arg = match (two_pi * t) / self.period_crystal {
            Ok(val) => val,
            Err(_) => S60::zero(),
        };
        let phase_crystal = sin_s60(phase_crystal_arg);

        // Venus layer: φ_venus = sin(2π * t / T_venus)
        let phase_venus_arg = match (two_pi * t) / self.period_venus {
            Ok(val) => val,
            Err(_) => S60::zero(),
        };
        let phase_venus = sin_s60(phase_venus_arg);

        // Average of 3 layers
        let sum = phase_bio + phase_crystal + phase_venus;
        let three = S60::from_int(3);

        match sum / three {
            Ok(avg) => avg,
            Err(_) => S60::zero(),
        }
    }

    /// Check if portal is open at time t
    ///
    /// A portal is "open" when resonance > threshold (0.75)
    ///
    /// # Arguments
    /// * `t` - Current time (in seconds as S60)
    ///
    /// # Returns
    /// * `bool` - True if portal is open
    pub fn is_portal_open(&self, t: S60) -> bool {
        let resonance = self.calculate_resonance(t);
        resonance > self.threshold
    }

    /// Get individual layer phases (for telemetry/debugging)
    ///
    /// Returns (bio_phase, crystal_phase, venus_phase)
    pub fn get_layer_phases(&self, t: S60) -> (S60, S60, S60) {
        let two_pi = S60::two_pi();

        let phase_bio_arg = match (two_pi * t) / self.period_bio {
            Ok(val) => val,
            Err(_) => S60::zero(),
        };
        let phase_bio = sin_s60(phase_bio_arg);

        let phase_crystal_arg = match (two_pi * t) / self.period_crystal {
            Ok(val) => val,
            Err(_) => S60::zero(),
        };
        let phase_crystal = sin_s60(phase_crystal_arg);

        let phase_venus_arg = match (two_pi * t) / self.period_venus {
            Ok(val) => val,
            Err(_) => S60::zero(),
        };
        let phase_venus = sin_s60(phase_venus_arg);

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

        // Verify periods
        assert_eq!(detector.period_bio, S60::from_int(17));
        assert_eq!(detector.period_crystal, S60::new(4, 15, 0, 0, 0).unwrap());
    }

    #[test]
    fn test_resonance_at_zero() {
        let detector = PortalDetector::new();
        let t_zero = S60::zero();

        // At t=0, all sins should be ~0, so resonance ~ 0
        let resonance = detector.calculate_resonance(t_zero);

        // Should be close to zero (allowing for computational error)
        assert!(resonance.to_base_units().abs() < 1000); // Very small
    }

    #[test]
    fn test_portal_not_always_open() {
        let detector = PortalDetector::new();

        // Test at multiple points - not all should be portals
        let times = vec![
            S60::from_int(0),
            S60::from_int(5),
            S60::from_int(10),
            S60::from_int(15),
        ];

        let open_count = times
            .iter()
            .filter(|&&t| detector.is_portal_open(t))
            .count();

        // Not all times should have open portals (EXP-028 showed ~1.18% portal time)
        assert!(open_count < times.len());
    }
}
