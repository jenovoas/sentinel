use axum::{
    extract::{State, Json, ConnectInfo},
    response::IntoResponse,
    routing::{post, get},
    Router,
};
use std::sync::Arc;
use tokio::sync::Mutex;
use serde::{Serialize, Deserialize};
use crate::security::soul_verifier::{SoulVerifier, ProofOfLife, AlmaChallenge, SoulError, BiologicalMetrics};
use crate::monitoring::{SystemMonitor, SystemMetrics};
use crate::actions::N8NClient;
use tower_http::cors::CorsLayer;
use std::net::SocketAddr;
use redis::AsyncCommands;

#[derive(Serialize, Deserialize, Debug, Clone)]
struct Alert {
    pub r#type: String,
    pub hash: String,
    pub ip: String,
    pub timestamp: i64,
    pub severity: String,
    pub lyapunov: f64,
    pub entropy: f64,
}

// Estado compartido de la aplicación
struct AppState {
    verifier: Mutex<SoulVerifier>,
    monitor: SystemMonitor,
    history: Mutex<Vec<ProofOfLife>>,
    alerts: Mutex<Vec<Alert>>,
    redis: Option<redis::Client>,
    n8n: N8NClient,
}

pub async fn start_api_server() {
    let n8n_url = std::env::var("N8N_URL").unwrap_or_else(|_| "http://n8n-security:5678".to_string());
    let redis_url = std::env::var("REDIS_URL").unwrap_or_else(|_| "redis://redis:6379".to_string());

    let redis_client = redis::Client::open(redis_url).ok();
    
    let state = Arc::new(AppState {
        verifier: Mutex::new(SoulVerifier::new()),
        monitor: SystemMonitor::new(),
        history: Mutex::new(Vec::new()),
        alerts: Mutex::new(Vec::new()),
        redis: redis_client,
        n8n: N8NClient::new(n8n_url),
    });

    let app = Router::new()
        .route("/api/v1/soul/challenge", post(generate_challenge))
        .route("/api/v1/soul/verify", post(verify_soul))
        .route("/api/v1/soul/history", get(get_soul_history))
        .route("/api/v1/system/status", get(get_system_status))
        .route("/api/v1/sentinel/alerts", get(get_alerts))
        .layer(CorsLayer::permissive()) // Permitir frontend local
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3005").await.unwrap();
    tracing::info!("🌌 Soul Verifier API listening on port 3005");
    
    // Axum serve with address info for IP tracking
    axum::serve(listener, app.into_make_service_with_connect_info::<SocketAddr>()).await.unwrap();
}

// Handlers
async fn get_alerts(
    State(state): State<Arc<AppState>>,
) -> Json<Vec<Alert>> {
    let alerts = state.alerts.lock().await;
    // Return last 20
    let result = alerts.iter().rev().take(20).cloned().collect();
    Json(result)
}

async fn get_soul_history(
    State(state): State<Arc<AppState>>,
) -> Json<Vec<ProofOfLife>> {
    let history = state.history.lock().await;
    // Return last 50 records
    let result = history.iter().rev().take(50).cloned().collect();
    Json(result)
}

async fn get_system_status(
    State(state): State<Arc<AppState>>,
) -> Json<SystemMetrics> {
    Json(state.monitor.get_metrics())
}

async fn generate_challenge(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<ChallengeRequest>,
) -> impl IntoResponse {
    let verifier = state.verifier.lock().await;
    let challenge = verifier.generate_challenge(&payload.user_id);
    Json(challenge)
}

async fn verify_soul(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    Json(payload): Json<VerifyRequest>,
) -> impl IntoResponse {
    let verifier = state.verifier.lock().await;
    
    match verifier.verify_proof_of_life(&payload.rppg_signal, &payload.challenge) {
        Ok(proof) => {
            // Persist proof to history
            let mut history = state.history.lock().await;
            history.push(proof.clone());
            
            Json(VerifyResponse {
                success: true,
                message: "Alma Verificada".to_string(),
                proof: Some(proof),
            })
        },
        Err(e) => {
            // 🚨 ALERT LOGIC
            if let SoulError::UnauthorizedIdentity(ref metrics) = e {
                tracing::warn!("🚨 UNAUTHORIZED SOUL DETECTED: {} from {}", payload.challenge.user_id, addr);
                
                let alert = Alert {
                    r#type: "biological_intrusion".to_string(),
                    hash: payload.challenge.user_id.clone(),
                    ip: addr.to_string(),
                    timestamp: chrono::Utc::now().timestamp(),
                    severity: "CRITICAL".to_string(),
                    lyapunov: metrics.lyapunov_exp,
                    entropy: metrics.chaos_entropy,
                };

                // Store in-memory
                {
                    let mut alerts_guard = state.alerts.lock().await;
                    alerts_guard.push(alert.clone());
                }

                // 1. Publish to Redis (Sentinel Dashboard)
                if let Some(client) = &state.redis {
                     if let Ok(mut conn) = client.get_async_connection().await {
                         let alert_payload = serde_json::to_string(&alert).unwrap_or_default();
                         let _ = conn.publish::<_, _, ()>("sentinel:intruder", alert_payload).await;
                     }
                }

                // 2. Trigger N8N Workflow
                let _ = state.n8n.trigger_alert("biological_intrusion", serde_json::json!({
                    "hash": payload.challenge.user_id,
                    "ip": addr.to_string(),
                    "lyapunov": metrics.lyapunov_exp,
                    "entropy": metrics.chaos_entropy
                })).await;
            }

            Json(VerifyResponse {
                success: false,
                message: format!("Rechazo de Resonancia: {:?}", e),
                proof: None,
            })
        }
    }
}

// DTOs
#[derive(serde::Deserialize)]
struct ChallengeRequest {
    user_id: String,
}

#[derive(serde::Deserialize)]
struct VerifyRequest {
    rppg_signal: Vec<f32>,
    challenge: AlmaChallenge,
}

#[derive(serde::Serialize)]
struct VerifyResponse {
    success: bool,
    message: String,
    proof: Option<ProofOfLife>,
}
