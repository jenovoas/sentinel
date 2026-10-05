// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
mod collectors;
mod engine;
mod models;
mod patterns;

use crate::engine::DecisionEngine;

fn should_send_alert(
    sent_alerts: &mut std::collections::HashMap<String, std::time::Instant>,
    key: &str,
    now: std::time::Instant,
    cooldown: Duration,
) -> bool {
    sent_alerts.retain(|_, last| {
        now.checked_duration_since(*last)
            .is_some_and(|age| age < cooldown)
    });
    !sent_alerts.contains_key(key)
}

use collectors::{LokiCollector, NervioBCollector, PrometheusCollector, RedisStreamCollector};
use std::time::Duration;

#[cfg(test)]
mod tests {
    use super::should_send_alert;
    use std::collections::HashMap;
    use std::time::{Duration, Instant};

    #[test]
    fn alert_cooldown_suppresses_duplicates_and_expires() {
        let start = Instant::now();
        let cooldown = Duration::from_secs(300);
        let mut sent = HashMap::new();

        assert!(should_send_alert(&mut sent, "incident", start, cooldown));
        sent.insert("incident".to_string(), start);
        assert!(!should_send_alert(
            &mut sent,
            "incident",
            start + Duration::from_secs(299),
            cooldown
        ));
        assert!(should_send_alert(
            &mut sent,
            "incident",
            start + cooldown,
            cooldown
        ));
        assert!(sent.is_empty());
    }
}

#[tokio::main]
async fn main() {
    // 1. Inicializar logging y variables de entorno
    tracing_subscriber::fmt::init();
    dotenvy::dotenv().ok();

    let prometheus_url =
        std::env::var("PROMETHEUS_URL").expect("PROMETHEUS_URL variable de entorno no encontrada");
    let n8n_url = std::env::var("N8N_URL").expect("N8N_URL variable de entorno no encontrada");
    let loki_url = std::env::var("LOKI_URL").expect("LOKI_URL variable de entorno no encontrada");
    let redis_url =
        std::env::var("REDIS_URL").expect("REDIS_URL variable de entorno no encontrada");

    // 2. Inicializar componentes
    let prom_collector = PrometheusCollector::new(prometheus_url.clone());
    let loki_collector = LokiCollector::new(loki_url);
    let mut redis_collector =
        RedisStreamCollector::new(&redis_url, &prometheus_url).expect("Failed to connect to Redis");
    let nervio_b_collector = NervioBCollector::new(prometheus_url.clone());
    let mut engine = DecisionEngine::new();
    let n8n_client = reqwest::Client::new();
    let mut sent_alerts: std::collections::HashMap<String, std::time::Instant> =
        std::collections::HashMap::new();
    let alert_cooldown = Duration::from_secs(300); // 5 min cooldown per incident key

    tracing::info!("🧠 Neural Guard Cortex iniciado. Esperando señales...");

    // 3. Bucle principal de orquestación
    let mut interval = tokio::time::interval(Duration::from_secs(10)); // Shorter interval for stream reading
    loop {
        interval.tick().await;
        tracing::info!("Recolectando eventos...");

        let mut all_events = Vec::new();

        // Collect from all sources
        if let Ok(events) = prom_collector.collect().await {
            all_events.extend(events);
        }
        if let Ok(events) = prom_collector.collect_redis_metrics().await {
            all_events.extend(events);
        }
        if let Ok(events) = prom_collector.collect_thermal_metrics().await {
            all_events.extend(events);
        }
        if let Ok(events) = loki_collector.collect_logs().await {
            all_events.extend(events);
        }
        if let Ok(events) = loki_collector.collect_metrics().await {
            all_events.extend(events);
        }
        if let Ok(events) = redis_collector.collect().await {
            all_events.extend(events);
        }
        if let Ok(events) = nervio_b_collector.collect().await {
            all_events.extend(events);
        }
        if let Ok(events) = loki_collector.collect_auditd().await {
            all_events.extend(events);
        }

        for event in all_events {
            tracing::warn!(?event, "Nuevo evento recibido");
            engine.add_event(event);
        }

        let incidents = engine.correlate();
        if !incidents.is_empty() {
            for incident in incidents {
                let alert_key = format!(
                    "{}:{:?}:{}",
                    incident.name, incident.severity, incident.n8n_playbook
                );
                let now = std::time::Instant::now();
                if should_send_alert(&mut sent_alerts, &alert_key, now, alert_cooldown) {
                    tracing::error!("🚨 Incidente correlacionado detectado: {:?}", incident);
                    let webhook_url = format!("{}/webhook/{}", n8n_url, incident.n8n_playbook);
                    match n8n_client.post(&webhook_url).json(&incident).send().await {
                        Ok(response) if response.status().is_success() => {
                            sent_alerts.insert(alert_key, std::time::Instant::now());
                        }
                        Ok(response) => tracing::warn!(
                            status = %response.status(),
                            "El webhook rechazó la alerta; se permitirá reintentar"
                        ),
                        Err(error) => tracing::error!(
                            %error,
                            "No se pudo entregar la alerta; se permitirá reintentar"
                        ),
                    }
                }
            }
        }
    }
}
