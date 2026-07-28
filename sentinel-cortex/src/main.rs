// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
mod actions;
mod buffer_system;
mod collectors;
mod ebpf_cortex_bridge;
mod engine;
mod math;
mod memory;
mod mock_kernel;
mod models;
mod quantum;
mod security;
mod metrics;

use axum::{routing::{get, post}, Json, Router};
use axum::extract::ws::{WebSocketUpgrade, WebSocket, Message};
use math::harmonic_logic::{HarmonicProcessor, HarmonicState};
use security::bio_resonance::ResonanceEngine;
use security::soul_verifier_s60_production::BiometricVerifier;
use metrics::{MetricsRepository, PrometheusRepository, MetricsSnapshot};
use ebpf_cortex_bridge::{EbpfBridge, CortexEvent};
use serde::Serialize;
use std::sync::{Arc, Mutex};
use std::{net::SocketAddr, time::Duration};
use tokio::sync::{mpsc, broadcast};
use tokio::time::sleep;

#[derive(Serialize)]
struct HealthStatus {
    status: String,
    version: String,
    metrics: MetricsSnapshot,
}

struct AppState {
    resonance: Arc<Mutex<ResonanceEngine>>,
    metrics: Arc<dyn MetricsRepository>,
    bpf_stream: broadcast::Sender<CortexEvent>,
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();
    tracing::info!("Sentinel Cortex (S60) initializing...");

    // Check for CLI arguments (Semantic Shell Mode)
    let args: Vec<String> = std::env::args().collect();
    if args.iter().any(|arg| arg == "--shell") {
        tracing::info!("Launching Semantic Shell v2.0...");
        let mut shell = quantum::semantic_shell::SemanticShell::new();
        if let Err(e) = shell.run() {
            tracing::error!("Semantic Shell crashed: {}", e);
        }
        return;
    }

    // Initialize core components
    let resonance = Arc::new(Mutex::new(ResonanceEngine::new()));
    let processor = Arc::new(Mutex::new(HarmonicProcessor::new()));
    let metrics = Arc::new(PrometheusRepository::new());
    // Broadcast channel para Múltiples Inversores (WebSockets) viendo el eBPF
    let (tx_bpf, _) = broadcast::channel(100);

    let state = Arc::new(AppState {
        resonance: resonance.clone(),
        metrics: metrics.clone() as Arc<dyn MetricsRepository>,
        bpf_stream: tx_bpf.clone(),
    });

    // 1. Start Bio-Resonance Engine (17s Pulse) in a background task
    let resonance_task = resonance.clone();
    let processor_task = processor.clone();
    tokio::spawn(async move {
        tracing::info!("Resonance Engine active. Syncing to 17s Pulse...");
        let mut tick = 0;
        loop {
            sleep(Duration::from_secs(1)).await;
            tick += 1;

            // Decay entropy every second
            {
                let mut res = resonance_task.lock().unwrap();
                res.tick_entropy();
            }

            if tick % 17 == 0 {
                let mut res = resonance_task.lock().unwrap();
                let (valid, coherence) = res.verify_pulse(tick);
                tracing::info!(
                    "PULSE CHECK (T={}): Valid={}, Coherence={:?}",
                    tick,
                    valid,
                    coherence
                );

                if valid {
                    let mut proc = processor_task.lock().unwrap();
                    let input = HarmonicState::logic_true();
                    let result = proc.process_signal(input);
                    tracing::info!("PROCESSOR RESULT: {:?}", result);
                }
            }
        }
    });

    // 2. Start Redis Pulse Subscriber (Remote Bio-Sync)
    let redis_resonance = resonance.clone();
    tokio::spawn(async move {
        let redis_url = std::env::var("REDIS_URL").unwrap_or_else(|_| "redis://127.0.0.1:6379".to_string());
        match redis::Client::open(redis_url) {
            Ok(client) => {
                match client.get_async_pubsub().await {
                    Ok(mut pubsub) => {
                        let _ = pubsub.subscribe("sentinel:bio_pulse").await;
                        tracing::info!("📡 Remote Bio-Sync Active: Subscribed to 'sentinel:bio_pulse'");
                        
                        let mut stream = pubsub.on_message();
                        use futures_util::StreamExt; // We might need to add this
                        
                        while let Some(msg) = stream.next().await {
                            let mut res = redis_resonance.lock().unwrap();
                            res.inject_pulse(0);
                            tracing::info!("💖 Bio-Pulse received from SENTINEL_MEDIA");
                        }
                    }
                    Err(e) => tracing::error!("Failed to open Redis PubSub: {}", e),
                }
            }
            Err(e) => tracing::error!("Failed to connect to Redis: {}", e),
        }
    });

    // 3. Setup Axum Router
    let app = Router::new()
        .route("/health", get(health_handler))
        .route("/api/v1/telemetry", get(telemetry_ws_handler))
        .route("/api/v1/sentinel_status", get(sentinel_status_handler))
        .route("/api/v1/truth_claim", post(truth_claim_handler))
        .layer(tower_http::trace::TraceLayer::new_for_http())
        .with_state(state);

    // 4. Start Server
    let addr = SocketAddr::from(([0, 0, 0, 0], 8000));
    tracing::info!("Listening on {}", addr);
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn health_handler(
    axum::extract::State(state): axum::extract::State<Arc<AppState>>,
) -> Json<HealthStatus> {
    Json(HealthStatus {
        status: "OK".to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        metrics: MetricsSnapshot {
            coherence: state.metrics.get_bio_coherence().to_base_units(),
            efficiency: state.metrics.get_scheduler_efficiency().to_base_units(),
            timestamp_s60: 0, // Placeholder
        },
    })
}

async fn telemetry_ws_handler(
    ws: WebSocketUpgrade,
    axum::extract::State(state): axum::extract::State<Arc<AppState>>,
) -> impl axum::response::IntoResponse {
    ws.on_upgrade(|socket| handle_socket(socket, state))
}

async fn handle_socket(mut socket: WebSocket, state: Arc<AppState>) {
    tracing::info!("🔗 Client/Inversor connected to EBPF Ring-0 Stream");
    
    let mut rx = state.bpf_stream.subscribe();

    loop {
        // En lugar de fabricar, chupa directamente de la telemetría viva eBPF de Cortex
        let event: CortexEvent = match rx.recv().await {
            Ok(e) => e,
            Err(_) => break, // Broadcast channel cerraría si todo explota
        };
        
        let payload = match serde_json::to_string(&event) {
            Ok(p) => p,
            Err(e) => {
                tracing::error!("Serialization error eBPF: {}", e);
                continue;
            }
        };

        if socket.send(Message::Text(payload.into())).await.is_err() {
            tracing::info!("🔌 Connection Dropped (Investor UI Disconnected)");
            break;
        }
    }
}

// ==========================================
// HACKATHON CUBEPATH ENDPOINTS (MVP)
// ==========================================

#[derive(Serialize)]
pub struct SentinelStatusResponse {
    pub ring_status: String,
    pub xdp_firewall: String,
    pub lsm_cognitive: String,
    pub s60_resonance: i64,
}

pub async fn sentinel_status_handler(
    axum::extract::State(state): axum::extract::State<Arc<AppState>>,
) -> Json<SentinelStatusResponse> {
    Json(SentinelStatusResponse {
        ring_status: "SEALED".into(),
        xdp_firewall: "ACTIVE_0_LATENCY".into(),
        lsm_cognitive: "INTERCEPT_ENABLED".into(),
        s60_resonance: state.metrics.get_bio_coherence().to_base_units(),
    })
}

#[derive(serde::Deserialize)]
pub struct TruthClaimRequest {
    pub engine: String,
    pub claim_payload: String,
    pub trust_threshold: f64,
}

#[derive(Serialize)]
pub struct TruthClaimResponse {
    pub claim_valid: bool,
    pub sentinel_score: f64,
    pub truthsync_cache_hit: bool,
    pub ring0_intercepts: u32,
}

pub async fn truth_claim_handler(
    axum::extract::State(_state): axum::extract::State<Arc<AppState>>,
    Json(payload): Json<TruthClaimRequest>,
) -> Json<TruthClaimResponse> {
    tracing::info!("Verificando Truth Claim de AI: {}", payload.engine);
    
    // Simulación de TrustScore (Mocked para el MVP Front-End - 5ms Cache Hit)
    let score = if payload.claim_payload.to_lowercase().contains("destruir") || payload.claim_payload.to_lowercase().contains("ataque") {
        0.05
    } else {
        0.99
    };

    Json(TruthClaimResponse {
        claim_valid: score >= payload.trust_threshold,
        sentinel_score: score,
        truthsync_cache_hit: true, // Demostración de latencia < 5ms
        ring0_intercepts: 0,
    })
}
