// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.

use crate::CrystalInput;
use futures_util::{SinkExt, StreamExt};
use me60os_core::spa::SPA;
use serde::Deserialize;
use std::sync::mpsc::{SyncSender, TrySendError};
use std::time::Duration;
use tokio::time::{sleep, timeout};
use tokio_tungstenite::tungstenite::Message;

const CONNECT_TIMEOUT: Duration = Duration::from_secs(10);
// mycnetd broadcasts mesh_tick every second even when no seeds arrive.
const READ_TIMEOUT: Duration = Duration::from_secs(30);
const RECONNECT_DELAY: Duration = Duration::from_secs(5);

#[derive(Debug, Deserialize)]
#[serde(tag = "type")]
enum MeshEvent {
    #[serde(rename = "fractal_seed_ingested")]
    Seed { token_id: u32, amplitude_s60: i64 },
    #[serde(other)]
    Other,
}

fn enqueue(text: &str, tx: &SyncSender<CrystalInput>) -> anyhow::Result<()> {
    let MeshEvent::Seed { token_id, amplitude_s60 } = serde_json::from_str(text)? else {
        return Ok(());
    };
    let index = (token_id % 64) as usize;
    match tx.try_send(CrystalInput::Security {
        index,
        amplitude: SPA::from_raw(amplitude_s60),
        mesh_token_id: Some(token_id),
    }) {
        Ok(()) => tracing::debug!(token_id, index, amplitude_raw = amplitude_s60, "MyCNet seed queued"),
        Err(TrySendError::Full(_)) => {
            tracing::warn!(token_id, "MyCNet seed rejected: CrystalRuntime channel full");
        }
        Err(TrySendError::Disconnected(_)) => {
            anyhow::bail!("CrystalRuntime input channel disconnected");
        }
    }
    Ok(())
}

async fn subscribe(url: &str, tx: &SyncSender<CrystalInput>) -> anyhow::Result<()> {
    let (mut ws, response) = timeout(CONNECT_TIMEOUT, tokio_tungstenite::connect_async(url)).await??;
    tracing::info!(status = response.status().as_u16(), "MyCNet mesh WebSocket connected");
    let mut first_text = true;
    loop {
        let Some(message) = timeout(READ_TIMEOUT, ws.next()).await? else {
            anyhow::bail!("MyCNet mesh stream ended");
        };
        match message? {
            Message::Text(text) => {
                if first_text {
                    tracing::info!("MyCNet mesh subscription receiving stream frames");
                    first_text = false;
                }
                if let Err(error) = enqueue(&text, tx) {
                    if matches!(error.downcast_ref::<serde_json::Error>(), Some(_)) {
                        tracing::warn!(%error, "MyCNet stream frame rejected: invalid JSON or seed fields");
                    } else {
                        return Err(error);
                    }
                }
            }
            Message::Ping(_) => ws.flush().await?,
            Message::Close(_) => anyhow::bail!("MyCNet mesh stream closed by peer"),
            _ => {}
        }
    }
}

pub(crate) async fn run(tx: SyncSender<CrystalInput>) {
    let url = std::env::var("MYCNET_STREAM_URL")
        .unwrap_or_else(|_| "ws://10.88.0.1:7474/api/v1/stream".to_string());
    loop {
        if let Err(error) = subscribe(&url, &tx).await {
            tracing::warn!(%error, "MyCNet mesh unavailable; reconnecting in 5s");
        }
        sleep(RECONNECT_DELAY).await;
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::mpsc::sync_channel;

    #[test]
    fn seed_reaches_security_channel_without_rescaling() {
        let (tx, rx) = sync_channel(1);
        enqueue(r#"{"type":"fractal_seed_ingested","token_id":129,"amplitude_s60":-17}"#, &tx).unwrap();
        let CrystalInput::Security { index, amplitude, mesh_token_id } = rx.try_recv().unwrap() else {
            panic!("seed must use the security lane");
        };
        assert_eq!(index, 1);
        assert_eq!(amplitude.to_raw(), -17);
        assert_eq!(mesh_token_id, Some(129));
    }

    #[test]
    fn seed_rejects_missing_boolean_float_and_out_of_range_fields() {
        let (tx, rx) = sync_channel(1);
        for token in ["true", "false", "-1", "4294967296", "1.0", "null", "\"1\""] {
            let text = format!(r#"{{"type":"fractal_seed_ingested","token_id":{token},"amplitude_s60":0}}"#);
            assert!(enqueue(&text, &tx).is_err(), "accepted token_id {token}");
        }
        for amplitude in ["true", "false", "1.0", "null", "\"0\"", "9223372036854775808"] {
            let text = format!(r#"{{"type":"fractal_seed_ingested","token_id":1,"amplitude_s60":{amplitude}}}"#);
            assert!(enqueue(&text, &tx).is_err(), "accepted amplitude {amplitude}");
        }
        assert!(enqueue(r#"{"type":"fractal_seed_ingested","token_id":1}"#, &tx).is_err());
        assert!(enqueue(r#"{"type":"fractal_seed_ingested","amplitude_s60":0}"#, &tx).is_err());
        assert!(rx.try_recv().is_err());
    }

    #[test]
    fn zero_is_valid_and_other_events_do_not_inject() {
        let (tx, rx) = sync_channel(1);
        enqueue(r#"{"type":"mesh_tick","tick":1}"#, &tx).unwrap();
        assert!(rx.try_recv().is_err());
        enqueue(r#"{"type":"fractal_seed_ingested","token_id":0,"amplitude_s60":0}"#, &tx).unwrap();
        let CrystalInput::Security { amplitude, .. } = rx.try_recv().unwrap() else {
            panic!("seed must use the security lane");
        };
        assert_eq!(amplitude.to_raw(), 0);
    }

    #[test]
    fn full_channel_does_not_claim_acceptance_and_disconnect_is_error() {
        let (tx, rx) = sync_channel(1);
        let text = r#"{"type":"fractal_seed_ingested","token_id":1,"amplitude_s60":17}"#;
        enqueue(text, &tx).unwrap();
        enqueue(text, &tx).unwrap();
        rx.try_recv().unwrap();
        assert!(rx.try_recv().is_err());
        drop(rx);
        assert!(enqueue(text, &tx).is_err());
    }

}
