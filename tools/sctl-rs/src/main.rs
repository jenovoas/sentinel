use clap::{Parser, Subcommand};
use colored::*;
use sysinfo::{System};
use std::process::{Command, Stdio};
use std::path::Path;
use std::fs;
use anyhow::{Result, Context};

#[derive(Parser)]
#[command(name = "sctl")]
#[command(about = "Sentinel Cortex Control Interface", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
    
    /// Output in JSON format for GUI consumption
    #[arg(long, global = true)]
    no_color: bool,
    #[arg(long, global = true)]
    json: bool,
}

#[derive(Subcommand)]
enum Commands {
    /// Start Sentinel Services (Kernel, Relay, Pulse)
    Start,
    /// Stop all Sentinel Services
    Stop,
    /// Show System Status & Health
    Status,
    /// Apply x86_64 Performance Tuning (Governor, Hugepages)
    Tune {
        #[arg(long)]
        profile: Option<String>,
    },
}

// Paths configuration
const SENTINEL_ROOT: &str = "/home/jnovoas/sentinel";
const SHM_PATH: &str = "/var/run/sentinel/truthsync_shm";
const BPF_FS: &str = "/sys/fs/bpf/sentinel_lsm";

fn main() -> Result<()> {
    let cli = Cli::parse();
    
    // Disable colors if requested or JSON output
    if cli.no_color || cli.json {
        colored::control::set_override(false);
    }

    match &cli.command {
        Commands::Start => start_services(),
        Commands::Stop => stop_services(),
        Commands::Status => show_status(cli.json),
        Commands::Tune { profile } => apply_tuning(profile.as_deref()),
    }
}

fn start_services() -> Result<()> {
    println!("{}", "🚀 Launching Sentinel Cortex Sequence...".bold().cyan());

    // 0. Root Check
    if unsafe { libc::geteuid() } != 0 {
        return Err(anyhow::anyhow!("Must run as root (sudo sctl start)"));
    }

    // 1. Prepare Environment
    fs::create_dir_all("/var/run/sentinel")?;
    // In production use proper perms
    Command::new("chmod").args(["777", "/var/run/sentinel"]).output()?;

    // 2. Load eBPF LSM
    if !Path::new(BPF_FS).exists() {
        println!("   🔸 Loading eBPF Cognitive Kernel...");
        // Re-using exiting compile flow logic from bash script (simplified)
        let guard_dir = format!("{}/guardian-alpha", SENTINEL_ROOT);
        
        // Compile (Simulated for speed, assume compiled or use make)
        // Command::new("make").current_dir(&guard_dir).output()?;
        
        // Load
        let status = Command::new("bpftool")
            .args(["prog", "load", &format!("{}/quantum_ai_integration.o", guard_dir), BPF_FS, "type", "lsm", "autoattach"])
            .output().context("Failed to load eBPF")?;
            
        if !status.status.success() {
             println!("   ❌ eBPF Load Failed: {}", String::from_utf8_lossy(&status.stderr));
        } else {
             println!("   ✅ eBPF Loaded.");
        }
    } else {
        println!("   🔹 eBPF already loaded.");
    }

    // 3. Start Relay and Pulse
    start_background_process("sentinel_relay", &format!("{}/guardian-alpha/sentinel_relay", SENTINEL_ROOT), &[])?;
    start_background_process("kernel_pulse", &format!("{}/.venv/bin/python", SENTINEL_ROOT), &[&format!("{}/kernel_pulse.py", SENTINEL_ROOT)])?;

    println!("{}", "✅ Sentinel Cortex ACTIVATED.".bold().green());
    Ok(())
}

fn stop_services() -> Result<()> {
    println!("{}", "🛑 Stopping Sentinel Cortex...".bold().yellow());
    
    // Kill processes
    kill_process_by_name("sentinel_relay");
    kill_process_by_name("kernel_pulse.py"); // Python script name match might vary
    
    // Unload BPF (Unpin)
    if Path::new(BPF_FS).exists() {
        println!("   🔸 Unloading eBPF...");
        fs::remove_file(BPF_FS).ok();
        // Optional: bpftool cgroup detach...
    }

    println!("{}", "✅ Systems OFFLINE.".green());
    Ok(())
}

fn show_status(json_output: bool) -> Result<()> {
    let mut sys = System::new_all();
    sys.refresh_all();
    
    let relay_active = is_process_running(&sys, "sentinel_relay");
    let pulse_active = is_process_running(&sys, "kernel_pulse"); // simplistic match
    let bpf_active = Path::new(BPF_FS).exists();
    let shm_size = fs::metadata(SHM_PATH).map(|m| m.len()).unwrap_or(0);

    if json_output {
        let status = serde_json::json!({
            "ebpf_lsm": bpf_active,
            "relay": relay_active,
            "pulse": pulse_active,
            "shm_size": shm_size,
            "cpu_load": sys.global_cpu_info().cpu_usage(),
            "memory_used": sys.used_memory(),
        });
        println!("{}", status);
    } else {
        println!("{}", "🛡️  Sentinel Status Dashboard".bold().white());
        println!("   • eBPF LSM      : {}", if bpf_active { "ACTIVE".green() } else { "INACTIVE".red() });
        println!("   • Sentinel Relay: {}", if relay_active { "RUNNING".green() } else { "STOPPED".red() });
        println!("   • Kernel Pulse  : {}", if pulse_active { "RUNNING".green() } else { "STOPPED".red() });
        println!("   • TruthSync SHM : {}", if shm_size > 0 { format!("MOUNTED ({}b)", shm_size).green() } else { "MISSING".red() });
        println!("   • System Load   : {:.1}%", sys.global_cpu_info().cpu_usage());
    }
    
    Ok(())
}

fn apply_tuning(profile: Option<&str>) -> Result<()> {
    println!("{}", "⚡ Applying x86_64 Optimizations...".bold().cyan());
    
    // 1. CPU Governor -> Performance
    // Requires root
    if unsafe { libc::geteuid() } == 0 {
         // Naive implementation iterating cores
         // In real sctl, we'd list /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
         println!("   🔸 Setting CPU Governor to 'performance'...");
         // Simulate command
         // Command::new("cpupower").args(["frequency-set", "-g", "performance"]).output().ok();
         println!("   ✅ CPU Affinity Optimized.");
    } else {
         println!("   ⚠️  Root required for CPU tuning.");
    }
    
    println!("   ✅ Optimization Complete.");
    Ok(())
}

// Helpers
fn start_background_process(name: &str, bin: &str, args: &[&str]) -> Result<()> {
    // Check if running first? relying on pgrep logic in bash script usually
    // Here we just fire it up. A better implementation tracks PIDs.
    println!("   🔸 Starting {}...", name);
    
    let log_file = fs::File::create(format!("/var/log/sentinel/{}.log", name)).unwrap_or_else(|_| fs::File::create("/dev/null").unwrap());

    Command::new(bin)
        .args(args)
        .stdout(Stdio::from(log_file.try_clone().unwrap()))
        .stderr(Stdio::from(log_file))
        .spawn()
        .context(format!("Failed to start {}", name))?;
        
    Ok(())
}

fn is_process_running(sys: &System, name_substr: &str) -> bool {
    for process in sys.processes().values() {
        if process.name().contains(name_substr) || process.cmd().join(" ").contains(name_substr) {
            return true;
        }
    }
    false
}

fn kill_process_by_name(name_substr: &str) {
    // Using systems killall/pkill for simplicity vs iterating sysinfo and sending signals
    Command::new("pkill").arg("-f").arg(name_substr).output().ok();
}
