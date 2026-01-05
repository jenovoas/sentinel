use reqwest::Client;
use serde::{Deserialize, Serialize};
use crate::models::{DetectedPattern, Severity};
use std::time::Duration;

#[derive(Debug, Serialize)]
pub struct TruthSyncRequest {
    text: String,
    priority: String,
    metadata: Option<serde_json::Value>,
}

#[derive(Debug, Deserialize)]
pub struct TruthSyncResponse {
    verified: bool,
    confidence: f32,
    explanation: String,
    cached: bool,
    latency_us: u64,
    cache_hit_count: u32,
}

pub struct TruthSyncClient {
    client: Client,
    base_url: String,
}

impl TruthSyncClient {
    pub fn new(base_url: String) -> Self {
        Self {
            client: Client::builder()
                .timeout(Duration::from_secs(10)) // 10s timeout
                .build()
                .unwrap(),
            base_url,
        }
    }
    
    pub async fn verify_pattern(&self, pattern: &DetectedPattern) -> Result<TruthSyncResponse, Box<dyn std::error::Error>> {
        let priority = match pattern.severity {
            Severity::Critical => "urgent".to_string(),
            Severity::High => "high".to_string(),
            Severity::Medium => "normal".to_string(),
            Severity::Low => "normal".to_string(),
        };
        
        let request_body = TruthSyncRequest {
            text: format!("{}: {}", pattern.name, pattern.recommended_action),
            priority,
            metadata: Some(serde_json::json!({ 
                "pattern_name": pattern.name,
                "pattern_confidence": pattern.confidence,
                "pattern_severity": format!("{:?}", pattern.severity),
                "event_count": pattern.events.len()
            })),
        };
        
        let url = format!("{}/verify", self.base_url);
        
        let response = self.client
            .post(&url)
            .json(&request_body)
            .send()
            .await?;
            
        if response.status().is_success() {
            let truth_response: TruthSyncResponse = response.json().await?;
            Ok(truth_response)
        } else {
            let status = response.status();
            let body = response.text().await?;
            Err(format!("TruthSync API error: Status {}, Body: {}", status, body).into())
        }
    }
}