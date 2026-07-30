// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ GUARDIAN LSM: RING 0 EXECUTION CONTROL 🛡️
//! 
//! User-space component of the eBPF LSM Guardian.
//! Enforces Base-60 coherence thresholds on system actions.

use crate::spa::SPA;
use crate::scv::ScvEngine;
use crate::time_crystal::LiquidLattice;
use std::sync::Arc;
use tokio::sync::Mutex;
use tracing::{info, warn, error};

#[cfg(feature = "extension-module")]
use pyo3::prelude::*;

#[cfg_attr(feature = "extension-module", pyclass(module = "me60os_core"))]
pub struct GuardianLsm {
    scv: ScvEngine,
    lattice: Arc<Mutex<LiquidLattice>>,
    // Threshold for critical actions (0.60 = 7,776,000)
    coherence_threshold: SPA,
}

impl GuardianLsm {
    pub fn new(lattice: Arc<Mutex<LiquidLattice>>) -> Self {
        Self {
            scv: ScvEngine::new(),
            lattice,
            coherence_threshold: SPA::from_raw(7_776_000), // 0.60 * SCALE_0
        }
    }

    /// Primary entry point for verifying a system-level action.
    /// Combines Semantic Integrity (SCV) with System Coherence (SPA).
    pub async fn verify_action(&self, actor: &str, action: &str, context: &str) -> bool {
        // 1. Check System Coherence
        let lattice = self.lattice.lock().await;
        let system_coherence = SPA::from_raw(lattice.buffer.coherence as i64);
        
        if system_coherence < self.coherence_threshold {
            warn!("🛡️ GUARDIAN: Acción bloqueada por BAJA COHERENCIA ({}) - Actor: {}", system_coherence, actor);
            return false;
        }

        // 2. Semantic Verification (TruthSync)
        let (is_valid, score, _entropy, _keywords) = self.scv.analyze(context);
        
        if !is_valid {
            error!("🛡️ GUARDIAN: Violación Semántica detectada - Acción: {} | Score: {}", action, score);
            return false;
        }

        info!("🛡️ GUARDIAN: Acción permitida - Actor: {} | Coherencia: {}", actor, system_coherence);
        true
    }

    /// Interface with eBPF Ring Buffer
    pub fn process_cortex_event(&self, event_type: u32, pid: u32) {
        // Here we would push feedback to eBPF maps if needed.
        // For now, it logs Ring 0 violations.
        match event_type {
            1 | 2 => warn!("🛡️ GUARDIAN: Bloqueo en Ring 0 detectado (PID: {}, Tipo: {})", pid, event_type),
            _ => (),
        }
    }
}
