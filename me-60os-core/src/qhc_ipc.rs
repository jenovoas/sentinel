// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.

use serde::{Deserialize, Serialize};
use std::{path::PathBuf, time::{SystemTime, UNIX_EPOCH}};

pub const DEFAULT_QHC_SOCKET_PATH: &str = "/run/soma/qhc.sock";

#[derive(Clone, Debug, Deserialize, PartialEq, Eq, Serialize)]
pub struct QhcSnapshot {
    pub tick: u64,
    pub phase: String,
    pub modulation: u8,
    pub correction_ns: u64,
    pub updated_unix_ms: u64,
}

impl QhcSnapshot {
    pub fn from_tick(tick: u64, modulation: u8, correction_ns: u64) -> Self {
        Self {
            tick,
            phase: phase_name(tick).to_string(),
            modulation,
            correction_ns,
            updated_unix_ms: now_unix_ms(),
        }
    }
}

pub fn phase_name(tick: u64) -> &'static str {
    match tick % 4 {
        0 => "YOD",
        1 => "HE",
        2 => "VAV",
        _ => "HE",
    }
}

pub fn socket_path() -> PathBuf {
    std::env::var_os("QHC_SOCKET_PATH")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from(DEFAULT_QHC_SOCKET_PATH))
}

fn now_unix_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0, |duration| duration.as_millis().min(u128::from(u64::MAX)) as u64)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn phase_cycle_matches_qhc_pattern() {
        assert_eq!(phase_name(0), "YOD");
        assert_eq!(phase_name(1), "HE");
        assert_eq!(phase_name(2), "VAV");
        assert_eq!(phase_name(3), "HE");
        assert_eq!(phase_name(4), "YOD");
    }

    #[test]
    fn snapshot_contains_tick_and_modulation() {
        let snapshot = QhcSnapshot::from_tick(68, 10, 700_000);
        assert_eq!(snapshot.tick, 68);
        assert_eq!(snapshot.phase, "YOD");
        assert_eq!(snapshot.modulation, 10);
        assert_eq!(snapshot.correction_ns, 700_000);
    }
}
