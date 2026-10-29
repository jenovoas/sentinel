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
#[cfg(feature = "extension-module")]
use pyo3::prelude::*;

#[cfg_attr(feature = "extension-module", pyclass(from_py_object))]
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
        self.v_membrane = self.v_membrane + current;

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

#[cfg(feature = "extension-module")]
#[pyclass]
pub struct NeuralMemory {
    #[pyo3(get)]
    pub processed: usize,
    #[pyo3(get)]
    pub total_spikes: u64,
    neurons: Vec<LIFNeuron>,
}

#[cfg(not(feature = "extension-module"))]
pub struct NeuralMemory {
    pub processed: usize,
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

    pub fn save_to_crystal(&self, path: &std::path::Path) -> std::io::Result<()> {
        use std::io::Write;
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)?;
        }
        let mut file = std::fs::File::create(path)?;
        // Magic header: 16 bytes
        file.write_all(b"CRYSTAL_SNN_V1\0\0")?;
        file.write_all(&(self.processed as u64).to_le_bytes())?;
        file.write_all(&self.total_spikes.to_le_bytes())?;
        file.write_all(&(self.neurons.len() as u32).to_le_bytes())?;

        for n in &self.neurons {
            file.write_all(&n.v_membrane.to_raw().to_le_bytes())?;
            file.write_all(&n.v_threshold.to_raw().to_le_bytes())?;
            file.write_all(&n.decay_factor.to_raw().to_le_bytes())?;
            file.write_all(&n.spike_count.to_le_bytes())?;
        }
        file.sync_all()
    }

    pub fn load_from_crystal(path: &std::path::Path) -> std::io::Result<Self> {
        use std::io::Read;
        let mut file = std::fs::File::open(path)?;
        let mut magic = [0u8; 16];
        file.read_exact(&mut magic)?;
        if &magic != b"CRYSTAL_SNN_V1\0\0" {
            return Err(std::io::Error::new(
                std::io::ErrorKind::InvalidData,
                "Cabecera mágica de archivo .crystal inválida",
            ));
        }

        let mut u64_buf = [0u8; 8];
        let mut u32_buf = [0u8; 4];

        file.read_exact(&mut u64_buf)?;
        let processed = u64::from_le_bytes(u64_buf) as usize;

        file.read_exact(&mut u64_buf)?;
        let total_spikes = u64::from_le_bytes(u64_buf);

        file.read_exact(&mut u32_buf)?;
        let count = u32::from_le_bytes(u32_buf) as usize;

        let mut neurons = Vec::with_capacity(count);
        for _ in 0..count {
            file.read_exact(&mut u64_buf)?;
            let v_mem = i64::from_le_bytes(u64_buf);
            file.read_exact(&mut u64_buf)?;
            let v_thresh = i64::from_le_bytes(u64_buf);
            file.read_exact(&mut u64_buf)?;
            let decay = i64::from_le_bytes(u64_buf);
            file.read_exact(&mut u64_buf)?;
            let spikes = u64::from_le_bytes(u64_buf);

            neurons.push(LIFNeuron {
                v_membrane: SPA::from_raw(v_mem),
                v_threshold: SPA::from_raw(v_thresh),
                decay_factor: SPA::from_raw(decay),
                spike_count: spikes,
            });
        }

        Ok(Self {
            processed,
            total_spikes,
            neurons,
        })
    }
}

// C. Python Bindings (PyO3)
#[cfg(feature = "extension-module")]
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_neural_memory_crystal_persistence_roundtrip() {
        let mut nm = NeuralMemory::new();
        let ev = CortexEvent::new(1000, 1, 42, 500_000, 1);
        nm.ingest_event(ev, SPA::from_raw(SPA::SCALE_0 / 10)); // Force integrate
        assert!(nm.processed == 1);

        let temp_dir = std::env::temp_dir();
        let test_path = temp_dir.join("test_snn_memory.crystal");

        nm.save_to_crystal(&test_path).expect("guardado exitoso");
        let loaded = NeuralMemory::load_from_crystal(&test_path).expect("carga exitosa");

        assert_eq!(loaded.processed, nm.processed);
        assert_eq!(loaded.total_spikes, nm.total_spikes);
        assert_eq!(loaded.neurons.len(), 64);
        assert_eq!(
            loaded.neurons[42].v_membrane.to_raw(),
            nm.neurons[42].v_membrane.to_raw()
        );

        let _ = std::fs::remove_file(test_path);
    }
}
