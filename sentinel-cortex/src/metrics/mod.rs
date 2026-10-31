// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ METRICS REPOSITORY (DIP) - SENTINEL CORTEX 🛡️
//!
//! Centralized metric management adhering to YATRA Protocol (S60 Precision).
//! This module decouples metric collection from the underlying exporter (Prometheus).

use serde::Serialize;

#[derive(Serialize)]
pub struct MetricsSnapshot {
    pub coherence: i64,
    pub efficiency: i64,
    pub efficiency_available: bool,
    pub timestamp_s60: i64,
    // Successful task executions, classified by the actual dispatch path.
    // The percentage is a portal share, not a measurement of energy savings.
    pub tasks_in_portal: u64,
    pub tasks_forced: u64,
    pub tasks_critical: u64,
    pub tasks_failed: u64,
    pub scheduler_queue_len: usize,
    pub scheduler_emergency_shutdown: bool,
    pub dual_lane_portal_open: bool,
    pub dtc_ticks: u64,
    pub bio_coherence_raw: i64,
    pub bio_portal_open: bool,
}
