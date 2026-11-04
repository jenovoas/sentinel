// Sentinel Benchmark Suite (Rust, S60 puro, sin floats en lógica de medición).
// Fases por CLI: idle | load
//   idle: sin carga de fondo
//   load: se asume carga masiva de CPU ya lanzada por el llamador
// Mide: latencia de tick del cristal, deriva temporal vs CLOCK_MONOTONIC,
// I/O del lattice (ResonantMatrix), temp térmica y CPU del sistema.

use me60os_core::quantum_core::IsochronousClock;
use me60os_core::resonant_matrix::ResonantMatrix;
use me60os_core::spa::SPA;
use std::time::Instant;

fn cpu_temp_millicelsius() -> i64 {
    std::fs::read_to_string("/sys/class/thermal/thermal_zone0/temp")
        .ok()
        .and_then(|value| value.trim().parse::<i64>().ok())
        .unwrap_or(-1000)
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
    let mut intervals: Vec<u64> =
        Vec::with_capacity(usize::try_from(ticks).expect("ticks fuera de usize"));
    let mut last = Instant::now();
    for _ in 0..ticks {
        clock.tick_internal();
        let now = Instant::now();
        intervals.push(
            u64::try_from(now.duration_since(last).as_nanos()).expect("intervalo fuera de u64"),
        );
        last = now;
    }
    intervals.sort_unstable();
    let min = intervals.first().copied().unwrap_or(0);
    let max = intervals.last().copied().unwrap_or(0);
    let avg =
        intervals.iter().sum::<u64>() / u64::try_from(intervals.len()).expect("muestra vacía");
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
    let elapsed = start.elapsed().as_nanos();
    let expected = u128::from(ticks) * u128::from(clock.tick_interval_ns);
    let drift = elapsed.abs_diff(expected);
    let ppm = drift * 1_000_000 / expected.max(1);
    println!(
        "[{}] crystal drift {} ticks: elapsed={}ns expected={}ns drift={}ns ({} ppm)",
        phase, ticks, elapsed, expected, drift, ppm
    );
}

fn lattice_io(phase: &str, ops: u64) {
    // Tamaño moderado para que el bench sea rápido pero representativo
    let n = 2000usize;
    let mut lattice = ResonantMatrix::new(n);
    let start = Instant::now();
    for i in 0..ops {
        let node = usize::try_from(i % u64::try_from(n).expect("nodos fuera de u64"))
            .expect("índice fuera de usize");
        lattice.inject(
            node,
            i64::try_from(i % 1000).expect("valor fuera de i64") - 500,
        );
        let _e: SPA = lattice.total_energy();
    }
    let elapsed = start.elapsed().as_nanos();
    let per_op = elapsed / (ops as u128).max(1);
    println!(
        "[{}] lattice I/O: {} ops en {}ns => {} ns/op (~{} ops/ms)",
        phase,
        ops,
        elapsed,
        per_op,
        u128::from(ops) * 1_000_000 / elapsed.max(1)
    );
}

fn main() {
    let phase = std::env::args().nth(1).unwrap_or_else(|| "idle".into());
    println!("=== SENTINEL BENCH [{}] ===", phase);
    let (b0, t0) = cpu_busy_total();
    let initial_temp = cpu_temp_millicelsius();
    println!(
        "[{}] temp_inicial={}.{:03}C",
        phase,
        initial_temp / 1000,
        initial_temp.abs() % 1000
    );

    crystal_latency(&phase, 600);
    crystal_drift(&phase, 600);
    lattice_io(&phase, 50_000);

    let (b1, t1) = cpu_busy_total();
    let busy = b1.saturating_sub(b0);
    let total = t1.saturating_sub(t0).max(1);
    let cpu_tenths_pct = u128::from(busy) * 1000 / u128::from(total);
    let final_temp = cpu_temp_millicelsius();
    println!(
        "[{}] cpu_sistema_durante_bench={}.{}% temp_final={}.{:03}C",
        phase,
        cpu_tenths_pct / 10,
        cpu_tenths_pct % 10,
        final_temp / 1000,
        final_temp.abs() % 1000
    );
    println!("=== FIN [{}] ===", phase);
}
