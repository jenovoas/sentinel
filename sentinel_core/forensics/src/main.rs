mod scanner;
mod cognitive;

use scanner::MemoryScanner;
use cognitive::CognitiveEngine;
use std::time::{Instant, Duration};
use std::sync::Arc;
use aya::programs::TracePoint;
use aya::{Ebpf, include_bytes_aligned, util::online_cpus};
use aya::maps::{perf::AsyncPerfEventArray, HashMap, MapData, Map};
use tokio::signal;
use tokio::sync::Mutex;
use tokio::time::sleep;
use bytes::BytesMut;
use forensics_common::ProcessEvent;
use futures::future::select_all;
use procfs::process::Process;
use axum::{
    extract::{ws::{Message, WebSocket, WebSocketUpgrade}, State},
    response::IntoResponse,
    routing::get,
    Router,
};
use tokio::sync::broadcast;
use serde::Serialize;
use tower_http::cors::CorsLayer;

#[derive(Serialize, Clone)]
#[serde(tag = "type", content = "data", rename_all = "snake_case")]
enum DashboardEvent {
    ProcessStart { pid: i32, comm: String },
    Detections { pid: i32, comm: String, findings: Vec<String> },
    Decision { pid: i32, comm: String, decision: String, blocked: bool },
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🧠 [Sentinel Forensics] Starting Memory Scanner (Rayon + eBPF)");

    // 1. Load forensics eBPF (C-based output)
    let bpf_data = include_bytes_aligned!("../ebpf_c/trace.bpf.o");
    let mut bpf = Ebpf::load(bpf_data)?;
    
    // Attach tracepoint to sys_exit_execve
    let program: &mut TracePoint = bpf.program_mut("trace_exit_execve")
        .expect("Program 'trace_exit_execve' not found")
        .try_into()?;
    program.load()?;
    program.attach("syscalls", "sys_exit_execve")?;

    println!("🔭 Forensics Tracepoint attached to sys_exit_execve.");

    // 2. Open Guardian-Alpha whitelist map
    let guardian_map_path = "/sys/fs/bpf/guardian_alpha/whitelist_map";
    let guardian_map: Option<HashMap<MapData, [u8; 256], u8>> = match MapData::from_pin(guardian_map_path) {
        Ok(m) => {
            println!("🔒 Connected to Guardian-Alpha Whitelist Map.");
            let map = Map::HashMap(m);
            Some(HashMap::try_from(map)?)
        },
        Err(_) => {
            println!("⚠️  Guardian-Alpha map not found. Blocking will be log-only.");
            None
        }
    };
    let shared_guardian_map = guardian_map.map(|m| Arc::new(Mutex::new(m)));

    // 3. Initialize Engines
    let patterns = vec![
        b"\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb".to_vec(), // Standard shellcode
        b"/bin/sh".to_vec(),
        b"chmod +x".to_vec(),
    ];
    let scanner = Arc::new(MemoryScanner::new(patterns));
    let engine = Arc::new(CognitiveEngine::new("llama3.2:3b"));

    // 4. Setup Broadcast Channel for Dashboard
    let (tx, _rx) = broadcast::channel::<DashboardEvent>(100);
    let tx_cloned = tx.clone();

    // 5. Start Web Server for Dashboard
    tokio::spawn(async move {
        let app = Router::new()
            .route("/ws", get(ws_handler))
            .layer(CorsLayer::permissive())
            .with_state(tx_cloned);

        let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await.unwrap();
        println!("📡 Dashboard WebSocket Server running on port 8080");
        axum::serve(listener, app).await.unwrap();
    });

    // 6. Handle eBPF events via AsyncPerfEventArray
    let mut perf_array = AsyncPerfEventArray::try_from(bpf.map_mut("suspicious_events").unwrap())?;
    
    println!("🛡️ Monitoring system for suspicious process activities...");

    let cpus = online_cpus().map_err(|e| format!("Failed to get online CPUs: {:?}", e))?;
    let mut cpu_tasks = Vec::new();

    for cpu_id in cpus {
        let buf = perf_array.open(cpu_id, None)?;
        cpu_tasks.push(Box::pin(poll_cpu(buf, scanner.clone(), engine.clone(), shared_guardian_map.clone(), tx.clone())));
    }

    println!("🚀 Cognitive Loop ACTIVE. Parallel scanner running.");

    tokio::select! {
        _ = async {
            while !cpu_tasks.is_empty() {
                let (res, _index, remaining) = select_all(cpu_tasks).await;
                if let Err(e) = res {
                    eprintln!("Error polling CPU: {:?}", e);
                }
                cpu_tasks = remaining;
            }
        } => {},
        _ = signal::ctrl_c() => {
            println!("\n👋 Shutting down...");
        }
    }

    Ok(())
}

async fn poll_cpu(
    mut buf: aya::maps::perf::AsyncPerfEventArrayBuffer<&mut aya::maps::MapData>, 
    scanner: Arc<MemoryScanner>,
    engine: Arc<CognitiveEngine>,
    guardian_map: Option<Arc<Mutex<HashMap<MapData, [u8; 256], u8>>>>,
    tx: broadcast::Sender<DashboardEvent>
) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let mut buffers = (0..10)
        .map(|_| BytesMut::with_capacity(4096))
        .collect::<Vec<_>>();

    loop {
        let summary = buf.read_events(&mut buffers).await?;
        for i in 0..summary.read {
            let buf_data = &buffers[i];
            let event: ProcessEvent = unsafe { std::ptr::read(buf_data.as_ptr() as *const _) };
            let pid = event.pid as i32;
            let comm = String::from_utf8_lossy(&event.comm).trim_matches(char::from(0)).to_string();

            if pid == 0 || comm.is_empty() { continue; }

            println!("📦 Event detected: PID {} ({})", pid, comm);
            
            let scanner_inner = scanner.clone();
            let engine_inner = engine.clone();
            let g_map_inner = guardian_map.clone();
            let tx_inner = tx.clone();
            
            tokio::spawn(async move {
                // Emitir evento: Inicio de Proceso
                let _ = tx_inner.send(DashboardEvent::ProcessStart { pid, comm: comm.clone() });

                // DELAY: Esperamos 300ms para permitir que los scripts de inyección actúen
                sleep(Duration::from_millis(300)).await;
                
                let start = Instant::now();
                match scanner_inner.scan_process(pid) {
                    Ok(findings) if !findings.is_empty() => {
                        println!("⚠️ [ALERTA] Actividad sospechosa detectada en PID {} ({}):", pid, comm);
                        // Emitir evento: Detecciones encontradas
                        let _ = tx_inner.send(DashboardEvent::Detections { pid, comm: comm.clone(), findings: findings.clone() });

                        for finding in &findings {
                            println!("  - {}", finding);
                        }
                        
                        // Consultar Motor Cognitivo
                        match engine_inner.ask_decision(pid, &comm, &findings).await {
                            Ok(is_block) => {
                                // Emitir evento: Decisión final
                                let _ = tx_inner.send(DashboardEvent::Decision { 
                                    pid, 
                                    comm: comm.clone(), 
                                    decision: if is_block { "BLOCK".to_string() } else { "ALLOW".to_string() },
                                    blocked: is_block
                                });

                                if is_block {
                                    block_via_ebpf(pid, g_map_inner).await;
                                } else {
                                    println!("✅ Decisión IA: PERMITIR PID {} ({}).", pid, comm);
                                }
                            },
                            Err(e) => eprintln!("❌ Fallo en análisis de IA: {:?}", e),
                        }
                        println!("⏱️ Bucle cognitivo completo en {:?}", start.elapsed());
                    },
                    _ => {} 
                }
            });
        }
    }
}

// WebSocket Handlers
async fn ws_handler(
    ws: WebSocketUpgrade,
    State(tx): State<broadcast::Sender<DashboardEvent>>,
) -> impl IntoResponse {
    ws.on_upgrade(|socket| handle_socket(socket, tx))
}

async fn handle_socket(mut socket: WebSocket, tx: broadcast::Sender<DashboardEvent>) {
    let mut rx = tx.subscribe();
    
    while let Ok(event) = rx.recv().await {
        if let Ok(msg) = serde_json::to_string(&event) {
            if socket.send(Message::Text(msg)).await.is_err() {
                break;
            }
        }
    }
}

async fn block_via_ebpf(pid: i32, guardian_map: Option<Arc<Mutex<HashMap<MapData, [u8; 256], u8>>>>) {
    let exe_path = match Process::new(pid).and_then(|p| p.exe()) {
        Ok(path) => path.to_string_lossy().to_string(),
        Err(_) => {
            println!("❌ Could not find executable path for PID {}", pid);
            return;
        }
    };

    println!("🛑 [BLOCK] Flagging malicious binary: {}", exe_path);

    if let Some(map_mutex) = guardian_map {
        let mut key = [0u8; 256];
        let bytes = exe_path.as_bytes();
        let len = bytes.len().min(255);
        key[..len].copy_from_slice(&bytes[..len]);

        let mut map = map_mutex.lock().await;
        if let Err(e) = map.insert(key, 0, 0) {
            println!("❌ Failed to update Guardian map: {:?}", e);
        } else {
            println!("✅ Guardian-Alpha whitelist updated: BLOCKED {}", exe_path);
        }
    }
}
