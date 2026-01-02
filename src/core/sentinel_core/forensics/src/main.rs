mod scanner;
mod cognitive;

use scanner::MemoryScanner;
use cognitive::CognitiveEngine;
use std::time::{Instant, Duration};
use std::sync::Arc;
use aya::programs::TracePoint;
use aya::{Ebpf, include_bytes_aligned, util::online_cpus};
use aya::maps::{perf::AsyncPerfEventArray, HashMap, MapData};
use tokio::signal;
use tokio::sync::mpsc;
use tokio::time::sleep;
use bytes::BytesMut;
use forensics_common::ProcessEvent;
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

#[derive(Debug)]
struct ProcessJob {
    pid: i32,
    comm: String,
}

#[derive(Debug)]
enum ForensicsCommand {
    Freeze { pid: i32 },
    Block { pid: i32, exe_path: String },
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🧠 [Sentinel Forensics] Starting Memory Scanner (Rayon + eBPF)");

    // 1. Load forensics eBPF
    let bpf_data = include_bytes_aligned!("../ebpf_c/trace.bpf.o");
    let bpf: &'static mut Ebpf = Box::leak(Box::new(Ebpf::load(bpf_data)?));
    
    let program: &mut TracePoint = bpf.program_mut("trace_exit_execve")
        .expect("Program 'trace_exit_execve' not found")
        .try_into()?;
    program.load()?;
    program.attach("syscalls", "sys_exit_execve")?;

    println!("🔭 Forensics Tracepoint attached to sys_exit_execve.");

    // 2. Channels
    let (job_tx, mut job_rx) = mpsc::channel::<ProcessJob>(100);
    let (cmd_tx, mut cmd_rx) = mpsc::channel::<ForensicsCommand>(100);
    
    // 3. Setup Dashboard
    let (tx, _rx) = broadcast::channel::<DashboardEvent>(100);
    let tx_cloned = tx.clone();
    tokio::spawn(async move {
        let app = Router::new()
            .route("/ws", get(ws_handler))
            .layer(CorsLayer::permissive())
            .with_state(tx_cloned);
        let listener = tokio::net::TcpListener::bind("0.0.0.0:8082").await.unwrap();
        println!("📡 Dashboard WebSocket Server running on port 8082");
        axum::serve(listener, app).await.unwrap();
    });

    // 4. Initialize Engines
    let patterns = vec![
        b"\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb".to_vec(),
        b"/bin/sh".to_vec(),
        b"chmod +x".to_vec(),
    ];
    let scanner = Arc::new(MemoryScanner::new(patterns));
    let engine = Arc::new(CognitiveEngine::new("llama3.2:3b"));
    let tx_for_worker = tx.clone();

    // 5. Cognitive Worker Loop
    let cmd_tx_worker = cmd_tx.clone();
    tokio::spawn(async move {
        while let Some(job) = job_rx.recv().await {
            let scanner = scanner.clone();
            let engine = engine.clone();
            let cmd_tx = cmd_tx_worker.clone();
            let tx = tx_for_worker.clone();
            
            tokio::spawn(async move {
                let pid = job.pid;
                let comm = job.comm;
                let _ = tx.send(DashboardEvent::ProcessStart { pid, comm: comm.clone() });

                sleep(Duration::from_millis(300)).await;
                
                match scanner.scan_process(pid) {
                    Ok(findings) if !findings.is_empty() => {
                        let _ = tx.send(DashboardEvent::Detections { pid, comm: comm.clone(), findings: findings.clone() });
                        
                        match engine.ask_decision(pid, &comm, &findings).await {
                            Ok(is_block) => {
                                let _ = tx.send(DashboardEvent::Decision { 
                                    pid, comm: comm.clone(), 
                                    decision: if is_block { "BLOCK".to_string() } else { "ALLOW".to_string() },
                                    blocked: is_block
                                });

                                if is_block {
                                    let _ = cmd_tx.send(ForensicsCommand::Freeze { pid }).await;
                                    if let Ok(exe_path) = Process::new(pid).and_then(|p| p.exe()) {
                                        let _ = cmd_tx.send(ForensicsCommand::Block { pid, exe_path: exe_path.to_string_lossy().to_string() }).await;
                                    }
                                }
                            },
                            Err(_) => {}
                        }
                    },
                    _ => {}
                }
            });
        }
    });

    // 6. Map Manager Loop
    // Use an alias to bypass the borrow checker for initialization of multiple asynchronous tasks
    let bpf_alias: &'static mut Ebpf = unsafe { &mut *(bpf as *mut Ebpf) };
    
    // 6.b Load UID Whitelist (Done first to release borrow)
    {
        if let Some(mut whitelist_map) = bpf_alias.map_mut("whitelist_uids").and_then(|m| HashMap::<_, u32, u8>::try_from(m).ok()) {
            let whitelist_file = "/home/jnovoas/sentinel/config/ebpf_whitelist.txt";
            if let Ok(content) = std::fs::read_to_string(whitelist_file) {
                println!("🛡️ [WHITELIST] Loading UIDs from {}...", whitelist_file);
                for line in content.lines() {
                    let part = line.split('#').next().unwrap_or("").trim();
                    if let Ok(uid) = part.parse::<u32>() {
                        println!("✅ [WHITELIST] Protecting UID: {}", uid);
                        let _ = whitelist_map.insert(uid, 1, 0);
                    }
                }
            } else {
                println!("⚠️ [WHITELIST] Config file not found, using defaults (0, 1000)");
                let _ = whitelist_map.insert(0, 1, 0);
                let _ = whitelist_map.insert(1000, 1, 0);
            }
        }
    }

    let mut freeze_map: HashMap<&mut MapData, u32, u8> = HashMap::try_from(bpf_alias.map_mut("freeze_commands").unwrap())?;
    
    tokio::spawn(async move {
        while let Some(cmd) = cmd_rx.recv().await {
            match cmd {
                ForensicsCommand::Freeze { pid } => {
                    println!("❄️ [FREEZE] Freezing PID {}", pid);
                    let _ = freeze_map.insert(pid as u32, 1, 0);
                },
                ForensicsCommand::Block { pid: _, exe_path } => {
                    println!("🛑 [BLOCK] Flagging binary: {}", exe_path);
                }
            }
        }
    });

    // 7. Perf Event Polling
    let mut perf_array = AsyncPerfEventArray::try_from(bpf.map_mut("suspicious_events").unwrap())?;
    let cpus = online_cpus().map_err(|e| format!("Failed to get online CPUs: {:?}", e))?;
    for cpu_id in cpus {
        let mut buf = perf_array.open(cpu_id, None)?;
        let job_tx_perf = job_tx.clone();
        tokio::spawn(async move {
            let mut buffers = (0..10).map(|_| BytesMut::with_capacity(4096)).collect::<Vec<_>>();
            loop {
                if let Ok(summary) = buf.read_events(&mut buffers).await {
                    for i in 0..summary.read {
                        let event: ProcessEvent = unsafe { std::ptr::read(buffers[i].as_ptr() as *const _) };
                        let pid = event.pid as i32;
                        let comm = String::from_utf8_lossy(&event.comm).trim_matches(char::from(0)).to_string();
                        if pid > 0 && !comm.is_empty() {
                            let _ = job_tx_perf.send(ProcessJob { pid, comm }).await;
                        }
                    }
                }
            }
        });
    }

    println!("🚀 Cognitive Loop ACTIVE. Channel bridge initialized.");
    signal::ctrl_c().await?;
    Ok(())
}

async fn ws_handler(ws: WebSocketUpgrade, State(tx): State<broadcast::Sender<DashboardEvent>>) -> impl IntoResponse {
    ws.on_upgrade(|socket| handle_socket(socket, tx))
}

async fn handle_socket(mut socket: WebSocket, tx: broadcast::Sender<DashboardEvent>) {
    let mut rx = tx.subscribe();
    while let Ok(event) = rx.recv().await {
        if let Ok(msg) = serde_json::to_string(&event) {
            if socket.send(Message::Text(msg)).await.is_err() { break; }
        }
    }
}
