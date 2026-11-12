// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/security/bio_resonance.rs
//! BIO-RESONANCE ENGINE (The Human Anchor)
//!
//! Ports the "Soul Verifier" logic to PURE Base-60 (60^4 accuracy).

use crate::math::harmonic_logic::{HarmonicProcessor, HarmonicState, LogicState};
use me60os_core::resonance_engine::ResonanceEngine as CoherenceEngine;
use me60os_core::spa::SPA as S60;

pub struct ResonanceEngine {
    npu: HarmonicProcessor,
    last_pulse_timestamp: u64,
    coherence: CoherenceEngine,
}

impl Default for ResonanceEngine {
    fn default() -> Self {
        Self::new()
    }
}

impl ResonanceEngine {
    pub fn new() -> Self {
        ResonanceEngine {
            npu: HarmonicProcessor::new(),
            last_pulse_timestamp: 0,
            coherence: CoherenceEngine::new(),
        }
    }

    /// Explicitly inject a biological pulse (Human activity)
    pub fn inject_pulse(&mut self, _timestamp: u64) {
        self.coherence.charge_from_coherence_milli(1_000);

        tracing::debug!(
            "PULSE INJECTED. New Coherence: {:?}",
            self.coherence.current_coherence()
        );
    }
    /// Carga coherencia desde la energía medida del cristal DTC (lane A+B).
    /// Fuente real: `CrystalRuntimeStatus.lane_a/b_energy_raw`, no señal sintética.
    /// Escala: energía total / (nodos × SCALE_0) → fracción [0,1] clampada.
    /// La memoria no-Markoviana vive en el PID del runtime (historial 68 ticks);
    /// aquí solo se refleja su estado actual, no se duplica el kernel.
    pub fn charge_from_crystal_energy(
        &mut self,
        energy_a_raw: i64,
        energy_b_raw: i64,
        node_count: usize,
    ) {
        self.coherence
            .charge_from_crystal_energy(energy_a_raw, energy_b_raw, node_count);
    }

    /// Decay coherence (Entropy)
    pub fn tick_entropy(&mut self) {
        self.coherence.tick_entropy();
    }

    /// Check if the system is "Coherent" enough to execute (Portal check)
    pub fn is_coherent(&self) -> bool {
        self.coherence.is_coherent()
    }

    pub fn verify_pulse(&mut self, timestamp: u64) -> (bool, LogicState) {
        // El pulso se verifica contra la Verdad (3:2), no contra el historial
        // propio: Unison×Unison da 0.67 (disonancia) y contaminaría el siguiente
        // check. (EXP-002: transferencia por simpatía, no acumulación.)
        self.npu.reset_to_truth();
        // Base verification logic using HarmonicProcessor
        let input_state = HarmonicState {
            ratio: self.coherence.current_coherence(),
            phase: S60::zero(),
            energy: 100,
        };

        let verdict = self.npu.process_signal(input_state);
        let is_valid = match verdict {
            LogicState::Unison | LogicState::True | LogicState::Reference => self.is_coherent(),
            _ => false,
        };

        self.last_pulse_timestamp = timestamp;
        (is_valid, verdict)
    }

    pub fn get_coherence_raw(&self) -> i64 {
        self.coherence.get_coherence_raw()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_perfect_pulse() {
        let mut engine = ResonanceEngine::new();
        // Cargar el motor al estado coherente (>90%) con pulsos biológicos
        for i in 0..10 {
            engine.inject_pulse(100 + i);
        }
        let (valid, state) = engine.verify_pulse(117);
        assert!(
            valid,
            "Engine debía estar cargado y validar correctamente a >90%"
        );
        // Validacion S60 Logica pura
        assert_eq!(state, LogicState::Unison);
    }
    #[test]
    fn test_charge_from_crystal_energy() {
        let mut engine = ResonanceEngine::new();
        // Energía cero → sin carga (honesto, no sintético)
        engine.charge_from_crystal_energy(0, 0, 64);
        assert_eq!(engine.get_coherence_raw(), 0);
        // Energía real medida (2.8e12 total, 67951 nodos → 41M/nodo → clamp 1.0)
        engine.charge_from_crystal_energy(2816001156461, 2798094666565, 67951);
        assert_eq!(engine.get_coherence_raw(), S60::SCALE_0 / 10);
        // Carga acumulada llega al máximo en 10 ticks
        for _ in 0..10 {
            engine.charge_from_crystal_energy(2816001156461, 2798094666565, 67951);
        }
        assert_eq!(engine.get_coherence_raw(), S60::SCALE_0);
        // Sin overflow con energías gigantes
        engine.charge_from_crystal_energy(i64::MAX, i64::MAX, 64);
        assert!(engine.get_coherence_raw() <= S60::SCALE_0);
    }
}
