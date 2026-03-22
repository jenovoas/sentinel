// src/quantum/semantic_router.rs
//! Semantic Router - Intent Classification via Vertex AI
//!
//! Classifies natural language queries into executable intents.

use reqwest::Client;
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::env;

#[derive(Debug, PartialEq, Clone)]
pub enum Intent {
    Oracle,
    SystemAction,
    SafetyCheck,
    Unknown,
}

#[derive(Serialize)]
struct GeminiRequest {
    contents: Vec<Content>,
    #[serde(rename = "generationConfig")]
    generation_config: GenerationConfig,
}

#[derive(Serialize)]
struct Content {
    role: String,
    parts: Vec<Part>,
}

#[derive(Serialize, Deserialize)]
struct Part {
    text: String,
}

#[derive(Serialize)]
struct GenerationConfig {
    temperature: f32,
}

#[derive(Deserialize)]
struct GeminiResponse {
    candidates: Option<Vec<Candidate>>,
}

#[derive(Deserialize)]
struct Candidate {
    content: Option<CandidateContent>,
}

#[derive(Deserialize)]
struct CandidateContent {
    parts: Option<Vec<Part>>,
}

pub struct SemanticRouter {
    client: Client,
    api_key: String,
    project_id: String,
}

impl SemanticRouter {
    pub fn new() -> Self {
        dotenvy::dotenv().ok(); // Load .env
        let api_key = env::var("GOOGLE_API_KEY").unwrap_or_default();
        let project_id = env::var("GOOGLE_CLOUD_PROJECT").unwrap_or("sentinel-cortex".to_string());

        Self {
            client: Client::new(),
            api_key,
            project_id,
        }
    }

    pub async fn classify(&self, query: &str) -> (Intent, String) {
        if self.api_key.is_empty() {
             return (Intent::Unknown, "Missing GOOGLE_API_KEY".to_string());
        }

        let system_prompt = r#"
        You are the Routing Cortex for the Sentinel System.
        
        RULES:
        1. SUPPORT SPANISH AND ENGLISH INPUTS.
        2. Classify greetings ("Hola", "Hello") as QUERY_ORACLE.
        
        CATEGORIES:
        1. QUERY_ORACLE: Philosophical questions, teaching, analysis, GREETINGS, or conversational inputs.
           Examples: "Explain Yatra", "Analyze matrix", "Hola", "Buenos días".
        2. SYSTEM_ACTION: explicit commands to change system state.
           Examples: "Start dashboard", "Run health check", "Activar escáner".
        3. SAFETY_CHECK: rules/safety questions.
           Examples: "Can I delete X?", "¿Puedo borrar esto?".
        4. UNKNOWN: gibberish or non-text inputs.

        Output ONLY JSON: {"category": "CATEGORY_NAME", "reason": "Short explanation"}
        
        CRITICAL FOR SYSTEM_ACTION:
        If the intent is SYSTEM_ACTION, the 'reason' field MUST contain the exact bash command to execute, prefixed with 'CMD: '.
        
        WORKFLOW MAPPINGS (Return pure commands):
        - "Research [topic]" -> "CMD: research --prompt '[topic]'"
        - "Produce [algo]" -> "CMD: produce [algo]"
        - "Certify [file]" -> "CMD: certify [file]" (Will be mapped to Rust)
        
        GENERIC EXAMPLES:
        Example: User: "List files" -> Reason: "CMD: ls -la"
        Example: User: "Check disk" -> Reason: "CMD: df -h"
        "#;

        let prompt = format!("USER INPUT: {}", query);

        let url = format!(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={}",
            self.api_key
        );

        let body = json!({
            "contents": [{
                "role": "user",
                "parts": [{ "text": format!("{}\n\n{}", system_prompt, prompt) }]
            }],
            "generationConfig": {
                "temperature": 0.0
            }
        });

        match self.client.post(&url).json(&body).send().await {
            Ok(resp) => {
                if let Ok(gemini_resp) = resp.json::<GeminiResponse>().await {
                    if let Some(candidates) = gemini_resp.candidates {
                        if let Some(first) = candidates.first() {
                            if let Some(content) = &first.content {
                                if let Some(parts) = &content.parts {
                                    if let Some(part) = parts.first() {
                                        return self.parse_response(&part.text);
                                    }
                                }
                            }
                        }
                    }
                }
                (Intent::Unknown, "Failed to parse API response".to_string())
            }
            Err(e) => (Intent::Unknown, format!("API Request failed: {}", e)),
        }
    }

    fn parse_response(&self, text: &str) -> (Intent, String) {
        // Simple JSON parsing wrapper
        // Clean markdown ```json blocks
        let clean_text = text.trim()
            .trim_start_matches("```json")
            .trim_start_matches("```")
            .trim_end_matches("```")
            .trim();

        if let Ok(val) = serde_json::from_str::<serde_json::Value>(clean_text) {
             let cat = val["category"].as_str().unwrap_or("UNKNOWN");
             let reason = val["reason"].as_str().unwrap_or("No reason").to_string();

             let intent = match cat {
                 "QUERY_ORACLE" => Intent::Oracle,
                 "SYSTEM_ACTION" => Intent::SystemAction,
                 "SAFETY_CHECK" => Intent::SafetyCheck,
                 _ => Intent::Unknown,
             };
             (intent, reason)
        } else {
            (Intent::Unknown, "Invalid JSON from AI".to_string())
        }
    }
}
