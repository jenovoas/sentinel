use axum::{
    extract::{State, Json},
    response::IntoResponse,
    routing::{post, get},
    Router,
};
use std::sync::Arc;
use tokio::sync::Mutex;
use crate::security::soul_verifier::{SoulVerifier, ProofOfLife, AlmaChallenge};
use crate::monitoring::{SystemMonitor, SystemMetrics};
use tower_http::cors::CorsLayer;

// Estado compartido de la aplicación
struct AppState {
    verifier: Mutex<SoulVerifier>,
    monitor: SystemMonitor,
    history: Mutex<Vec<ProofOfLife>>,
}

pub async fn start_api_server() {
    let state = Arc::new(AppState {
        verifier: Mutex::new(SoulVerifier::new()),
        monitor: SystemMonitor::new(),
        history: Mutex::new(Vec::new()),
    });

    let app = Router::new()
        .route("/api/v1/soul/challenge", post(generate_challenge))
        .route("/api/v1/soul/verify", post(verify_soul))
        .route("/api/v1/soul/history", get(get_soul_history))
        .route("/api/v1/system/status", get(get_system_status))
        .layer(CorsLayer::permissive()) // Permitir frontend local
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3005").await.unwrap();
    tracing::info!("🌌 Soul Verifier API listening on port 3005");
    axum::serve(listener, app).await.unwrap();
}

// Handlers
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
        Err(e) => Json(VerifyResponse {
            success: false,
            message: format!("Rechazo de Resonancia: {:?}", e),
            proof: None,
        }),
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
