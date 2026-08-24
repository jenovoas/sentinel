// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/neural_memory.rs
//! Real Leaky Integrate-and-Fire (LIF) Spiking Neural Network (SNN) implementation for PAI-60.
//! Integrates eBPF ringbuffer events as dynamic amplitude spikes over 64 neural channels.
//!
//! ## References (memoria fonónica / inteligencia mecánica cognitiva)
//! - [ZW-005] In-memory phononic learning toward cognitive mechanical intelligence. arXiv:2511.13543.
//! - [ZW-004] Uncovering multifunctional mechano-intelligence. arXiv:2305.19354.
//! - [P-TES] Novoa, J. (2026). *Tesis de Resonancia.* `docs/02_ciencia_y_quantum/research/TesiResonancia.md`.
//! - [P-RES] Novoa, J. (2026). *Aritmética Sexagesimal como Base de Sistemas.* `RESEARCH_es.md` — LIF SNN en base-60.

use crate::ebpf_cortex_bridge::CortexEvent;
use crate::spa::SPA;
use pyo3::prelude::*;

#[pyclass(from_py_object)]
#[derive(Clone)]
pub struct LIFNeuron {
    pub v_membrane: SPA,
    pub v_threshold: SPA,
    pub decay_factor: SPA,
    pub spike_count: u64,
}

impl Default for LIFNeuron {
    fn default() -> Self {
        Self::new()
    }
}

impl LIFNeuron {
    pub fn new() -> Self {
        Self {
            v_membrane: SPA::zero(),
            v_threshold: SPA::from_raw(SPA::SCALE_0 / 20), // Sensitive threshold 0.05
            decay_factor: SPA::from_raw(SPA::SCALE_0 / 100), // 1% leak per tick
            spike_count: 0,
        }
    }

    pub fn integrate(&mut self, current: SPA) -> bool {
        // Boost raw pressure into SPA scale so thermal/ring0 input dynamically charges membrane
        let current_scaled = if current.to_raw() > 0 && current.to_raw() < SPA::SCALE_0 {
            SPA::from_raw(current.to_raw() * (SPA::SCALE_0 / 100))
        } else {
            current
        };

        self.v_membrane = self.v_membrane + current_scaled;
        if self.v_membrane >= self.v_threshold {
            self.v_membrane = SPA::zero(); // Reset
            self.spike_count += 1;
            true
        } else {
            // Leak
            if self.v_membrane > self.decay_factor {
                self.v_membrane = self.v_membrane - self.decay_factor;
            } else {
                self.v_membrane = SPA::zero();
            }
            false
        }
    }
}

#[pyclass]
pub struct NeuralMemory {
    #[pyo3(get)]
    pub processed: usize,
    #[pyo3(get)]
    pub total_spikes: u64,
    neurons: Vec<LIFNeuron>,
}

impl Default for NeuralMemory {
    fn default() -> Self {
        Self::new()
    }
}

// B. Rust Implementation (Internal Logic)
impl NeuralMemory {
    pub fn new() -> Self {
        let mut neurons = Vec::with_capacity(64);
        for _ in 0..64 {
            neurons.push(LIFNeuron::new());
        }
        Self {
            processed: 0,
            total_spikes: 0,
            neurons,
        }
    }

    pub fn ingest_event(&mut self, ev: CortexEvent, entropy: SPA) {
        self.processed += 1;

        let neuron_idx = (ev.pid as usize) % 64;
        let input_current = entropy;

        let fired = self.neurons[neuron_idx].integrate(input_current);
        if fired {
            self.total_spikes += 1;
            tracing::debug!(
                "⚡ SNN SPIKE: Neuron {} fired! (Total Spikes: {})",
                neuron_idx,
                self.total_spikes
            );
        }
    }
}

// C. Python Bindings (PyO3)
#[pymethods]
impl NeuralMemory {
    #[new]
    pub fn py_new() -> Self {
        Self::new()
    }

    /// Python-friendly ingest (accepts raw SPA i64)
    #[pyo3(name = "ingest_event")]
    pub fn ingest_event_py(&mut self, ev: CortexEvent, entropy_raw: i64) {
        let entropy = SPA::from_raw(entropy_raw);
        self.ingest_event(ev, entropy);
    }

    #[getter]
    pub fn get_total_spikes(&self) -> u64 {
        self.total_spikes
    }
}
