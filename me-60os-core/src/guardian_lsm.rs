// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ GUARDIAN LSM: RING 0 EXECUTION CONTROL 🛡️
//!
//! User-space component of the eBPF LSM Guardian.
//! Enforces Base-60 coherence thresholds on system actions.
//!
//! ## References (eBPF / detección en Ring 0)
//! - [EXT-003] A flow-based IDS using Machine Learning in eBPF. arXiv:2102.09980.
//! - [EXT-007] eBPF-DDoS Mitigation for IoT. arXiv:2508.00851.
//! - [EXT-006] QUT-DV25: A Dataset for Dynamic Analysis of Next-Gen Software Supply Chain Attacks. arXiv:2505.13804.
//! - [P-RES] Novoa, J. (2026). *Aritmética Sexagesimal como Base de Sistemas.* `RESEARCH_es.md`.

use crate::scv::ScvEngine;
use crate::spa::SPA;
use crate::time_crystal::LiquidLattice;
use anyhow::{bail, Context, Result};
use std::sync::Arc;
use tokio::sync::Mutex;
use tracing::{error, info, warn};

#[cfg(feature = "extension-module")]
use pyo3::prelude::*;

const PID_ISOLATION_MAP_PATH: &str = "/sys/fs/bpf/sentinel/pid_isolation_map";
const PID_ISOLATION_TTL_NS: u64 = 300_000_000_000;
const COHERENCE_MILLI_SCALE: u64 = 1_000;

pub const EVENT_FILE_BLOCKED: u32 = 1;
pub const EVENT_EXEC_BLOCKED: u32 = 2;
pub const EVENT_FLOAT_CONTAMINATION: u32 = 10;

fn event_requires_pid_isolation(event_type: u32) -> bool {
    matches!(event_type, EVENT_FILE_BLOCKED | EVENT_EXEC_BLOCKED)
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ActionVerification {
    Allowed,
    RejectedByLowCoherence,
    RejectedBySemantics,
}

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
        matches!(
            self.verify_action_outcome(actor, action, context).await,
            ActionVerification::Allowed
        )
    }

    pub async fn verify_action_outcome(
        &self,
        actor: &str,
        action: &str,
        context: &str,
    ) -> ActionVerification {
        // 1. Check System Coherence
        let lattice = self.lattice.lock().await;
        let system_coherence = coherence_milli_to_spa(lattice.buffer.coherence);

        if system_coherence < self.coherence_threshold {
            warn!(
                "🛡️ GUARDIAN: Acción bloqueada por BAJA COHERENCIA ({}) - Actor: {}",
                system_coherence, actor
            );
            return ActionVerification::RejectedByLowCoherence;
        }

        // 2. Semantic Verification (TruthSync)
        let (is_valid, score, _entropy, _keywords) = self.scv.analyze(context);

        if !is_valid {
            error!(
                "🛡️ GUARDIAN: Violación Semántica detectada - Acción: {} | Score: {}",
                action, score
            );
            return ActionVerification::RejectedBySemantics;
        }

        info!(
            "🛡️ GUARDIAN: Acción permitida - Actor: {} | Coherencia: {}",
            actor, system_coherence
        );
        ActionVerification::Allowed
    }

    /// Procesa eventos del ring buffer y añade aislamiento temporal solo a bloqueos reales.
    pub async fn process_cortex_event(event_type: u32, pid: u32) -> Result<bool> {
        if event_requires_pid_isolation(event_type) {
            warn!(
                "🛡️ GUARDIAN: Bloqueo confirmado en Ring 0; se limita execve del PID por 300 s (PID: {}, Tipo: {})",
                pid, event_type
            );
            update_pid_isolation_map(pid).await?;
            return Ok(true);
        }

        if event_type == EVENT_FLOAT_CONTAMINATION {
            warn!(
                "🛡️ GUARDIAN: contaminación float registrada como telemetría; no se aísla (PID: {})",
                pid
            );
        }

        Ok(false)
    }

    /// Limita futuras llamadas execve del PID en el mapa del Guardian LSM por cinco minutos.
    pub async fn isolate_pid(&self, pid: u32, reason: &str) -> Result<()> {
        error!(
            "🛡️ GUARDIAN [AISLAMIENTO AUTÓNOMO]: limitando execve del PID {} por 300 s ({})",
            pid, reason
        );

        update_pid_isolation_map(pid).await?;
        let mut lattice = self.lattice.lock().await;
        lattice.buffer.coherence = 0;
        Ok(())
    }
}

fn coherence_milli_to_spa(coherence: u64) -> SPA {
    let normalized = i128::from(coherence.min(COHERENCE_MILLI_SCALE));
    let raw = normalized * i128::from(SPA::SCALE_0) / i128::from(COHERENCE_MILLI_SCALE);
    SPA::from_raw(i64::try_from(raw).expect("la coherencia normalizada cabe en SPA"))
}

fn pid_isolation_map_args(pid: u32, expires_at_ns: u64) -> Vec<String> {
    let mut args = vec![
        "map".to_string(),
        "update".to_string(),
        "pinned".to_string(),
        PID_ISOLATION_MAP_PATH.to_string(),
        "key".to_string(),
        "hex".to_string(),
    ];
    args.extend(pid.to_ne_bytes().map(|byte| format!("{byte:02x}")));
    args.extend(["value".to_string(), "hex".to_string()]);
    args.extend(
        expires_at_ns
            .to_ne_bytes()
            .map(|byte| format!("{byte:02x}")),
    );
    args
}

fn monotonic_now_ns() -> Result<u64> {
    let mut timestamp = std::mem::MaybeUninit::<libc::timespec>::zeroed();
    let result = unsafe { libc::clock_gettime(libc::CLOCK_MONOTONIC, timestamp.as_mut_ptr()) };
    if result != 0 {
        return Err(std::io::Error::last_os_error())
            .context("no se pudo leer CLOCK_MONOTONIC para aislar el PID");
    }

    let timestamp = unsafe { timestamp.assume_init() };
    let seconds =
        u64::try_from(timestamp.tv_sec).context("CLOCK_MONOTONIC devolvió segundos negativos")?;
    let nanoseconds = u64::try_from(timestamp.tv_nsec)
        .context("CLOCK_MONOTONIC devolvió nanosegundos negativos")?;
    seconds
        .checked_mul(1_000_000_000)
        .and_then(|base| base.checked_add(nanoseconds))
        .context("desbordamiento al convertir CLOCK_MONOTONIC a nanosegundos")
}

async fn update_pid_isolation_map(pid: u32) -> Result<()> {
    if pid == 0 {
        bail!("el PID 0 no se puede aislar");
    }

    let expires_at_ns = monotonic_now_ns()?
        .checked_add(PID_ISOLATION_TTL_NS)
        .context("desbordamiento al calcular la caducidad del aislamiento")?;
    let args = pid_isolation_map_args(pid, expires_at_ns);
    let output = tokio::process::Command::new("bpftool")
        .args(&args)
        .output()
        .await
        .context("no se pudo ejecutar bpftool para actualizar pid_isolation_map")?;

    if !output.status.success() {
        bail!(
            "bpftool rechazó el aislamiento del PID {}: {}",
            pid,
            String::from_utf8_lossy(&output.stderr).trim()
        );
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::{
        coherence_milli_to_spa, event_requires_pid_isolation, pid_isolation_map_args,
        EVENT_EXEC_BLOCKED, EVENT_FILE_BLOCKED, EVENT_FLOAT_CONTAMINATION,
    };
    use crate::spa::SPA;

    #[test]
    fn convierte_coherencia_x1000_a_spa_sin_float() {
        assert_eq!(coherence_milli_to_spa(600).to_raw(), SPA::SCALE_0 * 3 / 5);
        assert_eq!(coherence_milli_to_spa(u64::MAX).to_raw(), SPA::SCALE_0);
    }

    #[test]
    fn solo_los_eventos_1_y_2_aislan_el_pid() {
        assert!(event_requires_pid_isolation(EVENT_FILE_BLOCKED));
        assert!(event_requires_pid_isolation(EVENT_EXEC_BLOCKED));
        assert!(!event_requires_pid_isolation(EVENT_FLOAT_CONTAMINATION));
        assert!(!event_requires_pid_isolation(99));
    }

    #[test]
    fn argumentos_bpftool_serializan_pid_y_expiracion_byte_a_byte() {
        let args = pid_isolation_map_args(42, 0x0102_0304_0506_0708);
        assert_eq!(
            &args[..6],
            [
                "map",
                "update",
                "pinned",
                "/sys/fs/bpf/sentinel/pid_isolation_map",
                "key",
                "hex"
            ]
        );
        let pid_bytes = 42_u32.to_ne_bytes().map(|byte| format!("{byte:02x}"));
        let expiry_bytes = 0x0102_0304_0506_0708_u64
            .to_ne_bytes()
            .map(|byte| format!("{byte:02x}"));
        assert_eq!(&args[6..10], pid_bytes);
        assert_eq!(&args[10..12], ["value", "hex"]);
        assert_eq!(&args[12..20], expiry_bytes);
    }
}
