use crate::models::{Event, EventSource, Severity};
use chrono::Utc;
use reqwest::Client;
use redis::{Commands, RedisResult};
use uuid::Uuid;

/// Un colector genérico para realizar consultas HTTP a servicios como Loki o Prometheus.
struct HttpCollector {
    client: Client,
    base_url: String,
}

impl HttpCollector {
    fn new(base_url: String) -> Self {
        Self {
            client: Client::new(),
            base_url,
        }
    }

    /// Realiza una consulta GET a un endpoint específico.
    async fn query(&self, endpoint: &str, query: &str) -> Result<serde_json::Value, reqwest::Error> {
        let url = format!("{}{}", self.base_url, endpoint);
        let response = self.client.get(&url).query(&[("query", query)]).send().await?;
        response.json().await
    }
}

impl LokiCollector {
    pub fn new(loki_url: String) -> Self {
        Self { http: HttpCollector::new(loki_url) }
    }

    pub async fn collect_logs(&self) -> Result<Vec<Event>, reqwest::Error> {
        let mut events = Vec::new();
        // LogQL para buscar intentos de login fallidos en los logs del sistema
        let failed_login_query = r#"{job="systemd-journal"} |= "Failed password""#;

        let json = self.http.query("/loki/api/v1/query_range", failed_login_query).await?;

        if let Some(streams) = json["data"]["result"].as_array() {
            for stream in streams {
                if let Some(values) = stream["values"].as_array() {
                    for value_pair in values {
                        events.push(Event {
                            event_type: "failed_login".to_string(),
                            source: EventSource::NervioAIntrusion, // Es un evento de seguridad
                            severity: Severity::Medium,
                            metadata: serde_json::json!({
                                "log_entry": value_pair[1].clone(),
                                "labels": stream["stream"].clone(),
                            }),
                            ..Default::default()
                        });
                    }
                }
            }
        }
        Ok(events)
    }

    pub async fn collect_metrics(&self) -> Result<Vec<Event>, reqwest::Error> {
        let mut events = Vec::new();

        // LogQL para contar errores 5xx de Nginx en los últimos 5 minutos
        let nginx_5xx_query = r#"sum(count_over_time({container_name="sentinel-nginx"}[5m] |~ "HTTP/1\.[01]\" 5[0-9]{2}"))"#;

        let json = self.http.query("/loki/api/v1/query", nginx_5xx_query).await?;

        if let Some(results) = json["data"]["result"].as_array() {
            if let Some(first_result) = results.get(0) {
                if let Some(value_str) = first_result["value"][1].as_str() {
                    if let Ok(count) = value_str.parse::<u64>() {
                        if count > 0 {
                            events.push(Event {
                                event_type: "nginx_5xx_spike".to_string(),
                                source: EventSource::Prometheus, // Actúa como una métrica
                                severity: Severity::High,
                                metadata: serde_json::json!({
                                    "count": count,
                                    "timespan_minutes": 5
                                }),
                                ..Default::default()
                            });
                        }
                    }
                }
            }
        }
        Ok(events)
    }
}

pub struct LokiCollector {
    http: HttpCollector,
}

impl PrometheusCollector {
    pub fn new(prometheus_url: String) -> Self {
        Self { http: HttpCollector::new(prometheus_url) }
    }

    pub async fn collect(&self) -> Result<Vec<Event>, reqwest::Error> {
        let mut events = Vec::new();

        // Ejemplo: Query para CPU alto
        let cpu_query = "rate(node_cpu_seconds_total{mode='system'}[1m]) * 100 > 80";
        let json = self.http.query("/api/v1/query", cpu_query).await?;
        let cpu_alerts = json["data"]["result"].as_array().cloned().unwrap_or_default();

        for alert in cpu_alerts {
            if let Some(value_str) = alert["value"][1].as_str() {
                if let Ok(value_int) = value_str.parse::<f64>().map(|f| f as u64) {
                    if value_int > 0 {
                        events.push(Event {
                            event_type: "high_cpu_usage".to_string(),
                            source: EventSource::Prometheus,
                            severity: Severity::High,
                            metadata: serde_json::json!({
                                "host": alert["metric"]["instance"],
                                "value": value_int,
                                "description": "CPU usage over 80% for 1 minute."
                            }),
                            ..Default::default() // Usa valores por defecto para id y timestamp
                        });
                    }
                }
            }
        }
        Ok(events)
    }

    pub async fn collect_redis_metrics(&self) -> Result<Vec<Event>, reqwest::Error> {
        let mut events = Vec::new();
        let redis_memory_query = "redis_memory_used_bytes";

        let json = self.http.query("/api/v1/query", redis_memory_query).await?;
        let redis_metrics = json["data"]["result"].as_array().cloned().unwrap_or_default();

        for metric in redis_metrics {
            if let Some(value_str) = metric["value"][1].as_str() {
                if let Ok(memory_bytes) = value_str.parse::<f64>().map(|f| f as u64) {
                    // El evento se crea siempre, el umbral se aplica en el DecisionEngine
                    events.push(Event {
                        event_type: "redis_memory_usage".to_string(),
                        source: EventSource::Prometheus,
                        severity: Severity::Info, // La severidad se determina en el motor
                        metadata: serde_json::json!({
                            "instance": metric["metric"]["instance"],
                            "used_bytes": memory_bytes,
                        }),
                        ..Default::default()
                    });
                }
            }
        }

        Ok(events)
    }

}

pub struct PrometheusCollector {
    http: HttpCollector,
}

pub struct RedisStreamCollector {
    client: redis::Client,
    last_id: String,
}

impl RedisStreamCollector {
    pub fn new(redis_url: &str) -> RedisResult<Self> {
        Ok(Self {
            client: redis::Client::open(redis_url)?,
            last_id: "0-0".to_string(), // Start from the beginning of the stream
        })
    }

    pub fn collect(&mut self) -> RedisResult<Vec<Event>> {
        let mut con = self.client.get_connection()?;
        let result: redis::Value = con.xread(
            &["swarm:infra:log"],
            &[&self.last_id],
        )?;

        let mut events = Vec::new();

        if let redis::Value::Bulk(streams) = result {
            for stream in streams {
                if let redis::Value::Bulk(mut stream_data) = stream {
                    if let redis::Value::Bulk(messages) = stream_data.pop().unwrap() {
                        for message in messages {
                            if let redis::Value::Bulk(mut msg_data) = message {
                                let msg_id: String = redis::from_redis_value(&msg_data[0])?;
                                self.last_id = msg_id;

                                let fields: std::collections::HashMap<String, String> = redis::from_redis_value(&msg_data[1])?;

                                if fields.get("event_type") == Some(&"CONTAINER_RESTART".to_string()) {
                                    events.push(Event {
                                        event_type: "container_restarted".to_string(),
                                        source: EventSource::NervioBIntegrity, // System integrity event
                                        severity: Severity::Medium,
                                        metadata: serde_json::json!({
                                            "node": fields.get("node"),
                                            "service": fields.get("service"),
                                            "restarts": fields.get("restarts").and_then(|s| s.parse::<i64>().ok()),
                                        }),
                                        ..Default::default()
                                    });
                                }
                            }
                        }
                    }
                }
            }
        }
        Ok(events)
    }
}

// Implementación por defecto para los campos que no se especifican
impl Default for Event {
    fn default() -> Self {
        Event {
            id: Uuid::new_v4(),
            timestamp: Utc::now(),
            source: EventSource::Prometheus,
            severity: Severity::Info,
            event_type: String::new(),
            metadata: serde_json::Value::Null,
        }
    }
}