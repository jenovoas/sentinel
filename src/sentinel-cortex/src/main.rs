mod models;
mod collectors;
mod engine;
mod actions;
pub mod security;
mod api_server;

use crate::actions::QuantumPulseEmitter;
use collectors::PrometheusCollector;
use engine::PatternDetector;
use actions::N8NClient;
use std::time::Duration;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Setup logging
    tracing_subscriber::fmt()
        .with_env_filter("sentinel_cortex=debug,info")
        .init();
    
    // Load config from .env
    dotenvy::dotenv().ok();
    
    let prometheus_url = std::env::var("PROMETHEUS_URL")
        .unwrap_or_else(|_| "http://prometheus:9090".to_string());
    let n8n_url = std::env::var("N8N_URL")
        .unwrap_or_else(|_| "http://n8n-security:5678".to_string());
    let redis_url = std::env::var("REDIS_URL")
        .unwrap_or_else(|_| "redis://redis:6379".to_string());
    
    tracing::info!("🧠 Neural Guard Decision Engine starting...");
    tracing::info!("📊 Prometheus URL: {}", prometheus_url);
    tracing::info!("🔗 N8N URL: {}", n8n_url);
    tracing::info!("⚡ EventBus URL: {}", redis_url);
    tracing::info!("⚡ EventBus URL: {}", redis_url); // Keep this logging line
    
    // Initialize components
    let prometheus = PrometheusCollector::new(prometheus_url);
    let detector = PatternDetector::new();
    let n8n = N8NClient::new(n8n_url);
    
    // --- QUANTUM PULSE EMITTER ---
    let quantum_emitter: Option<QuantumPulseEmitter> = match std::env::var("REDIS_URL") {
        Ok(url) => {
            // The previous logging line for EventBus URL is kept above.
            // tracing::info!("⚡ EventBus URL: {}", url); // This line is redundant if redis_url is logged above
            match QuantumPulseEmitter::new(&url) {
                Ok(emitter) => {
                    tracing::info!("✅ Quantum Pulse Emitter connected");
                    Some(emitter)
                },
                Err(e) => {
                    tracing::error!("❌ Failed to connect Quantum Pulse: {}", e);
                    None
                }
            }
        },
        Err(_) => {
            tracing::warn!("⚠️ REDIS_URL not set. Quantum Pulse disabled.");
            None
        }
    };

    // --- SOUL VERIFIER API ---
    tokio::spawn(async {
        api_server::start_api_server().await;
    });

    tracing::info!("✅ Neural Guard started successfully");
    
    // Main loop: collect → detect → act
    let mut iteration = 0;
    loop {
        iteration += 1;
        tracing::debug!("🔄 Iteration {} - Collecting events...", iteration);
        
        // Collect events from Prometheus
        match prometheus.collect().await {
            Ok(events) => {
                tracing::info!("📊 Collected {} events", events.len());
                
                // Detect patterns
                let patterns = detector.detect(&events);

                // --- QUANTUM PULSE EMISSION ---
                if let Some(emitter) = &quantum_emitter {
                    // Disonancia = Raw event count (Background noise)
                    // Axiones = Detected patterns (Meaningful signal)
                    let disonancia = events.len() as f64;
                    let axiones = patterns.len() as u32;

                    if let Err(e) = emitter.emit_signal(disonancia, axiones).await {
                        tracing::error!("⚡ Failed to emit quantum signal: {}", e);
                    }
                }
                // ------------------------------
                
                if !patterns.is_empty() {
                    tracing::warn!("🚨 Detected {} patterns", patterns.len());
                    
                    // Trigger playbooks for detected patterns
                    for pattern in patterns {
                        tracing::warn!(
                            "⚠️  Pattern: {} (confidence: {:.2})",
                            pattern.name,
                            pattern.confidence
                        );
                        
                        // Only trigger if confidence > 0.7
                        if pattern.confidence > 0.7 {
                            if let Err(e) = n8n.trigger_playbook(&pattern).await {
                                tracing::error!("❌ Failed to trigger playbook: {}", e);
                            }
                        } else {
                            tracing::info!("ℹ️  Skipping playbook (low confidence)");
                        }
                    }
                } else {
                    tracing::debug!("✓ No patterns detected");
                }
            }
            Err(e) => {
                tracing::error!("❌ Failed to collect events: {}", e);
            }
        }
        
        // Wait 30 seconds before next iteration
        tokio::time::sleep(Duration::from_secs(30)).await;
    }
}

