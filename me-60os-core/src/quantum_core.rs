// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 💎 CORE CUÁNTICO ME-60OS 💎
//! Logic Pura Rust con soporte condicional para PyO3

use crate::isochronous_oscillator::IsochronousOscillator;
use crate::spa::SPA;
use serde::{Deserialize, Serialize};
use std::collections::VecDeque;
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

#[cfg(feature = "extension-module")]
use pyo3::prelude::*;

// =============================================================================
// S60 PID CONTROLLER (Extended with Non-Markovian History Kernel)
// =============================================================================
//
// Extension based on Nandi & Vitiello 2026 (arXiv:2606.30890) — [EXT-NV]:
// The Bateman dual oscillator generates non-Markovian memory via partial trace.
// The reduced dynamics contains a history-dependent memory kernel.
// Extending PID integral to full lattice history eliminates need for external
// Salto-17 correction (self-correction via intrinsic dynamics).
//
// ## References (S60PID Non-Markovian kernel)
// - [EXT-NV] / [NV-050] Nandi & Vitiello (2026). arXiv:2606.30890 — Bateman dual oscillator / Non-Markovian memory.
//   PDF local: `papers/referencias_locales/Papers/nandi_vitiello/Nandi_2606.30890.pdf`.
// - [NV-049] Nandi (2026). arXiv:2606.08595 — *Is Exact Markovianity Fundamental Once Time Is Relational?*
// - [NV-040] Nandi (2025). arXiv:2503.19688 — *Gravitationally induced entanglement: a memory-driven time-crystalline phase?*
// - [P-RES] Novoa, J. (2026). *Aritmética Sexagesimal como Base de Sistemas.* `RESEARCH_es.md`.

// #[cfg_attr(feature = "extension-module", pyclass)]
#[derive(Clone, Serialize, Deserialize)]
pub struct S60PID {
    kp: i64,
    ki: i64,
    kd: i64,
    pub setpoint: SPA,
    pub integral: SPA,
    pub prev_error: SPA,
    // Non-Markovian history kernel (Nandi & Vitiello 2026)
    // Stores full lattice error history for memory-dependent correction
    history: VecDeque<SPA>,
    history_capacity: usize,
    // Kernel weights for history integration (exponential decay default)
    kernel_alpha: SPA,
}

impl S60PID {
    pub fn new(kp_raw: i64, ki_raw: i64, kd_raw: i64, setpoint_raw: i64) -> Self {
        Self {
            kp: kp_raw,
            ki: ki_raw,
            kd: kd_raw,
            setpoint: SPA::from_raw(setpoint_raw),
            integral: SPA::zero(),
            prev_error: SPA::zero(),
            history: VecDeque::with_capacity(68), // 68 ticks = 1 Salto-17 cycle
            history_capacity: 68,
            kernel_alpha: SPA::new(0, 50, 0, 0, 0), // 5/6 decay (0.833...)
        }
    }

    /// Standard PID update (backward compatible)
    pub fn update(&mut self, measured_raw: i64, dt_raw: i64) -> i64 {
        self.update_internal(measured_raw, dt_raw)
    }

    /// Resets internal PID state (integral, prev_error, history)
    pub fn reset(&mut self) {
        self.integral = SPA::zero();
        self.prev_error = SPA::zero();
        self.history.clear();
    }

    /// Standard PID update (internal implementation)
    pub fn update_internal(&mut self, measured_raw: i64, dt_raw: i64) -> i64 {
        let measured = SPA::from_raw(measured_raw);
        let dt = SPA::from_raw(dt_raw);
        let error = self.setpoint - measured;

        let kp_spa = SPA::from_raw(self.kp);
        let ki_spa = SPA::from_raw(self.ki);
        let kd_spa = SPA::from_raw(self.kd);

        let p_term = kp_spa * error;
        self.integral = self.integral + (error * dt);
        let i_term = ki_spa * self.integral;

        let d_term = if dt.to_raw() > 0 {
            let d_error = error - self.prev_error;
            kd_spa * d_error / dt
        } else {
            SPA::zero()
        };

        self.prev_error = error;

        // Store in history for non-Markovian kernel
        self.history.push_back(error);
        if self.history.len() > self.history_capacity {
            self.history.pop_front();
        }

        (p_term + i_term + d_term).to_raw()
    }

    /// Non-Markovian PID update with full lattice history
    /// Implements memory kernel from Nandi & Vitiello 2026:
    /// The correction depends on entire history, not just current error
    pub fn update_with_history_internal(
        &mut self,
        measured_raw: i64,
        dt_raw: i64,
        lattice_errors: Vec<i64>,
    ) -> i64 {
        let measured = SPA::from_raw(measured_raw);
        let dt = SPA::from_raw(dt_raw);
        let error = self.setpoint - measured;

        let kp_spa = SPA::from_raw(self.kp);
        let ki_spa = SPA::from_raw(self.ki);
        let kd_spa = SPA::from_raw(self.kd);

        let p_term = kp_spa * error;

        // Standard integral (local memory)
        self.integral = self.integral + (error * dt);

        // Non-Markovian kernel: integrate full lattice history
        // Kernel: exponential decay with alpha = 5/6 (base-60 harmonic)
        let mut non_markovian_integral = SPA::zero();
        let mut weight = SPA::one();

        for &hist_error in self.history.iter().rev() {
            non_markovian_integral = non_markovian_integral + (hist_error * weight);
            // Decay weight by alpha (5/6 in base-60)
            weight = weight * self.kernel_alpha;
        }

        // Also integrate current lattice errors (global state)
        for lattice_err_raw in lattice_errors {
            let lattice_err = SPA::from_raw(lattice_err_raw);
            non_markovian_integral = non_markovian_integral + (lattice_err * weight);
            weight = weight * self.kernel_alpha;
        }

        // Combined integral: local + non-Markovian
        let combined_integral = self.integral + non_markovian_integral;
        let i_term = ki_spa * combined_integral;

        let d_term = if dt.to_raw() > 0 {
            let d_error = error - self.prev_error;
            kd_spa * d_error / dt
        } else {
            SPA::zero()
        };

        self.prev_error = error;

        // Store in history
        self.history.push_back(error);
        if self.history.len() > self.history_capacity {
            self.history.pop_front();
        }

        (p_term + i_term + d_term).to_raw()
    }

    pub fn reset_internal(&mut self) {
        self.integral = SPA::zero();
        self.prev_error = SPA::zero();
        self.history.clear();
    }

    /// Get non-Markovian correction for Salto-17 elimination
    /// Returns correction in nanoseconds based on history kernel
    pub fn calculate_drift_correction(&self, current_tick: u64) -> u64 {
        if current_tick == 0 || !current_tick.is_multiple_of(68) {
            return 0;
        }

        // Instead of fixed 700,000ns, compute from history kernel
        let mut correction_accum = SPA::zero();
        let mut weight = SPA::one();

        for hist_error in self.history.iter().rev() {
            let correction = hist_error.to_raw().abs() * 1000; // scale to ns
            if correction > 0 {
                correction_accum = correction_accum + SPA::from_raw(correction);
            }
            weight = weight * self.kernel_alpha;
        }

        correction_accum.to_raw().unsigned_abs()
    }

    pub fn set_history_capacity(&mut self, capacity: usize) {
        self.history_capacity = capacity;
        self.history = VecDeque::with_capacity(capacity);
    }
}

// =============================================================================
// ISOCHRONOUS CLOCK
// =============================================================================

#[cfg(feature = "extension-module")]
#[pyclass(module = "me60os_core")]
pub struct IsochronousClock {
    pub tick_interval_ns: u64,
    pub ticks: u64,
    start_time: Instant,
}

#[cfg(not(feature = "extension-module"))]
pub struct IsochronousClock {
    pub tick_interval_ns: u64,
    pub ticks: u64,
    start_time: Instant,
}

#[cfg(feature = "extension-module")]
#[pymethods]
impl IsochronousClock {
    #[new]
    pub fn py_new() -> Self {
        Self::new_internal()
    }

    #[pyo3(name = "tick")]
    pub fn py_tick(&mut self) {
        self.tick_internal();
    }

    #[pyo3(name = "get_nanos")]
    pub fn py_get_nanos(&self) -> u64 {
        self.get_nanos_internal()
    }
}

impl IsochronousClock {
    pub fn new_internal() -> Self {
        Self {
            tick_interval_ns: 23_939_835,
            ticks: 0,
            start_time: Instant::now(),
        }
    }

    pub fn tick_internal(&mut self) {
        self.ticks += 1;

        let target_ns = self.ticks as u128 * self.tick_interval_ns as u128;
        let elapsed_ns = self.start_time.elapsed().as_nanos();

        if target_ns > elapsed_ns {
            let sleep_ns = target_ns - elapsed_ns;
            thread::sleep(Duration::from_nanos(sleep_ns as u64));
        }
    }

    pub fn get_nanos_internal(&self) -> u64 {
        self.start_time.elapsed().as_nanos() as u64
    }
}

// =============================================================================
// SNAPSHOT STRUCTURES
// =============================================================================

#[derive(Clone, Serialize, Deserialize)]
pub struct CellSnapshot {
    pub index: usize,
    pub amplitude_raw: i64,
    pub phase_raw: i64,
    pub metadata: Option<String>,
}

#[derive(Clone, Serialize, Deserialize)]
pub struct CrystalSnapshot {
    pub timestamp: u64,
    pub size: usize,
    pub lattice: Vec<CellSnapshot>,
    pub phase: String,
    /// Coherencia escalada x1000 (ej: 600 = 0.60, 1000 = 1.00) — sin floats (Base-60)
    pub coherence: u64,
    pub tick: u64,
}

// =============================================================================
// RESONANT BUFFER
// =============================================================================

// #[cfg_attr(feature = "extension-module", pyclass)]
pub struct ResonantBuffer {
    pub size: usize,
    pub lattice: Vec<IsochronousOscillator>,
    pub metadata_map: Vec<Option<String>>,
    pub pids: Vec<S60PID>,
    pub target_amplitudes: Vec<SPA>,
    pub clock: IsochronousClock,
    pub dt: SPA,
    pub use_harmonic: bool,
    pub phase: String,
    /// Coherencia escalada x1000 (ej: 600 = 0.60, 1000 = 1.00) — sin floats (Base-60)
    pub coherence: u64,
}

// #[cfg_attr(feature = "extension-module", pymethods)]
impl ResonantBuffer {
    // #[cfg_attr(feature = "extension-module", new)]
    pub fn new(size_slots: usize, use_harmonic: bool) -> Self {
        let lattice: Vec<IsochronousOscillator> = (0..size_slots)
            .map(|i| IsochronousOscillator::new(&format!("Cell-{}", i)))
            .collect();

        let kp = SPA::new(0, 30, 0, 0, 0).to_raw();
        let ki = SPA::new(0, 10, 0, 0, 0).to_raw();
        let kd = SPA::new(0, 5, 0, 0, 0).to_raw();

        let pids: Vec<S60PID> = (0..size_slots)
            .map(|_| S60PID::new(kp, ki, kd, 0))
            .collect();

        Self {
            size: size_slots,
            lattice,
            metadata_map: vec![None; size_slots],
            pids,
            target_amplitudes: vec![SPA::zero(); size_slots],
            clock: IsochronousClock::new_internal(),
            dt: SPA::new(0, 1, 0, 0, 0),
            use_harmonic,
            phase: "YOD".to_string(),
            coherence: 0,
        }
    }

    // #[cfg_attr(feature = "extension-module", pyo3(signature = (filename)))]
    pub fn save_snapshot(&self, filename: String) -> std::io::Result<bool> {
        let mut cell_data = Vec::new();
        for (i, xtal) in self.lattice.iter().enumerate() {
            let amp_raw = xtal.get_amplitude().to_raw();
            if amp_raw > 0 {
                cell_data.push(CellSnapshot {
                    index: i,
                    amplitude_raw: amp_raw,
                    phase_raw: xtal.get_phase().to_raw(),
                    metadata: self.metadata_map[i].clone(),
                });
            }
        }

        let snapshot = CrystalSnapshot {
            timestamp: SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs(),
            size: self.size,
            lattice: cell_data,
            phase: self.phase.clone(),
            coherence: self.coherence,
            tick: self.clock.ticks,
        };

        let json = serde_json::to_string_pretty(&snapshot).expect("JSON Serialization failed");
        std::fs::write(filename, json)?;
        Ok(true)
    }

    // #[cfg_attr(feature = "extension-module", pyo3(signature = (filename)))]
    pub fn load_snapshot(&mut self, filename: String) -> std::io::Result<bool> {
        if !std::path::Path::new(&filename).exists() {
            return Ok(false);
        }
        let json = std::fs::read_to_string(filename)?;
        let snapshot: CrystalSnapshot =
            serde_json::from_str(&json).expect("JSON Deserialization failed");

        for cell in snapshot.lattice {
            if cell.index < self.size {
                self.lattice[cell.index].amplitude = SPA::from_raw(cell.amplitude_raw);
                self.lattice[cell.index].phase = SPA::from_raw(cell.phase_raw);
                self.metadata_map[cell.index] = cell.metadata;
                self.target_amplitudes[cell.index] = self.lattice[cell.index].amplitude;
                self.pids[cell.index].setpoint = self.lattice[cell.index].amplitude;
                self.pids[cell.index].reset();
            }
        }
        self.phase = snapshot.phase;
        self.coherence = snapshot.coherence; // u64 x1000
        self.clock.ticks = snapshot.tick;
        Ok(true)
    }
}

// =============================================================================
// LIQUID LATTICE STORAGE
// =============================================================================

// #[cfg_attr(feature = "extension-module", pyclass)]
pub struct LiquidLattice {
    pub buffer: ResonantBuffer,
}

// #[cfg_attr(feature = "extension-module", pymethods)]
impl LiquidLattice {
    // #[cfg_attr(feature = "extension-module", new)]
    pub fn new(size_slots: usize) -> Self {
        Self {
            buffer: ResonantBuffer::new(size_slots, false),
        }
    }

    // #[cfg_attr(feature = "extension-module", pyo3(signature = (payload_a, payload_b)))]
    pub fn inject_dual_channel(&mut self, payload_a: Vec<u8>, payload_b: Vec<u8>) {
        let chunk_a = 8;
        let chunks_a: Vec<Vec<u8>> = payload_a.chunks(chunk_a).map(|c| c.to_vec()).collect();
        let chunks_b: Vec<Vec<u8>> = payload_b.chunks(1).map(|c| c.to_vec()).collect();

        for i in 0..self.buffer.size {
            if i < chunks_a.len() {
                let val = i64::from_be_bytes(pad_to_8(&chunks_a[i]));
                self.buffer.lattice[i].amplitude = SPA::from_raw(val);
                self.buffer.target_amplitudes[i] = self.buffer.lattice[i].amplitude;
                self.buffer.pids[i].setpoint = self.buffer.lattice[i].amplitude;
            }
            if i < chunks_b.len() {
                let deg = ((chunks_b[i][0] as i64) * 360) / 256;
                let deg_norm = deg.clamp(0, 359);
                self.buffer.lattice[i].phase = SPA::new(deg_norm, 0, 0, 0, 0);
            }
        }
    }

    // #[cfg_attr(feature = "extension-module", pyo3(signature = (filename)))]
    pub fn save(&self, filename: String) -> std::io::Result<bool> {
        self.buffer.save_snapshot(filename)
    }
    // #[cfg_attr(feature = "extension-module", pyo3(signature = (filename)))]
    pub fn load(&mut self, filename: String) -> std::io::Result<bool> {
        self.buffer.load_snapshot(filename)
    }

    pub fn retrieve_dual_channel(&self, count_a: usize, count_b: usize) -> (Vec<u8>, Vec<u8>) {
        let mut rec_a = Vec::new();
        let mut rec_b = Vec::new();
        for i in 0..self.buffer.size {
            let amp = self.buffer.lattice[i].amplitude;
            if amp.to_raw() > 0 {
                let raw_amp = amp.to_raw().unsigned_abs();
                let bytes = raw_amp.to_be_bytes();
                let non_zero: Vec<u8> = bytes.iter().copied().skip_while(|&b| b == 0).collect();
                if rec_a.len() < count_a {
                    rec_a.extend_from_slice(&non_zero);
                }
            }
            if rec_b.len() < count_b {
                let phase = self.buffer.lattice[i].phase;
                let phase_deg = phase.to_raw() / SPA::SCALE_0;
                let deg_normalized = phase_deg.clamp(0, 359);
                let byte_val = ((deg_normalized * 256) / 360) as u8;
                rec_b.push(byte_val);
            }
        }
        (rec_a, rec_b)
    }
}

fn pad_to_8(data: &[u8]) -> [u8; 8] {
    let mut padded = [0u8; 8];
    let len = data.len().min(8);
    padded[8 - len..].copy_from_slice(&data[..len]);
    padded
}
