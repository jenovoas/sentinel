// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
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
//!
//! ## References (ratios armónicos exactos en base-60)
//! - [P-RES] Novoa, J. (2026). *Aritmética Sexagesimal como Base de Sistemas.* `RESEARCH_es.md`
//!   — 3:2 = 1;30 (quinta justa), 4:3 = 1;20 (cuarta), 45:32 (tritono) son exactos en base-60.
//! - [EXT-MAN] Mansfield & Wildberger (2017). Historia Mathematica. DOI:10.1016/j.hm.2017.08.001
//!   — ratios pitagóricos exactos en base sexagesimal.
//! - Lógica armónica (consonancia/disonancia como estados lógicos) es diseño original de Sentinel
//!   (Novoa 2026, nota técnica no publicada).

// Harmonic logic primitives: part of the 未来-ready S60 math library.
// Silenced at module level; items are used indirectly via the processor.
#![allow(dead_code)]

use me60os_core::spa::SPA;

/// Logic Score: SPA[0;0] (Pure Noise) to SPA[1;0] (Pure Tonal Unity)
/// PURE SPA: No float contamination
pub type CoherenceScore = SPA;

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
    pub ratio: SPA,  // Current frequency ratio relative to Root
    pub phase: SPA,  // Phase offset (0-360 degrees)
    pub energy: u32, // "Amplitude" or confidence
}

impl HarmonicState {
    /// Create a new Harmonic State
    pub fn new(d: i64, m: i64, s: i64) -> Self {
        HarmonicState {
            ratio: SPA::new(d, m, s, 0, 0),
            phase: SPA::zero(),
            energy: 100,
        }
    }

    // Define Standard Harmonic Logic Constants

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
        // Get raw value for comparison (SCALE_0 = 12,960,000)
        let val = self.ratio.to_raw();

        // Constants in raw SPA units
        // TRUE: 3/2 = 1.5 = 19,440,000
        let true_val = SPA::new(1, 30, 0, 0, 0).to_raw();
        // MAYBE: 4/3 = 1.333... = 17,280,000
        let maybe_val = SPA::new(1, 20, 0, 0, 0).to_raw();
        // REFERENCE: 26.0 = 26 * 12,960,000
        let ref_val = SPA::new(26, 0, 0, 0, 0).to_raw();
        // FALSE: Tritone 45/32 ≈ 1.40625 = 18,225,000
        let false_val = SPA::new(1, 24, 22, 30, 0).to_raw();

        // Bug 1.5 fix: el comentario original ("3 minutes (0.05) / 3*216,000 = 648,000")
        // confundía dos escalas: en `sentinel-cortex/s60.rs` SCALE_0=216,000 (60³),
        // pero ESTE archivo (harmonic_logic.rs) usa `me60os_core::spa::SPA` cuya
        // SCALE_0=12,960,000 (60⁴). Aquí `tolerance=648,000` se interpreta como
        // 648,000 / 12,960,000 = 0.05 abstracto (5% de margen armónico), NO como
        // "3 minutos de arco" (que sería en grados-sexagesimales tradicionales).
        // El 0.05 final sigue siendo el valor deseado; el comentario/console log
        // anterior era la confusión típica de IA que mezcló contextos.
        let tolerance = 648_000; // 5% abstracto en escala SPA (60⁴)

        if (val - ref_val).abs() < tolerance {
            LogicState::Reference
        } else if (val - SPA::SCALE_0).abs() < tolerance {
            // Unison Check (1.0)
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
        let (max, min) = if a.ratio.to_raw() >= b.ratio.to_raw() {
            (a.ratio, b.ratio)
        } else {
            (b.ratio, a.ratio)
        };

        // Interval = Max / Min (SPA division returns SPA directly)
        let raw_ratio = if min.to_raw() != 0 {
            max / min
        } else {
            SPA::one()
        };

        // Phase Difference
        let diff_phase = (a.phase - b.phase).abs();

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

        // Multiply (SPA * SPA result normalized to SCALE_0)
        let product = a.ratio * b.ratio;
        // Divide by 3:2 (Truth reference)
        let raw_product = product / true_ratio;

        let phase_sum = a.phase + b.phase;
        let phase_avg = phase_sum / 2i64;

        HarmonicState {
            ratio: raw_product,
            phase: phase_avg, // Avg phase
            energy: (a.energy + b.energy) / 2,
        }
    }

    /// H-OR: Superposition (Average)
    /// Represents the mixing of two signals.
    /// Example: (3:2 + 3:2)/2 = 3:2 (True + True = True)
    fn h_or(a: HarmonicState, b: HarmonicState) -> HarmonicState {
        let sum = a.ratio + b.ratio;
        let avg = sum / 2i64; 

        let phase_sum = a.phase + b.phase;
        let phase_avg = phase_sum / 2i64;

        HarmonicState {
            ratio: avg,
            phase: phase_avg,
            energy: std::cmp::max(a.energy, b.energy),
        }
    }

    /// H-NOT: Inversion
    /// Inverts the interval relative to the Octave (2:1).
    /// NOT(3:2) = 2 / (3:2) = 4:3 (Fifth -> Fourth)
    /// NOT(Tritone) -> Inverted Tritone
    fn h_not(a: HarmonicState) -> HarmonicState {
        let octave = SPA::new(2, 0, 0, 0, 0);
        let inverse = octave / a.ratio;

        HarmonicState {
            ratio: inverse,
            phase: a.phase + SPA::new(180, 0, 0, 0, 0), // +180 deg phase shift
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

        // Ratio += pattern/60
        let shift = SPA::new(0, pattern as i64, 0, 0, 0);

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

impl Default for HarmonicProcessor {
    fn default() -> Self {
        Self::new()
    }
}

impl HarmonicProcessor {
    pub fn new() -> Self {
        HarmonicProcessor {
            context: HarmonicState::logic_true(), // Start with Truth (3:2)
            tick: 0,
        }
    }

    /// Returns the LogicState (True/False/Ref) of the integration.
    pub fn process_signal(&mut self, input: HarmonicState) -> LogicState {
        self.tick += 1;
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
