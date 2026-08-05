// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//
// Prometheus metrics collector; pending routing to the main event loop.
#![allow(dead_code)]

use reqwest::Client;
use crate::models::{Event, EventSource, EventType, Severity};
use chrono::Utc;
use crate::math::s60::S60;

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
    
    /// Consulta Prometheus y devuelve eventos usando matemáticas S60 puras
    pub async fn collect(&self) -> Result<Vec<Event>, Box<dyn std::error::Error>> {
        let mut events = Vec::new();
        
        // Umbrales en S60 (Base-60, SCALE_0 = 60^4 = 12_960_000)
        // 0.8 = 4/5 → 12_960_000 * 4 / 5 = 10_368_000
        let cpu_threshold = S60::from_raw(10_368_000); 
        
        // 0.1 = 1/10 → 12_960_000 / 10 = 1_296_000
        let mem_threshold = S60::from_raw(1_296_000);

        // Query 1: CPU alto
        let cpu_query = "rate(node_cpu_seconds_total[5m])";
        if let Ok(value) = self.query_scalar_s60(cpu_query).await {
            if value > cpu_threshold {
                events.push(Event {
                    id: uuid::Uuid::new_v4().to_string(),
                    source: EventSource::Prometheus,
                    timestamp: Utc::now(),
                    severity: Severity::High,
                    event_type: EventType::CpuSpike,
                    metadata: serde_json::json!({
                        "cpu_usage_tertia": value.to_base_units(),
                        "threshold_tertia": cpu_threshold.to_base_units(),
                    }),
                });
            }
        }
        
        // Query 2: Memoria disponible
        let mem_query = "node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes";
        if let Ok(value) = self.query_scalar_s60(mem_query).await {
            if value < mem_threshold {
                events.push(Event {
                    id: uuid::Uuid::new_v4().to_string(),
                    source: EventSource::Prometheus,
                    timestamp: Utc::now(),
                    severity: Severity::Critical,
                    event_type: EventType::MemoryLeak,
                    metadata: serde_json::json!({
                        "available_memory_tertia": value.to_base_units(),
                        "threshold_tertia": mem_threshold.to_base_units(),
                    }),
                });
            }
        }
        
        Ok(events)
    }
    
    async fn query_scalar_s60(&self, query: &str) -> Result<S60, Box<dyn std::error::Error>> {
        let url = format!("{}/api/v1/query?query={}", self.base_url, query);
        let response = self.client.get(&url).send().await?;
        let json: serde_json::Value = response.json().await?;
        
        // Extraer primer valor del resultado
        let value_str = json["data"]["result"][0]["value"][1]
            .as_str()
            .ok_or("No value found")?;
        
        Ok(parse_prometheus_value_to_s60(value_str)?)
    }
}

/// Parsea un string numérico de Prometheus a S60 sin usar tipos de coma flotante.
/// Soporta notación científica y números decimales.
fn parse_prometheus_value_to_s60(s: &str) -> Result<S60, Box<dyn std::error::Error>> {
    if s.eq_ignore_ascii_case("nan") || s.eq_ignore_ascii_case("+inf") || s.eq_ignore_ascii_case("-inf") || s.eq_ignore_ascii_case("inf") {
        return Err("Cannot parse NaN or Inf to S60".into());
    }

    let (mantissa_str, exp_val) = if let Some(idx) = s.find(|c: char| c == 'e' || c == 'E') {
        let mant = &s[..idx];
        let exp: i32 = s[idx + 1..].parse()?;
        (mant, exp)
    } else {
        (s, 0)
    };

    let parts: Vec<&str> = mantissa_str.split('.').collect();
    let int_part_str = parts[0];
    let is_negative = int_part_str.starts_with('-');
    
    let mut digits = String::new();
    if is_negative {
        digits.push_str(&int_part_str[1..]);
    } else {
        digits.push_str(int_part_str);
    }
    
    let frac_len = if parts.len() > 1 {
        digits.push_str(parts[1]);
        parts[1].len() as i32
    } else {
        0
    };

    if digits.is_empty() {
        return Ok(S60::ZERO);
    }

    let parsed_digits = digits.parse::<i128>()?;
    let mut total_exp = exp_val - frac_len;
    
    let mut tertia = parsed_digits * (S60::SCALE_0 as i128);
    
    while total_exp > 0 {
        tertia *= 10;
        total_exp -= 1;
    }
    while total_exp < 0 {
        tertia /= 10;
        total_exp += 1;
    }
    
    if is_negative {
        tertia = -tertia;
    }
    
    Ok(S60::from_raw(tertia as i64))
}
