use reqwest::Client;
use crate::models::DetectedPattern;

pub struct N8NClient {
    client: Client,
    base_url: String,
}

impl N8NClient {
    pub fn new(base_url: String) -> Self {
        Self {
            client: Client::new(),
            base_url,
        }
    }
    
    /// Ejecuta un playbook en N8N
    pub async fn trigger_playbook(
        &self,
        pattern: &DetectedPattern
    ) -> Result<(), Box<dyn std::error::Error>> {
        let webhook_url = format!("{}/webhook/{}", self.base_url, pattern.playbook);
        
        let payload = serde_json::json!({
            "pattern_name": pattern.name,
            "confidence": pattern.confidence,
            "severity": pattern.severity,
            "event_count": pattern.events.len(),
            "recommended_action": pattern.recommended_action,
            "timestamp": chrono::Utc::now().to_rfc3339(),
        });
        
        tracing::info!("📤 Triggering playbook: {}", pattern.playbook);
        
        let response = self.client
            .post(&webhook_url)
            .json(&payload)
            .send()
            .await?;
        
        if response.status().is_success() {
            tracing::info!("✅ Playbook '{}' triggered successfully", pattern.playbook);
        } else {
            tracing::error!("❌ Failed to trigger playbook '{}': {}", pattern.playbook, response.status());
        }
        
        Ok(())
    }
}
