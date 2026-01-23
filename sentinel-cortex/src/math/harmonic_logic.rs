// src/math/harmonic_logic.rs
//! HARMONIC LOGIC: Harmonic Processor Core
//!
//! Replaces Binary Logic (True/False) with Harmonic Logic (Consonance/Dissonance).
//!
//! Logic States:
//! - TRUE  = 3:2 (Perfect Fifth) => High Consonance
//! - FALSE = 45:32 (Tritone/Augmented Fourth) => High Dissonance
//! - MAYBE = 4:3 (Perfect Fourth) => Tension/Pending
//! - REF   = 10;5,6,5 (Divine Order / Reference) => Absolute Override
//!
//! Reference: `implementation_plan.md` (Sentinel v8.0)

use crate::math::s60::S60;
use std::fmt;

/// Logic Score: S60[0;0] (Pure Noise) to S60[1;0] (Pure Tonal Unity)
/// PURE S60: No float contamination
pub type CoherenceScore = S60;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum LogicState {
    Unison,    // 1:1 -> Nirvana (Stop/Coherence)
    True,      // 3:2 -> Direction (Accelerate)
    False,     // Tritone -> Disonancia (Phase Correct)
    Maybe,     // 4:3 -> Tension (Search)
    Reference, // Master Pattern (Override)
    Noise,     // Unknown
}

/// Represents a state in the Harmonic Processor
#[derive(Debug, Clone, Copy)]
pub struct HarmonicState {
    pub ratio: S60,  // Current frequency ratio relative to Root
    pub phase: S60,  // Phase offset (0-360 degrees)
    pub energy: u32, // "Amplitude" or confidence
}

impl HarmonicState {
    /// Create a new Harmonic State
    pub fn new(d: i32, m: u8, s: u8) -> Self {
        HarmonicState {
            ratio: S60::new(d, m, s, 0, 0).unwrap_or(S60::ZERO),
            phase: S60::ZERO,
            energy: 100,
        }
    }

    /// Define Standard Harmonic Logic Constants

    // TRUE: Perfect Fifth (3:2 = 1.5 = 1;30)
    pub fn logic_true() -> Self {
        HarmonicState::new(1, 30, 0)
    }

    // FALSE: Tritone (45:32 ≈ 1.40625 = 1;24,22,30)
    // Using simple approx 1;24 for dissonance marker
    pub fn logic_false() -> Self {
        HarmonicState::new(1, 24, 22)
    }

    // MAYBE: Perfect Fourth (4:3 = 1.333... = 1;20)
    pub fn logic_maybe() -> Self {
        HarmonicState::new(1, 20, 0)
    }

    // REFERENCE: The 10;5,6,5 pattern summation (Master Key)
    // 10/60 + 5/60 + 6/60 + 5/60 = 26/60 = 0.4333... = 0;26
    // But here we might represent it as the GEMATRIA VALUE itself: 26 (26;00)
    pub fn logic_ref() -> Self {
        HarmonicState::new(26, 0, 0)
    }

    /// Evaluate the "Truthiness" (Consonance) of the state
    pub fn evaluate_logic(&self) -> LogicState {
        // Get raw value for comparison
        let val = self.ratio.to_base_units();

        // Constants in raw S60 units
        let true_val = S60::new(1, 30, 0, 0, 0).unwrap().to_base_units();
        let maybe_val = S60::new(1, 20, 0, 0, 0).unwrap().to_base_units();
        let ref_val = S60::new(26, 0, 0, 0, 0).unwrap().to_base_units();
        let false_val = S60::new(1, 24, 22, 0, 0).unwrap().to_base_units();

        // Tolerance window: 3 minutes (0.05) to accommodate integer timestamp quantization
        // 17s period implies +/- 0.5s error => 0.5/17 = 0.029 deviation.
        // 1 min (0.016) is too strict. 2 min (0.033) is tight. 3 min (0.05) is safe.
        let minute = S60::new(0, 1, 0, 0, 0).unwrap();
        let three = S60::new(3, 0, 0, 0, 0).unwrap();
        let tolerance = (minute * three).to_base_units();

        if (val - ref_val).abs() < tolerance {
            LogicState::Reference
        } else if (val - S60::ONE.to_base_units()).abs() < tolerance {
            // Unison Check
            LogicState::Unison
        } else if (val - true_val).abs() < tolerance {
            LogicState::True
        } else if (val - maybe_val).abs() < tolerance {
            LogicState::Maybe
        } else if (val - false_val).abs() < tolerance * 2 {
            // Tritone detection (wider net for dissonance)
            LogicState::False
        } else {
            LogicState::Noise
        }
    }
}

pub trait HarmonicGate {
    fn h_and(a: HarmonicState, b: HarmonicState) -> HarmonicState;
    fn h_or(a: HarmonicState, b: HarmonicState) -> HarmonicState;
    fn h_not(a: HarmonicState) -> HarmonicState;
    fn h_xor(a: HarmonicState, b: HarmonicState) -> HarmonicState;
    fn phase_modulate(a: HarmonicState, tick: u64) -> HarmonicState;
}

impl HarmonicGate for HarmonicState {
    /// H-XOR: Harmonic Difference (Interval)
    /// Calculates the "Distance" between two states.
    /// A XOR B = Interval(A, B) = Max(A,B) / Min(A,B)
    /// Unison XOR Unison = 1.0 (Nirvana/Null)
    /// True XOR True = 1.0 (Nirvana/Null)
    /// True XOR Unison = True
    fn h_xor(a: HarmonicState, b: HarmonicState) -> HarmonicState {
        // Find Max and Min to calculate interval >= 1.0
        let (max, min) = if a.ratio.to_base_units() >= b.ratio.to_base_units() {
            (a.ratio, b.ratio)
        } else {
            (b.ratio, a.ratio)
        };

        // Interval = Max / Min (S60 / S60 division)
        let interval = max / min; // returns Result<S60, S60Error>
        let raw_ratio = interval.unwrap_or(S60::new(1, 0, 0, 0, 0).unwrap());

        // Phase Difference
        let diff_phase = if a.phase.to_base_units() >= b.phase.to_base_units() {
            a.phase - b.phase
        } else {
            b.phase - a.phase
        };

        HarmonicState {
            ratio: raw_ratio,
            phase: diff_phase,
            energy: (a.energy + b.energy) / 2, // Energy is conserved/averaged
        }
    }

    /// H-AND: Constructive Interference (Multiplication)
    /// Represents the combined harmonic product of two states.
    /// Example: 3:2 * 4:3 = 2:1 (Octave) -> Consonant result.
    fn h_and(a: HarmonicState, b: HarmonicState) -> HarmonicState {
        // Refined H-AND: Normalized Multiplication relative to Truth (3:2)
        // Keeps T*T=T and T*F=F
        let true_ratio = HarmonicState::logic_true().ratio;

        let product = a.ratio * b.ratio;
        // Divide by 3:2 (Truth reference)
        let normalized = product / true_ratio;
        let raw_product = normalized.unwrap_or(S60::ZERO); // Handle division error

        let phase_sum = a.phase + b.phase;
        let two = S60::new(2, 0, 0, 0, 0).unwrap();
        let phase_avg = phase_sum / two;

        HarmonicState {
            ratio: raw_product,
            phase: phase_avg.unwrap_or(S60::ZERO), // Avg phase
            energy: (a.energy + b.energy) / 2,
        }
    }

    /// H-OR: Superposition (Average)
    /// Represents the mixing of two signals.
    /// Example: (3:2 + 3:2)/2 = 3:2 (True + True = True)
    fn h_or(a: HarmonicState, b: HarmonicState) -> HarmonicState {
        let sum = a.ratio + b.ratio;
        let two = S60::new(2, 0, 0, 0, 0).unwrap();
        let avg = sum / two; // S60 division returns Result

        let phase_sum = a.phase + b.phase;
        let phase_avg = phase_sum / two;

        HarmonicState {
            ratio: avg.unwrap_or(S60::ZERO),
            phase: phase_avg.unwrap_or(S60::ZERO),
            energy: std::cmp::max(a.energy, b.energy),
        }
    }

    /// H-NOT: Inversion
    /// Inverts the interval relative to the Octave (2:1).
    /// NOT(3:2) = 2 / (3:2) = 4:3 (Fifth -> Fourth)
    /// NOT(Tritone) -> Inverted Tritone
    fn h_not(a: HarmonicState) -> HarmonicState {
        let octave = S60::new(2, 0, 0, 0, 0).unwrap();
        let inverse = octave / a.ratio;

        HarmonicState {
            ratio: inverse.unwrap_or(S60::ZERO),
            phase: a.phase + S60::new(180, 0, 0, 0, 0).unwrap(), // +180 deg phase shift
            energy: a.energy,
        }
    }

    /// Phase Modulation Gate: The 10;5,6,5 Modulator
    /// Injects the Reference Pattern to force resolution or modulation.
    /// Pattern: 10 -> 5 -> 6 -> 5
    fn phase_modulate(a: HarmonicState, tick: u64) -> HarmonicState {
        let pattern = match tick % 4 {
            0 => 10,
            1 => 5,
            2 => 6,
            3 => 5,
            _ => 10,
        };

        // Modulator: Add pattern/60 to the ratio?
        // Or Multiply?
        // Let's use it as a phase shifter or fine tuner.
        // Modulate phase by pattern degrees?
        // Pattern 10 -> 10/60 * 360 deg = 60 deg phase shift?
        // S60(pattern, 0,0) represents degrees if typically used.

        // Let's simply ADD the pattern as "minutes" to the ratio,
        // shifting the pitch slightly ("Breathing").
        // Ratio += pattern/60
        let shift = S60::new(0, pattern as u8, 0, 0, 0).unwrap();

        HarmonicState {
            ratio: a.ratio + shift,
            phase: a.phase,
            energy: 100, // Reference restores energy
        }
    }
}

/// The Harmonic Processor
/// Process logic streams using Harmonic Inteference
pub struct HarmonicProcessor {
    context: HarmonicState, // The current "thought" or harmonic context
    tick: u64,
}

impl HarmonicProcessor {
    pub fn new() -> Self {
        HarmonicProcessor {
            context: HarmonicState::logic_true(), // Start with Truth (3:2)
            tick: 0,
        }
    }

    /// Process a new signal.
    /// Returns the LogicState (True/False/Ref) of the integration.
    pub fn process_signal(&mut self, input: HarmonicState) -> LogicState {
        self.tick += 1;

        // 1. Attempt Integration (H-AND)
        // Combine input with current context to see if they resonate.
        let integrated = HarmonicState::h_and(self.context, input);

        // 2. Evaluate Result
        let logic_state = integrated.evaluate_logic();

        match logic_state {
            LogicState::Unison | LogicState::True | LogicState::Reference => {
                // Constructive Interference / Nirvana: Update context
                self.context = integrated;
                logic_state
            }
            LogicState::Maybe => {
                // Tension: Keep context but maybe shift phase?
                // For now, treat as non-updating state
                LogicState::Maybe
            }
            LogicState::False | LogicState::Noise => {
                // Dissonance: Reject input.
                // Apply phase modulation to try to resolve it?
                // This simulates "Thinking" - trying to find a harmonic angle.

                let modulated = HarmonicState::phase_modulate(input, self.tick);
                let integrated_mod = HarmonicState::h_and(self.context, modulated);
                let mod_state = integrated_mod.evaluate_logic();

                if mod_state == LogicState::True || mod_state == LogicState::Reference {
                    // Resolution found via modulation intervention!
                    self.context = integrated_mod;
                    LogicState::Reference // It was forced by Reference Pattern
                } else {
                    LogicState::False // Still dissonant
                }
            }
        }
    }
}
