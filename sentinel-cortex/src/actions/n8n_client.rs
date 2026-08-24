// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
use crate::models::DetectedPattern;
use reqwest::Client;

#[allow(dead_code)]
pub struct N8NClient {
    client: Client,
    base_url: String,
    auth: Option<(String, String)>,
}

#[allow(dead_code)]
impl N8NClient {
    pub fn new(base_url: String, auth: Option<(String, String)>) -> Self {
        Self {
            client: Client::new(),
            base_url,
            auth,
        }
    }

    /// Ejecuta un playbook en N8N
    pub async fn trigger_playbook(
        &self,
        pattern: &DetectedPattern,
    ) -> Result<(), Box<dyn std::error::Error>> {
        // La URL del webhook en N8N suele ser /webhook/slug o /webhook-test/slug
        // Asumimos /webhook/ para producción
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

        let mut request = self.client.post(&webhook_url);

        // Aplicar Basic Auth si está configurado
        if let Some((username, password)) = &self.auth {
            request = request.basic_auth(username, Some(password));
        }

        let response = request.json(&payload).send().await?;

        if response.status().is_success() {
            tracing::info!("✅ Playbook '{}' triggered successfully", pattern.playbook);
        } else {
            tracing::error!(
                "❌ Failed to trigger playbook '{}': {}",
                pattern.playbook,
                response.status()
            );
            // Log body for debugging
            if let Ok(text) = response.text().await {
                tracing::error!("   Response: {}", text);
            }
        }

        Ok(())
    }
}
