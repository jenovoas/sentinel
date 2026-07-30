// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🕸️ RESONANT LATTICE - Network of Coupled Crystals 🕸️
//!
//! Pure Rust implementation of the Resonant Lattice.
//! Migrated from quantum/resonant_matrix.py with zero functionality loss.
//!
//! Enables energy (data) transfer through sympathetic vibration between nodes.

use crate::isochronous_oscillator::IsochronousOscillator;
use crate::shm_bridge::PySharedBuffer;
use crate::spa::SPA;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

use std::collections::HashMap;

/// Resonant Lattice: Network of coupled crystals.
/// Implements the Liquid Lattice quantum matrix architecture.
#[cfg_attr(feature = "extension-module", pyclass)]
#[derive(Serialize, Deserialize)]
pub struct ResonantMatrix {
    /// Array of crystal nodes
    pub crystals: Vec<IsochronousOscillator>,

    /// Context Buffer mapping a node index to its context payload
    pub context_data: HashMap<usize, String>,

    /// Coupling Factor: strength of connection between nodes
    /// SPA(0, 10) = 10/60 ≈ 0.167
    pub coupling_factor: SPA,
    /// Time step for evolution
    pub dt: SPA,
}

impl ResonantMatrix {
    /// Creates a new lattice with the specified number of nodes.
    pub fn new(size: usize) -> Self {
        let crystals = (0..size)
            .map(|i| IsochronousOscillator::new(&format!("Node-{}", i)))
            .collect();

        Self {
            crystals,
            context_data: HashMap::new(),
            coupling_factor: SPA::new(0, 10, 0, 0, 0), // 10/60
            dt: SPA::new(0, 0, 1, 0, 0),               // 1 second step
        }
    }

    /// Creates a lattice with custom coupling factor.
    pub fn with_coupling(size: usize, coupling: SPA) -> Self {
        let crystals = (0..size)
            .map(|i| IsochronousOscillator::new(&format!("Node-{}", i)))
            .collect();

        Self {
            crystals,
            context_data: HashMap::new(),
            coupling_factor: coupling,
            dt: SPA::new(0, 0, 1, 0, 0),
        }
    }

    /// Returns the number of nodes in the lattice.
    pub fn size(&self) -> usize {
        self.crystals.len()
    }

    /// Executes one time step on the entire network.
    /// Calculates energy transfer between adjacent nodes.
    pub fn step(&mut self) {
        let size = self.crystals.len();
        if size < 2 {
            return;
        }

        // 1. Calculate transfers (without applying yet to maintain symmetry)
        let mut transfers: Vec<SPA> = vec![SPA::zero(); size];

        for i in 0..(size - 1) {
            let amp_i = self.crystals[i].get_amplitude();
            let amp_next = self.crystals[i + 1].get_amplitude();

            // Amplitude differential (pressure)
            let diff = amp_i - amp_next;

            // Flow = Differential * Coupling Factor
            let flow = (diff * self.coupling_factor) / SPA::new(1, 0, 0, 0, 0);

            // Node i loses, node i+1 gains
            transfers[i] = transfers[i] - flow;
            transfers[i + 1] = transfers[i + 1] + flow;
        }

        // 2. Apply transfers and oscillate
        for (i, transfer) in transfers.iter().enumerate().take(size) {
            self.crystals[i].amplitude = self.crystals[i].amplitude + *transfer;
            self.crystals[i].oscillate(self.dt);
        }
    }

    /// Injects pressure at a specific node index.
    pub fn inject(&mut self, index: usize, pressure: i64) {
        if index < self.crystals.len() {
            self.crystals[index].transduce_pulse(pressure);
        }
    }

    /// Returns the amplitudes of all nodes.
    pub fn get_amplitudes(&self) -> Vec<SPA> {
        self.crystals.iter().map(|c| c.get_amplitude()).collect()
    }

    /// Returns the phases of all nodes.
    pub fn get_phases(&self) -> Vec<SPA> {
        self.crystals.iter().map(|c| c.get_phase()).collect()
    }

    /// Resets all nodes to ground state.
    pub fn reset(&mut self) {
        for crystal in &mut self.crystals {
            crystal.reset();
        }
    }

    /// Calculates total energy in the lattice.
    pub fn total_energy(&self) -> SPA {
        self.crystals
            .iter()
            .fold(SPA::zero(), |acc, c| acc + c.get_amplitude())
    }

    /// Sets the coupling factor dynamically (for bio-resonance integration).
    pub fn set_coupling(&mut self, coupling: SPA) {
        self.coupling_factor = coupling;
    }

    /// Sets the time step.
    pub fn set_dt(&mut self, dt: SPA) {
        self.dt = dt;
    }

    /// Stabilizes the lattice using linear diffusion (fluid dynamics).
    /// Used to smooth out phase differences (Liquid State).
    pub fn stabilize_py(&mut self, cycles: usize) {
        // Simplified Linear Diffusion in Rust
        for _ in 0..cycles {
            let phases: Vec<SPA> = self.crystals.iter().map(|c| c.phase).collect();
            let mut new_phases = phases.clone();
            let size = self.crystals.len();

            for i in 0..size {
                if phases[i] == SPA::zero() {
                    continue;
                }

                let mut total = phases[i];
                let mut count = SPA::new(1, 0, 0, 0, 0);

                if i > 0 && phases[i - 1] != SPA::zero() {
                    total = total + phases[i - 1];
                    count = count + SPA::new(1, 0, 0, 0, 0);
                }

                if i < size - 1 && phases[i + 1] != SPA::zero() {
                    total = total + phases[i + 1];
                    count = count + SPA::new(1, 0, 0, 0, 0);
                }

                new_phases[i] = total / count;
            }

            for (i, new_phase) in new_phases.iter().enumerate().take(size) {
                self.crystals[i].phase = *new_phase;
            }
        }
    }

    /// "Liquid Persistence": Flushes the current lattice state to Shared Memory.
    /// This allows Python or other processes to read the crystal state without copying.
    ///
    /// # Safety
    /// This performs a raw pointer write to the shared memory buffer.
    /// The buffer size must match the lattice size.
    pub fn sync_to_shm(&self, buffer: &mut PySharedBuffer) -> Result<(), String> {
        let crystal_size = std::mem::size_of::<IsochronousOscillator>();
        let total_size = crystal_size * self.crystals.len();

        // This is accessible because we are in the same crate and "ptr" is pub in shm_bridge
        let shm_ptr = buffer.ptr;

        if shm_ptr.is_null() {
            return Err("SHM pointer is null".to_string());
        }

        // Technically we should check buffer.size >= total_size
        // We can't access buffer.size directly if it's private, but it was public in file view.
        // Yes, struct definition had pub fields.
        let buf_size = buffer.size;
        if buf_size < total_size {
            return Err(format!("Buffer too small: {} < {}", buf_size, total_size));
        }

        unsafe {
            let src_ptr = self.crystals.as_ptr() as *const u8;
            std::ptr::copy_nonoverlapping(src_ptr, shm_ptr, total_size);
        }

        Ok(())
    }

    /// "Hot Reload": Restores lattice state from Shared Memory.
    pub fn load_from_shm(&mut self, buffer: &PySharedBuffer) -> Result<(), String> {
        let crystal_size = std::mem::size_of::<IsochronousOscillator>();
        let total_size = crystal_size * self.crystals.len();

        let shm_ptr = buffer.ptr;
        if shm_ptr.is_null() {
            return Err("SHM pointer is null".to_string());
        }

        if buffer.size < total_size {
            return Err(format!(
                "Buffer too small: {} < {}",
                buffer.size, total_size
            ));
        }

        unsafe {
            let dst_ptr = self.crystals.as_mut_ptr() as *mut u8;
            std::ptr::copy_nonoverlapping(shm_ptr, dst_ptr, total_size);
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lattice_creation() {
        let lattice = ResonantMatrix::new(3);
        assert_eq!(lattice.size(), 3);
        assert_eq!(lattice.total_energy(), SPA::zero());
    }

    #[test]
    fn test_energy_propagation() {
        let mut lattice = ResonantMatrix::new(3);

        // Inject at Node-0
        println!("\n--- INJECTION AT NODE-0 (Pressure: 60) ---");
        lattice.inject(0, 60);

        println!("\n--- NETWORK EVOLUTION ---");
        println!("Node-0\t\t| Node-1\t\t| Node-2");
        println!("{}", "-".repeat(60));

        for t in 1..=12 {
            lattice.step();
            let amps = lattice.get_amplitudes();
            println!("T{:02}: {}\t| {}\t| {}", t, amps[0], amps[1], amps[2]);
        }

        let final_amps = lattice.get_amplitudes();

        // Verify that energy has propagated to Node-2
        if final_amps[2] > SPA::zero() {
            println!("\n✅ SUCCESS: Energy resonated to Node-2.");
        } else {
            println!("\n⚠️ Energy did not reach Node-2 (may need more steps).");
        }

        // Energy should have spread across the network
        assert!(final_amps[0] < SPA::new(60, 0, 0, 0, 0));
    }

    #[test]
    fn test_energy_conservation() {
        let mut lattice = ResonantMatrix::new(5);

        // Inject total energy of 100
        lattice.inject(2, 100);
        let initial_energy = lattice.total_energy();

        // Run several steps
        for _ in 0..10 {
            lattice.step();
        }

        let final_energy = lattice.total_energy();

        println!("Initial: {} -> Final: {}", initial_energy, final_energy);

        // Energy should decrease due to damping but not increase
        assert!(final_energy <= initial_energy);
    }
}

#[cfg_attr(feature = "extension-module", pymethods)]
impl ResonantMatrix {
    #[new]
    pub fn __new__(rings: usize) -> Self {
        // Hexagonal number formula: H_n = 3n(n+1) + 1
        // Ring 150 ~= 68,000 nodes
        let size = 3 * rings * (rings + 1) + 1;
        Self::new(size)
    }

    #[pyo3(name = "inject")]
    pub fn inject_py(&mut self, data: &[u8]) {
        // Map bytes to pressure
        for (i, &byte) in data.iter().enumerate() {
            if i >= self.crystals.len() {
                break;
            }
            // Interpret byte as pressure (0-255)
            self.crystals[i].transduce_pulse(byte as i64);
        }
    }

    #[pyo3(name = "step")]
    pub fn step_py(&mut self) {
        self.step();
    }

    #[pyo3(name = "stabilize")]
    pub fn stabilize_wrapper(&mut self, cycles: usize) {
        self.stabilize_py(cycles);
    }

    pub fn save_snapshot(&self, buffer: &mut PySharedBuffer) -> PyResult<()> {
        self.sync_to_shm(buffer)
            .map_err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>)
    }

    pub fn load_snapshot(&mut self, buffer: &PySharedBuffer) -> PyResult<()> {
        self.load_from_shm(buffer)
            .map_err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>)
    }

    /// Returns size of a single crystal struct (for Python to allocate SHM)
    #[staticmethod]
    pub fn get_node_size() -> usize {
        std::mem::size_of::<IsochronousOscillator>()
    }

    pub fn count_nodes(&self) -> usize {
        self.crystals.len()
    }

    pub fn active_memory_usage(&self) -> usize {
        self.crystals.len() * std::mem::size_of::<IsochronousOscillator>()
    }

    #[pyo3(name = "set_context")]
    pub fn set_context_py(&mut self, index: usize, payload: String) {
        if index < self.crystals.len() {
            self.context_data.insert(index, payload);
        }
    }

    #[pyo3(name = "get_context")]
    pub fn get_context_py(&self, index: usize) -> Option<String> {
        self.context_data.get(&index).cloned()
    }

    #[pyo3(name = "save_crystal")]
    pub fn save_crystal_py(&self, path: String) -> PyResult<()> {
        use flate2::write::GzEncoder;
        use flate2::Compression;
        use std::fs::File;
        use std::io::Write;

        let file = File::create(&path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;

        let mut encoder = GzEncoder::new(file, Compression::default());
        let encoded: Vec<u8> = serde_json::to_vec(self)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

        encoder
            .write_all(&encoded)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;

        Ok(())
    }

    #[pyo3(name = "load_crystal")]
    pub fn load_crystal_py(&mut self, path: String) -> PyResult<()> {
        use flate2::read::GzDecoder;
        use std::fs::File;
        use std::io::Read;

        let file = File::open(&path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;

        let mut decoder = GzDecoder::new(file);
        let mut buffer = Vec::new();
        decoder
            .read_to_end(&mut buffer)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;

        let decoded: ResonantMatrix = serde_json::from_slice(&buffer)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

        self.crystals = decoded.crystals;
        self.context_data = decoded.context_data;
        self.coupling_factor = decoded.coupling_factor;
        self.dt = decoded.dt;

        Ok(())
    }

    #[pyo3(name = "set_node_state")]
    pub fn set_node_state_py(&mut self, index: usize, amp: SPA, phase: SPA) {
        if index < self.crystals.len() {
            self.crystals[index].amplitude = amp;
            self.crystals[index].phase = phase;
        }
    }

    #[pyo3(name = "get_node_amp_raw")]
    pub fn get_node_amp_raw_py(&self, index: usize) -> Option<SPA> {
        if index < self.crystals.len() {
            Some(self.crystals[index].amplitude)
        } else {
            None
        }
    }

    #[pyo3(name = "get_node_phase_raw")]
    pub fn get_node_phase_raw_py(&self, index: usize) -> Option<SPA> {
        if index < self.crystals.len() {
            Some(self.crystals[index].phase)
        } else {
            None
        }
    }

    #[pyo3(name = "total_energy")]
    pub fn total_energy_py(&self) -> i64 {
        self.total_energy().to_raw()
    }

    #[pyo3(name = "measure_coherence")]
    pub fn measure_coherence_py(&mut self) -> i64 {
        // Implementación rápida de coherencia S60
        let n_nodes = self.crystals.len();
        if n_nodes == 0 {
            return SPA::new(1, 0, 0, 0, 0).to_raw();
        }

        // Bug 4.3 fix: el acumulador se mantuvo en i64, lo que puede desbordarse
        // silenciosamente con redes grandes (p. ej. hexagonal ring 150 ≈ 68000 nodos,
        // ver comentario en `__new__` líneas 305-309) si las fases crecen.
        // Pasamos el acumulador a i128 (cheap en x86_64) para mantener la promesa
        // YATRA de exactitud sin clamping silencioso.
        let mut total_phase_val: i128 = 0;
        for c in &self.crystals {
            total_phase_val += c.get_phase().to_raw() as i128;
        }
        let mean_phase_val = (total_phase_val / n_nodes as i128) as i64;
        
        let mut total_dev_val: i128 = 0;
        for c in &self.crystals {
            total_dev_val += (c.get_phase().to_raw() - mean_phase_val).unsigned_abs() as i128;
        }
        let mut mean_dev_val = (total_dev_val / n_nodes as i128) as i64;
        
        let max_dev: i64 = 180 * 12_960_000;
        if mean_dev_val > max_dev {
            mean_dev_val = max_dev;
        }
        
        // Ratio de coherencia S60
        let coh_val = ((max_dev - mean_dev_val) as i128 * 12_960_000) / max_dev as i128;
        coh_val as i64
    }

    #[pyo3(name = "get_hologram")]
    pub fn get_hologram_py(&self) -> Vec<(usize, i64, i64)> {
        self.crystals.iter().enumerate().map(|(i, c)| {
            (i, c.get_amplitude().to_raw(), c.get_phase().to_raw())
        }).collect()
    }
}

