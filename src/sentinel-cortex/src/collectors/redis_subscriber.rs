use redis::AsyncCommands;
use tokio::sync::mpsc;
use serde::{Deserialize, Serialize};
use std::error::Error;
use tracing::{error, debug};
use futures::StreamExt; // Usamos el crate 'futures' recién añadido

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct QuantumEvent {
    pub source: String,
    pub disonancia: f64,
    pub axiones: f64,
    pub frequency: f64,
    pub raw_event: String,
    pub timestamp: f64,
}

pub struct RedisSubscriber {
    redis_url: String,
    channel: String,
}

impl RedisSubscriber {
    pub fn new(redis_url: &str, channel: &str) -> Self {
        Self {
            redis_url: redis_url.to_string(),
            channel: channel.to_string(),
        }
    }

    pub async fn start(self, tx: mpsc::Sender<QuantumEvent>) -> Result<(), Box<dyn Error>> {
        let client = redis::Client::open(self.redis_url)?;
        let mut conn = client.get_async_connection().await?;
        let mut pubsub = conn.into_pubsub();
        
        pubsub.subscribe(&self.channel).await?;
        tracing::info!("📡 Suscrito al canal de señales cuánticas: {}", self.channel);

        let mut stream = pubsub.on_message();

        while let Some(msg) = stream.next().await {
            match msg.get_payload::<String>() {
                Ok(payload) => {
                    match serde_json::from_str::<QuantumEvent>(&payload) {
                        Ok(event) => {
                            debug!("📥 Señal recibida del bus: {} (D={:.2})", event.source, event.disonancia);
                            let _ = tx.try_send(event);
                        }
                        Err(e) => error!("❌ Error decodificando señal cuántica: {}", e),
                    }
                }
                Err(e) => error!("❌ Error obteniendo payload de Redis: {}", e),
            }
        }

        Ok(())
    }
}
