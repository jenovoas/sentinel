use reqwest::Client;
use crate::models::{Event, EventSource, EventType, Severity};
use chrono::Utc;

pub struct PrometheusCollector {
    client: Client,
    base_url: String,
}

impl PrometheusCollector {
    pub fn new(base_url: String) -> Self {
        Self {
            client: Client::new(),
            base_url,
        }
    }
    
    /// Consulta Prometheus y devuelve eventos
    pub async fn collect(&self) -> Result<Vec<Event>, Box<dyn std::error::Error>> {
        let mut events = Vec::new();
        
        // Query 1: CPU alto
        let cpu_query = "rate(node_cpu_seconds_total[5m])";
        if let Ok(value) = self.query_scalar(cpu_query).await {
            if value > 0.8 {  // 80% CPU
                events.push(Event {
                    id: uuid::Uuid::new_v4().to_string(),
                    source: EventSource::Prometheus,
                    timestamp: Utc::now(),
                    severity: Severity::High,
                    event_type: EventType::CpuSpike,
                    metadata: serde_json::json!({
                        "cpu_usage": value,
                        "threshold": 0.8,
                    }),
                });
            }
        }
        
        // Query 2: Memoria disponible
        let mem_query = "node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes";
        if let Ok(value) = self.query_scalar(mem_query).await {
            if value < 0.1 {  // Menos de 10% disponible
                events.push(Event {
                    id: uuid::Uuid::new_v4().to_string(),
                    source: EventSource::Prometheus,
                    timestamp: Utc::now(),
                    severity: Severity::Critical,
                    event_type: EventType::MemoryLeak,
                    metadata: serde_json::json!({
                        "available_memory_pct": value,
                        "threshold": 0.1,
                    }),
                });
            }
        }
        
        Ok(events)
    }
    
    async fn query_scalar(&self, query: &str) -> Result<f64, Box<dyn std::error::Error>> {
        let url = format!("{}/api/v1/query?query={}", self.base_url, query);
        let response = self.client.get(&url).send().await?;
        let json: serde_json::Value = response.json().await?;
        
        // Extraer primer valor del resultado
        let value_str = json["data"]["result"][0]["value"][1]
            .as_str()
            .ok_or("No value found")?;
        
        Ok(value_str.parse()?)
    }
}
