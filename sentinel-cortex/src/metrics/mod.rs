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
}
