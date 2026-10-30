// Autor: Jaime Novoa Sepúlveda — Sentinel security gateway for Marte.
// Guardian Alpha (eBPF) → AIOpsShield/TelemetrySanitizer → forensic WAL → Cortex/Fenix.

use axum::extract::{DefaultBodyLimit, State};
use axum::http::{header, HeaderMap, StatusCode};
use axum::routing::{get, post};
use axum::{Json, Router};
use sentinel_cortex::ebpf_cortex_bridge::{CortexEvent, EbpfBridge};
use sentinel_cortex::security::telemetry_sanitizer::TelemetrySanitizer;
use sentinel_cortex::security::{AIOpsSemanticFirewall, DataLane, ForensicWal};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha3::{Digest, Sha3_256};
use std::collections::BTreeSet;
use std::env;
use std::net::SocketAddr;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::mpsc;
use tracing::{error, info, warn};

const DEFAULT_BIND: &str = "10.88.0.6:8090";
const DEFAULT_RINGBUF: &str = "/sys/fs/bpf/guardian_alpha/events";
const DEFAULT_BACKEND_URL: &str = "http://10.88.0.1:8000/api/v1/cortex/events";
const DEFAULT_WAL: &str = "/var/log/sentinel/guardian_security_wal.jsonl";
const MAX_BODY_BYTES: usize = 65_536;

#[derive(Clone)]
struct GatewayState {
    shield_token: Arc<str>,
    backend_url: Arc<str>,
    backend_token: Arc<str>,
    client: reqwest::Client,
    wal: Arc<ForensicWal>,
    requests_total: Arc<AtomicU64>,
    blocked_total: Arc<AtomicU64>,
    forwarded_total: Arc<AtomicU64>,
    forward_errors_total: Arc<AtomicU64>,
    ring_drops_total: Arc<AtomicU64>,
}

#[derive(Debug, Deserialize)]
struct SanitizeRequest {
    source: String,
    record: Value,
}

#[derive(Debug, Serialize)]
struct SanitizeResponse {
    event_id: String,
    safe: bool,
    categories: Vec<String>,
    record_sha3_256: String,
    sanitized_record: Value,
}

fn required_env(name: &str) -> anyhow::Result<String> {
    let value = env::var(name)?;
    if value.trim().is_empty() {
        anyhow::bail!("{name} must not be empty");
    }
    Ok(value)
}

fn constant_time_equal(left: &[u8], right: &[u8]) -> bool {
    let max_len = left.len().max(right.len());
    let mut difference = left.len() ^ right.len();
    for index in 0..max_len {
        let a = left.get(index).copied().unwrap_or(0);
        let b = right.get(index).copied().unwrap_or(0);
        difference |= usize::from(a ^ b);
    }
    difference == 0
}

fn valid_source(source: &str) -> bool {
    !source.is_empty()
        && source.len() <= 64
        && source
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || b"._:-".contains(&byte))
}

fn sanitize_strings(
    value: &mut Value,
    firewall: &AIOpsSemanticFirewall,
    sanitizer: &TelemetrySanitizer,
    categories: &mut BTreeSet<String>,
) {
    match value {
        Value::String(text) => {
            let semantic_detections = firewall.inspect(text);
            let generic_result = sanitizer.sanitize_prompt(text);
            if !semantic_detections.is_empty() || !generic_result.is_safe {
                for detection in &semantic_detections {
                    categories.insert(detection.injection_type.as_str().to_string());
                }
                for pattern in generic_result.blocked_patterns {
                    categories.insert(format!("telemetry:{pattern}"));
                }

                if !semantic_detections.is_empty() {
                    let (redacted, _) = firewall.sanitize(text);
                    *text = redacted;
                } else {
                    *text = "[REDACTED_BY_TELEMETRY_SANITIZER]".to_string();
                }
            }
        }
        Value::Array(items) => {
            for item in items {
                sanitize_strings(item, firewall, sanitizer, categories);
            }
        }
        Value::Object(fields) => {
            for item in fields.values_mut() {
                sanitize_strings(item, firewall, sanitizer, categories);
            }
        }
        _ => {}
    }
}

fn sanitize_record(mut record: Value) -> (Value, Vec<String>, String) {
    let original = serde_json::to_vec(&record).unwrap_or_default();
    let digest = hex::encode(Sha3_256::digest(original));
    let mut categories = BTreeSet::new();
    sanitize_strings(
        &mut record,
        &AIOpsSemanticFirewall::new(),
        &TelemetrySanitizer::new(true),
        &mut categories,
    );
    (record, categories.into_iter().collect(), digest)
}

fn authorized(headers: &HeaderMap, expected: &str) -> bool {
    let Some(value) = headers.get(header::AUTHORIZATION) else {
        return false;
    };
    let Ok(value) = value.to_str() else {
        return false;
    };
    let Some(provided) = value.strip_prefix("Bearer ") else {
        return false;
    };
    constant_time_equal(provided.as_bytes(), expected.as_bytes())
}

async fn health() -> Json<Value> {
    Json(json!({"status":"healthy","service":"sentinel-security-gateway","node":"marte"}))
}

async fn metrics(State(state): State<GatewayState>) -> String {
    format!(
        "# TYPE sentinel_aiops_shield_requests_total counter\nsentinel_aiops_shield_requests_total {}\n# TYPE sentinel_aiops_shield_blocked_total counter\nsentinel_aiops_shield_blocked_total {}\n# TYPE sentinel_guardian_forwarded_total counter\nsentinel_guardian_forwarded_total {}\n# TYPE sentinel_guardian_forward_errors_total counter\nsentinel_guardian_forward_errors_total {}\n# TYPE sentinel_guardian_ring_drops_total counter\nsentinel_guardian_ring_drops_total {}\n",
        state.requests_total.load(Ordering::Relaxed),
        state.blocked_total.load(Ordering::Relaxed),
        state.forwarded_total.load(Ordering::Relaxed),
        state.forward_errors_total.load(Ordering::Relaxed),
        state.ring_drops_total.load(Ordering::Relaxed),
    )
}

async fn sanitize(
    State(state): State<GatewayState>,
    headers: HeaderMap,
    Json(request): Json<SanitizeRequest>,
) -> (StatusCode, Json<Value>) {
    if !authorized(&headers, &state.shield_token) {
        return (
            StatusCode::UNAUTHORIZED,
            Json(json!({"error":"unauthorized"})),
        );
    }
    state.requests_total.fetch_add(1, Ordering::Relaxed);
    if !valid_source(&request.source) || !request.record.is_object() {
        return (
            StatusCode::BAD_REQUEST,
            Json(json!({"error":"source must be a short identifier and record must be an object"})),
        );
    }

    let (sanitized_record, categories, digest) = sanitize_record(request.record);
    let safe = categories.is_empty();
    let event_id = uuid::Uuid::new_v4().to_string();

    if !safe {
        state.blocked_total.fetch_add(1, Ordering::Relaxed);
        let evidence = json!({
            "source": request.source,
            "record_sha3_256": digest,
            "categories": categories,
        });
        let payload = match serde_json::to_string(&evidence) {
            Ok(payload) => payload,
            Err(_) => {
                return (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(json!({"error":"evidence serialization failed"})),
                );
            }
        };
        if state
            .wal
            .append(&event_id, "aiops_shield", &payload, DataLane::Security)
            .is_err()
        {
            error!("AIOpsShield could not persist a blocked telemetry record");
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(json!({"error":"forensic WAL unavailable"})),
            );
        }
    }

    let response = SanitizeResponse {
        event_id,
        safe,
        categories,
        record_sha3_256: digest,
        sanitized_record,
    };
    (StatusCode::OK, Json(json!(response)))
}

fn start_ring_reader(
    path: String,
    tx: mpsc::Sender<CortexEvent>,
    ring_drops_total: Arc<AtomicU64>,
) {
    tokio::task::spawn_blocking(move || loop {
        let map = match libbpf_rs::MapHandle::from_pinned_path(&path) {
            Ok(map) => map,
            Err(error) => {
                warn!("Guardian ring map unavailable at configured pin: {error}");
                std::thread::sleep(Duration::from_secs(2));
                continue;
            }
        };

        let mut builder = libbpf_rs::RingBufferBuilder::new();
        let tx = tx.clone();
        let drops = ring_drops_total.clone();
        if let Err(error) = builder.add(&map, move |data: &[u8]| -> i32 {
            if let Some(event) = EbpfBridge::parse_event(data) {
                if tx.try_send(event).is_err() {
                    drops.fetch_add(1, Ordering::Relaxed);
                }
            }
            0
        }) {
            warn!("Could not attach userspace reader to Guardian ring map: {error}");
            std::thread::sleep(Duration::from_secs(2));
            continue;
        }

        match builder.build() {
            Ok(ring) => {
                info!("Guardian Alpha ring buffer reader connected at configured pin");
                loop {
                    if let Err(error) = ring.poll(Duration::from_millis(100)) {
                        warn!("Guardian ring poll failed; reconnecting: {error}");
                        break;
                    }
                }
            }
            Err(error) => {
                warn!("Could not build Guardian ring reader: {error}");
                std::thread::sleep(Duration::from_secs(2));
            }
        }
    });
}

async fn forward_event(state: &GatewayState, event: CortexEvent) {
    let event_id = format!(
        "guardian-alpha-{}-{}-{}",
        event.timestamp_ns, event.pid, event.event_type
    );
    let raw = match serde_json::to_value(&event) {
        Ok(value) => value,
        Err(error) => {
            error!("Could not serialize Guardian event: {error}");
            return;
        }
    };
    let (sanitized, categories, digest) = sanitize_record(raw);
    if !categories.is_empty() {
        let evidence = json!({"record_sha3_256":digest,"categories":categories});
        if let Ok(payload) = serde_json::to_string(&evidence) {
            if state
                .wal
                .append(&event_id, "aiops_shield", &payload, DataLane::Security)
                .is_err()
            {
                error!("Blocked Guardian event could not be written to forensic WAL");
            }
        }
        return;
    }

    let payload = json!({
        "event_type": event.event_type,
        "source": "guardian_alpha",
        "data": sanitized,
    });
    let serialized = match serde_json::to_string(&payload) {
        Ok(value) => value,
        Err(error) => {
            error!("Could not serialize sanitized Guardian event: {error}");
            return;
        }
    };
    if state
        .wal
        .append(&event_id, "guardian_alpha", &serialized, DataLane::Security)
        .is_err()
    {
        error!("Guardian event withheld because forensic WAL append failed");
        return;
    }

    let mut delay = Duration::from_secs(1);
    loop {
        let result = state
            .client
            .post(state.backend_url.as_ref())
            .header("X-Sentinel-Token", state.backend_token.as_ref())
            .header("Idempotency-Key", &event_id)
            .json(&payload)
            .send()
            .await;
        match result {
            Ok(response) if response.status().is_success() => {
                state.forwarded_total.fetch_add(1, Ordering::Relaxed);
                return;
            }
            Ok(response) => {
                state.forward_errors_total.fetch_add(1, Ordering::Relaxed);
                warn!(
                    "Fenix rejected Guardian event with HTTP {}; retrying",
                    response.status()
                );
            }
            Err(error) => {
                state.forward_errors_total.fetch_add(1, Ordering::Relaxed);
                warn!("Fenix event transport failed; retrying: {error}");
            }
        }
        tokio::time::sleep(delay).await;
        delay = (delay * 2).min(Duration::from_secs(30));
    }
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| tracing_subscriber::EnvFilter::new("info")),
        )
        .init();

    let bind: SocketAddr = env::var("AIOPS_SHIELD_BIND")
        .unwrap_or_else(|_| DEFAULT_BIND.to_string())
        .parse()?;
    let ring_path = env::var("EBPF_EVENTS_PATH").unwrap_or_else(|_| DEFAULT_RINGBUF.to_string());
    std::fs::metadata(&ring_path)?;
    let backend_url =
        env::var("SENTINEL_BACKEND_URL").unwrap_or_else(|_| DEFAULT_BACKEND_URL.to_string());
    let shield_token = required_env("AIOPS_SHIELD_TOKEN")?;
    let backend_token = required_env("SENTINEL_TELEMETRY_TOKEN")?;
    let wal_key = hex::decode(required_env("SENTINEL_WAL_KEY_HEX")?)?;
    if wal_key.len() < 32 {
        anyhow::bail!("SENTINEL_WAL_KEY_HEX must decode to at least 32 bytes");
    }
    let wal_path =
        env::var("SENTINEL_SECURITY_WAL_PATH").unwrap_or_else(|_| DEFAULT_WAL.to_string());
    let wal = Arc::new(ForensicWal::new(wal_path, &wal_key)?);

    let client = reqwest::Client::builder()
        .connect_timeout(Duration::from_secs(3))
        .timeout(Duration::from_secs(10))
        .build()?;
    let state = GatewayState {
        shield_token: shield_token.into(),
        backend_url: backend_url.into(),
        backend_token: backend_token.into(),
        client,
        wal,
        requests_total: Arc::new(AtomicU64::new(0)),
        blocked_total: Arc::new(AtomicU64::new(0)),
        forwarded_total: Arc::new(AtomicU64::new(0)),
        forward_errors_total: Arc::new(AtomicU64::new(0)),
        ring_drops_total: Arc::new(AtomicU64::new(0)),
    };

    let (tx, mut rx) = mpsc::channel::<CortexEvent>(1024);
    start_ring_reader(ring_path, tx, state.ring_drops_total.clone());
    let forwarding_state = state.clone();
    tokio::spawn(async move {
        while let Some(event) = rx.recv().await {
            forward_event(&forwarding_state, event).await;
        }
    });

    let app = Router::new()
        .route("/health", get(health))
        .route("/metrics", get(metrics))
        .route("/api/v1/aiops/sanitize", post(sanitize))
        .layer(DefaultBodyLimit::max(MAX_BODY_BYTES))
        .with_state(state);
    let listener = tokio::net::TcpListener::bind(bind).await?;
    info!("Sentinel security gateway listening on configured private address");
    axum::serve(listener, app).await?;
    Ok(())
}
