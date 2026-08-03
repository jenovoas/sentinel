// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/lib.rs
#![forbid(clippy::float_arithmetic)]
#![forbid(clippy::float_cmp)]
#![forbid(clippy::cast_possible_truncation)]
#![forbid(clippy::cast_precision_loss)]
//! SENTINEL CORTEX - FFI Library Interface
//!
//! Provides C-ABI exports for Python integration via ctypes.
//!
//! This library exposes:
//! - BioResonator: Bio-quantum coherence tracking
//! - QuantumScheduler: Adiabatic task scheduling (future)
//! - Portal Detection: Harmonic convergence detection (future)

mod math;
mod quantum;
mod buffer_system;
mod memory;
pub mod concentrator;

use lazy_static::lazy_static;
use quantum::BioResonator;
use std::sync::{Arc, Mutex};

// Global singleton instances
lazy_static! {
    static ref SHARED_BIO: Arc<Mutex<BioResonator>> = Arc::new(Mutex::new(BioResonator::new()));
    static ref CORTEX_SCHEDULER: Mutex<QuantumScheduler> =
        Mutex::new(QuantumScheduler::new(SHARED_BIO.clone()));
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// FFI EXPORTS - BioResonator
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/// Inject biological pulse (keyboard/mouse event)
///
/// # Safety
/// This function is thread-safe via Mutex.
#[no_mangle]
pub extern "C" fn cortex_inject_pulse() {
    let mut bio = SHARED_BIO.lock().unwrap();
    bio.inject_bio_pulse();
}

/// Get current bio-coherence (raw S60 value)
///
/// Returns: i64 representing coherence in S60 base units (tertia)
///
/// # Safety
/// This function is thread-safe via Mutex.
#[no_mangle]
pub extern "C" fn cortex_get_bio_coherence() -> i64 {
    let bio = SHARED_BIO.lock().unwrap();
    bio.get_coherence_raw()
}

/// Apply entropy decay tick
/// Should be called by TimeCrystal at ~41Hz
///
/// # Safety
/// This function is thread-safe via Mutex.
#[no_mangle]
pub extern "C" fn cortex_tick_entropy() {
    let mut bio = SHARED_BIO.lock().unwrap();
    bio.tick_entropy();
}

/// Check if bio-portal is open (coherence >= 90%)
///
/// Returns: 1 if portal open, 0 otherwise
///
/// # Safety
/// This function is thread-safe via Mutex.
#[no_mangle]
pub extern "C" fn cortex_is_bio_portal_open() -> u8 {
    let bio = SHARED_BIO.lock().unwrap();
    if bio.is_portal_open() {
        1
    } else {
        0
    }
}

/// Check if pilot is present (Dead Man's Switch)
///
/// Returns: 1 if pilot present (pulse within 30s), 0 if absent
///
/// # Safety
/// This function is thread-safe via Mutex.
#[no_mangle]
pub extern "C" fn cortex_is_pilot_present() -> u8 {
    let bio = SHARED_BIO.lock().unwrap();
    if bio.is_pilot_present() {
        1
    } else {
        0
    }
}

/// Get normalized coherence level [0.0, 1.0] (as raw S60 tertia)
/// For GUI/telemetry display only
///
/// Returns: i64 in range [0, 216000] (Tertia)
///
/// # Safety
/// This function is thread-safe via Mutex.
#[no_mangle]
pub extern "C" fn cortex_get_coherence_normalized() -> i64 {
    let bio = SHARED_BIO.lock().unwrap();
    bio.get_coherence_raw()
}

/// Get time since last pulse (milliseconds)
///
/// Returns: u64 milliseconds since last biological event
///
/// # Safety
/// This function is thread-safe via Mutex.
#[no_mangle]
pub extern "C" fn cortex_time_since_pulse_ms() -> u64 {
    let bio = SHARED_BIO.lock().unwrap();
    bio.time_since_pulse_ms()
}

/// Reset coherence to zero (manual/emergency reset)
///
/// # Safety
/// This function is thread-safe via Mutex.
#[no_mangle]
pub extern "C" fn cortex_reset_bio() {
    let mut bio = SHARED_BIO.lock().unwrap();
    bio.reset();
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// FFI EXPORTS - QuantumScheduler
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

use math::s60::S60;
use quantum::{QuantumScheduler, Task, TaskType};

/// Tick the quantum scheduler (call at 41.77 Hz)
///
/// # Arguments
/// * `time_s60_raw` - Current time in S60 base units (tertia)
#[no_mangle]
pub extern "C" fn scheduler_tick(time_s60_raw: i64) {
    let mut sched = CORTEX_SCHEDULER.lock().unwrap();
    let time = S60::from_raw(time_s60_raw);
    sched.tick(time);
}

/// Get scheduler efficiency (raw S60 tertia)
#[no_mangle]
pub extern "C" fn scheduler_get_efficiency() -> i64 {
    let sched = CORTEX_SCHEDULER.lock().unwrap();
    sched.get_stats().efficiency.to_base_units()
}

/// Get total energy saved (can be negative)
#[no_mangle]
pub extern "C" fn scheduler_get_energy_saved() -> i64 {
    let sched = CORTEX_SCHEDULER.lock().unwrap();
    sched.get_stats().energy_saved
}

/// Get count of tasks executed in portal
#[no_mangle]
pub extern "C" fn scheduler_get_tasks_in_portal() -> u64 {
    let sched = CORTEX_SCHEDULER.lock().unwrap();
    sched.get_stats().tasks_in_portal
}

/// Get count of tasks forced (overflow)
#[no_mangle]
pub extern "C" fn scheduler_get_tasks_forced() -> u64 {
    let sched = CORTEX_SCHEDULER.lock().unwrap();
    sched.get_stats().tasks_forced
}

/// Get current queue length
#[no_mangle]
pub extern "C" fn scheduler_queue_len() -> usize {
    let sched = CORTEX_SCHEDULER.lock().unwrap();
    sched.queue_len()
}

/// Reset scheduler statistics
#[no_mangle]
pub extern "C" fn scheduler_reset_stats() {
    let mut sched = CORTEX_SCHEDULER.lock().unwrap();
    sched.reset_stats();
}

/// Enqueue a task from FFI
///
/// # Safety
/// This function is thread-safe via Mutex.
/// `callback` must be a valid C-compatible function pointer.
#[no_mangle]
pub extern "C" fn scheduler_enqueue(id: u64, task_type: u8, cost: u32, callback: extern "C" fn()) {
    let mut sched = CORTEX_SCHEDULER.lock().unwrap();

    let t_type = match task_type {
        1 => TaskType::ZPETune,
        2 => TaskType::BCISync,
        3 => TaskType::LatticeGC,
        4 => TaskType::BackupS60,
        5 => TaskType::PhaseAlign,
        _ => TaskType::PhaseAlign, // Default
    };

    let task = Task {
        id,
        task_type: t_type,
        cost,
        callback: unsafe { std::mem::transmute(callback) },
    };

    sched.enqueue(task);
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Tests
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#[cfg(test)]
mod tests {
    use super::*;

    // Serializa los tests que mutan el singleton global SHARED_BIO.
    // Sin esto, corren en paralelo (default cargo) y un test hermano inyecta
    // un pulso entre el reset() y el read() de otro, rompiendo assert_eq!(initial, 0).
    static BIO_TEST_LOCK: Mutex<()> = Mutex::new(());

    #[test]
    fn test_ffi_pulse_injection() {
        let _guard = BIO_TEST_LOCK.lock().unwrap();
        cortex_reset_bio();

        let initial = cortex_get_bio_coherence();
        assert_eq!(initial, 0);

        cortex_inject_pulse();

        let after_pulse = cortex_get_bio_coherence();
        assert!(after_pulse > initial);
    }

    #[test]
    fn test_ffi_portal_detection() {
        let _guard = BIO_TEST_LOCK.lock().unwrap();
        cortex_reset_bio();

        // Not open initially
        assert_eq!(cortex_is_bio_portal_open(), 0);

        // Inject many pulses
        for _ in 0..15 {
            cortex_inject_pulse();
        }

        // Should be open now
        assert_eq!(cortex_is_bio_portal_open(), 1);
    }

    #[test]
    fn test_ffi_entropy_decay() {
        let _guard = BIO_TEST_LOCK.lock().unwrap();
        cortex_reset_bio();

        // Charge
        for _ in 0..10 {
            cortex_inject_pulse();
        }

        let charged = cortex_get_bio_coherence();

        // Decay
        for _ in 0..50 {
            cortex_tick_entropy();
        }

        let decayed = cortex_get_bio_coherence();
        assert!(decayed < charged);
    }
}
