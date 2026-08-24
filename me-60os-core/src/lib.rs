// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// 🛡️ ME-60OS CORE LIBRARY - RUST 🛡️
#![allow(clippy::cast_possible_truncation, clippy::cast_precision_loss)]
#![deny(clippy::float_cmp)]
#[cfg(feature = "extension-module")]
use pyo3::prelude::*;

// Core Modules (Always included for Rust Binaries)
pub mod isochronous_oscillator;
pub mod pai60_lib;
pub mod optomechanical;
pub mod flux_stabilizer; // Estabilizador de flux cuántico (LCG + damping S60)
pub mod quantum_core;
pub mod s60_pid;
pub mod spa;
pub mod spa_complex;
pub mod spa_math;
pub mod time_crystal; // Wrapper
pub mod hexagonal_control;
pub mod atlantean;
pub mod ram_meter; // RAM meter + dimensionado de lattice (sysinfo, S60 puro)
pub mod buffer;   // Predictor de ráfagas: memoria no-Markoviana (kernel OU, S60 puro)
pub mod liquid_memory; // KV-store cognitivo: SHM POSIX nativo + inyección dual a LiquidLattice

// SOMA Backend Modules
pub mod soma;

// Optional Python Modules (Included for logic, but only exported as classes if verified)
pub mod resonant_matrix;

// Utility Modules
pub mod adm;
pub mod agent_manager;
pub mod bci;
pub mod bio;
pub mod buffer_system;
pub mod cortex;
pub mod ebpf_cortex_bridge;
pub mod neural_memory;
pub mod physics;
pub mod qhc;
pub mod resonant_loop;
pub mod scheduler;
pub mod scv;
pub mod guardian_lsm;
pub mod crystal_cipher; // Clave efímera por pulso del cristal (capa de cifrado ring0-adjacent)
pub mod dual_lane; // Dual-lane router: Security (WAL fsync) + Observability (buffer/backpressure)
pub mod dsp; // S60 DSP multiplier: 128-bit accumulator + overflow traps (hardware model)
pub mod celestial; // Celestial navigation: SVector3 + Kepler orbital mechanics (S60)
pub mod numerical_control; // SovereignDDA: interpolador DDA S60 (trayectoria determinista)
pub mod orbital_ascent; // Orbital ascent dynamics: drag/gravedad/thrust S60 (física real)
pub mod shm_bridge;

#[cfg(feature = "extension-module")]
#[pyfunction]
fn py_pai60_divide(a_raw: i64, b: u32) -> PyResult<Option<i64>> {
    let a = crate::spa::SPA::from_raw(a_raw);
    Ok(crate::pai60_lib::pai60_divide(a, b).map(|s| s.to_raw()))
}

#[cfg(feature = "extension-module")]
#[pymodule]
fn me60os_core(m: &Bound<'_, pyo3::types::PyModule>) -> PyResult<()> {
    // Solo exportar clases verificadas y seguras
    m.add_class::<isochronous_oscillator::IsochronousOscillator>()?;
    m.add_class::<spa::SPA>()?;
    m.add_class::<spa_math::SPAMath>()?;
    m.add_class::<spa_complex::ComplexSPA>()?;
    m.add_class::<resonant_matrix::ResonantMatrix>()?;
    m.add_class::<shm_bridge::PySharedBuffer>()?;
    m.add_class::<quantum_core::IsochronousClock>()?;
    m.add_class::<optomechanical::OptomechanicalCooler>()?;
    m.add_class::<s60_pid::S60PID>()?;
    m.add_class::<hexagonal_control::HexagonalController>()?;

    // SOMA classes
    m.add_class::<soma::quantum_scheduler::QuantumSchedulerCore>()?;
    m.add_class::<soma::quantum_scheduler::QuantumBuffer>()?;
    m.add_class::<soma::quantum_scheduler::QuantumSchedulerDaemon>()?;
    m.add_class::<soma::anomaly_detector::AnomalyDetectorCore>()?;
    m.add_class::<guardian_lsm::GuardianLsm>()?;
    m.add_class::<scv::ScvEngine>()?;

    // Core module additions
    m.add_function(wrap_pyfunction!(py_pai60_divide, m)?)?;

    Ok(())
}
