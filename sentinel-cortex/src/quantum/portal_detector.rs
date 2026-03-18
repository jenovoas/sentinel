// src/quantum/portal_detector.rs
//! Portal Detector - Penta-Resonance Convergence

use crate::math::s60::S60;
use crate::math::SPAMath;

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
            period_crystal: S60::new(4, 15, 0, 0, 0),
            period_venus: S60::new(16, 10, 48, 0, 0),
            threshold: S60::new(0, 45, 0, 0, 0),
        }
    }

    pub fn calculate_resonance(&self, t: S60) -> S60 {
        let two_pi = S60::two_pi();
        
        // Use direct SPAMath functions
        let phase_bio = SPAMath::sin((two_pi * t).div_safe(self.period_bio).unwrap_or(S60::zero()));
        let phase_crystal = SPAMath::sin((two_pi * t).div_safe(self.period_crystal).unwrap_or(S60::zero()));
        let phase_venus = SPAMath::sin((two_pi * t).div_safe(self.period_venus).unwrap_or(S60::zero()));

        let sum = phase_bio + phase_crystal + phase_venus;
        let three = S60::from_int(3);
        sum.div_safe(three).unwrap_or(S60::zero())
    }

    pub fn is_portal_open(&self, t: S60) -> bool {
        self.calculate_resonance(t) > self.threshold
    }

    pub fn get_portal_intensity(&self, t: S60) -> S60 {
        let res = self.calculate_resonance(t);
        if res > self.threshold { res } else { S60::zero() }
    }
}
