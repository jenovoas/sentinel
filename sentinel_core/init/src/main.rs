// sentinel_core/init/src/main.rs
mod forensics;

use aya::programs::KProbe;
use aya::{Ebpf, include_bytes_aligned};
use nix::mount::{mount, MsFlags};
use nix::sys::signal::{kill, Signal};
use nix::sys::wait::{waitpid, WaitPidFlag};
use nix::unistd::Pid;
use rlimit::{setrlimit, Resource};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::error::Error;
use std::fs;
use std::path::Path;
use std::sync::{Arc, Mutex};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::UnixStream;
use tokio::signal::unix::{signal, SignalKind};
use tokio::time::{sleep, Duration};
use crate::forensics::MemoryScanner;

// Placeholder: load eBPF object compiled separately (e.g., init_kprobe.o)
const BPF_OBJECT: &[u8] = include_bytes_aligned!("../../../ebpf/init_kprobe.o");
const BRAIN_SOCKET: &str = "/tmp/sentinel_cortex.sock";

#[derive(Serialize)]
struct BrainRequest {
    pid: u32,
    path: String,
}

#[derive(Deserialize)]
struct BrainResponse {
    allow: bool,
}

struct CognitiveDecider {
    cache: Arc<Mutex<HashMap<String, bool>>>,
}

impl CognitiveDecider {
    fn new() -> Self {
        Self {
            cache: Arc::new(Mutex::new(HashMap::new())),
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
        let mut stream = UnixStream::connect(BRAIN_SOCKET).await?;
        let req = BrainRequest { pid, path: path.to_string() };
        let req_json = serde_json::to_vec(&req)?;
        
        stream.write_all(&req_json).await?;
        stream.shutdown().await?;

        let mut response_json = Vec::new();
        stream.read_to_end(&mut response_json).await?;
        
        let resp: BrainResponse = serde_json::from_slice(&response_json)?;
        Ok(resp.allow)
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

    if let Err(e) = load_and_run(decider.clone(), hunter.clone()).await {
        eprintln!("[init] Cog-Loop Error: {}", e);
        eprintln!("[init] eBPF unavailable. Entering Heuristic Fallback Mode...");
        fallback_run(decider, hunter).await?;
    }

    Ok(())
}

async fn fallback_run(decider: Arc<CognitiveDecider>, hunter: Arc<MemoryScanner>) -> Result<(), Box<dyn Error>> {
    println!("[init] Sentinel Heuristic-Loop active. Supervising scans...");

    let mut sigint = signal(SignalKind::interrupt())?;
    let mut sigterm = signal(SignalKind::terminate())?;

    loop {
        tokio::select! {
            _ = sigint.recv() => {
                println!("[init] Received SIGINT, shutting down...");
                break;
            }
            _ = sigterm.recv() => {
                println!("[init] Received SIGTERM, shutting down...");
                break;
            }
            _ = sleep(Duration::from_secs(5)) => {
                reap_zombies();
                if let Ok(pids) = scan_cgroups() {
                    for pid in pids {
                        let d_inner = decider.clone();
                        let h_inner = hunter.clone();
                        
                        tokio::spawn(async move {
                            // 1. Cognitive Risk Scan
                            let risk = d_inner.check_risk(pid).await;
                            
                            // 2. Proactive Memory Hunt (The Hunter)
                            if let Ok(result) = h_inner.hunt_pid(pid) {
                                if result.score >= 1.0 {
                                    println!("[init] [HUNTER] THREAT: PID {} score={:.1}", pid, result.score);
                                    let _ = kill(Pid::from_raw(pid as i32), Signal::SIGKILL);
                                    return;
                                }
                            }

                            if risk > 0.9 {
                                let _ = kill(Pid::from_raw(pid as i32), Signal::SIGKILL);
                                println!("[init] 🚫 (Fallback) KILLED PID {} due to risk ({:.2})", pid, risk);
                            }
                        });
                    }
                }
            }
        }
    }
    Ok(())
}

async fn load_and_run(decider: Arc<CognitiveDecider>, hunter: Arc<MemoryScanner>) -> Result<(), Box<dyn Error>> {
    // Load eBPF program
    let mut ebpf = Ebpf::load(BPF_OBJECT)?;
    let program: &mut KProbe = ebpf.program_mut("sentinel_init").ok_or("program sentinel_init not found")?.try_into()?;
    program.load()?;
    program.attach("do_execve", 0)?;

    println!("[init] Sentinel Cog-Loop alive. Supervising processes...");

    // Signal handlers for graceful shutdown and zombie reaping
    let mut sigint = signal(SignalKind::interrupt())?;
    let mut sigterm = signal(SignalKind::terminate())?;

    loop {
        tokio::select! {
            _ = sigint.recv() => {
                println!("[init] Received SIGINT, shutting down...");
                break;
            }
            _ = sigterm.recv() => {
                println!("[init] Received SIGTERM, shutting down...");
                break;
            }
            _ = sleep(Duration::from_secs(5)) => {
                // Periodically reap zombies
                reap_zombies();

                // Scan cgroup processes
                if let Ok(pids) = scan_cgroups() {
                    for pid in pids {
                        let d_inner = decider.clone();
                        let h_inner = hunter.clone();
                        
                        tokio::spawn(async move {
                            // 1. Cognitive Risk
                            let risk = d_inner.check_risk(pid).await;
                            
                            // 2. Memory Hunt
                            if let Ok(hunt) = h_inner.hunt_pid(pid) {
                                if hunt.score >= 1.0 {
                                    println!("[init] [HUNTER] 🏹 TERMINATED MALICIOUS PID {} (Score: {:.1})", pid, hunt.score);
                                    let _ = kill(Pid::from_raw(pid as i32), Signal::SIGKILL);
                                    return;
                                }
                            }

                            if risk > 0.9 {
                                let _ = kill(Pid::from_raw(pid as i32), Signal::SIGKILL);
                                println!("[init] 🚫 Cog-Loop KILLED PID {} due to high cognitive risk ({:.2})", pid, risk);
                            }
                        });
                    }
                }
            }
        }
    }

    println!("[init] Shutdown complete.");
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


// ---------------------------------------------------------------------
// Unit Tests
// ---------------------------------------------------------------------
#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::tempdir;

    #[test]
    fn test_cognitive_risk_low() {
        // PID 1 surely doesn't run from /tmp (usually /sbin/init or similar)
        let risk = cognitive_risk(1);
        assert!(risk < 0.1);
    }

    #[test]
    fn test_visit_cgroups_mock() -> Result<(), Box<dyn Error>> {
        let dir = tempdir()?;
        let sub_dir = dir.path().join("subgroup1");
        fs::create_dir(&sub_dir)?;
        
        let procs_file = sub_dir.join("cgroup.procs");
        fs::write(procs_file, "123\n456\n")?;

        let mut pids = Vec::new();
        visit_cgroups(dir.path(), &mut pids)?;

        assert!(pids.contains(&123));
        assert!(pids.contains(&456));
        assert_eq!(pids.len(), 2);

        Ok(())
    }
}
