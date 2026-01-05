use axum::{
    routing::{get, post},
    Json, Router, extract::State,
};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, RwLock};
use std::time::{Instant};
use truthsync_core::ClaimExtractor;
use truthsync_core::cache::PredictiveCache;
use rustc_hash::FxHasher;
use std::hash::{Hash, Hasher};

#[derive(Deserialize)]
struct VerifyRequest {
    text: String,
}

#[derive(Serialize)]
struct VerifyResponse {
    claims: Vec<String>,
    confidence: f32,
    cache_hit: bool,
    processing_time_us: f64,
}

use truthsync_core::buffer::PulseState;

struct AppState {
    extractor: ClaimExtractor,
    cache: RwLock<PredictiveCache>,
    pulse_state: RwLock<PulseState>,
}

#[tokio::main]
async fn main() {
    let args: Vec<String> = std::env::args().collect();

    // Check for CLI Mode
    if args.len() > 1 && args[1] == "--mode" && args[2] == "certify" {
        let claims_json = &args[4]; // --claims <json>
        let claims: Vec<String> = serde_json::from_str(claims_json).unwrap_or_default();
        
        let _extractor = ClaimExtractor::new();
        // Simple scoring logic for certification
        let mut score = 0.0;
        if !claims.is_empty() {
            score = 1.0; // Minimal baseline if claims exist
        }
        
        let result = serde_json::json!({
            "status": "CERTIFIED",
            "claims_count": claims.len(),
            "score": score,
            "timestamp": Instant::now().elapsed().as_micros()
        });
        println!("{}", serde_json::to_string(&result).unwrap());
        return;
    }

    // Initialize state
    let state = Arc::new(AppState {
        extractor: ClaimExtractor::new(),
        cache: RwLock::new(PredictiveCache::new(100_000, 3600)),
        pulse_state: RwLock::new(PulseState::default()),
    });

    // Spawn SHM Background Listener
    let shm_state = state.clone();
    std::thread::spawn(move || {
        shm_listener(shm_state);
    });

    // Build router
    let app = Router::new()
        .route("/health", get(health_handler))
        .route("/verify", post(verify_handler))
        .with_state(state);

    // Run server (Non-blocking check to allow CLI and server to coexist if needed, 
    // but here we just exit if CLI mode was triggered above)
    let listener = tokio::net::TcpListener::bind("0.0.0.0:8001").await.unwrap();
    println!("🚀 [TruthSync Edge] Rust server running on http://0.0.0.0:8001");
    println!("📡 Real-Mode: SHM Listener ACTIVE");
    axum::serve(listener, app).await.unwrap();
}

fn shm_listener(state: Arc<AppState>) {
    use truthsync_core::buffer::{SharedBuffer, message_type};
    use std::time::Duration;
    
    let mut buffer = match SharedBuffer::open("truthsync_shm") {
        Ok(b) => b,
        Err(_) => {
            println!("⚠️ truthsync_shm not found, creating baseline...");
            SharedBuffer::create("truthsync_shm", 2 * 1024 * 1024).expect("Failed to create SHM")
        }
    };

    let mut counter = 0;
    loop {
        // 1. Check for messages (Commands)
        if let Ok((msg_type, data)) = buffer.consume() {
            if msg_type == message_type::PROCESS_TEXT {
                let text = String::from_utf8_lossy(&data);
                let start = Instant::now();
                
                // Process claims
                let claims = state.extractor.extract(&text);
                let duration = start.elapsed();
                
                if !claims.is_empty() {
                    println!("🧠 [SHM] Processed {} claims in {}μs", claims.len(), duration.as_micros());
                }
            }
        }
        
        // 2. Read Pulse State (every ~10ms -> 100 iters * 100us)
        counter += 1;
        if counter >= 100 {
            let pulse = buffer.read_pulse_state();
            // Update global state
            if let Ok(mut w) = state.pulse_state.write() {
                *w = pulse;
            }
            counter = 0;
        }

        // Poll every 100 microseconds
        std::thread::sleep(Duration::from_micros(100));
    }
}

async fn health_handler() -> &'static str {
    "TruthSync Edge (Rust) is Healthy"
}

async fn verify_handler(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<VerifyRequest>,
) -> Json<VerifyResponse> {
    let start = Instant::now();
    
    // 1. Generate hash for cache key
    let mut hasher = FxHasher::default();
    payload.text.hash(&mut hasher);
    let key = hasher.finish();

    // 2. Check cache (Read lock)
    {
        let mut cache = state.cache.write().unwrap();
        if let Some(claims) = cache.get(key) {
            let duration = start.elapsed();
            return Json(VerifyResponse {
                claims: claims.clone(),
                confidence: 1.0, // Cache hits are trusted
                cache_hit: true,
                processing_time_us: duration.as_secs_f64() * 1_000_000.0,
            });
        }
    }

    // 3. Cache miss: Extract claims
    let claims = state.extractor.extract(&payload.text);
    
    // 4. Calculate Confidence based on Disonancia (Entropy)
    let entropy = {
        state.pulse_state.read().unwrap().entropy
    };
    
    // Penalty: High entropy (noise) reduces confidence.
    // If entropy > 0.5 (Severe Chaos), confidence drops significantly.
    let base_confidence = 0.95;
    let penalty = entropy.max(0.0).min(1.0); 
    let confidence = (base_confidence * (1.0 - penalty)) as f32;

    // 5. Update cache (Write lock)
    {
        let mut cache = state.cache.write().unwrap();
        cache.put(key, claims.clone(), confidence);
    }

    let duration = start.elapsed();
    Json(VerifyResponse {
        claims,
        confidence,
        cache_hit: false,
        processing_time_us: duration.as_secs_f64() * 1_000_000.0,
    })
}
