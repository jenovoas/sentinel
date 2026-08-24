// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
use anyhow::{bail, Context, Result};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::process::Command;

#[derive(Serialize, Deserialize, Debug)]
pub struct VertexRequest {
    pub contents: Vec<VertexContent>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub system_instruction: Option<VertexContent>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct VertexContent {
    pub parts: Vec<VertexPart>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub role: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct VertexPart {
    pub text: String,
}

#[derive(Deserialize, Debug)]
pub struct VertexResponse {
    pub candidates: Vec<VertexCandidate>,
}

#[derive(Deserialize, Debug)]
pub struct VertexCandidate {
    pub content: VertexContentResponse,
}

#[derive(Deserialize, Debug)]
pub struct VertexContentResponse {
    pub parts: Vec<VertexPart>,
}

#[derive(Debug, PartialEq)]
pub enum Intent {
    Research(String),
    Memorize(String),
    Produce(String),
    Unknown,
}

pub async fn classify_intent(prompt: &str, api_key: &str) -> Result<Intent> {
    let client = Client::new();
    let url = format!(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={}",
        api_key
    );

    let system_msg = r#"
    You are the Semantic Router for the Sentinel Swarm Control Room.
    Your job is to map natural language user requests to specific agent commands.

    AVAILABLE COMMANDS:
    1. Research: For requests to investigate, learn, search, study, or analyze a topic.
    2. Memorize: For requests to remember, store, save facts, or learn rules.
    3. Produce: For requests to create videos, media, reports, or artifacts.

    OUTPUT FORMAT:
    Return a JSON object with "action" and "parameter".
    - action: "RESEARCH", "MEMORIZE", "PRODUCE", or "UNKNOWN"
    - parameter: The extracted subject/topic without verbs.
    "#;

    let req = VertexRequest {
        contents: vec![VertexContent {
            role: Some("user".to_string()),
            parts: vec![VertexPart {
                text: prompt.to_string(),
            }],
        }],
        system_instruction: Some(VertexContent {
            role: None,
            parts: vec![VertexPart {
                text: system_msg.to_string(),
            }],
        }),
    };

    let res = client.post(url).json(&req).send().await?;

    if !res.status().is_success() {
        let err = res.text().await?;
        bail!("Gemini API Error: {}", err);
    }

    let res_json = res.json::<VertexResponse>().await?;
    let raw_text = res_json
        .candidates
        .first()
        .and_then(|c| c.content.parts.first())
        .map(|p| p.text.trim())
        .unwrap_or("{}");

    let cleaned = raw_text
        .trim_matches('`')
        .replace("json", "")
        .trim()
        .to_string();

    #[derive(Deserialize)]
    struct RouterResponse {
        action: String,
        parameter: String,
    }

    let parsed: RouterResponse = serde_json::from_str(&cleaned).unwrap_or(RouterResponse {
        action: "UNKNOWN".to_string(),
        parameter: "".to_string(),
    });

    match parsed.action.to_uppercase().as_str() {
        "RESEARCH" => Ok(Intent::Research(parsed.parameter)),
        "MEMORIZE" => Ok(Intent::Memorize(parsed.parameter)),
        "PRODUCE" => Ok(Intent::Produce(parsed.parameter)),
        _ => Ok(Intent::Unknown),
    }
}

pub struct FallbackConfig {
    pub gemini_api_key: Option<String>,
    pub gcloud_project_id: Option<String>,
    pub gcloud_region: Option<String>,
}

pub async fn synthesize_vertex(
    client: &Client,
    config: &FallbackConfig,
    system_msg: &str,
    user_msg: &str,
) -> Result<String> {
    if let Some(ref api_key) = config.gemini_api_key {
        let url = format!(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={}",
            api_key
        );

        let body = json!({
            "contents": [
                { "role": "user", "parts": [{ "text": user_msg }] }
            ],
            "systemInstruction": { "role": "system", "parts": [{ "text": system_msg }] }
        });

        let res = client.post(&url).json(&body).send().await?;

        if res.status().is_success() {
            let json: VertexResponse = res.json().await?;
            if let Some(candidate) = json.candidates.first() {
                if let Some(part) = candidate.content.parts.first() {
                    return Ok(part.text.clone());
                }
            }
            bail!("Google AI retornó una respuesta vacía");
        }
    }

    // Fallback a gcloud Vertex AI
    let project = config
        .gcloud_project_id
        .as_ref()
        .context("gcloud_project_id no configurado para Fallback de Vertex")?;
    let region = config.gcloud_region.as_deref().unwrap_or("us-central1");
    let model = "gemini-1.5-flash";

    let token_out = Command::new("gcloud")
        .args(["auth", "print-access-token"])
        .output()
        .context("Error al ejecutar gcloud auth print-access-token")?;

    if !token_out.status.success() {
        bail!("Error al obtener token de gcloud");
    }

    let token = String::from_utf8_lossy(&token_out.stdout)
        .trim()
        .to_string();
    let url = format!(
        "https://{}-aiplatform.googleapis.com/v1/projects/{}/locations/{}/publishers/google/models/{}:generateContent", 
        region, project, region, model
    );

    let body = json!({
        "contents": [{ "role": "user", "parts": [{ "text": user_msg }] }],
        "systemInstruction": { "parts": [{ "text": system_msg }] }
    });

    let res = client
        .post(&url)
        .header("Authorization", format!("Bearer {}", token))
        .json(&body)
        .send()
        .await?;

    if res.status().is_success() {
        let json: VertexResponse = res.json().await?;
        if let Some(candidate) = json.candidates.first() {
            if let Some(part) = candidate.content.parts.first() {
                return Ok(part.text.clone());
            }
        }
        bail!("Vertex AI retornó una respuesta vacía");
    } else {
        bail!("Vertex AI Error: {}", res.text().await.unwrap_or_default());
    }
}
