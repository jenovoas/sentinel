// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/security/mutual_surveillance.rs
//! # 🛡️ Mutual Surveillance Mechanism for Dual-Guardian Architecture (Claim 3 - Patent Pending)
//!
//! Implementa la "Resiliencia Cognitiva Soberana" donde:
//! - Guardian-Beta (Cortex en User-Space) vigila la actividad del Ring Buffer y la salud de Guardian-Alpha (eBPF en Kernel-Space).
//! - Si Alpha pierde eventos o se detecta anomalía, Beta reconfigura o escala a Guardian Gamma (Human-in-the-loop).
//! - Si Beta se corrompe o cuelga, Alpha ejecuta aislamiento autónomo en Ring-0.

use parking_lot::Mutex;
use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum GuardianHealth {
    Healthy,
    Degraded,
    Compromised,
    Dead,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GuardianStatusReport {
    pub guardian_name: String,
    pub health: GuardianHealth,
    pub timestamp_sec: u64,
    pub events_processed: u64,
    pub errors_detected: u64,
    pub heartbeat_drift_ms: u64,
    pub recommended_action: String,
}

pub struct MutualSurveillance {
    alpha_last_heartbeat_sec: Mutex<u64>,
    alpha_events_count: Mutex<u64>,
    beta_events_count: Mutex<u64>,
    max_heartbeat_timeout_sec: u64,
}

impl Default for MutualSurveillance {
    fn default() -> Self {
        Self::new(30)
    }
}

impl MutualSurveillance {
    pub fn new(max_heartbeat_timeout_sec: u64) -> Self {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();

        Self {
            alpha_last_heartbeat_sec: Mutex::new(now),
            alpha_events_count: Mutex::new(0),
            beta_events_count: Mutex::new(0),
            max_heartbeat_timeout_sec,
        }
    }

    /// Registra un latido (heartbeat) proveniente de Guardian Alpha (eBPF / driver)
    pub fn record_alpha_heartbeat(&self, events_count: u64) {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();

        *self.alpha_last_heartbeat_sec.lock() = now;
        *self.alpha_events_count.lock() = events_count;
    }

    /// Registra el procesamiento de un evento en Guardian Beta (Cortex)
    pub fn record_beta_processing(&self) {
        let mut count = self.beta_events_count.lock();
        *count = count.saturating_add(1);
    }

    /// Audita la salud de Guardian Alpha desde Guardian Beta
    pub fn audit_alpha_health(&self) -> GuardianStatusReport {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();

        let last_hb = *self.alpha_last_heartbeat_sec.lock();
        let events = *self.alpha_events_count.lock();
        let elapsed = now.saturating_sub(last_hb);

        let (health, action) = if elapsed <= 5 {
            (GuardianHealth::Healthy, "NORMAL_OPERATION".to_string())
        } else if elapsed <= self.max_heartbeat_timeout_sec {
            (GuardianHealth::Degraded, "WARN_WATCHDOG_POLL".to_string())
        } else if elapsed <= self.max_heartbeat_timeout_sec * 2 {
            (GuardianHealth::Compromised, "RELOAD_EBPF_PROG".to_string())
        } else {
            (
                GuardianHealth::Dead,
                "EMERGENCY_FAILSAFE_LOCKDOWN".to_string(),
            )
        };

        GuardianStatusReport {
            guardian_name: "Guardian-Alpha-eBPF".to_string(),
            health,
            timestamp_sec: now,
            events_processed: events,
            errors_detected: 0,
            heartbeat_drift_ms: elapsed * 1000,
            recommended_action: action,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_mutual_surveillance_healthy() {
        let surveillance = MutualSurveillance::new(10);
        surveillance.record_alpha_heartbeat(42);
        let report = surveillance.audit_alpha_health();
        assert_eq!(report.health, GuardianHealth::Healthy);
        assert_eq!(report.events_processed, 42);
    }
}
