// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
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
#[allow(unused_imports)]
pub(crate) use bio_resonator::BioResonator;
#[allow(unused_imports)]
pub(crate) use portal_detector::PortalDetector;
#[allow(unused_imports)]
pub(crate) use quantum_scheduler::{QuantumScheduler, Task, TaskType};
#[allow(unused_imports)]
pub(crate) use semantic_router::{Intent, SemanticRouter};
#[allow(unused_imports)]
pub(crate) use semantic_shell::SemanticShell;
