// src/quantum/mod.rs
//! Quantum components - Bio-Resonance, Portal Detection, Scheduler
//!
//! Implements the core quantum-bio alignment logic in S60.

pub mod bio_resonator;
pub mod portal_detector;
pub mod quantum_scheduler;
pub mod semantic_router;
pub mod semantic_shell;

// Re-exports for internal crate use
pub(crate) use bio_resonator::BioResonator;
pub(crate) use portal_detector::PortalDetector;
pub(crate) use quantum_scheduler::{QuantumScheduler, SchedulerStats, Task, TaskType};
pub(crate) use semantic_router::{Intent, SemanticRouter};
pub(crate) use semantic_shell::SemanticShell;
