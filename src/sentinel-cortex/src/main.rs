mod models;
mod collectors;
mod engine;
mod actions;
pub mod security;
pub mod monitoring;
mod api_server;
mod math;

use crate::actions::QuantumPulseEmitter;
use collectors::PrometheusCollector;
use engine::{PatternDetector, FluidController, FlowScale, SemanticFirewall};
use actions::N8NClient;
use collectors::redis_subscriber::{RedisSubscriber, QuantumEvent};
use tokio::sync::mpsc;
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
    
    // --- BUFFER DE TELEMETRÍA (MPSC) ---
    let buffer_capacity = 1024;
    let (tx_events, mut rx_events) = mpsc::channel::<QuantumEvent>(buffer_capacity);
    let mut fluid_ctrl = FluidController::new(buffer_capacity);
    let semantic_firewall = SemanticFirewall::new();
    
    // Lanzar suscriptor de Redis en background
    let redis_url_clone = redis_url.clone();
    tokio::spawn(async move {
        let redis_sub = RedisSubscriber::new(&redis_url_clone, "quantum_signals");
        if let Err(e) = redis_sub.start(tx_events).await {
            tracing::error!("❌ Error en el suscriptor de Redis: {}", e);
        }
    });

    // --- QUANTUM PULSE EMITTER ---
    let quantum_emitter: Option<QuantumPulseEmitter> = match std::env::var("REDIS_URL") {
        Ok(url) => {
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

    tracing::info!("✅ Neural Guard started successfully (Fluid Mode)");
    
    // --- MAIN LOOP ---
    let mut iteration = 0;
    loop {
        iteration += 1;
        let start_time = std::time::Instant::now();
        
        // 1. DRENAJE FLUIDO (Dynamic Buffering)
        let batch_size = fluid_ctrl.get_batch_size();
        
        let mut ebpf_signals = Vec::new();
        for _ in 0..batch_size {
            match rx_events.try_recv() {
                Ok(mut event) => {
                    // Sanitización Semántica (AIOpsShield)
                    let (sanitized_raw, is_malicious) = semantic_firewall.sanitize(&event.raw_event);
                    if is_malicious {
                        tracing::warn!("🛡️  Ignorando señal del Kernel por riesgo semántico: {}", event.source);
                        continue;
                    }
                    event.raw_event = sanitized_raw;
                    ebpf_signals.push(event);
                },
                Err(_) => break,
            }
        }
        
        // Medir latencia de procesamiento de este batch
        let processing_latency_ms = start_time.elapsed().as_secs_f64() * 1000.0;
        
        // Ajustamos la escala basada en cuántos procesamos realmente Y la latencia medida
        let scale = fluid_ctrl.observe(ebpf_signals.len(), processing_latency_ms);
        
        if !ebpf_signals.is_empty() {
            tracing::info!(
                "🌊 Flujo {:?}: Procesando batch de {} señales (Latencia: {:.2}ms)", 
                scale, 
                ebpf_signals.len(),
                processing_latency_ms
            );
        }

        // 2. Colectar Prometheus (Gating Sexagesimal)
        // En modo Laminar colectamos siempre, en FlashFlood priorizamos telemetría crítica.
        // Gating: Cada 6 iteraciones (1/10 de 60) para mantener armonía.
        let should_collect_metrics = iteration % 6 == 0 || scale == FlowScale::Laminar;
        
        if should_collect_metrics {
            match prometheus.collect().await {
                Ok(events) => {
                    let patterns = detector.detect(&events);
                    
                    if let Some(emitter) = &quantum_emitter {
                        // Disonancia armonizada f64 (Final Physical Layer)
                        let disonancia = events.len() as f64 + ebpf_signals.iter().map(|s| s.disonancia).sum::<f64>();
                        let axiones = patterns.len() as u32;
                        let _ = emitter.emit_signal(disonancia, axiones).await;
                    }
                    
                    for pattern in patterns {
                        // Umbral de Confianza Soberana: 42/60 (0.7)
                        if pattern.confidence > (42.0 / 60.0) {
                            let _ = n8n.trigger_playbook(&pattern).await;
                        }
                    }
                }
                Err(e) => tracing::error!("❌ Prometheus error: {}", e),
            }
        }
        
        // 3. Sleep Adaptativo (Backpressure / Fluidity S60)
        tokio::time::sleep(fluid_ctrl.get_sleep_duration()).await;
    }
}

