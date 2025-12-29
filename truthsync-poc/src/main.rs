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

struct AppState {
    extractor: ClaimExtractor,
    cache: RwLock<PredictiveCache>,
}

#[tokio::main]
async fn main() {
    // Initialize state
    let state = Arc::new(AppState {
        extractor: ClaimExtractor::new(),
        cache: RwLock::new(PredictiveCache::new(100_000, 3600)),
    });

    // Build router
    let app = Router::new()
        .route("/health", get(health_handler))
        .route("/verify", post(verify_handler))
        .with_state(state);

    // Run server
    let listener = tokio::net::TcpListener::bind("0.0.0.0:8001").await.unwrap();
    println!("🚀 [TruthSync Edge] Rust server running on http://0.0.0.0:8001");
    axum::serve(listener, app).await.unwrap();
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
                confidence: 1.0,
                cache_hit: true,
                processing_time_us: duration.as_secs_f64() * 1_000_000.0,
            });
        }
    }

    // 3. Cache miss: Extract claims
    let claims = state.extractor.extract(&payload.text);
    let confidence = 0.95; // Fixed for now

    // 4. Update cache (Write lock)
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
