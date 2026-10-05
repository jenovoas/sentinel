// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.

use axum::{
    extract::{Query, State},
    Json,
};
use chrono::{DateTime, Utc};
use serde::Deserialize;
use serde_json::{json, Value};
use std::{
    fs,
    path::Path,
    sync::Arc,
    time::SystemTime,
};

use crate::AppState;

#[derive(Debug, Deserialize)]
pub struct AnalyticsQuery {
    pub hours: Option<u64>,
    pub limit: Option<usize>,
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

static CPU_SNAPSHOT: std::sync::Mutex<Option<((u64, u64), SystemTime, Option<u64>)>> =
    std::sync::Mutex::new(None);

fn sample_cpu_utilization() -> Option<u64> {
    let now = SystemTime::now();
    let current_counters = cpu_counters()?;
    let mut guard = CPU_SNAPSHOT.lock().ok()?;

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

fn memory_utilization() -> Option<u64> {
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
    Some(total.saturating_sub(available).saturating_mul(100) / total)
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
            if !metadata.is_file() {
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
                "completed"
            } else {
                "stale"
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

pub async fn failsafe_status_handler() -> Json<Value> {
    Json(json!({
        "available": false,
        "status": "not_configured",
        "last_auto_remediation": "Not configured",
        "active_playbooks": 0,
        "success_rate_30d": 0,
        "total_executions": 0,
        "playbooks": [],
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
    let efficiency = state.metrics.get_scheduler_efficiency().to_base_units();

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
        "anomalies_count": 0,
        "anomalies_available": false,
    }))
}

pub async fn analytics_anomalies_handler(Query(query): Query<AnalyticsQuery>) -> Json<Value> {
    Json(json!({
        "window_hours": query.hours.unwrap_or(24).clamp(1, 168),
        "limit": query.limit.unwrap_or(10).min(100),
        "available": false,
        "anomalies": [],
    }))
}

pub async fn ai_health_handler() -> Json<Value> {
    Json(json!({
        "enabled": false,
        "available": false,
        "status": "not_configured",
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
    fn backup_status_has_frontend_contract_without_backup_directory() {
        let path = "/tmp/sentinel-dashboard-test-backups-does-not-exist";
        std::env::set_var("SENTINEL_BACKUP_DIR", path);
        let status = backup_status();
        assert_eq!(status["health"], "warning");
        assert_eq!(status["last_backup"]["status"], "not_available");
        std::env::remove_var("SENTINEL_BACKUP_DIR");
    }
}
