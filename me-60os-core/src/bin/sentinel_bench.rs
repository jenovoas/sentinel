// Sentinel Benchmark Suite (Rust, S60 puro, sin floats en lógica de medición).
// Fases por CLI: idle | load
//   idle: sin carga de fondo
//   load: se asume carga masiva de CPU ya lanzada por el llamador
// Mide: latencia de tick del cristal, deriva temporal vs CLOCK_MONOTONIC,
// I/O del lattice (ResonantMatrix), temp térmica y CPU del sistema.

use me60os_core::quantum_core::IsochronousClock;
use me60os_core::resonant_matrix::ResonantMatrix;
use me60os_core::spa::SPA;
use std::time::{Duration, Instant};

fn cpu_temp() -> f64 {
    std::fs::read_to_string("/sys/class/thermal/thermal_zone0/temp")
        .ok()
        .and_then(|s| s.trim().parse::<f64>().ok())
        .map(|c| c / 1000.0)
        .unwrap_or(-1.0)
}

fn cpu_busy_total() -> (u64, u64) {
    // (busy_jiffies, total_jiffies) del primer linea de /proc/stat
    let line = match std::fs::read_to_string("/proc/stat") {
        Ok(c) => c,
        Err(_) => return (0, 0),
    };
    let first = line.lines().next().unwrap_or("");
    let parts: Vec<u64> = first
        .split_whitespace()
        .skip(1)
        .filter_map(|x| x.parse::<u64>().ok())
        .collect();
    if parts.len() < 4 {
        return (0, 0);
    }
    let idle = parts[3];
    let total: u64 = parts.iter().sum();
    (total - idle, total)
}

fn crystal_latency(phase: &str, ticks: u64) {
    let mut clock = IsochronousClock::new_internal();
    let mut intervals: Vec<u64> = Vec::with_capacity(ticks as usize);
    let mut last = Instant::now();
    for _ in 0..ticks {
        clock.tick_internal();
        let now = Instant::now();
        intervals.push(now.duration_since(last).as_nanos() as u64);
        last = now;
    }
    intervals.sort_unstable();
    let min = intervals.first().copied().unwrap_or(0);
    let max = intervals.last().copied().unwrap_or(0);
    let avg = intervals.iter().sum::<u64>() / intervals.len() as u64;
    let p99 = intervals[(intervals.len() * 99 / 100).min(intervals.len() - 1)];
    println!(
        "[{}] crystal tick interval ns: min={} avg={} p99={} max={} (target={})",
        phase, min, avg, p99, max, clock.tick_interval_ns
    );
}

fn crystal_drift(phase: &str, ticks: u64) {
    let mut clock = IsochronousClock::new_internal();
    let start = Instant::now();
    for _ in 0..ticks {
        clock.tick_internal();
    }
    let elapsed = start.elapsed().as_nanos() as i128;
    let expected = ticks as i128 * clock.tick_interval_ns as i128;
    let drift = (elapsed - expected).abs();
    let ppm = (drift as f64 / expected as f64) * 1_000_000.0;
    println!(
        "[{}] crystal drift {} ticks: elapsed={}ns expected={}ns drift={}ns ({:.2} ppm)",
        phase, ticks, elapsed, expected, drift, ppm
    );
}

fn lattice_io(phase: &str, ops: u64) {
    // Tamaño moderado para que el bench sea rápido pero representativo
    let n = 2000usize;
    let mut lattice = ResonantMatrix::new(n);
    let start = Instant::now();
    for i in 0..ops {
        lattice.inject((i as usize) % n, ((i % 1000) as i64) - 500);
        let _e: SPA = lattice.total_energy();
    }
    let elapsed = start.elapsed().as_nanos();
    let per_op = elapsed / (ops as u128).max(1);
    println!(
        "[{}] lattice I/O: {} ops en {}ns => {} ns/op (~{:.1} ops/ms)",
        phase,
        ops,
        elapsed,
        per_op,
        (ops as f64) / elapsed as f64 * 1e6
    );
}

fn main() {
    let phase = std::env::args().nth(1).unwrap_or_else(|| "idle".into());
    println!("=== SENTINEL BENCH [{}] ===", phase);
    let (b0, t0) = cpu_busy_total();
    println!("[{}] temp_inicial={:.2}C", phase, cpu_temp());

    crystal_latency(&phase, 600);
    crystal_drift(&phase, 600);
    lattice_io(&phase, 50_000);

    let (b1, t1) = cpu_busy_total();
    let busy = (b1 as i128 - b0 as i128).max(0) as u64;
    let tot = (t1 as i128 - t0 as i128).max(1) as u64;
    let cpu_pct = (busy as f64 / tot as f64) * 100.0;
    println!(
        "[{}] cpu_sistema_durante_bench={:.1}% temp_final={:.2}C",
        phase,
        cpu_pct,
        cpu_temp()
    );
    println!("=== FIN [{}] ===", phase);
    // Evitar warning de import no usado
    let _ = Duration::from_secs(0);
}
