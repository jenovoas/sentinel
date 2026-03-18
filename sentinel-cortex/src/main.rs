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

use axum::{routing::get, Json, Router};
use math::harmonic_logic::{HarmonicProcessor, HarmonicState};
use security::bio_resonance::ResonanceEngine;
use security::soul_verifier_s60_production::BiometricVerifier;
use serde::Serialize;
use std::sync::{Arc, Mutex};
use std::{net::SocketAddr, time::Duration};
use tokio::time::sleep;

#[derive(Serialize)]
struct HealthStatus {
    status: String,
    version: String,
    resonance_coherence: i64,
}

struct AppState {
    resonance: Arc<Mutex<ResonanceEngine>>,
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
    let state = Arc::new(AppState {
        resonance: resonance.clone(),
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

            if tick % 17 == 0 {
                let mut res = resonance_task.lock().unwrap();
                let (valid, coherence) = res.verify_pulse(tick);
                tracing::info!(
                    "PULSE (T={}): Valid={}, Coherence={:?}",
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

    // 2. Setup Axum Router
    let app = Router::new()
        .route("/health", get(health_handler))
        .layer(tower_http::trace::TraceLayer::new_for_http())
        .with_state(state);

    // 3. Start Server
    let addr = SocketAddr::from(([0, 0, 0, 0], 8000));
    tracing::info!("Listening on {}", addr);
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn health_handler(
    axum::extract::State(state): axum::extract::State<Arc<AppState>>,
) -> Json<HealthStatus> {
    let res = state.resonance.lock().unwrap();
    Json(HealthStatus {
        status: "OK".to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        resonance_coherence: res.get_coherence_raw(),
    })
}
