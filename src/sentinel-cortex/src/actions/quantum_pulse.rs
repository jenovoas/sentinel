use redis::AsyncCommands;
use serde::{Deserialize, Serialize};
use std::error::Error;
use std::sync::Arc;
use tokio::sync::Mutex;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct QuantumSignal {
    pub disonancia: f64,
    pub axiones_count: u32,
    pub source: String,
    pub timestamp: i64,
}

pub struct QuantumPulseEmitter {
    client: redis::Client,
    conn: Arc<Mutex<Option<redis::aio::Connection>>>,
    channel: String,
}

impl QuantumPulseEmitter {
    pub fn new(redis_url: &str) -> Result<Self, Box<dyn Error>> {
        let client = redis::Client::open(redis_url)?;
        Ok(Self {
            client,
            conn: Arc::new(Mutex::new(None)),
            channel: "sentinel:quantum:pulse".to_string(),
        })
    }

    /// Establish connection if not exists or broken
    async fn get_connection(&self) -> Result<redis::aio::Connection, Box<dyn Error>> {
        let _conn_guard = self.conn.lock().await;

        // Note: Cloning connections in redis-rs is not straightforward for async connections 
        // in a simple way without a pool, but here we restart if needed.
        // For simplicity in this implementation, we just open a new one if we don't store it,
        // or we can use a proper pool later. Here we essentially create a fresh one for the action
        // or try to reuse if we implement a MultiplexedConnection logic.
        // To keep it robust and simple for this "pulse":
        
        let conn = self.client.get_async_connection().await?;
        Ok(conn)
    }

    /// Emite una señal "cruda" al bus de eventos (Redis Pub/Sub)
    /// Este es el "zumbido constante" que escucha la Neurona Maestra
    pub async fn emit_signal(&self, disonancia: f64, axiones: u32) -> Result<(), Box<dyn Error>> {
        let signal = QuantumSignal {
            disonancia,
            axiones_count: axiones,
            source: "cortex_internal".to_string(),
            timestamp: chrono::Utc::now().timestamp_millis(),
        };

        let payload = serde_json::to_string(&signal)?;
        let mut conn = self.get_connection().await?;

        // Publish to the synchronization channel
        conn.publish::<_, _, ()>(&self.channel, payload).await?;

        // Sutil log para debug (demasiado ruido si es constante, usar trace)
        tracing::trace!("🌌 Quantum Pulse Emitted: d={:.4} a={}", disonancia, axiones);

        Ok(())
    }

}
