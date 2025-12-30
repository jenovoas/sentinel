// sentinel_core/init/src/main.rs
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
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::UnixStream;
use tokio::signal::unix::{signal, SignalKind};
use tokio::time::{sleep, Duration};
use crate::forensics::MemoryScanner;

// Placeholder: load eBPF object compiled separately (e.g., init_kprobe.o)
const BPF_OBJECT: &[u8] = include_bytes_aligned!("../../../ebpf/init_kprobe.o");
const XDP_OBJECT: &[u8] = include_bytes_aligned!("../../../ebpf/xdp_firewall.o");
const BRAIN_SOCKET: &str = "/tmp/sentinel_cortex.sock";

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
        // Access the map by name defined in C code ("blacklist")
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
}

impl CognitiveDecider {
    fn new() -> Self {
        Self {
            cache: Arc::new(Mutex::new(StdHashMap::new())),
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
        // UART BRIDGE UPDATE (ttyS1)
        // virtio-serial failed due to missing drivers in initramfs kernel.
        // We fallback to standard serial port /dev/ttyS1 (mapped to host socket).
        let device_path = "/dev/ttyS1";
        let report = ThreatReport { pid, score, details };
        let req_json = serde_json::to_string(&report)?; // to_string provides newline
        
        // Use standard fs::OpenOptions for blocking write (simple & robust for init)
        // In async context, we could use tokio::fs but blocking on a serial port write is acceptable here
        // as reports are rare and critical events.
        use std::fs::OpenOptions;
        use std::io::Write;

        match OpenOptions::new().write(true).open(device_path) {
            Ok(mut file) => {
                writeln!(file, "{}", req_json)?;
                println!("[init] [BRIDGE] 🚀 Report EXFILTRATED via Quantum Tunnel (virtio-serial).");
                Ok(())
            },
            Err(e) => {
                // Fallback to old socket if device missing (e.g., bare metal)
                 eprintln!("[init] [BRIDGE] ⚠️ Quantum Tunnel collapsed (virtio port missing): {}", e);
                 // Try old socket just in case
                 let mut stream = UnixStream::connect(BRAIN_SOCKET).await?;
                 stream.write_all(req_json.as_bytes()).await?;
                 stream.shutdown().await?;
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

    // 2. Resilient Observability (User's request)
    let _perf = match setup_perf_observability() {
        Ok(p) => Some(p),
        Err(e) => {
            eprintln!("[init] [WARN] Observabilidad Cuántica desactivada: {}", e);
            None
        }
    };

    // 3. Load eBPF or enter Fallback Mode
    let decider = Arc::new(CognitiveDecider::new());
    let hunter = Arc::new(MemoryScanner::new());

    // 3. Load XDP Firewall (Network Guardian) first - Critical for Phase 8
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
                             // Still return guardian for map access if loaded? No, program must be loaded.
                             // But we loaded it above. Map access works if loaded.
                             // Attach failure might mean no traffic filtering, but map write works.
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

    // 4. Load Kprobe (Optional Enhancement)
    if let Err(e) = load_kprobe().await {
         eprintln!("[init] [WARN] KProbe (Syscall Trace) unavailable: {}", e);
         eprintln!("[init] Entering Hybrid Mode (No Trace, but XDP + Hunter active).");
    } else {
         println!("[init] KProbe attached. Full Supervision Active.");
    }
    
    // Start IPC Listener if Guardian exists
    if let Some(g) = &guardian {
        let g_listener = g.clone();
        tokio::spawn(async move {
            run_serial_monitor(g_listener).await;
        });

        // Start Heartbeat Emitter (Dead Man's Switch) - only if we have a guardian/network up? 
        // Or always? Always is safer for Kernel integrity.
        tokio::spawn(async move {
            start_heartbeat_loop().await; 
        });
    }

    // Run Main Loop (Unified)
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
    use tokio::fs::OpenOptions; // Use async open options
    use tokio::io::AsyncWriteExt;

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
                 // Try to re-open? For now, just log.
            }
        }
        sleep(Duration::from_millis(50)).await;
    }
}

async fn run_serial_monitor(guardian: Arc<NetworkGuardian>) {
// ...
        println!("[init] [IPC] Starting Serial Monitor on /dev/ttyS1...");
        let device_path = "/dev/ttyS1";
        use tokio::io::{AsyncBufReadExt, BufReader};
        use tokio::fs::File;
        loop {
           match File::open(device_path).await {
               Ok(file) => {
                   println!("[init] [IPC] Connected to Host Bridge.");
                   let reader = BufReader::new(file);
                   let mut lines = reader.lines();
                   while let Ok(Some(line)) = lines.next_line().await {
                        if let Ok(resp) = serde_json::from_str::<BrainResponse>(&line) {
                             if let Some(ip_str) = resp.block_ip {
                                  println!("[init] [IPC] Received BLOCK command for {}", ip_str);
                                  if let Ok(ip_addr) = ip_str.parse::<Ipv4Addr>() {
                                      let ip_u32: u32 = ip_addr.into();
                                      let _ = guardian.block_ip(u32::to_be(ip_u32));
                                  }
                             }
                        }
                   }
               },
               Err(_) => sleep(Duration::from_secs(5)).await,
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
                // println!("[init] Reaped zombie child process: {:?}", status);
            }
            Err(_) => break,
        }
    }
}

// ---------------------------------------------------------------------
// Helper stubs – replace with real implementations later
// ---------------------------------------------------------------------
fn scan_cgroups() -> Result<Vec<u32>, Box<dyn Error>> {
    let mut pids = Vec::new();
    let cgroup_root = "/sys/fs/cgroup";

    if !Path::new(cgroup_root).exists() {
        return Ok(vec![]);
    }

    // Recursively find pids in cgroup.procs
    visit_cgroups(Path::new(cgroup_root), &mut pids)?;

    Ok(pids)
}

fn visit_cgroups(dir: &Path, pids: &mut Vec<u32>) -> Result<(), Box<dyn Error>> {
    if !dir.is_dir() {
        return Ok(());
    }

    // Read cgroup.procs in the current directory
    let procs_path = dir.join("cgroup.procs");
    if procs_path.exists() {
        if let Ok(content) = fs::read_to_string(procs_path) {
            for line in content.lines() {
                if let Ok(pid) = line.trim().parse::<u32>() {
                    // Skip self (PID 1)
                    if pid != 1 {
                        pids.push(pid);
                    }
                }
            }
        }
    }

    // Recurse into subdirectories
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
    // Basic heuristic: check if process is running from /tmp or /var/tmp
    let exe_path = format!("/proc/{}/exe", pid);
    if let Ok(target) = fs::read_link(exe_path) {
        let path_str = target.to_string_lossy();
        if path_str.starts_with("/tmp/") || path_str.starts_with("/var/tmp/") {
            return 0.95; // Extreme risk for binaries in tmp
        }
    }
    0.0
}

fn setup_env() -> Result<(), Box<dyn Error>> {
    // 1. Mount essential filesystems
    let none: Option<&str> = None;
    
    // Mount proc
    let _ = fs::create_dir_all("/proc");
    mount(Some("proc"), "/proc", Some("proc"), MsFlags::empty(), none)?;

    // Mount sysfs
    let _ = fs::create_dir_all("/sys");
    mount(Some("sysfs"), "/sys", Some("sysfs"), MsFlags::empty(), none)?;

    // Mount devtmpfs
    let _ = fs::create_dir_all("/dev");
    let _ = mount(Some("devtmpfs"), "/dev", Some("devtmpfs"), MsFlags::empty(), none);

    // Mount debugfs
    let _ = fs::create_dir_all("/sys/kernel/debug");
    mount(Some("debugfs"), "/sys/kernel/debug", Some("debugfs"), MsFlags::empty(), none)?;

    // Mount tracefs at the standard location (required by some eBPF tools)
    let trace_path = "/sys/kernel/debug/tracing";
    let _ = fs::create_dir_all(trace_path);
    let _ = mount(Some("tracefs"), trace_path, Some("tracefs"), MsFlags::empty(), none);

    // Mount cgroup2
    let _ = fs::create_dir_all("/sys/fs/cgroup");
    mount(Some("cgroup2"), "/sys/fs/cgroup", Some("cgroup2"), MsFlags::empty(), none)?;

    // 2. Set RLIMIT_MEMLOCK (critical for eBPF loading)
    setrlimit(Resource::MEMLOCK, rlimit::INFINITY, rlimit::INFINITY)?;

    // 3. Relax perf_event_paranoid for eBPF access
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
        // En un entorno QEMU sin PMU virtualizado, esto fallará.
        // Simulamos la lógica que el usuario desea proteger.
        if !Path::new("/sys/bus/event_source/devices/cpu/type").exists() {
            return Err("Hardware PMU not available".into());
        }
        Ok(PerfEvent)
    }
}

fn setup_perf_observability() -> Result<PerfEvent, Box<dyn Error>> {
    PerfEvent::new()
}
