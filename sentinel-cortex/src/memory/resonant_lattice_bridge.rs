// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//
// Direct integration bridge with me-60os ResonantLattice. Silenced at module level.
#![allow(dead_code)]

//! # 🧠 Resonant Lattice Bridge (ME-60OS) 🧠
//!
//! Direct Rust integration with ME-60OS ResonantLattice + PySharedBuffer.
//! This avoids Python-level bridging and preserves S60-only arithmetic.

use me60os_core::resonant_matrix::ResonantMatrix as ResonantLattice;
use me60os_core::shm_bridge::PySharedBuffer;
use me60os_core::spa::SPA as MeS60;

/// Bridge wrapper for ME-60OS ResonantLattice
pub struct ResonantLatticeBridge {
    lattice: ResonantLattice,
}

impl ResonantLatticeBridge {
    /// Create a new resonant lattice with N nodes.
    pub fn new(nodes: usize) -> Self {
        Self {
            lattice: ResonantLattice::new(nodes),
        }
    }

    /// Create a lattice with custom coupling (raw S60 in ME-60OS scale).
    pub fn with_coupling_raw(nodes: usize, coupling_raw: i64) -> Self {
        let coupling = MeS60::from_raw(coupling_raw);
        Self {
            lattice: ResonantLattice::with_coupling(nodes, coupling),
        }
    }

    /// Execute one time-step.
    pub fn step(&mut self) {
        self.lattice.step();
    }

    /// Inject pressure at node index.
    pub fn inject(&mut self, index: usize, pressure: i64) {
        self.lattice.inject(index, pressure);
    }

    /// Convierte dato binario a amplitud armónica EXACTA via PAI-60 y la inyecta.
    /// PRUEBA: reemplaza `inject` crudo en el drive continuo cuando esta activo.
    pub fn inject_pai(&mut self, index: usize, value: i64, denominator: u32) {
        self.lattice.inject_pai(index, value, denominator);
    }

    /// Inyecta una amplitud SPA ya escalada SIN re-escalar.
    /// Usar para valores en raw ME-60OS (ej. entropy_s60_raw del kernel eBPF):
    /// `inject()` interpreta su i64 como unidades enteras y lo multiplica por SCALE_0.
    pub fn inject_spa(&mut self, index: usize, amp: MeS60) {
        self.lattice.inject_spa(index, amp);
    }

    /// Get total energy as ME-60OS raw S60.
    pub fn total_energy_raw(&self) -> i64 {
        self.lattice.total_energy().to_raw()
    }

    /// Get amplitudes as ME-60OS raw S60 values.
    pub fn amplitudes_raw(&self) -> Vec<i64> {
        self.lattice
            .get_amplitudes()
            .iter()
            .map(|v| v.to_raw())
            .collect()
    }

    /// Get phases as ME-60OS raw S60 values.
    pub fn phases_raw(&self) -> Vec<i64> {
        self.lattice
            .get_phases()
            .iter()
            .map(|v| v.to_raw())
            .collect()
    }

    /// Reset lattice to ground state.
    pub fn reset(&mut self) {
        self.lattice.reset();
    }

    /// Set coupling factor (raw S60 in ME-60OS scale).
    pub fn set_coupling_raw(&mut self, coupling_raw: i64) {
        self.lattice.set_coupling(MeS60::from_raw(coupling_raw));
    }

    /// Set time step (raw S60 in ME-60OS scale).
    pub fn set_dt_raw(&mut self, dt_raw: i64) {
        self.lattice.set_dt(MeS60::from_raw(dt_raw));
    }

    /// Stabilize lattice phases (linear diffusion).
    pub fn stabilize(&mut self, cycles: usize) {
        self.lattice.stabilize_py(cycles);
    }

    /// Sync current lattice state to shared memory.
    pub fn sync_to_shm(&self, buffer: &mut PySharedBuffer) -> Result<(), String> {
        self.lattice.sync_to_shm(buffer)
    }

    /// Load lattice state from shared memory.
    pub fn load_from_shm(&mut self, buffer: &PySharedBuffer) -> Result<(), String> {
        self.lattice.load_from_shm(buffer)
    }
}

/// Helper to create shared memory buffer (ME-60OS PySharedBuffer).
pub fn create_shared_buffer(name: &str, size: usize, create: bool) -> Result<PySharedBuffer, String> {
    PySharedBuffer::new(name.to_string(), size, create).map_err(|e| e.to_string())
}
