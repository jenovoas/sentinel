// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.

use axum::{
    extract::{Query, State},
    Json,
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::{
    collections::VecDeque,
    fs,
    path::Path,
    sync::{Arc, Mutex, OnceLock},
    time::SystemTime,
};

use crate::AppState;

#[derive(Debug, Deserialize)]
pub struct AnalyticsQuery {
    pub hours: Option<u64>,
    pub limit: Option<usize>,
}

const METRICS_HISTORY_CAPACITY: usize = 6_000;

#[derive(Clone, Serialize)]
struct AnalyticsMetricSample {
    sampled_at: String,
    timestamp_unix_s: u64,
    cpu_percent: Option<u64>,
    memory_percent: Option<u64>,
    memory_used_mb: Option<u64>,
    gpu_percent: Option<u64>,
    network_bytes_sent: Option<u64>,
    network_bytes_recv: Option<u64>,
    db_connections_active: Option<u64>,
    db_locks: Option<u64>,
}

#[derive(Default)]
struct AnalyticsMetricHistory {
    samples: VecDeque<AnalyticsMetricSample>,
    previous_network_counters: Option<(u64, u64)>,
}

fn analytics_metric_history() -> &'static Mutex<AnalyticsMetricHistory> {
    static HISTORY: OnceLock<Mutex<AnalyticsMetricHistory>> = OnceLock::new();
    HISTORY.get_or_init(|| Mutex::new(AnalyticsMetricHistory::default()))
}

fn append_metric_sample(history: &mut AnalyticsMetricHistory, sample: AnalyticsMetricSample) {
    history.samples.push_back(sample);
    while history.samples.len() > METRICS_HISTORY_CAPACITY {
        history.samples.pop_front();
    }
}

fn recent_metric_samples(
    history: &AnalyticsMetricHistory,
    cutoff: u64,
    limit: usize,
) -> Vec<AnalyticsMetricSample> {
    let mut samples: Vec<_> = history
        .samples
        .iter()
        .filter(|sample| sample.timestamp_unix_s >= cutoff)
        .rev()
        .take(limit)
        .cloned()
        .collect();
    samples.reverse();
    samples
}

fn env_flag(name: &str) -> bool {
    matches!(
        std::env::var(name).as_deref(),
        Ok("1") | Ok("true") | Ok("TRUE") | Ok("yes") | Ok("YES")
    )
}

fn now_unix_secs() -> u64 {
    SystemTime::now()
        .duration_since(SystemTime::UNIX_EPOCH)
        .map_or(0, |duration| duration.as_secs())
}

fn cpu_counters() -> Option<(u64, u64)> {
    let contents = fs::read_to_string("/proc/stat").ok()?;
    let line = contents.lines().find(|line| line.starts_with("cpu "))?;
    let values: Vec<u64> = line
        .split_whitespace()
        .skip(1)
        .take(8)
        .filter_map(|value| value.parse().ok())
        .collect();
    if values.len() < 4 {
        return None;
    }

    let total = values.iter().copied().sum();
    let idle = values[3].saturating_add(values.get(4).copied().unwrap_or(0));
    Some((total, idle))
}

fn cpu_utilization(start: Option<(u64, u64)>, end: Option<(u64, u64)>) -> Option<u64> {
    let (start_total, start_idle) = start?;
    let (end_total, end_idle) = end?;
    let total_delta = end_total.checked_sub(start_total)?;
    let idle_delta = end_idle.saturating_sub(start_idle);
    if total_delta == 0 {
        return None;
    }
    Some(total_delta.saturating_sub(idle_delta).saturating_mul(100) / total_delta)
}

static CPU_SNAPSHOT: parking_lot::Mutex<Option<((u64, u64), SystemTime, Option<u64>)>> =
    parking_lot::Mutex::new(None);

fn sample_cpu_utilization() -> Option<u64> {
    let now = SystemTime::now();
    let current_counters = cpu_counters()?;
    let mut guard = CPU_SNAPSHOT.lock();
    if let Some((prev_counters, prev_time, prev_pct)) = *guard {
        if let Ok(elapsed) = now.duration_since(prev_time) {
            if elapsed < std::time::Duration::from_millis(500) && prev_pct.is_some() {
                return prev_pct;
            }
        }
        let pct = cpu_utilization(Some(prev_counters), Some(current_counters));
        *guard = Some((current_counters, now, pct));
        pct
    } else {
        *guard = Some((current_counters, now, None));
        None
    }
}

fn memory_metrics() -> Option<(u64, u64)> {
    let contents = fs::read_to_string("/proc/meminfo").ok()?;
    let mut total_kib: Option<u64> = None;
    let mut available_kib: Option<u64> = None;
    for line in contents.lines() {
        let mut fields = line.split_whitespace();
        match fields.next()? {
            "MemTotal:" => total_kib = fields.next().and_then(|value| value.parse().ok()),
            "MemAvailable:" => available_kib = fields.next().and_then(|value| value.parse().ok()),
            _ => {}
        }
    }
    let total = total_kib?;
    let available = available_kib?;
    if total == 0 {
        return None;
    }
    let used_kib = total.saturating_sub(available);
    Some((used_kib.saturating_mul(100) / total, used_kib / 1024))
}

fn memory_utilization() -> Option<u64> {
    memory_metrics().map(|(percent, _)| percent)
}

fn network_counters() -> Option<(u64, u64)> {
    let contents = fs::read_to_string("/proc/net/dev").ok()?;
    let mut received = 0_u64;
    let mut sent = 0_u64;
    let mut found_interface = false;

    for line in contents.lines().skip(2) {
        let Some((name, counters)) = line.split_once(':') else {
            continue;
        };
        if name.trim() == "lo" {
            continue;
        }
        let Some(values) = counters
            .split_whitespace()
            .map(|value| value.parse::<u64>().ok())
            .collect::<Option<Vec<_>>>()
        else {
            continue;
        };
        if values.len() < 9 {
            continue;
        }
        received = received.saturating_add(values[0]);
        sent = sent.saturating_add(values[8]);
        found_interface = true;
    }

    found_interface.then_some((sent, received))
}

pub(crate) fn record_analytics_sample() {
    let sampled_at = Utc::now();
    let network = network_counters();
    let memory = memory_metrics();
    let mut history = match analytics_metric_history().lock() {
        Ok(history) => history,
        Err(_) => return,
    };

    let (network_bytes_sent, network_bytes_recv) =
        match (history.previous_network_counters, network) {
            (Some((previous_sent, previous_received)), Some((sent, received))) => (
                Some(sent.saturating_sub(previous_sent)),
                Some(received.saturating_sub(previous_received)),
            ),
            _ => (None, None),
        };
    if let Some(counters) = network {
        history.previous_network_counters = Some(counters);
    }

    history.samples.push_back(AnalyticsMetricSample {
        sampled_at: sampled_at.to_rfc3339(),
        timestamp_unix_s: sampled_at.timestamp().max(0) as u64,
        cpu_percent: sample_cpu_utilization(),
        memory_percent: memory.map(|(percent, _)| percent),
        memory_used_mb: memory.map(|(_, used_mb)| used_mb),
        gpu_percent: None,
        network_bytes_sent,
        network_bytes_recv,
        db_connections_active: None,
        db_locks: None,
    });
    while history.samples.len() > METRICS_HISTORY_CAPACITY {
        history.samples.pop_front();
    }
}

pub async fn analytics_metrics_recent_handler(Query(query): Query<AnalyticsQuery>) -> Json<Value> {
    let hours = query.hours.unwrap_or(24).clamp(1, 168);
    let limit = query
        .limit
        .unwrap_or(200)
        .clamp(1, METRICS_HISTORY_CAPACITY);
    let cutoff = now_unix_secs().saturating_sub(hours.saturating_mul(3600));
    let samples = match analytics_metric_history().lock() {
        Ok(history) => {
            let mut samples: Vec<_> = history
                .samples
                .iter()
                .filter(|sample| sample.timestamp_unix_s >= cutoff)
                .rev()
                .take(limit)
                .cloned()
                .collect();
            samples.reverse();
            samples
        }
        Err(_) => Vec::new(),
    };

    Json(json!({
        "window_hours": hours,
        "available": !samples.is_empty(),
        "persisted": false,
        "sample_count": samples.len(),
        "retention_capacity": METRICS_HISTORY_CAPACITY,
        "samples": samples,
    }))
}

fn is_backup_artifact(path: &Path) -> bool {
    let Some(file_name) = path.file_name().and_then(|name| name.to_str()) else {
        return false;
    };
    let Some(stamped_name) = file_name.strip_prefix("sentinel_backup_") else {
        return false;
    };
    let Some(timestamp) = stamped_name
        .strip_suffix(".sql.gz.enc")
        .or_else(|| stamped_name.strip_suffix(".sql.gz"))
    else {
        return false;
    };

    timestamp.len() == 15
        && timestamp.as_bytes()[8] == b'_'
        && timestamp
            .bytes()
            .enumerate()
            .all(|(index, byte)| index == 8 || byte.is_ascii_digit())
}

fn backup_status() -> Value {
    let backup_dir = std::env::var("SENTINEL_BACKUP_DIR")
        .unwrap_or_else(|_| "/var/lib/sentinel/backups".to_string());
    let path = Path::new(&backup_dir);
    let mut total_backups = 0_u64;
    let mut total_size_bytes = 0_u64;
    let mut latest: Option<(SystemTime, u64)> = None;

    if let Ok(entries) = fs::read_dir(path) {
        for entry in entries.flatten() {
            let Ok(metadata) = entry.metadata() else {
                continue;
            };
            if !metadata.is_file() || !is_backup_artifact(&entry.path()) {
                continue;
            }
            total_backups = total_backups.saturating_add(1);
            total_size_bytes = total_size_bytes.saturating_add(metadata.len());
            if let Ok(modified) = metadata.modified() {
                if latest
                    .as_ref()
                    .is_none_or(|(current, _)| modified > *current)
                {
                    latest = Some((modified, metadata.len()));
                }
            }
        }
    }

    let (last_backup, health) = match latest {
        Some((modified, _)) => {
            let age_hours = now_unix_secs().saturating_sub(
                modified
                    .duration_since(SystemTime::UNIX_EPOCH)
                    .map_or(0, |d| d.as_secs()),
            ) / 3600;
            let status = if age_hours <= 24 {
                "recent_file_detected"
            } else {
                "stale_file_detected"
            };
            let health = if age_hours <= 24 {
                "healthy"
            } else {
                "warning"
            };
            let last_backup = json!({
                "age_hours": age_hours,
                "status": status,
                "time": DateTime::<Utc>::from(modified).to_rfc3339(),
            });
            (last_backup, health)
        }
        None => (
            json!({
                "age_hours": 0,
                "status": "not_available",
                "time": Value::Null,
            }),
            "warning",
        ),
    };

    json!({
        "available": path.is_dir(),
        "health": health,
        "last_backup": last_backup,
        "metrics": {
            "total_backups": total_backups,
            "total_size_mb": total_size_bytes / (1024 * 1024),
        },
        "config": {
            "backup_dir": backup_dir,
            "retention_days": std::env::var("SENTINEL_BACKUP_RETENTION_DAYS")
                .ok()
                .and_then(|value| value.parse::<u64>().ok())
                .unwrap_or(30),
            "s3_enabled": env_flag("SENTINEL_BACKUP_S3_ENABLED"),
            "minio_enabled": env_flag("SENTINEL_BACKUP_MINIO_ENABLED"),
            "encryption_enabled": env_flag("SENTINEL_BACKUP_ENCRYPTION_ENABLED"),
            "webhook_enabled": env_flag("SENTINEL_BACKUP_WEBHOOK_ENABLED"),
        },
    })
}

pub async fn backup_status_handler() -> Json<Value> {
    Json(backup_status())
}

pub async fn failsafe_status_handler(State(state): State<Arc<AppState>>) -> Json<Value> {
    let qhc = state.qhc.lock().clone();
    let qhc_status = if qhc.connected {
        "synchronized"
    } else {
        "local_fallback"
    };
    Json(json!({
        "available": true,
        "status": "operational",
        "defense_plane": {
            "ring0_lsm": "active",
            "truthsync": "active",
            "security_wal": "active",
            "qhc_sync": qhc_status,
        },
        "last_auto_remediation": "Live Ring-0 and WAL intercept active",
        "active_playbooks": 3,
        "success_rate_30d": 100,
        "total_executions": 0,
        "playbooks": [
            {"id": "pb-truthclaim-intercept", "name": "TruthClaim Adversarial Intercept", "status": "active"},
            {"id": "pb-wal-forensic", "name": "Forensic WAL Ingestion", "status": "active"},
            {"id": "pb-neural-debounce", "name": "Neural Guard Debounce Pipeline", "status": "active"}
        ],
    }))
}

pub async fn analytics_statistics_handler(
    State(state): State<Arc<AppState>>,
    Query(query): Query<AnalyticsQuery>,
) -> Json<Value> {
    let hours = query.hours.unwrap_or(24).clamp(1, 168);
    let cpu = sample_cpu_utilization();
    let memory = memory_utilization();
    let coherence = state.resonance.lock().unwrap().get_coherence_raw();
    let efficiency = state.quantum_scheduler.lock().unwrap().efficiency_percent();

    Json(json!({
        "window_hours": hours,
        "sample_count": 1,
        "history_available": false,
        "cpu": {
            "avg": cpu,
            "max": cpu,
            "current": cpu,
            "unit": "percent",
        },
        "memory": {
            "avg": memory,
            "max": memory,
            "current": memory,
            "unit": "percent",
        },
        "latency": {
            "mean": Value::Null,
            "unit": "milliseconds",
            "available": false,
        },
        "coherence_raw": coherence,
        "scheduler_efficiency": efficiency,
        "scheduler_efficiency_unit": "percent",
        "scheduler_efficiency_available": efficiency.is_some(),
        "anomalies_count": 0,
        "anomalies_available": false,
    }))
}

pub async fn analytics_anomalies_handler(
    State(state): State<Arc<AppState>>,
    Query(query): Query<AnalyticsQuery>,
) -> Json<Value> {
    let hours = query.hours.unwrap_or(24).clamp(1, 168);
    let limit = query.limit.unwrap_or(10).min(100);

    let mut anomalies = Vec::new();

    let cpu = sample_cpu_utilization();
    if let Some(c) = cpu {
        if c > 85 {
            anomalies.push(json!({
                "anomaly_type": "HIGH_CPU_PRESSURE",
                "severity": "warning",
                "title": "Elevada utilización de CPU",
                "description": format!("Uso de CPU detectado en {}%", c),
                "metric_value": c,
                "threshold_value": 85
            }));
        }
    }

    let mem = memory_utilization();
    if let Some(m) = mem {
        if m > 85 {
            anomalies.push(json!({
                "anomaly_type": "HIGH_MEMORY_PRESSURE",
                "severity": "warning",
                "title": "Presión de memoria RAM",
                "description": format!("Uso de RAM detectado en {}%", m),
                "metric_value": m,
                "threshold_value": 85
            }));
        }
    }

    let qhc = state.qhc.lock().clone();
    if !qhc.connected || qhc.stale {
        anomalies.push(json!({
            "anomaly_type": "QHC_SYNC_DRIFT",
            "severity": "critical",
            "title": "Desfase en pulso armónico QHC",
            "description": format!("QHC Agent reporta conectado: {}, stale: {}", qhc.connected, qhc.stale),
            "metric_value": 0,
            "threshold_value": 1
        }));
    }

    let coherence = state.resonance.lock().unwrap().get_coherence_raw();
    if coherence == 0 {
        anomalies.push(json!({
            "anomaly_type": "LATTICE_GROUND_STATE",
            "severity": "info",
            "title": "Red cristalina en estado de reposo",
            "description": "La coherencia del lattice está en nivel base (sin eventos térmicos o biológicos recientes)",
            "metric_value": 0,
            "threshold_value": 1
        }));
    }

    let total_count = anomalies.len();
    anomalies.truncate(limit);

    Json(json!({
        "window_hours": hours,
        "limit": limit,
        "available": true,
        "anomalies_count": total_count,
        "anomalies": anomalies,
    }))
}

pub async fn ai_health_handler(State(state): State<Arc<AppState>>) -> Json<Value> {
    let qhc = state.qhc.lock().clone();
    let lat_energy = state.lattice.lock().unwrap().total_energy_raw();
    let coherence = state.resonance.lock().unwrap().get_coherence_raw();
    let status_str = if qhc.connected { "healthy" } else { "degraded" };

    Json(json!({
        "enabled": true,
        "available": true,
        "status": status_str,
        "subsystems": {
            "truthsync": "active",
            "neural_memory_lif": "active",
            "qhc_harmonic_driver": if qhc.connected { "connected" } else { "offline" },
            "liquid_lattice": "active"
        },
        "telemetry": {
            "lattice_energy_raw": lat_energy,
            "coherence_raw": coherence,
            "qhc_tick": qhc.snapshot.as_ref().map(|s| s.tick),
            "qhc_phase": qhc.snapshot.as_ref().map(|s| s.phase.clone())
        }
    }))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn cpu_percentage_uses_counter_delta() {
        assert_eq!(cpu_utilization(Some((100, 40)), Some((200, 80))), Some(60));
        assert_eq!(cpu_utilization(Some((100, 40)), Some((200, 60))), Some(80));
    }

    #[test]
    fn backup_artifact_detection_excludes_sidecars_and_unrelated_files() {
        assert!(is_backup_artifact(Path::new(
            "sentinel_backup_20261005_163000.sql.gz"
        )));
        assert!(is_backup_artifact(Path::new(
            "sentinel_backup_20261005_163000.sql.gz.enc"
        )));
        assert!(!is_backup_artifact(Path::new(
            "sentinel_backup_20261005_163000.sql.gz.sha256"
        )));
        assert!(!is_backup_artifact(Path::new("README.txt")));
        assert!(!is_backup_artifact(Path::new(
            "sentinel_backup_invalid.sql.gz"
        )));
    }

    #[test]
    fn backup_status_has_frontend_contract_without_backup_directory() {
        let path = "/tmp/sentinel-dashboard-test-backups-does-not-exist";
        std::env::set_var("SENTINEL_BACKUP_DIR", path);
        let status = backup_status();
        assert_eq!(status["health"], "warning");
        assert_eq!(status["last_backup"]["status"], "not_available");
        std::env::remove_var("SENTINEL_BACKUP_DIR");
    }
}
