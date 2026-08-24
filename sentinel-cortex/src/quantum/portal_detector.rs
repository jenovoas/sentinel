// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/quantum/portal_detector.rs
//! Portal Detector - Penta-Resonance Convergence
//
// Penta-resonance convergence detector; consumed by the quantum scheduler.
#![allow(dead_code)]

use crate::math::s60::S60;
use crate::math::s60_math::sin_s60;

/// Portal Detector - Detects harmonic convergence across 5 layers
pub struct PortalDetector {
    period_bio: S60,
    period_crystal: S60,
    period_venus: S60,
    threshold: S60,
}

impl Default for PortalDetector {
    fn default() -> Self {
        Self::new()
    }
}

impl PortalDetector {
    pub fn new() -> Self {
        PortalDetector {
            // EXP-028 / me60os_core::bin::exp028_system_portals
            // Periodos en S60 (1.0 unidad = 1 segundo, definicion operativa)
            period_bio: S60::from_int(17), // 17s (pulso humano / operador)
            // 4.25s = 17/4 (cristal YHWH, 4 ciclos por ciclo bio)
            // raw = 4 * SCALE_0 + 15 * SCALE_1 = 51_840_000 + 3_240_000 = 55_080_000
            period_crystal: S60::from_raw(4 * S60::SCALE_0 + 15 * S60::SCALE_1),
            // 16.18s (Venus Phi-ratio 13:8)
            // raw = 16 * SCALE_0 + 10 * SCALE_1 + 48 * SCALE_2 = 207_360_000 + 2_160_000 + 172_800 = 209_692_800
            period_venus: S60::from_raw(16 * S60::SCALE_0 + 10 * S60::SCALE_1 + 48 * S60::SCALE_2),
            // 0.75 umbral (45/60 = 3/4 en base 60)
            // raw = 45 * SCALE_1 = 45 * 216_000 = 9_720_000
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

