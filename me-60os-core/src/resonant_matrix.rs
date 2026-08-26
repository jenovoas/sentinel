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
#[cfg(feature = "extension-module")]
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

    /// Reusable transfer buffer (hoisted out of step() to avoid per-tick alloc)
    transfers_buf: Vec<SPA>,
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
            transfers_buf: vec![SPA::zero(); size],
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
            transfers_buf: vec![SPA::zero(); size],
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

        // 1. Reuse transfer buffer (hoisted out of step() to avoid per-tick alloc)
        self.transfers_buf.clear();
        self.transfers_buf.resize(size, SPA::zero());
        let transfers: &mut [SPA] = &mut self.transfers_buf;

        // 2D Hexagonal Ring Radius Approximation
        // integer ceil(sqrt(size)) sin float: binary search en [1, size]
        let side = {
            let mut lo = 1usize;
            let mut hi = size;
            while lo < hi {
                let mid = (lo + hi) >> 1;
                if mid * mid >= size {
                    hi = mid;
                } else {
                    lo = mid + 1;
                }
            }
            lo
        };

        for i in 0..size {
            let amp_i = self.crystals[i].get_amplitude();

            // Nearest Neighbors in Hexagonal 2D Grid Topology
            let mut neighbor_indices = Vec::with_capacity(6);
            if i >= side {
                neighbor_indices.push(i - side);
            } // North
            if i + side < size {
                neighbor_indices.push(i + side);
            } // South
            if i % side > 0 {
                neighbor_indices.push(i - 1);
            } // West
            if (i + 1) % side != 0 && i + 1 < size {
                neighbor_indices.push(i + 1);
            } // East
            if i >= side && (i + 1) % side != 0 {
                neighbor_indices.push(i - side + 1);
            } // North-East
            if i + side < size && i % side > 0 {
                neighbor_indices.push(i + side - 1);
            } // South-West

            for &n_idx in &neighbor_indices {
                let amp_neighbor = self.crystals[n_idx].get_amplitude();
                let diff = amp_i - amp_neighbor;
                if diff.to_raw() > 0 {
                    let flow = (diff * self.coupling_factor) / SPA::new(6, 0, 0, 0, 0); // Normalized by 6 hexagonal neighbors
                    transfers[i] = transfers[i] - flow;
                    transfers[n_idx] = transfers[n_idx] + flow;
                }
            }
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

    /// Convierte un dato binario (0..denominator-1) a amplitud armónica EXACTA
    /// vía PAI-60 (tabla recíproca base-60) y la inyecta en el nodo.
    ///
    /// Esto es el "conversor binario -> amplitud" que faltaba enchufar: en lugar
    /// de meter `i64` crudo como presión (inject), deriva la amplitud como
    /// `pai60_divide(SPA::from_raw(value), denominator)` -> razón recíproca exacta
    /// en escala 60^4, sin contaminación float.
    ///
    /// Si el denominador no es regular (no está en la tabla PAI-60), cae back al
    /// inject crudo para no perder el pulso.
    pub fn inject_pai(&mut self, index: usize, value: i64, denominator: u32) {
        if index >= self.crystals.len() {
            return;
        }
        let numer = SPA::from_int(value);
        let amp = match crate::pai60_lib::pai60_divide(numer, denominator) {
            Some(a) => a,
            None => {
                if denominator > 0 {
                    let raw = (value as i128 * SPA::SCALE_0 as i128) / (denominator as i128);
                    SPA::from_raw(raw as i64)
                } else {
                    SPA::from_int(value)
                }
            }
        };
        // Suma la amplitud SPA ya calculada directo al oscilador.
        // NO usar transduce_pulse(amp.to_raw()): ese metodo espera un entero y
        // lo re-escala por SCALE_0 (doble escala -> 8.4e13 en vez de 1/2).
        self.crystals[index].amplitude = self.crystals[index].amplitude + amp;
    }

    /// Adds an SPA amplitude directly to a node's amplitude without re-scaling.
    /// Use this when you already have an SPA value (not an integer pressure).
    /// Mirrors the internal pattern from `inject_pai` line 153.
    pub fn inject_spa(&mut self, index: usize, amp: SPA) {
        if index < self.crystals.len() {
            self.crystals[index].amplitude = self.crystals[index].amplitude + amp;
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

        // SAFETY: buf_size was checked >= total_size on line 256; src/dst are non-overlapping; n is exact byte count
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

        // SAFETY: buffer.size was checked >= total_size on line 278; src/dst are non-overlapping; n is exact byte count
        unsafe {
            let dst_ptr = self.crystals.as_mut_ptr() as *mut u8;
            std::ptr::copy_nonoverlapping(shm_ptr, dst_ptr, total_size);
        }

        Ok(())
    }
}

#[cfg_attr(feature = "extension-module", pymethods)]
impl ResonantMatrix {
    #[cfg_attr(feature = "extension-module", new)]
    pub fn __new__(rings: usize) -> Self {
        // Hexagonal number formula: H_n = 3n(n+1) + 1
        // Ring 150 ~= 68,000 nodes
        let size = 3 * rings * (rings + 1) + 1;
        Self::new(size)
    }

    #[cfg_attr(feature = "extension-module", pyo3(name = "inject"))]
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

    #[cfg_attr(feature = "extension-module", pyo3(name = "step"))]
    pub fn step_py(&mut self) {
        self.step();
    }

    #[cfg_attr(feature = "extension-module", pyo3(name = "stabilize"))]
    pub fn stabilize_wrapper(&mut self, cycles: usize) {
        self.stabilize_py(cycles);
    }

    pub fn save_snapshot(&self, buffer: &mut PySharedBuffer) -> Result<(), String> {
        self.sync_to_shm(buffer)
    }

    pub fn load_snapshot(&mut self, buffer: &PySharedBuffer) -> Result<(), String> {
        self.load_from_shm(buffer)
    }

    /// Returns size of a single crystal struct (for Python to allocate SHM)
    #[cfg_attr(feature = "extension-module", staticmethod)]
    pub fn get_node_size() -> usize {
        std::mem::size_of::<IsochronousOscillator>()
    }

    pub fn count_nodes(&self) -> usize {
        self.crystals.len()
    }

    pub fn active_memory_usage(&self) -> usize {
        self.crystals.len() * std::mem::size_of::<IsochronousOscillator>()
    }

    #[cfg_attr(feature = "extension-module", pyo3(name = "set_context"))]
    pub fn set_context_py(&mut self, index: usize, payload: String) {
        if index < self.crystals.len() {
            self.context_data.insert(index, payload);
        }
    }

    #[cfg_attr(feature = "extension-module", pyo3(name = "get_context"))]
    pub fn get_context_py(&self, index: usize) -> Option<String> {
        self.context_data.get(&index).cloned()
    }

    #[cfg_attr(feature = "extension-module", pyo3(name = "save_crystal"))]
    pub fn save_crystal_py(&self, path: String) -> Result<(), String> {
        use flate2::write::GzEncoder;
        use flate2::Compression;
        use std::fs::File;
        use std::io::Write;

        let file = File::create(&path).map_err(|e| e.to_string())?;

        let mut encoder = GzEncoder::new(file, Compression::default());
        let encoded: Vec<u8> = serde_json::to_vec(self).map_err(|e| e.to_string())?;

        encoder.write_all(&encoded).map_err(|e| e.to_string())?;

        Ok(())
    }

    #[cfg_attr(feature = "extension-module", pyo3(name = "load_crystal"))]
    pub fn load_crystal_py(&mut self, path: String) -> Result<(), String> {
        use flate2::read::GzDecoder;
        use std::fs::File;
        use std::io::Read;

        let file = File::open(&path).map_err(|e| e.to_string())?;

        let mut decoder = GzDecoder::new(file);
        let mut buffer = Vec::new();
        decoder
            .read_to_end(&mut buffer)
            .map_err(|e| e.to_string())?;

        let decoded: ResonantMatrix = serde_json::from_slice(&buffer).map_err(|e| e.to_string())?;

        self.crystals = decoded.crystals;
        self.context_data = decoded.context_data;
        self.coupling_factor = decoded.coupling_factor;
        self.dt = decoded.dt;

        Ok(())
    }

    #[cfg_attr(feature = "extension-module", pyo3(name = "set_node_state"))]
    pub fn set_node_state_py(&mut self, index: usize, amp: SPA, phase: SPA) {
        if index < self.crystals.len() {
            self.crystals[index].amplitude = amp;
            self.crystals[index].phase = phase;
        }
    }

    #[cfg_attr(feature = "extension-module", pyo3(name = "get_node_amp_raw"))]
    pub fn get_node_amp_raw_py(&self, index: usize) -> Option<SPA> {
        if index < self.crystals.len() {
            Some(self.crystals[index].amplitude)
        } else {
            None
        }
    }

    #[cfg_attr(feature = "extension-module", pyo3(name = "get_node_phase_raw"))]
    pub fn get_node_phase_raw_py(&self, index: usize) -> Option<SPA> {
        if index < self.crystals.len() {
            Some(self.crystals[index].phase)
        } else {
            None
        }
    }

    #[cfg_attr(feature = "extension-module", pyo3(name = "total_energy"))]
    pub fn total_energy_py(&self) -> i64 {
        self.total_energy().to_raw()
    }

    #[cfg_attr(feature = "extension-module", pyo3(name = "measure_coherence"))]
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

    #[cfg_attr(feature = "extension-module", pyo3(name = "get_hologram"))]
    pub fn get_hologram_py(&self) -> Vec<(usize, i64, i64)> {
        self.crystals
            .iter()
            .enumerate()
            .map(|(i, c)| (i, c.get_amplitude().to_raw(), c.get_phase().to_raw()))
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_inject_pai_derives_exact_reciprocal() {
        // Conversor binario -> amplitud PAI-60: value=30, denom=60 => 30/60 = 0;30 = 1/2
        // Amplitude inyectada debe ser la recíproca EXACTA (SPA raw de 1/2),
        // NO el i64 crudo (que seria 30).
        let mut lattice = ResonantMatrix::new(3);
        lattice.inject_pai(0, 30, 60);

        let amp = lattice.get_amplitudes()[0].to_raw();
        let half = SPA::new(0, 30, 0, 0, 0).to_raw(); // 30/60 = 0;30 = 1/2
        assert_eq!(
            amp, half,
            "inject_pai debe derivar 30/60=1/2 exacto, no 30 crudo"
        );
        assert_ne!(amp, 30, "no debe inyectar el entero crudo");

        let mut lattice2 = ResonantMatrix::new(3);
        lattice2.inject_pai(0, 21, 7);
        assert_eq!(lattice2.get_amplitudes()[0], SPA::from_int(3));
    }

    #[test]
    fn test_inject_spa_no_double_scale() {
        // inject_spa añade el SPA directo sin re-escalar.
        // La landmine anterior era: inject(0, signal.to_raw()) en cortex.rs:92,
        // que re-escalaba por SCALE_0 (doble-escala -> 8.4e13 en vez de 1/2).
        let mut l = ResonantMatrix::new(3);
        l.inject_spa(0, SPA::new(0, 30, 0, 0, 0)); // 1/2
        let amp = l.get_amplitudes()[0];
        assert_eq!(
            amp,
            SPA::new(0, 30, 0, 0, 0),
            "amplitude should be 1/2 exactly"
        );
        assert_ne!(amp.to_raw(), 30, "should NOT be the raw integer 30");
        assert_ne!(
            amp.to_raw(),
            30 * SPA::SCALE_0,
            "should NOT be 30 * SCALE_0 (double-scale)"
        );
    }

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

    #[test]
    fn test_inject_pai_non_regular_scaling() {
        let mut matrix = ResonantMatrix::new(3);
        matrix.inject_pai(0, 1, 2);
        assert_eq!(matrix.get_amplitudes()[0].to_raw(), 6_480_000);

        matrix.inject_pai(1, 1, 17);
        assert_eq!(matrix.get_amplitudes()[1].to_raw(), 762_352);
    }
}
