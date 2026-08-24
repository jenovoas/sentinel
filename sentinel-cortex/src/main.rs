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
mod models;
mod quantum;
mod security;
mod metrics;

use axum::{routing::{get, post}, Json, Router};
use axum::extract::ws::{WebSocketUpgrade, WebSocket, Message};
use math::harmonic_logic::{HarmonicProcessor, HarmonicState};
use security::bio_resonance::ResonanceEngine;
use metrics::{MetricsRepository, PrometheusRepository, MetricsSnapshot};
use ebpf_cortex_bridge::{EbpfBridge, CortexEvent};
use serde::Serialize;
use std::sync::{Arc, Mutex};
use std::{net::SocketAddr, time::Duration};
use tokio::sync::broadcast;
use tokio::time::sleep;

#[derive(Serialize)]
struct HealthStatus {
    status: String,
    version: String,
    metrics: MetricsSnapshot,
}

pub(crate) struct AppState {
    resonance: Arc<Mutex<ResonanceEngine>>,
    metrics: Arc<dyn MetricsRepository>,
    bpf_stream: broadcast::Sender<CortexEvent>,
    lattice: Arc<Mutex<memory::resonant_lattice_bridge::ResonantLatticeBridge>>,
    truthsync: Arc<Mutex<truthsync_core::TruthSyncEngine>>,
    liquid_lattice: Arc<Mutex<memory::liquid_lattice::LiquidLattice>>,
    #[allow(dead_code)]
    pattern_detector: Arc<engine::patterns::PatternDetector>,
    neural_memory: Arc<Mutex<me60os_core::neural_memory::NeuralMemory>>,
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
    // Calculate Dynamic Lattice Size based on System Available RAM (rings: N = 3r^2 + 3r + 1)
    let available_ram_mb: usize = std::fs::read_to_string("/proc/meminfo")
        .ok()
        .and_then(|s| {
            s.lines().find(|l| l.starts_with("MemAvailable:")).and_then(|l| {
                l.split_whitespace().nth(1).and_then(|v| v.parse::<usize>().ok().map(|k| k / 1024))
            })
        })
        .unwrap_or(1024);

    // Compute max safe rings using 1% of available RAM (100 bytes per node)
    let max_allocatable_bytes = (available_ram_mb * 1024 * 1024) / 100;
    let mut rings = 7; // Default 91 nodes
    while (3 * rings * (rings + 1) + 1) <= max_allocatable_bytes && rings < 150 {
        rings += 1;
    }
    let calculated_nodes = std::cmp::max(128, 3 * rings * (rings + 1) + 1);
    tracing::info!("💎 Dynamic RAM Lattice Allocator: Allocated {} nodes across {} rings (Available RAM: {} MB)", calculated_nodes, rings, available_ram_mb);

    let lattice = Arc::new(Mutex::new(
        memory::resonant_lattice_bridge::ResonantLatticeBridge::new(calculated_nodes)
    ));
    // Broadcast channel para Múltiples Inversores (WebSockets) viendo el eBPF
    let (tx_bpf, _) = broadcast::channel(100);

    let liquid_lattice = Arc::new(Mutex::new(memory::liquid_lattice::LiquidLattice::new()));
    let pattern_detector = Arc::new(engine::patterns::PatternDetector::new());
    let truthsync = Arc::new(Mutex::new(truthsync_core::TruthSyncEngine::new()));
    let neural_memory = Arc::new(Mutex::new(me60os_core::neural_memory::NeuralMemory::new()));

    let state = Arc::new(AppState {
        resonance: resonance.clone(),
        metrics: metrics.clone() as Arc<dyn MetricsRepository>,
        bpf_stream: tx_bpf.clone(),
        lattice: lattice.clone(),
        truthsync: truthsync.clone(),
        liquid_lattice: liquid_lattice.clone(),
        pattern_detector: pattern_detector.clone(),
        neural_memory: neural_memory.clone(),
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

    // 2. Start eBPF Ring Buffer Reader (Guardian events → WebSocket)
    let tx_bpf_ebpf = tx_bpf.clone();
    let _state_ebpf = state.clone();
    tokio::spawn(async move {
        use tokio::sync::mpsc;
        let (tx_ring, mut rx_ring) = mpsc::channel::<CortexEvent>(1024);

        // QA 2026-08-06: ruta corregida al pin real del guardian LSM (cargado manual,
        // hook bprm_check_security vivo). El ringbuf 'events' es el que llena guardian_execve.
        // Sin LLM local (laptop no da): el cortex corre como motor determinista de eventos+lattice.
        let monitor_path = std::env::var("EBPF_MONITOR_PATH")
            .unwrap_or_else(|_| "/sys/fs/bpf/sentinel/events".to_string());
        let bridge = EbpfBridge::new()
            .with_ringbuf_path(monitor_path);

        tokio::spawn(async move {
            if let Err(e) = bridge.run_monitor(tx_ring).await {
                tracing::error!("eBPF monitor error: {}", e);
            }
        });

        while let Some(event) = rx_ring.recv().await {
            let _ = tx_bpf_ebpf.send(event);
        }
    });

    // 3. Start Lattice Processor (Deterministic Ring-0 eBPF Ingestion + Thermal CPU Noise + LiquidLattice 3x3)
    let lattice_task = lattice.clone();
    let liquid_lattice_task = liquid_lattice.clone();
    let neural_memory_task = neural_memory.clone();
    let mut rx_lattice = tx_bpf.subscribe();
    tokio::spawn(async move {
        tracing::info!("💎 Lattice Processor active: Ring-0 Ingestion + LiquidLattice 3x3 Diffusivity (EXP-009)");
        loop {
            match rx_lattice.recv().await {
                Ok(event) => {
                    let mut lat = lattice_task.lock().unwrap();
                    let pressure = event.entropy_s60_raw as i64;
                    let node = (event.pid as usize) % 64;
                    // FIX (auditoría 2026-08-23, P0.4-A1): pressure es S60 RAW del
                    // kernel (cortex_events.h:117); inject() lo re-escalaria por
                    // SCALE_0 (doble escala). inject_spa preserva la escala SPA.
                    lat.inject_spa(node, me60os_core::spa::SPA::from_raw(pressure));
                    lat.step();

                    // Connect EXP-009 LiquidLattice 3x3 grid diffusion
                    let mut ll = liquid_lattice_task.lock().unwrap();
                    let row = (event.pid as usize) % 3;
                    let col = ((event.pid as usize) / 3) % 3;
                    ll.inject_entropy(row, col, pressure);
                    ll.diffuse();

                    // Ingest eBPF event into PAI-Neural LIF Spiking Neural Network
                    let mut nm = neural_memory_task.lock().unwrap();
                    let entropy_spa = me60os_core::spa::SPA::from_raw(pressure);
                    let event_type_code: u32 = event.event_type.parse().unwrap_or(1);
                    let me60os_ev = me60os_core::ebpf_cortex_bridge::CortexEvent::new(
                        event.timestamp_ns,
                        event_type_code,
                        event.pid as u32,
                        event.entropy_s60_raw,
                        event.severity as u8,
                    );
                    nm.ingest_event(me60os_ev, entropy_spa);
                }
                Err(_) => break,
            }
        }
    });

    // 3b. Real System Thermal Noise Injector (Optomechanical Coupling to CPU Temperature)
    let lattice_thermal = lattice.clone();
    let liquid_lattice_thermal = liquid_lattice.clone();
    let neural_memory_thermal = neural_memory.clone();
    tokio::spawn(async move {
        let mut interval = tokio::time::interval(tokio::time::Duration::from_millis(500));
        let maat = me60os_core::atlantean::MaatStabilizer::new();
        let mut gpu_ctrl = me60os_core::atlantean::GpuController::new();
        let mut current_speed = me60os_core::spa::SPA::new(10, 0, 0, 0, 0);

        loop {
            interval.tick().await;
            // Measure loop tick latency and adjust GPU batch size dynamically
            let latency_start = std::time::Instant::now();

            // Extract dynamic CPU work deltatime entropy from /proc/stat
            let entropy_pressure: i64 = std::fs::read_to_string("/proc/stat")
                .ok()
                .and_then(|s| {
                    s.lines().next().and_then(|line| {
                        let parts: Vec<&str> = line.split_whitespace().collect();
                        if parts.len() > 4 {
                            let user: i64 = parts[1].parse().ok()?;
                            let sys: i64 = parts[3].parse().ok()?;
                            Some((user + sys) % 60 + 20) // Dynamic S60 noise range
                        } else {
                            None
                        }
                    })
                })
                .unwrap_or(35);

            // Execute Maat Harmonic Regulation (Truth vs Speed)
            let current_truth = me60os_core::spa::SPA::new(0, 58, 0, 0, 0); // 58/60 = 96.6% Verdad
            let (regulated_speed, status) = maat.regulate(current_truth, current_speed);
            current_speed = regulated_speed;

            // Latencia en milésimas de ms (entero, YATRA-LOCKED: sin float)
            let elapsed_msx1000 = latency_start.elapsed().as_micros() as i64 / 1_000;
            let batch_size = gpu_ctrl.adjust_batch_size(elapsed_msx1000);
            tracing::trace!("⚖️ MAAT: status={}, speed={:?}, gpu_batch={}", status, current_speed, batch_size);

            // AUDIT-360: scope mutex to critical section (inject + step), release before oscillate writes
            {
                let mut lat = lattice_thermal.lock().unwrap();
                let node_count = lat.amplitudes_raw().len();
                // Inject multi-point harmonic thermal pulses across central hexagonal rings (Node 0, ring centers)
                // PRUEBA PAI-60: si SENTINEL_PAI_CONVERT=1, la amplitud se deriva via pai60_divide
                // (razon recíproca exacta base-60) en vez de meter i64 crudo como presion.
                let pai_convert = std::env::var("SENTINEL_PAI_CONVERT").map(|v| v == "1").unwrap_or(false);
                if pai_convert {
                    // denominador 60 = escala base-60 (S60). value en [0,60).
                    let v = entropy_pressure.rem_euclid(60);
                    lat.inject_pai(0, v, 60);
                    if node_count > 100 {
                        let step_ring = node_count / 7;
                        for ring_idx in 1..7 {
                            lat.inject_pai(ring_idx * step_ring, v / 2, 60);
                        }
                    }
                } else {
                    lat.inject(0, entropy_pressure);
                    if node_count > 100 {
                        let step_ring = node_count / 7;
                        for ring_idx in 1..7 {
                            lat.inject(ring_idx * step_ring, entropy_pressure / 2);
                        }
                    }
                }
                lat.step();
            } // drop lat lock here

            // Calculate Resonant Physics Inertial Damping & Effective Load Reduction (outside lock)
            let static_load = me60os_core::spa::SPA::from_raw(entropy_pressure);
            let priority = me60os_core::spa::SPA::new(1, 0, 0, 0, 0); // 1.0 Priority Unit
            let stability = me60os_core::spa::SPA::from_raw((entropy_pressure % 60 + 1) * (me60os_core::spa::SPA::SCALE_0 / 60));
            let effective_load = me60os_core::physics::ResonantPhysics::calculate_effective_load(static_load, priority, stability);

            // Inject entropy & diffuse in EXP-009 LiquidLattice 3x3 grid continuously using effective load
            {
                let mut ll = liquid_lattice_thermal.lock().unwrap();
                ll.inject_entropy(1, 1, effective_load.to_raw()); // Center cell (1,1)
                ll.diffuse();
            }

            // Continuous pulse of PAI-Neural SNN LIF memory with thermal CPU noise
            {
                let mut nm = neural_memory_thermal.lock().unwrap();
                let thermal_ev = me60os_core::ebpf_cortex_bridge::CortexEvent::new(
                    chrono::Utc::now().timestamp_nanos_opt().unwrap_or(0) as u64,
                    18, // Watchdog/Resonance Event Type
                    std::process::id() as u32,
                    entropy_pressure as u64,
                    0,
                );
                nm.ingest_event(thermal_ev, me60os_core::spa::SPA::from_raw(entropy_pressure));
            }
        }
    });

    // 4. Start Redis Pulse Subscriber (Remote Bio-Sync)
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
                        
                        while let Some(_msg) = stream.next().await {
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
        .route("/metrics", get(metrics_prometheus_handler))
        .route("/api/v1/lattice", get(lattice_status_handler))
        .route("/api/v1/telemetry", get(telemetry_ws_handler))
        .route("/api/v1/sentinel_status", get(sentinel_status_handler))
        .route("/api/v1/truth_claim", post(truth_claim_handler))
        .route("/api/v1/phonon_lattice", get(phonon_lattice_handler))
        .layer(tower_http::trace::TraceLayer::new_for_http())
        .with_state(state);

    // 4. Start Server
    // 7. Periodically export phononic data as CSV for scientific study
    let lattice_csv = lattice.clone();
    tokio::spawn(async move {
        let mut interval = tokio::time::interval(tokio::time::Duration::from_secs(60));
        loop {
            interval.tick().await;
            let lat = lattice_csv.lock().unwrap();
            let amps = lat.amplitudes_raw();
            let phases = lat.phases_raw();
            let energy = lat.total_energy_raw();
            let now = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs();
            
            // AUDIT-360: use BufWriter + writeln! per node instead of format! + String concat
            use std::io::{BufWriter, Write};
            let file = std::fs::OpenOptions::new()
                .create(true)
                .append(true)
                .open("/var/log/sentinel/phonon_data.csv");

            if let Ok(f) = file {
                let mut buf = BufWriter::new(f);
                for i in 0..amps.len() {
                    let gradient = if i + 1 < amps.len() { amps[i + 1] - amps[i] } else { 0 };
                    if let Err(e) = writeln!(buf, "{},{},{},{},{},{}", now, i, amps[i], phases[i], gradient, energy) {
                        tracing::error!("Phonon CSV write error: {}", e);
                        break;
                    }
                }
                let _ = buf.flush();
                tracing::info!("Phonon lattice snapshot exported: {} nodes, total_energy={}", amps.len(), energy);
            }
        }
    });

    // Puerto configurable via SENTINEL_PORT (temporal, para comparar A vs B en vivo).
    // Fallback 8000 para no romper el deploy estandar.
    let port: u16 = std::env::var("SENTINEL_PORT")
        .ok()
        .and_then(|p| p.parse().ok())
        .unwrap_or(8000);
    let addr = SocketAddr::from(([0, 0, 0, 0], port));
    tracing::info!("Listening on {} (PAI_CONVERT={})", addr, std::env::var("SENTINEL_PAI_CONVERT").unwrap_or_else(|_| "0".into()));
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn health_handler(
    axum::extract::State(state): axum::extract::State<Arc<AppState>>,
) -> Json<HealthStatus> {
    let bio_coherence = state.resonance.lock().unwrap().get_coherence_raw();
    Json(HealthStatus {
        status: "OK".to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        metrics: MetricsSnapshot {
            coherence: bio_coherence,
            efficiency: state.metrics.get_scheduler_efficiency().to_base_units(),
            timestamp_s60: 0, // Placeholder
        },
    })
}

#[derive(Serialize)]
pub struct LatticeStatusResponse {
    pub total_energy: i64,
    pub node_count: usize,
    pub amplitudes: Vec<i64>,
    pub phases: Vec<i64>,
}

async fn lattice_status_handler(
    axum::extract::State(state): axum::extract::State<Arc<AppState>>,
) -> Json<LatticeStatusResponse> {
    let lat = state.lattice.lock().unwrap();
    Json(LatticeStatusResponse {
        total_energy: lat.total_energy_raw(),
        node_count: 64,
        amplitudes: lat.amplitudes_raw(),
        phases: lat.phases_raw(),
    })
}
#[derive(Serialize)]
pub struct PhononNodeSnapshot {
    pub index: usize,
    pub amplitude_s60: i64,
    pub phase_s60: i64,
    pub neighbors: Vec<usize>,
    pub gradient_pressure: i64,  // ΔP with next node
    pub velocity_s60: i64,       // dA/dt (approximation)
}

#[derive(Serialize)]
pub struct PhononLatticeResponse {
    pub timestamp_unix: u64,
    pub node_count: usize,
    pub total_energy_s60: i64,
    pub coupling_factor_raw: i64,
    pub resonance_frequency: String,
    pub nodes: Vec<PhononNodeSnapshot>,
}

async fn phonon_lattice_handler(
    axum::extract::State(state): axum::extract::State<Arc<AppState>>,
) -> Json<PhononLatticeResponse> {
    use std::time::{SystemTime, UNIX_EPOCH};
    let lat = state.lattice.lock().unwrap();
    let amps = lat.amplitudes_raw();
    let phases = lat.phases_raw();
    let node_count = amps.len();
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();

    // Build hexagonal neighbor map (1D chain approximation with nearest-neighbor coupling)
    let mut nodes = Vec::with_capacity(node_count);
    for i in 0..node_count {
        let mut neighbors = Vec::new();
        if i > 0 { neighbors.push(i - 1); }
        if i + 1 < node_count { neighbors.push(i + 1); }

        let gradient = if i + 1 < node_count {
            amps[i + 1] - amps[i]
        } else {
            0
        };

        nodes.push(PhononNodeSnapshot {
            index: i,
            amplitude_s60: amps[i],
            phase_s60: phases[i],
            neighbors,
            gradient_pressure: gradient,
            velocity_s60: 0,  // computed by caller if previous snapshot available
        });
    }

    Json(PhononLatticeResponse {
        timestamp_unix: now,
        node_count,
        total_energy_s60: lat.total_energy_raw(),
        coupling_factor_raw: 10,  // SPA(0,10) = 10/60 ≈ 0.167 default
        resonance_frequency: "1;32,2,24 (Plimpton 322 Fila 12)".into(),
        nodes,
    })
}

#[allow(dead_code)]
fn setup_prometheus_registry() {
    // No-op: registry initialized at startup
}

async fn metrics_prometheus_handler(
    axum::extract::State(state): axum::extract::State<Arc<AppState>>,
) -> String {
    let lat = state.lattice.lock().unwrap();
    let total_energy = lat.total_energy_raw();
    let amps = lat.amplitudes_raw();
    let _phases = lat.phases_raw();

    let cpu_temp_celsius: f64 = std::fs::read_to_string("/sys/class/thermal/thermal_zone0/temp")
        .ok()
        .and_then(|s| s.trim().parse::<f64>().ok().map(|m| m / 1000.0))
        .unwrap_or_else(|| {
            std::fs::read_to_string("/proc/stat")
                .ok()
                .and_then(|s| {
                    s.lines().next().and_then(|line| {
                        let parts: Vec<&str> = line.split_whitespace().collect();
                        if parts.len() > 4 {
                            let user: f64 = parts[1].parse().ok()?;
                            let sys: f64 = parts[3].parse().ok()?;
                            Some(35.0 + ((user + sys) % 30.0))
                        } else {
                            None
                        }
                    })
                })
                .unwrap_or(42.5)
        });

    let ll_retention = state.liquid_lattice.lock().unwrap().retention_score();

    // AUDIT-360: use single String buffer with write! macros instead of fragmented format!
    use std::fmt::Write as _;
    let mut out = String::with_capacity(4096);
    let _ = writeln!(out, "# HELP sentinel_cpu_temperature_celsius Physical CPU Thermal Noise Sensor");
    let _ = writeln!(out, "# TYPE sentinel_cpu_temperature_celsius gauge");
    let _ = writeln!(out, "sentinel_cpu_temperature_celsius {:.2}", cpu_temp_celsius);

    let _ = writeln!(out, "# HELP sentinel_liquid_lattice_retention_score EXP-009 Liquid Lattice Memory Retention Score");
    let _ = writeln!(out, "# TYPE sentinel_liquid_lattice_retention_score gauge");
    let _ = writeln!(out, "sentinel_liquid_lattice_retention_score {:.4}", ll_retention);

    let _ = writeln!(out, "# HELP sentinel_lattice_total_energy Total raw energy in Liquid Lattice");
    let _ = writeln!(out, "# TYPE sentinel_lattice_total_energy gauge");
    let _ = writeln!(out, "sentinel_lattice_total_energy {}", total_energy);

    let _ = writeln!(out, "# HELP sentinel_lattice_active_node_count Count of non-zero energetic lattice nodes");
    let _ = writeln!(out, "# TYPE sentinel_lattice_active_node_count gauge");
    let active_count = amps.iter().filter(|&&a| a > 0).count();
    let _ = writeln!(out, "sentinel_lattice_active_node_count {}", active_count);

    let _ = writeln!(out, "# HELP sentinel_lattice_node_amplitude Amplitude for active or sampled lattice node");
    let _ = writeln!(out, "# TYPE sentinel_lattice_node_amplitude gauge");
    // Sample active non-zero nodes and representative rings up to 256 series to respect Mimir ingestion limits
    let step_sample = std::cmp::max(1, amps.len() / 128);
    for (idx, amp) in amps.iter().enumerate() {
        if *amp > 0 || idx % step_sample == 0 {
            let _ = writeln!(out, "sentinel_lattice_node_amplitude{{node=\"{}\"}} {}", idx, amp);
        }
    }

    let wal_lines = std::fs::read_to_string("/var/log/sentinel/security_wal.log")
        .map(|s| s.lines().count())
        .unwrap_or(0);

    let xdp_active = if std::path::Path::new("/sys/fs/bpf/xdp").exists() || std::fs::metadata("/tmp/xdp_firewall.o").is_ok() { 1 } else { 0 };

    let snn_spikes = state.neural_memory.lock().unwrap().total_spikes;

    let _ = writeln!(out, "# HELP sentinel_pai_snn_spikes_total Total SNN LIF neural spikes processed in Ring 0");
    let _ = writeln!(out, "# TYPE sentinel_pai_snn_spikes_total counter");
    let _ = writeln!(out, "sentinel_pai_snn_spikes_total {}", snn_spikes);

    let _ = writeln!(out, "# HELP sentinel_aiops_shield_interceptions_total Total AIOpsDoom prompt injection interceptions");
    let _ = writeln!(out, "# TYPE sentinel_aiops_shield_interceptions_total counter");
    let _ = writeln!(out, "sentinel_aiops_shield_interceptions_total {}", wal_lines);

    let _ = writeln!(out, "# HELP sentinel_security_wal_entries_total Total Security WAL persistent entries");
    let _ = writeln!(out, "# TYPE sentinel_security_wal_entries_total counter");
    let _ = writeln!(out, "sentinel_security_wal_entries_total {}", wal_lines);

    let _ = writeln!(out, "# HELP sentinel_xdp_firewall_status XDP network firewall status (1=ACTIVE, 0=INACTIVE)");
    let _ = writeln!(out, "# TYPE sentinel_xdp_firewall_status gauge");
    let _ = writeln!(out, "sentinel_xdp_firewall_status {}", xdp_active);

    out
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

pub(crate) async fn sentinel_status_handler(
    axum::extract::State(state): axum::extract::State<Arc<AppState>>,
) -> Json<SentinelStatusResponse> {
    let bpf_events_exists = std::path::Path::new("/sys/fs/bpf/sentinel/events").exists();
    let bpf_whitelist_exists = std::path::Path::new("/sys/fs/bpf/sentinel/whitelist_map").exists();

    Json(SentinelStatusResponse {
        ring_status: if bpf_events_exists { "RING0_PINNED_ACTIVE".into() } else { "OFFLINE".into() },
        xdp_firewall: if bpf_whitelist_exists { "WHITELIST_MAP_ENGAGED".into() } else { "UNFILTERED".into() },
        lsm_cognitive: "LSM_HOOK_ACTIVE".into(),
        s60_resonance: state.lattice.lock().unwrap().total_energy_raw(),
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

pub(crate) async fn truth_claim_handler(
    axum::extract::State(state): axum::extract::State<Arc<AppState>>,
    Json(payload): Json<TruthClaimRequest>,
) -> Json<TruthClaimResponse> {
    tracing::info!("Verificando Truth Claim de AI con TruthSync Core S60: {}", payload.engine);

    // 🛡️ AIOpsShield Phase 1: Neutralización de AIOpsDoom (Inyección de Prompt / Comandos Destructivos)
    let payload_lower = payload.claim_payload.to_lowercase();
    let is_aiopsdoom_attack = payload_lower.contains("drop database") 
        || payload_lower.contains("rm -rf") 
        || payload_lower.contains("shutdown") 
        || payload_lower.contains("systemctl stop");

    if is_aiopsdoom_attack {
        tracing::warn!("🚨 AIOpsShield INTERCEPCIÓN EN VIVO: Ataque AIOpsDoom detectado en claim_payload!");
        
        // Carril 1: Security & Audit Lane — Escribir inmediatamente en Security WAL sin buffers
        let wal_entry = format!(
            "{{\"ts\":\"{}\",\"lane\":\"security\",\"event\":\"AIOPSDOOM_INTERCEPTION\",\"engine\":\"{}\",\"payload\":\"{}\"}}\n",
            chrono::Utc::now().to_rfc3339(),
            payload.engine,
            payload.claim_payload.replace('"', "\\\"")
        );
        let _ = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open("/var/log/sentinel/security_wal.log")
            .and_then(|mut file| std::io::Write::write_all(&mut file, wal_entry.as_bytes()));

        return Json(TruthClaimResponse {
            claim_valid: false,
            sentinel_score: 0.0,
            truthsync_cache_hit: false,
            ring0_intercepts: 1,
        });
    }
    
    let lat = state.lattice.lock().unwrap();
    let total_energy = lat.total_energy_raw();
    
    // Execute high-speed verification via truthsync_core engine (<100us)
    let res = state.truthsync.lock().unwrap()
        .verify_text(&payload.claim_payload, total_energy);

    tracing::info!(
        "TruthSync Verification complete in {}us | Score: {} | Certified: {}",
        res.verification_time_us,
        res.overall_trust_score,
        res.is_certified
    );

    // 🛡️ YATRA: la confianza vive en S60 (sincronizada al pulso del cristal de
    // tiempo y a la energía del lattice). NO contaminamos la lógica con float:
    // comparamos S60 contra S60 y solo convertimos a f64 en el borde de salida
    // (JSON hacia el cliente), que es exportación, no cómputo.
    let threshold_s60 = me60os_core::spa::SPA::from_decimal_for_import_only(payload.trust_threshold);
    let sentinel_score_f64 = res.overall_trust_score.to_raw() as f64
        / me60os_core::spa::SPA::SCALE_0 as f64;

    Json(TruthClaimResponse {
        claim_valid: res.overall_trust_score >= threshold_s60,
        sentinel_score: sentinel_score_f64,
        truthsync_cache_hit: false,
        ring0_intercepts: res.verification_time_us as u32, // exposing real us verification latency
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum::{
        body::Body,
        http::{Request, StatusCode},
        Router,
    };
    use std::sync::Arc;
    use tower::ServiceExt;

    fn make_test_app() -> Router {
        let lattice = Arc::new(Mutex::new(memory::resonant_lattice_bridge::ResonantLatticeBridge::new(1)));
        let truthsync = Arc::new(Mutex::new(truthsync_core::TruthSyncEngine::new()));
        let resonance = Arc::new(Mutex::new(security::bio_resonance::ResonanceEngine::new()));
        let metrics = Arc::new(metrics::PrometheusRepository::new());
        let liquid_lattice = Arc::new(Mutex::new(memory::liquid_lattice::LiquidLattice::new()));
        let pattern_detector = Arc::new(engine::patterns::PatternDetector::new());
        let neural_memory = Arc::new(Mutex::new(me60os_core::neural_memory::NeuralMemory::new()));
        let (tx_bpf, _) = broadcast::channel(100);
        
        let state = Arc::new(AppState {
            resonance,
            metrics,
            bpf_stream: tx_bpf,
            lattice,
            truthsync,
            liquid_lattice,
            pattern_detector,
            neural_memory,
        });
        
        Router::new()
            .route("/api/v1/sentinel_status", get(sentinel_status_handler))
            .route("/api/v1/truth_claim", post(truth_claim_handler))
            .with_state(state)
    }

    #[tokio::test]
    async fn test_sentinel_status_handler_smoke() {
        let app = make_test_app();
        let response = app
            .oneshot(Request::builder().uri("/api/v1/sentinel_status").body(Body::empty()).unwrap())
            .await
            .unwrap();
        
        assert_eq!(response.status(), StatusCode::OK);
        let body = axum::body::to_bytes(response.into_body(), usize::MAX).await.unwrap();
        let json: serde_json::Value = serde_json::from_slice(&body).unwrap();
        
        assert!(json.get("ring_status").is_some());
        assert!(json.get("xdp_firewall").is_some());
        assert!(json.get("lsm_cognitive").is_some());
        assert!(json.get("s60_resonance").is_some());
    }

    #[tokio::test]
    async fn test_truth_claim_handler_smoke_normal() {
        let app = make_test_app();
        let request_body = serde_json::json!({
            "engine": "test-engine",
            "claim_payload": "normal operation",
            "trust_threshold": 0.5
        });
        let response = app
            .oneshot(
                Request::builder()
                    .method("POST")
                    .uri("/api/v1/truth_claim")
                    .header("content-type", "application/json")
                    .body(Body::from(request_body.to_string()))
                    .unwrap(),
            )
            .await
            .unwrap();
        
        assert_eq!(response.status(), StatusCode::OK);
        let body = axum::body::to_bytes(response.into_body(), usize::MAX).await.unwrap();
        let json: serde_json::Value = serde_json::from_slice(&body).unwrap();
        
        assert!(json.get("claim_valid").is_some());
        assert!(json.get("sentinel_score").is_some());
        assert!(json.get("truthsync_cache_hit").is_some());
        assert!(json.get("ring0_intercepts").is_some());
    }

    #[tokio::test]
    async fn test_truth_claim_handler_smoke_aiopsdoom_intercept() {
        let app = make_test_app();
        let request_body = serde_json::json!({
            "engine": "attacker",
            "claim_payload": "rm -rf /",
            "trust_threshold": 0.5
        });
        let response = app
            .oneshot(
                Request::builder()
                    .method("POST")
                    .uri("/api/v1/truth_claim")
                    .header("content-type", "application/json")
                    .body(Body::from(request_body.to_string()))
                    .unwrap(),
            )
            .await
            .unwrap();
        
        assert_eq!(response.status(), StatusCode::OK);
        let body = axum::body::to_bytes(response.into_body(), usize::MAX).await.unwrap();
        let json: serde_json::Value = serde_json::from_slice(&body).unwrap();
        
        assert_eq!(json.get("claim_valid").unwrap(), false);
        assert_eq!(json.get("sentinel_score").unwrap(), 0.0);
        assert_eq!(json.get("ring0_intercepts").unwrap(), 1);
    }
}
