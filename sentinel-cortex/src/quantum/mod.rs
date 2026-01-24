// src/quantum/mod.rs
//! Quantum components - Bio-Resonance, Portal Detection, Scheduler
//!
//! Implements the core quantum-bio alignment logic in S60.

pub mod bio_resonator;
pub mod portal_detector;
pub mod quantum_scheduler;

// Re-exports for internal crate use
pub(crate) use bio_resonator::BioResonator;
pub(crate) use portal_detector::PortalDetector;
pub(crate) use quantum_scheduler::{QuantumScheduler, SchedulerStats, Task, TaskType};
