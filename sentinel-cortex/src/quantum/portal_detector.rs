// src/quantum/portal_detector.rs
//! Portal Detector - Penta-Resonance Convergence

use crate::math::s60::S60;
use crate::math::s60_math::sin_s60;

/// Portal Detector - Detects harmonic convergence across 5 layers
pub struct PortalDetector {
    period_bio: S60,
    period_crystal: S60,
    period_venus: S60,
    threshold: S60,
}

impl PortalDetector {
    pub fn new() -> Self {
        PortalDetector {
            period_bio: S60::from_int(17),
            // 4;15,0,0 = 4 * 216,000 + 15 * 3,600 = 918,000
            period_crystal: S60::from_raw(4 * S60::SCALE_0 + 15 * S60::SCALE_1),
            // 16;10,48 = 16 * 216,000 + 10 * 3,600 + 48 * 60 = 3,492,480
            period_venus: S60::from_raw(16 * S60::SCALE_0 + 10 * S60::SCALE_1 + 48 * S60::SCALE_2),
            // 0;45 = 45 * 3,600 = 162,000
            threshold: S60::from_raw(45 * S60::SCALE_1),
        }
    }

    pub fn calculate_resonance(&self, t: S60) -> S60 {
        let two_pi = S60::two_pi();

        // phase = (two_pi * t) / period
        let phase_bio = match (two_pi * t) / self.period_bio {
            Ok(p) => sin_s60(p),
            Err(_) => S60::zero(),
        };
        let phase_crystal = match (two_pi * t) / self.period_crystal {
            Ok(p) => sin_s60(p),
            Err(_) => S60::zero(),
        };
        let phase_venus = match (two_pi * t) / self.period_venus {
            Ok(p) => sin_s60(p),
            Err(_) => S60::zero(),
        };

        let sum = phase_bio + phase_crystal + phase_venus;
        match sum / S60::from_int(3) {
            Ok(avg) => avg,
            Err(_) => S60::zero(),
        }
    }

    pub fn is_portal_open(&self, t: S60) -> bool {
        self.calculate_resonance(t) > self.threshold
    }

    pub fn get_portal_intensity(&self, t: S60) -> S60 {
        let res = self.calculate_resonance(t);
        if res > self.threshold { res } else { S60::zero() }
    }
}

