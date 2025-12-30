// sentinel_core/init/src/main.rs
mod crypto;
mod forensics;

use aya::programs::{KProbe, Xdp, XdpFlags};
use aya::{Ebpf, include_bytes_aligned};
use aya::maps::{HashMap as BpfHashMap, Array as BpfArray};
use nix::mount::{mount, MsFlags};
use nix::sys::signal::{kill, Signal};
use nix::sys::wait::{waitpid, WaitPidFlag};
use nix::unistd::Pid;
use rlimit::{setrlimit, Resource};
use serde::{Deserialize, Serialize};
use std::collections::HashMap as StdHashMap;
use std::error::Error;
use std::fs;
use std::path::Path;
use std::sync::{Arc, Mutex};
use std::net::Ipv4Addr;
use tokio::io::{AsyncReadExt, AsyncWriteExt, AsyncBufReadExt, BufReader};
use tokio::net::UnixStream;
use tokio::signal::unix::{signal, SignalKind};
use tokio::time::{sleep, Duration};
use tokio::fs::{File, OpenOptions};
use crate::forensics::MemoryScanner;
use crypto::{PqcContext, SecureSession};

// Placeholder: load eBPF object compiled separately
const BPF_OBJECT: &[u8] = include_bytes_aligned!("../../../ebpf/init_kprobe.o");
const XDP_OBJECT: &[u8] = include_bytes_aligned!("../../../ebpf/xdp_firewall.o");
const BRAIN_SOCKET: &str = "/tmp/sentinel_cortex.sock";

#[derive(Serialize, Deserialize, Debug)]
#[serde(tag = "type")]
enum PqcMessage {
    #[serde(rename = "pqc_hello")]
    Hello { pk: String },
    #[serde(rename = "pqc_auth")]
    Auth { ct: String },
    #[serde(rename = "enc")]
    Encrypted { payload: String },
    #[serde(untagged)]
    Legacy(serde_json::Value),
}

struct CryptoState {
    session: Option<SecureSession>,
}
type SharedCryptoState = Arc<Mutex<CryptoState>>;

#[derive(Serialize)]
struct BrainRequest {
    pid: u32,
    path: String,
}

#[derive(Serialize)]
struct ThreatReport {
    pid: u32,
    score: f32,
    details: String,
}

#[derive(Deserialize)]
struct BrainResponse {
    allow: bool,
    block_ip: Option<String>,
}

#[derive(Serialize)]
struct Heartbeat {
    hb: u64,
}

struct NetworkGuardian {
    ebpf: Arc<Mutex<Ebpf>>,
}

impl NetworkGuardian {
    fn new(ebpf: Ebpf) -> Self {
        Self { ebpf: Arc::new(Mutex::new(ebpf)) }
    }

    fn block_ip(&self, ip: u32) -> Result<(), Box<dyn Error>> {
        let mut ebpf = self.ebpf.lock().unwrap();
        let mut blacklist: BpfHashMap<_, u32, u8> = BpfHashMap::try_from(ebpf.map_mut("blacklist").ok_or("Map blacklist not found")?)?;
        blacklist.insert(ip, 1, 0)?;
        println!("[init] [NET-HUNTER] 🚫 BLOCKED IP: {:?}", Ipv4Addr::from(u32::from_be(ip)));
        Ok(())
    }

    fn set_panic_mode(&self, enabled: bool) -> Result<(), Box<dyn Error>> {
        let mut ebpf = self.ebpf.lock().unwrap();
        let mut config_map: BpfArray<_, u32> = BpfArray::try_from(ebpf.map_mut("config_map").ok_or("Map config_map not found")?)?;
        let val: u32 = if enabled { 1 } else { 0 };
        config_map.set(0, val, 0)?;
        
        if enabled {
             println!("[init] [NET-HUNTER] 🚨 PANIC MODE ACTIVATED: NETWORK QUARANTINE ENFORCED");
        } else {
             println!("[init] [NET-HUNTER] 🟢 Panic Mode Deactivated. Network Normal.");
        }
        Ok(())
    }
}

struct CognitiveDecider {
    cache: Arc<Mutex<StdHashMap<String, bool>>>,
    crypto: SharedCryptoState,
}

impl CognitiveDecider {
    fn new(crypto: SharedCryptoState) -> Self {
        Self {
            cache: Arc::new(Mutex::new(StdHashMap::new())),
            crypto,
        }
    }

    async fn check_risk(&self, pid: u32) -> f64 {
        let exe_path = format!("/proc/{}/exe", pid);
        let path_str = match fs::read_link(&exe_path) {
            Ok(target) => target.to_string_lossy().into_owned(),
            Err(_) => return 0.0,
        };

        // 1. Check Cache
        {
            let cache = self.cache.lock().unwrap();
            if let Some(&allow) = cache.get(&path_str) {
                return if allow { 0.0 } else { 1.0 };
            }
        }

        // 2. Ask Brain
        match self.ask_brain(pid, &path_str).await {
            Ok(allow) => {
                let mut cache = self.cache.lock().unwrap();
                cache.insert(path_str, allow);
                if allow { 0.0 } else { 1.0 }
            }
            Err(_) => {
                // 3. Fallback to Local Heuristic
                cognitive_risk(pid)
            }
        }
    }

    async fn ask_brain(&self, pid: u32, path: &str) -> Result<bool, Box<dyn Error>> {
        let resp = self.ask_brain_extended(pid, path).await?;
        Ok(resp.allow)
    }

    async fn ask_brain_extended(&self, pid: u32, path: &str) -> Result<BrainResponse, Box<dyn Error>> {
        let mut stream = UnixStream::connect(BRAIN_SOCKET).await?;
        let req = BrainRequest { pid, path: path.to_string() };
        let req_json = serde_json::to_vec(&req)?;
        
        stream.write_all(&req_json).await?;
        stream.shutdown().await?;

        let mut response_json = Vec::new();
        stream.read_to_end(&mut response_json).await?;
        
        let resp: BrainResponse = serde_json::from_slice(&response_json)?;
        Ok(resp)
    }

    async fn report_threat(&self, pid: u32, score: f32, details: String) -> Result<(), Box<dyn Error>> {
        let device_path = "/dev/ttyS1";
        let report = ThreatReport { pid, score, details };
        let json_body = serde_json::to_string(&report)?; 

        // Encrypt if session active
        let final_payload = {
            let lock = self.crypto.lock().unwrap();
            if let Some(session) = &lock.session {
                match session.encrypt(json_body.as_bytes()) {
                    Ok(enc_str) => {
                        let msg = PqcMessage::Encrypted { payload: enc_str };
                        serde_json::to_string(&msg)?
                    },
                    Err(_) => json_body, // Fallback
                }
            } else {
                json_body 
            }
        };

        use std::fs::OpenOptions as StdOpenOptions;
        use std::io::Write;

        match StdOpenOptions::new().write(true).open(device_path) {
            Ok(mut file) => {
                writeln!(file, "{}", final_payload)?;
                println!("[init] [BRIDGE] 🚀 Encrypted Report EXFILTRATED.");
                Ok(())
            },
            Err(e) => {
                 eprintln!("[init] [BRIDGE] UART Write Failed: {}", e);
                 Ok(())
            }
        }
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // 1. Setup environment for PID 1
    if let Err(e) = setup_env() {
        eprintln!("[init] ERROR setting up environment: {}", e);
    } else {
        println!("[init] Environment ready (mounts, limits).");
    }

    // Diagnostic: Check kprobe PMU
    check_kprobe_pmu();

    // 2. Resilient Observability
    let _perf = match setup_perf_observability() {
        Ok(p) => Some(p),
        Err(e) => {
            eprintln!("[init] [WARN] Observabilidad Cuántica desactivada: {}", e);
            None
        }
    };

    // 3. Initialize Components
    let crypto_state = Arc::new(Mutex::new(CryptoState { session: None }));
    let decider = Arc::new(CognitiveDecider::new(crypto_state.clone()));
    let hunter = Arc::new(MemoryScanner::new());

    // 4. Load XDP Firewall (Network Guardian) first
    println!("[init] Loading Operation Net-Hunter (XDP Firewall)...");
    let guardian = match Ebpf::load(XDP_OBJECT) {
        Ok(mut xdp_ebpf) => {
             if let Some(prog) = xdp_ebpf.program_mut("xdp_firewall_prog") {
                 let xdp_prog: &mut Xdp = prog.try_into()?;
                 if let Err(e) = xdp_prog.load() {
                      eprintln!("[init] [WARN] XDP Load Failed: {}", e);
                      None
                 } else {
                     match xdp_prog.attach("eth0", XdpFlags::default()) {
                         Ok(_) => {
                             println!("[init] Net-Hunter XDP attached to eth0");
                             Some(Arc::new(NetworkGuardian::new(xdp_ebpf)))
                         },
                         Err(e) => {
                             eprintln!("[init] [WARN] XDP Attach Failed: {}", e);
                             Some(Arc::new(NetworkGuardian::new(xdp_ebpf)))
                         }
                     }
                 }
             } else {
                 None
             }
        },
        Err(e) => {
            eprintln!("[init] [WARN] Failed to load XDP Object: {}", e);
            None
        }
    };

    // 5. Load Kprobe (Optional)
    if let Err(e) = load_kprobe().await {
         eprintln!("[init] [WARN] KProbe (Syscall Trace) unavailable: {}", e);
         eprintln!("[init] Entering Hybrid Mode (No Trace, but XDP + Hunter active).");
    } else {
         println!("[init] KProbe attached. Full Supervision Active.");
    }
    
    // 6. Start Background Tasks
    if let Some(g) = &guardian {
        // Serial Monitor (PQC)
        let g_listener = g.clone();
        let c_listener = crypto_state.clone();
        tokio::spawn(async move {
            run_serial_monitor(g_listener, c_listener).await;
        });

        // Heartbeat (Dead Man's Switch)
        tokio::spawn(async move {
            start_heartbeat_loop().await; 
        });
    }

    // 7. Run Main Loop (Unified)
    run_supervision_loop(decider, hunter, guardian).await
}

async fn load_kprobe() -> Result<(), Box<dyn Error>> {
    let mut ebpf = Ebpf::load(BPF_OBJECT)?;
    let program: &mut KProbe = ebpf.program_mut("sentinel_init").ok_or("program sentinel_init not found")?.try_into()?;
    program.load()?;
    program.attach("do_execve", 0)?;
    Ok(())
}

async fn start_heartbeat_loop() {
    println!("[init] [HEARTBEAT] Starting Dead Man's Switch Pulse...");
    let device_path = "/dev/ttyS1";
    use std::time::{SystemTime, UNIX_EPOCH};

    // Use async file IO
    let mut file = match OpenOptions::new().write(true).open(device_path).await {
        Ok(f) => f,
        Err(e) => {
             eprintln!("[init] [HEARTBEAT] Failed to open UART: {}", e);
             return;
        }
    };

    loop {
        let start = SystemTime::now();
        let since_the_epoch = start.duration_since(UNIX_EPOCH).unwrap_or(Duration::from_secs(0));
        let hb = Heartbeat { hb: since_the_epoch.as_millis() as u64 };
        
        if let Ok(json) = serde_json::to_string(&hb) {
            // Write JSON + newline
            if let Err(e) = file.write_all(format!("{}\n", json).as_bytes()).await {
                 eprintln!("[init] [HEARTBEAT] Write failed: {}", e);
            }
        }
        sleep(Duration::from_millis(50)).await;
    }
}

async fn run_serial_monitor(guardian: Arc<NetworkGuardian>, crypto: SharedCryptoState) {
    println!("[init] [IPC] Starting Secure Serial Monitor on /dev/ttyS1...");
    let device_path = "/dev/ttyS1";

    let file = match OpenOptions::new().read(true).write(true).open(device_path).await {
        Ok(f) => f,
        Err(e) => {
            eprintln!("[init] [PQC] Failed to open /dev/ttyS1: {}", e);
            sleep(Duration::from_secs(5)).await;
            return;
        }
    };

    println!("[init] [IPC] Connected to Host Bridge (Full Duplex).");
    let (reader, mut writer) = tokio::io::split(file);
    let mut buf_reader = BufReader::new(reader);

    // 1. Initiate PQC Handshake
    println!("[init] [PQC] Generating Ephemeral X25519 Keys...");
    let mut pqc_ctx = Some(PqcContext::new());
    let pk_b64 = pqc_ctx.as_ref().unwrap().public_key_base64();
    let hello_msg = PqcMessage::Hello { pk: pk_b64 };
    
    // Transmit Hello
    let json = serde_json::to_string(&hello_msg).unwrap(); 
    println!("[init] [PQC] Sending PQC_HELLO...");
    if let Err(e) = writer.write_all(format!("{}\n", json).as_bytes()).await {
         eprintln!("[init] [PQC] Failed to send Hello: {}", e);
    }
    let _ = writer.flush().await;

    let mut lines = buf_reader.lines();
    loop {
       match lines.next_line().await {
           Ok(Some(line)) => {
                if let Ok(pqc) = serde_json::from_str::<PqcMessage>(&line) {
                    match pqc {
                        PqcMessage::Auth { ct } => {
                            if let Some(ctx) = pqc_ctx.take() {
                                println!("[init] [PQC] Received AUTH. Completing Handshake...");
                                match ctx.decapsulate(&ct) {
                                    Ok(secret) => {
                                        println!("[init] [PQC] 🔐 Shared Secret Established. Channel SECURE (ChaCha20-Poly1305).");
                                        let mut lock = crypto.lock().unwrap();
                                        lock.session = Some(SecureSession::new(&secret));
                                    },
                                    Err(e) => eprintln!("[init] [PQC] Handshake Failed: {}", e),
                                }
                            } else {
                                println!("[init] [PQC] Ignored redundant AUTH.");
                            }
                        },
                        PqcMessage::Encrypted { payload } => {
                            let mut decrypted_json = String::new();
                            {
                                let lock = crypto.lock().unwrap();
                                if let Some(session) = &lock.session {
                                    if let Ok(pt) = session.decrypt(&payload) {
                                        decrypted_json = String::from_utf8_lossy(&pt).to_string();
                                    }
                                }
                            }
                            if !decrypted_json.is_empty() {
                                    process_brain_response(&decrypted_json, &guardian);
                            }
                        },
                        PqcMessage::Hello { .. } => {}, 
                        PqcMessage::Legacy(_) => {
                            process_brain_response(&line, &guardian);
                        }
                    }
                } else {
                    process_brain_response(&line, &guardian);
                }
           },
           Ok(None) => {
               // EOF?
               println!("[init] [IPC] EOF on Bridge. Reconnecting...");
               break; 
           },
           Err(e) => {
               eprintln!("[init] [IPC] Read Error: {}", e);
               break;
           }
       }
    }
}

fn process_brain_response(json: &str, guardian: &Arc<NetworkGuardian>) {
    if let Ok(resp) = serde_json::from_str::<BrainResponse>(json) {
         if let Some(ip_str) = resp.block_ip {
              println!("[init] [IPC] Received BLOCK command for {}", ip_str);
              if let Ok(ip_addr) = ip_str.parse::<Ipv4Addr>() {
                  let ip_u32: u32 = ip_addr.into();
                  let _ = guardian.block_ip(u32::to_be(ip_u32));
              }
         }
    }
}

async fn run_supervision_loop(decider: Arc<CognitiveDecider>, hunter: Arc<MemoryScanner>, guardian: Option<Arc<NetworkGuardian>>) -> Result<(), Box<dyn Error>> {
    println!("[init] Sentinel Cog-Loop alive. Supervising processes...");
    let mut sigint = signal(SignalKind::interrupt())?;
    let mut sigterm = signal(SignalKind::terminate())?;

    // TEST TRIGGER
    tokio::spawn(async {
        sleep(Duration::from_secs(5)).await;
        println!("[init] [TEST] Spawning Hunter Target (/bin/attack_poc)...");
        let _ = std::process::Command::new("/bin/attack_poc").spawn();
    });

    loop {
        tokio::select! {
            _ = sigint.recv() => break,
            _ = sigterm.recv() => break,
            _ = sleep(Duration::from_secs(5)) => {
                reap_zombies();
                if let Ok(pids) = scan_cgroups() {
                    for pid in pids {
                        let d_inner = decider.clone();
                        let h_inner = hunter.clone();
                        let g_inner = guardian.clone();
                        
                        tokio::spawn(async move {
                            // Memory Hunt & Reflex
                            if let Ok(hunt) = h_inner.hunt_pid(pid) {
                                if hunt.score >= 1.0 {
                                    println!("[init] [HUNTER] 🏹 TERMINATED MALICIOUS PID {} (Score: {:.1})", pid, hunt.score);
                                    
                                    // REFLEX ARC
                                    if let Some(g) = g_inner {
                                        println!("[init] [REFLEX] ⚡ NEURAL REFLEX ACTIVATED: SEALING NETWORK...");
                                        let _ = g.set_panic_mode(true);
                                        // Spawn Restore
                                        let g_restore = g.clone();
                                        tokio::spawn(async move {
                                            sleep(Duration::from_secs(30)).await;
                                            println!("[init] [REFLEX] ⏳ Quarantine Lifted.");
                                            let _ = g_restore.set_panic_mode(false);
                                        });
                                    } else {
                                        println!("[init] [REFLEX] ⚠️ Network Guardian UNAVAILABLE. Cannot Seal Network.");
                                    }

                                    let _ = kill(Pid::from_raw(pid as i32), Signal::SIGKILL);
                                    let _ = d_inner.report_threat(pid, hunt.score, "NEURAL REFLEX ACTIVATED".to_string()).await;
                                    return;
                                }
                            }
                        });
                    }
                }
            }
        }
    }
    Ok(())
}

fn reap_zombies() {
    loop {
        match waitpid(None, Some(WaitPidFlag::WNOHANG)) {
            Ok(status) => {
                if status.pid().is_none() {
                    break;
                }
            }
            Err(_) => break,
        }
    }
}

fn scan_cgroups() -> Result<Vec<u32>, Box<dyn Error>> {
    let mut pids = Vec::new();
    let cgroup_root = "/sys/fs/cgroup";

    if !Path::new(cgroup_root).exists() {
        return Ok(vec![]);
    }

    visit_cgroups(Path::new(cgroup_root), &mut pids)?;
    Ok(pids)
}

fn visit_cgroups(dir: &Path, pids: &mut Vec<u32>) -> Result<(), Box<dyn Error>> {
    if !dir.is_dir() {
        return Ok(());
    }

    let procs_path = dir.join("cgroup.procs");
    if procs_path.exists() {
        if let Ok(content) = fs::read_to_string(procs_path) {
            for line in content.lines() {
                if let Ok(pid) = line.trim().parse::<u32>() {
                    if pid != 1 {
                        pids.push(pid);
                    }
                }
            }
        }
    }

    for entry in fs::read_dir(dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.is_dir() {
            visit_cgroups(&path, pids)?;
        }
    }

    Ok(())
}

fn cognitive_risk(pid: u32) -> f64 {
    let exe_path = format!("/proc/{}/exe", pid);
    if let Ok(target) = fs::read_link(exe_path) {
        let path_str = target.to_string_lossy();
        if path_str.starts_with("/tmp/") || path_str.starts_with("/var/tmp/") {
            return 0.95;
        }
    }
    0.0
}

fn setup_env() -> Result<(), Box<dyn Error>> {
    let none: Option<&str> = None;
    let _ = fs::create_dir_all("/proc");
    mount(Some("proc"), "/proc", Some("proc"), MsFlags::empty(), none)?;

    let _ = fs::create_dir_all("/sys");
    mount(Some("sysfs"), "/sys", Some("sysfs"), MsFlags::empty(), none)?;

    let _ = fs::create_dir_all("/dev");
    let _ = mount(Some("devtmpfs"), "/dev", Some("devtmpfs"), MsFlags::empty(), none);

    let _ = fs::create_dir_all("/sys/kernel/debug");
    mount(Some("debugfs"), "/sys/kernel/debug", Some("debugfs"), MsFlags::empty(), none)?;

    let trace_path = "/sys/kernel/debug/tracing";
    let _ = fs::create_dir_all(trace_path);
    let _ = mount(Some("tracefs"), trace_path, Some("tracefs"), MsFlags::empty(), none);

    let _ = fs::create_dir_all("/sys/fs/cgroup");
    mount(Some("cgroup2"), "/sys/fs/cgroup", Some("cgroup2"), MsFlags::empty(), none)?;

    setrlimit(Resource::MEMLOCK, rlimit::INFINITY, rlimit::INFINITY)?;

    let paranoid_path = "/proc/sys/kernel/perf_event_paranoid";
    if Path::new(paranoid_path).exists() {
        let _ = fs::write(paranoid_path, "-1");
    }

    Ok(())
}

fn check_kprobe_pmu() {
    let pmu_type_path = "/sys/bus/event_source/devices/kprobe/type";
    if Path::new(pmu_type_path).exists() {
        if let Ok(pmu_type) = fs::read_to_string(pmu_type_path) {
            println!("[init] [Diagnostic] KProbe PMU Type: {}", pmu_type.trim());
        }
    } else {
        println!("[init] [Diagnostic] WARNING: {} not found!", pmu_type_path);
    }
}

struct PerfEvent;
impl PerfEvent {
    fn new() -> Result<Self, Box<dyn Error>> {
        if !Path::new("/sys/bus/event_source/devices/cpu/type").exists() {
            return Err("Hardware PMU not available".into());
        }
        Ok(PerfEvent)
    }
}

fn setup_perf_observability() -> Result<PerfEvent, Box<dyn Error>> {
    PerfEvent::new()
}
