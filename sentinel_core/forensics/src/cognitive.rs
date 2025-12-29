use serde::{Deserialize, Serialize};
use reqwest::Client;
use std::time::Duration;
use dashmap::DashMap;

#[derive(Serialize)]
struct OllamaRequest {
    model: String,
    prompt: String,
    stream: bool,
}

#[derive(Deserialize)]
struct OllamaResponse {
    response: String,
}

pub struct CognitiveEngine {
    client: Client,
    model: String,
    // Caché de decisiones: (Nombre de proceso + Firmas ordenadas) -> Decisión (true = BLOCK)
    cache: DashMap<String, bool>,
}

impl CognitiveEngine {
    pub fn new(model: &str) -> Self {
        Self {
            client: Client::builder()
                .timeout(Duration::from_secs(10))
                .build()
                .unwrap(),
            model: model.to_string(),
            cache: DashMap::new(),
        }
    }

    pub async fn ask_decision(&self, pid: i32, comm: &str, signatures: &[String]) -> Result<bool, Box<dyn std::error::Error + Send + Sync>> {
        // Crear una clave única para la caché basada en el binario y las firmas detectadas
        let mut sorted_sigs = signatures.to_vec();
        sorted_sigs.sort();
        let cache_key = format!("{}:{:?}", comm, sorted_sigs);

        if let Some(decision) = self.cache.get(&cache_key) {
            println!("🚀 [Cognitive Engine] [CACHE HIT] Usando decisión previa para {} (PID: {})", comm, pid);
            return Ok(*decision);
        }

        println!("🧠 [Cognitive Engine] Consultando IA para PID {} ({})...", pid, comm);
        
        // Prompt simplificado para mínima latencia
        let prompt = format!(
            "Evidence for {}: {:?}. Decide: BLOCK/ALLOW. Respond 1 word.",
            comm, signatures
        );

        let request = OllamaRequest {
            model: self.model.clone(),
            prompt,
            stream: false,
        };

        let res = self.client.post("http://localhost:11434/api/generate")
            .json(&request)
            .send()
            .await?;

        if !res.status().is_success() {
            println!("❌ [Cognitive Engine] Error en Ollama: {}", res.status());
            return Err("Ollama API error".into());
        }

        let response: OllamaResponse = res.json().await?;
        let decision_raw = response.response.trim().to_uppercase();
        let is_block = decision_raw.contains("BLOCK");

        println!("🧠 [Cognitive Loop] Decisión IA para PID {}: '{}'", pid, decision_raw);

        // Guardar resultado en caché
        self.cache.insert(cache_key, is_block);

        Ok(is_block)
    }
}
