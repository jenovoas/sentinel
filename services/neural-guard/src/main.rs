mod collectors;
mod engine;
mod models;
mod patterns;

use crate::engine::DecisionEngine;
use collectors::{LokiCollector, PrometheusCollector, RedisStreamCollector};
use std::time::Duration;

#[tokio::main]
async fn main() {
    // 1. Inicializar logging y variables de entorno
    tracing_subscriber::fmt::init();
    dotenvy::dotenv().ok();

    let prometheus_url =
        std::env::var("PROMETHEUS_URL").expect("PROMETHEUS_URL variable de entorno no encontrada");
    let n8n_url = std::env::var("N8N_URL").expect("N8N_URL variable de entorno no encontrada");
    let loki_url = std::env::var("LOKI_URL").expect("LOKI_URL variable de entorno no encontrada");
    let redis_url = std::env::var("REDIS_URL").expect("REDIS_URL variable de entorno no encontrada");

    // 2. Inicializar componentes
    let prom_collector = PrometheusCollector::new(prometheus_url);
    let loki_collector = LokiCollector::new(loki_url);
    let mut redis_collector = RedisStreamCollector::new(&redis_url).expect("Failed to connect to Redis");
    let mut engine = DecisionEngine::new();
    let n8n_client = reqwest::Client::new();

    tracing::info!("🧠 Neural Guard Cortex iniciado. Esperando señales...");

    // 3. Bucle principal de orquestación
    let mut interval = tokio::time::interval(Duration::from_secs(10)); // Shorter interval for stream reading
    loop {
        interval.tick().await;
        tracing::info!("Recolectando eventos...");

        let mut all_events = Vec::new();

        // Collect from all sources
        if let Ok(events) = prom_collector.collect().await { all_events.extend(events); }
        if let Ok(events) = prom_collector.collect_redis_metrics().await { all_events.extend(events); }
        if let Ok(events) = prom_collector.collect_thermal_metrics().await { all_events.extend(events); }
        if let Ok(events) = loki_collector.collect_logs().await { all_events.extend(events); }
        if let Ok(events) = loki_collector.collect_metrics().await { all_events.extend(events); }
        if let Ok(events) = redis_collector.collect() { all_events.extend(events); }

        for event in all_events {
            tracing::warn!(?event, "Nuevo evento recibido");
            engine.add_event(event);
        }

        let incidents = engine.correlate();
        if !incidents.is_empty() {
            for incident in incidents {
                 // Avoid sending duplicate alerts for the same crash loop
                let should_send = true; // In a real scenario, you'd check if this incident was recently sent

                if should_send {
                    tracing::error!("🚨 Incidente correlacionado detectado: {:?}", incident);
                    let webhook_url = format!("{}/webhook/{}", n8n_url, incident.n8n_playbook);
                    let _ = n8n_client.post(&webhook_url).json(&incident).send().await;
                }
            }
        }
    }
}