mod models;
mod collectors;
mod engine;
mod actions;
mod ebpf_cortex_bridge;
mod mock_kernel;

use collectors::PrometheusCollector;
use engine::PatternDetector;
use engine::resonant_loop::ResonantLoop;
use actions::N8NClient;
use std::time::Duration;
use tokio::sync::mpsc;
use mock_kernel::MockKernelGenerator;
use ebpf_cortex_bridge::CortexEvent;

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
    
    // Auth configuration for N8N
    let n8n_user = std::env::var("N8N_USER").ok();
    let n8n_pass = std::env::var("N8N_PASSWORD").ok();
    let n8n_auth = match (n8n_user, n8n_pass) {
        (Some(u), Some(p)) => Some((u, p)),
        _ => None,
    };

    let mock_mode = std::env::var("KERNEL_MOCK_MODE")
        .unwrap_or_else(|_| "false".to_string())
        .parse::<bool>()
        .unwrap_or(false);
    
    tracing::info!("🧠 Neural Guard Decision Engine starting...");
    tracing::info!("📊 Prometheus URL: {}", prometheus_url);
    tracing::info!("🔗 N8N URL: {}", n8n_url);
    if n8n_auth.is_some() {
        tracing::info!("🔐 N8N Auth: Enabled");
    }

    // Channel for Kernel/Mock Events (High Frequency)
    let (tx, mut rx) = mpsc::channel::<CortexEvent>(1000);

    // 1. Start Kernel Bridge (Real or Phantom)
    if mock_mode {
        tracing::warn!("👻 KERNEL_MOCK_MODE ENABLED: Starting Phantom Generator");
        tokio::spawn(async move {
            let mut generator = MockKernelGenerator::new();
            generator.run(tx).await;
        });
    } else {
        tracing::info!("🛡️  KERNEL MODE: Waiting for eBPF bridge (Not active in this demo)");
        // Here we would spawn the real EbpfBridge
    }

    // 2. Spawn Resonant Heartbeat (Metronome)
    tokio::spawn(async move {
        let mut loop_control = ResonantLoop::new();
        loop {
            // This waits for 17s breath / 68s reset
            let is_reset = loop_control.wait_next_pulse().await;
            if is_reset {
                tracing::info!("🫀 SYSTEM HEARTBEAT: 68s Cycle Complete - Entropy Reset");
            } else {
                tracing::debug!("🫁 SYSTEM BREATH: 17s Sync");
            }
        }
    });

    // 3. Spawn Event Processor (The "Cortex" processing stream)
    tokio::spawn(async move {
        while let Some(event) = rx.recv().await {
            // Process high-frequency events here
            // For now, we just log interesting ones to show it works
            if event.event_type == "EXEC" || event.entropy.stability > 50 {
                tracing::debug!(
                    "⚡ CORTEX EVENT: [{}] PID:{} Stability:{} Payload:{}", 
                    event.event_type, 
                    event.pid, 
                    event.entropy.stability,
                    event.payload
                );
            }
        }
    });
    
    // Initialize components
    let prometheus = PrometheusCollector::new(prometheus_url);
    let detector = PatternDetector::new();
    let n8n = N8NClient::new(n8n_url, n8n_auth);
    
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
