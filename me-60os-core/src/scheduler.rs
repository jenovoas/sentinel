// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 📅 QUANTUM SCHEDULER: RUST CORE 📅
//!
//! Orchestrates system pulse, batch sizing, and bio-resonance alignment.
//! Implements Axiom V: "Bio-Centrism" & "The 17-Second Discovery".
//!
//! Protocols:
//! - P-Controller (Latency -> Batch Size)
//! - Dead Man's Switch (SoulVerifier)
//! - Venus Drift Correction (Phase Reset at T=68s)

use crate::bio::SoulVerifier;
use crate::spa::SPA;
use std::cmp;

#[derive(Debug, Clone, PartialEq)]
pub enum SchedulerAction {
    Continue { batch_size: usize },
    Halt { reason: String },
    Emergency { phase: SPA },
}

pub struct QuantumScheduler {
    pub current_batch_size: usize,
    pub min_batch: usize,
    pub max_batch: usize,
    pub baseline_ms: SPA,

    // Bio-Resonance State
    pub ticks_since_reset: u64,
    pub venus_phase_error: SPA,
}

impl QuantumScheduler {
    pub fn new() -> Self {
        Self {
            current_batch_size: 1000,
            min_batch: 100,
            max_batch: 65536,
            baseline_ms: SPA::new(20, 0, 0, 0, 0), // 20ms

            ticks_since_reset: 0,
            venus_phase_error: SPA::zero(),
        }
    }

    /// Primary Tick Logic (41Hz)
    pub fn tick(&mut self, latency_ms: SPA, bio_signal: &[SPA]) -> SchedulerAction {
        // 1. Bio-Resonance Check (Dead Man's Switch)
        // Only run check if we enough signal data
        if bio_signal.len() >= 3 {
            let metrics = SoulVerifier::analyze(bio_signal);
            if !metrics.is_alive {
                return SchedulerAction::Halt {
                    reason: "PILOT_LOST: Bio-Resonance coherence failed".to_string(),
                };
            }
        }

        // 2. Venus Drift Correction (Axiom V)
        // Reset phase every 68s (approx 2788 ticks at 41Hz) -> logic says T=68s.
        // 41Hz * 68s = 2788 ticks.
        self.ticks_since_reset += 1;
        if self.ticks_since_reset >= 2788 {
            self.ticks_since_reset = 0;
            // Force phase reset
            return SchedulerAction::Emergency { phase: SPA::zero() };
        }

        // 3. Adaptive Batch Sizing (P-Controller)
        let epsilon = SPA::new(0, 6, 0, 0, 0); // 0.1ms
        let safe_latency = latency_ms + epsilon;

        // scale = baseline / latency
        let scale_factor = self.baseline_ms / safe_latency;

        // Clamp scale [0.5, 1.5]
        let lower = SPA::new(0, 30, 0, 0, 0); // 0.5
        let upper = SPA::new(1, 30, 0, 0, 0); // 1.5

        let clamped_scale = if scale_factor < lower {
            lower
        } else if scale_factor > upper {
            upper
        } else {
            scale_factor
        };

        // New batch
        // current * scale
        let current_spa = SPA::from_raw(self.current_batch_size as i64 * SPA::SCALE_0);
        let new_batch_spa = current_spa * clamped_scale;

        // Convert back to usize
        let new_batch = new_batch_spa.to_degrees() as usize;

        self.current_batch_size = cmp::max(self.min_batch, cmp::min(self.max_batch, new_batch));

        SchedulerAction::Continue {
            batch_size: self.current_batch_size,
        }
    }
}

impl Default for QuantumScheduler {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_scheduler_init() {
        let sched = QuantumScheduler::new();
        assert_eq!(sched.current_batch_size, 1000);
    }

    #[test]
    fn test_p_controller_increase() {
        let mut sched = QuantumScheduler::new();
        // Latency 10ms (half of 20ms baseline) -> Scale 2.0 -> clamped to 1.5
        // New batch = 1000 * 1.5 = 1500
        let latency = SPA::new(10, 0, 0, 0, 0);
        let action = sched.tick(latency, &[]);

        if let SchedulerAction::Continue { batch_size } = action {
            assert_eq!(batch_size, 1500);
            assert_eq!(sched.current_batch_size, 1500);
        } else {
            panic!("Expected Continue action");
        }
    }

    #[test]
    fn test_p_controller_decrease() {
        let mut sched = QuantumScheduler::new();
        // Latency 40ms (double 20ms baseline) -> Scale 0.5 -> clamped to 0.5
        // New batch = 1000 * 0.5 = 500
        let latency = SPA::new(40, 0, 0, 0, 0);
        let action = sched.tick(latency, &[]);

        if let SchedulerAction::Continue { batch_size } = action {
            assert_eq!(batch_size, 500);
        } else {
            panic!("Expected Continue action");
        }
    }

    #[test]
    fn test_venus_phase_reset() {
        let mut sched = QuantumScheduler::new();
        let latency = SPA::new(20, 0, 0, 0, 0);
        let signal = [];

        // Tick 2787 times
        for _ in 0..2787 {
            sched.tick(latency, &signal);
        }

        assert_eq!(sched.ticks_since_reset, 2787);

        // 2788th tick -> Should trigger reset
        let action = sched.tick(latency, &signal);
        match action {
            SchedulerAction::Emergency { phase } => {
                assert_eq!(phase, SPA::zero());
                assert_eq!(sched.ticks_since_reset, 0);
            }
            _ => panic!("Expected Emergency Phase Reset at tick 2788"),
        }
    }
}
