// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// 🛡️ ME-60OS: CORTEX ENGINE 🛡️
// Conexión del Cortex Engine con el Lattice Fonónico Principal (ResonantMatrix)

use crate::buffer_system::ResonantBuffer;
use crate::resonant_matrix::ResonantMatrix;
use crate::spa::SPA;
use std::sync::Arc;

/// Cortex Engine acoplado al Lattice Fonónico Principal
pub struct CortexEngine {
    pub neurons: usize,
    pub buffer: Arc<ResonantBuffer>,
    pub input_buffer: Option<Arc<ResonantBuffer>>,
    pub total_energy: SPA,
    pub lattice: ResonantMatrix,
}

impl CortexEngine {
    pub fn new(neurons: usize) -> Self {
        let size = if neurons == 0 { 64 } else { neurons };
        Self {
            neurons: size,
            buffer: Arc::new(ResonantBuffer::new()),
            input_buffer: None,
            total_energy: SPA::zero(),
            lattice: ResonantMatrix::new(size),
        }
    }

    pub fn process_thought(&mut self, input_val: i64, _dt_seconds: i64) -> i64 {
        // Inyectar presión en el lattice fonónico principal y avanzar un paso
        let target_node = (input_val.unsigned_abs() as usize) % self.neurons;
        self.lattice.inject(target_node, input_val);
        self.lattice.step();
        self.total_energy = self.lattice.total_energy();
        self.lattice.total_energy().to_raw()
    }

    pub fn attach_buffer(&mut self, buffer: Arc<ResonantBuffer>) {
        self.input_buffer = Some(buffer);
    }

    pub fn consume_buffer(&mut self) -> i64 {
        let mut processed = 0i64;
        while let Some(event) = self.buffer.pop() {
            let raw_val = event.entropy_signal as i64;
            let target_node = (raw_val.unsigned_abs() as usize) % self.neurons;
            self.lattice.inject(target_node, raw_val);
            processed += 1;
        }
        if processed > 0 {
            self.lattice.step();
            self.total_energy = self.lattice.total_energy();
        }
        processed
    }

    pub fn quantum_pulse(&mut self, phase_raw: i64) -> bool {
        self.lattice.step();
        let energy = self.lattice.total_energy().to_raw();
        self.total_energy = self.lattice.total_energy();
        (energy ^ phase_raw) >= 0
    }

    pub fn add_synapse(&mut self, _from_id: usize, _to_id: u32, weight_raw: i64, _delay_raw: i64) {
        let target_node = (_to_id as usize) % self.neurons;
        self.lattice.inject(target_node, weight_raw);
    }

    pub fn get_guardian_telemetry(&self) -> (SPA, SPA) {
        (self.total_energy, self.lattice.coupling_factor)
    }

    pub fn init_persistence(&mut self, _path: &str) -> Result<(), Box<dyn std::error::Error>> {
        Ok(())
    }

    pub fn sync_persistence(&self) {
    }

    pub fn apply_plasticity(&mut self, entropy: SPA) {
        let raw = entropy.to_raw();
        let new_coupling = self.lattice.coupling_factor + SPA::from_raw(raw / 60);
        self.lattice.set_coupling(new_coupling);
    }

    pub fn activate_neuron(&mut self, neuron_id: usize, signal: SPA) {
        let target_node = neuron_id % self.neurons;
        self.lattice.inject(target_node, signal.to_raw());
        self.lattice.step();
        self.total_energy = self.lattice.total_energy();
    }
}
