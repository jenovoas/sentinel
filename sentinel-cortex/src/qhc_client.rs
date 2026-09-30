// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.

use axum::{extract::State, Json};
use me60os_core::qhc_ipc::{socket_path, QhcSnapshot};
use parking_lot::Mutex;
use serde::Serialize;
use std::{sync::Arc, time::{Duration, SystemTime, UNIX_EPOCH}};
use tokio::{io::{AsyncReadExt, AsyncWriteExt}, net::UnixStream, time::{sleep, timeout}};

const QHC_REQUEST_TIMEOUT: Duration = Duration::from_millis(500);
const QHC_STALE_AFTER_MS: u64 = 3_000;

#[derive(Clone, Debug, Serialize)]
pub struct QhcStatus {
    pub connected: bool,
    pub stale: bool,
    pub socket_path: String,
    pub last_error: Option<String>,
    pub snapshot: Option<QhcSnapshot>,
}

impl QhcStatus {
    pub fn unavailable() -> Self {
        Self {
            connected: false,
            stale: true,
            socket_path: socket_path().display().to_string(),
            last_error: Some("qhc_agent_unavailable".to_string()),
            snapshot: None,
        }
    }
}

pub fn spawn(state: Arc<Mutex<QhcStatus>>) {
    tokio::spawn(async move {
        let path = socket_path();
        loop {
            match fetch_snapshot(&path).await {
                Ok(snapshot) => {
                    let stale = snapshot_age_ms(snapshot.updated_unix_ms) > QHC_STALE_AFTER_MS;
                    let mut current = state.lock();
                    current.connected = !stale;
                    current.stale = stale;
                    current.socket_path = path.display().to_string();
                    current.last_error = stale.then_some("qhc_snapshot_stale".to_string());
                    current.snapshot = Some(snapshot);
                }
                Err(error) => {
                    let mut current = state.lock();
                    current.connected = false;
                    current.stale = true;
                    current.socket_path = path.display().to_string();
                    current.last_error = Some(error);
                }
            }
            sleep(Duration::from_secs(1)).await;
        }
    });
}

pub fn live_tick(status: &QhcStatus) -> Option<u64> {
    status
        .connected
        .then(|| status.snapshot.as_ref().map(|snapshot| snapshot.tick))
        .flatten()
}

pub async fn status_handler(State(state): State<Arc<crate::AppState>>) -> Json<QhcStatus> {
    Json(state.qhc.lock().clone())
}

async fn fetch_snapshot(path: &std::path::Path) -> Result<QhcSnapshot, String> {
    let mut stream = timeout(QHC_REQUEST_TIMEOUT, UnixStream::connect(path))
        .await
        .map_err(|_| "qhc_connect_timeout".to_string())?
        .map_err(|error| format!("qhc_connect_failed:{error}"))?;
    timeout(QHC_REQUEST_TIMEOUT, stream.write_all(b"SNAPSHOT\n"))
        .await
        .map_err(|_| "qhc_write_timeout".to_string())?
        .map_err(|error| format!("qhc_write_failed:{error}"))?;
    let mut response = Vec::new();
    timeout(QHC_REQUEST_TIMEOUT, stream.read_to_end(&mut response))
        .await
        .map_err(|_| "qhc_read_timeout".to_string())?
        .map_err(|error| format!("qhc_read_failed:{error}"))?;
    serde_json::from_slice::<QhcSnapshot>(&response)
        .map_err(|error| format!("qhc_invalid_snapshot:{error}"))
}

fn snapshot_age_ms(updated_unix_ms: u64) -> u64 {
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0, |duration| duration.as_millis().min(u128::from(u64::MAX)) as u64);
    now.saturating_sub(updated_unix_ms)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn unavailable_status_is_stale_and_not_connected() {
        let status = QhcStatus::unavailable();
        assert!(!status.connected);
        assert!(status.stale);
        assert!(status.snapshot.is_none());
    }

    #[test]
    fn live_tick_requires_connected_snapshot() {
        let mut status = QhcStatus::unavailable();
        assert_eq!(live_tick(&status), None);
        status.connected = true;
        status.stale = false;
        status.snapshot = Some(QhcSnapshot::from_tick(17, 5, 700_000));
        assert_eq!(live_tick(&status), Some(17));
    }
}
