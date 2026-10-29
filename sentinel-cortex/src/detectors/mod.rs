// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # Detectores de anomalías y resonancias en Sentinel Cortex

pub mod periodic;

#[allow(unused_imports)]
pub use periodic::{PeriodicAlert, PeriodicDetector};
