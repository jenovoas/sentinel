// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 💎 RESONANT CRYSTAL - SPA Piezoelectric Oscillator 💎
//!
//! Pure Rust implementation of the Resonant Crystal memory cell.
//! Migrated from quantum/isochronous_oscillator.py with zero functionality loss.
//!
//! Uses existing SPAMath functions (sin, cos, exp) for oscillation and damping.

use crate::spa::SPA;
use crate::spa_math::SPAMath;
#[cfg(feature = "extension-module")]
use pyo3::prelude::*;

use serde::{Deserialize, Serialize};

/// Resonant Crystal: Piezoelectric oscillator tuned to Base-60 mathematics.
/// Acts as a resonant memory cell in the Quantum Matrix.
#[cfg_attr(feature = "extension-module", pyclass)]
#[repr(C)]
#[derive(Clone, Debug, Copy, Serialize, Deserialize)] // Copy is needed for simple struct, but String inside prevents it? No, fixed size buffer prevents String.
                                                      // Wait, I changed it to name: [u8; 32], so it is Copy.
pub struct IsochronousOscillator {
    /// Fixed-size name buffer for SHM compatibility (32 bytes)
    pub name: [u8; 32],
    /// Natural frequency derived from Plimpton 322 (Row 17 tuned)
    pub natural_frequency: SPA,
    /// Internal energy state (vibration amplitude)
    pub amplitude: SPA,
    /// Current oscillation phase
    pub phase: SPA,
    /// Damping factor (Q-Factor): controlled loss per cycle
    /// SPA(0, 0, 30) = 30/3600 ≈ 0.0083 loss per tick
    pub damping_factor: SPA,
}

impl Default for IsochronousOscillator {
    fn default() -> Self {
        Self::new("Quartz-SPA")
    }
}

impl IsochronousOscillator {
    /// Creates a new crystal with default Plimpton 322 Row 17 resonance.
    pub fn new(name_str: &str) -> Self {
        let mut name = [0u8; 32];
        let bytes = name_str.as_bytes();
        let len = bytes.len().min(32);
        name[..len].copy_from_slice(&bytes[..len]);

        Self {
            name,
            // Uses existing constant from spa_math.rs
            natural_frequency: SPAMath::AXION_RESONANCE_RATIO,
            amplitude: SPA::zero(),
            phase: SPA::zero(),
            // Damping: SPA(0, 0, 30) = 30 seconds = 0.5 degrees loss
            damping_factor: SPA::new(0, 0, 30, 0, 0),
        }
    }

    /// Creates a crystal with custom frequency.
    pub fn with_frequency(name_str: &str, freq: SPA) -> Self {
        let mut name = [0u8; 32];
        let bytes = name_str.as_bytes();
        let len = bytes.len().min(32);
        name[..len].copy_from_slice(&bytes[..len]);

        Self {
            name,
            natural_frequency: freq,
            amplitude: SPA::zero(),
            phase: SPA::zero(),
            damping_factor: SPA::new(0, 0, 30, 0, 0),
        }
    }

    /// Helper to get name as String
    pub fn get_name(&self) -> String {
        let len = self.name.iter().position(|&c| c == 0).unwrap_or(32);
        String::from_utf8_lossy(&self.name[..len]).to_string()
    }

    /// Injects an energy pulse based on 'data pressure'.
    /// Translates external impulses into vibratory amplitude.
    pub fn transduce_pulse(&mut self, data_pressure: i64) {
        let input_force = SPA::new(data_pressure, 0, 0, 0, 0);
        // Force adds to current amplitude (constructive excitation)
        self.amplitude = self.amplitude + input_force;
    }

    /// Applies thermodynamic degradation (entropy).
    /// Loss is proportional to Amplitude and time elapsed.
    /// Returns the decay amount.
    pub fn apply_entropy(&mut self, dt: SPA) -> SPA {
        // Decay = A * lambda * dt
        // Using SPA multiplication: (amplitude * damping) / SCALE then * dt
        let decay = (self.amplitude * self.damping_factor) / SPA::new(1, 0, 0, 0, 0);
        let decay = (decay * dt) / SPA::new(1, 0, 0, 0, 0);

        self.amplitude = self.amplitude - decay;

        // Ground state check (prevent negative amplitude from precision)
        if self.amplitude.to_raw() < SPA::new(0, 0, 0, 0, 1).to_raw() {
            self.amplitude = SPA::zero();
        }

        decay
    }

    /// Advances time, calculates vibratory state and applies entropy.
    /// Returns the output signal (amplitude * sin(phase)).
    pub fn oscillate(&mut self, dt: SPA) -> SPA {
        // 1. Advance Phase: theta = omega * t
        let delta_phase = (self.natural_frequency * dt) / SPA::new(1, 0, 0, 0, 0);
        self.phase = self.phase + delta_phase;

        // 2. Calculate Signal via SPAMath::sin (Taylor series)
        let signal_wave = SPAMath::sin(self.phase);
        let output_signal = (self.amplitude * signal_wave) / SPA::new(1, 0, 0, 0, 0);

        // 3. Apply physical entropy
        self.apply_entropy(dt);

        output_signal
    }

    /// Returns the current stored energy (amplitude).
    pub fn get_amplitude(&self) -> SPA {
        self.amplitude
    }

    /// Returns the current phase.
    pub fn get_phase(&self) -> SPA {
        self.phase
    }

    /// Resets the crystal to ground state.
    pub fn reset(&mut self) {
        self.amplitude = SPA::zero();
        self.phase = SPA::zero();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crystal_creation() {
        let crystal = IsochronousOscillator::new("Test-Crystal");
        assert_eq!(crystal.amplitude, SPA::zero());
        assert_eq!(crystal.natural_frequency, SPAMath::AXION_RESONANCE_RATIO);
    }

    #[test]
    fn test_pulse_injection() {
        let mut crystal = IsochronousOscillator::new("Test-Crystal");
        crystal.transduce_pulse(60);
        assert_eq!(crystal.amplitude, SPA::new(60, 0, 0, 0, 0));

        crystal.transduce_pulse(30);
        assert_eq!(crystal.amplitude, SPA::new(90, 0, 0, 0, 0));
    }

    #[test]
    fn test_oscillation() {
        let mut crystal = IsochronousOscillator::new("Test-Crystal");
        crystal.transduce_pulse(60);

        let dt = SPA::new(0, 1, 0, 0, 0); // 1 minute step

        for i in 0..12 {
            let signal = crystal.oscillate(dt);
            println!(
                "T{:02}: Amplitude={} Signal={}",
                i, crystal.amplitude, signal
            );
        }

        // After 12 steps with damping, amplitude should be reduced
        assert!(crystal.amplitude < SPA::new(60, 0, 0, 0, 0));
    }

    #[test]
    fn test_entropy_decay() {
        let mut crystal = IsochronousOscillator::new("Test-Crystal");
        crystal.transduce_pulse(100);

        let dt = SPA::new(1, 0, 0, 0, 0); // 1 degree step
        let initial = crystal.amplitude;

        crystal.apply_entropy(dt);

        assert!(crystal.amplitude < initial);
        println!(
            "Initial: {} -> After entropy: {}",
            initial, crystal.amplitude
        );
    }
}
