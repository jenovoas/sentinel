// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! 🛡️ SENTINEL BENCH — SALTO-17 PREDICTIVO (Kernel No-Markoviano vs Sin Kernel)
//!
//! Compara drift del cristal bajo carga CON vs SIN kernel no-Markoviano (Nandi 2026).
//! Mide: latencia tick, deriva temporal vs CLOCK_MONOTONIC, I/O lattice, CPU.

use me60os_core::quantum_core::IsochronousClock;
use me60os_core::quantum_core::S60PID;
use me60os_core::resonant_matrix::ResonantMatrix;
use me60os_core::spa::SPA;
use std::thread;
use std::time::{Duration, Instant};

fn cpu_temp_millicelsius() -> i64 {
    std::fs::read_to_string("/sys/class/thermal/thermal_zone0/temp")
        .ok()
        .and_then(|value| value.trim().parse::<i64>().ok())
        .unwrap_or(-1000)
}

fn cpu_busy_total() -> (u64, u64) {
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

fn crystal_latency(
    phase: &str,
    ticks: u64,
    pid: &mut Option<S60PID>,
    lattice: &mut Option<ResonantMatrix>,
) {
    let mut clock = IsochronousClock::new_internal();
    let mut intervals: Vec<u64> =
        Vec::with_capacity(usize::try_from(ticks).expect("ticks fuera de usize"));
    let mut last = Instant::now();

    for _ in 0..ticks {
        clock.tick_internal();

        // Si hay PID + lattice, inyectar corrección no-Markoviana
        if let (Some(p), Some(l)) = (pid.as_mut(), lattice.as_mut()) {
            let lattice_errors: Vec<i64> = l.get_phases().iter().map(|ph| ph.to_raw()).collect();
            let measured_raw = i64::try_from(clock.ticks).expect("tick fuera de i64");
            let dt_raw = 1; // 1 tick
            let _ = p.update_with_history_internal(measured_raw, dt_raw, lattice_errors);
        }

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

fn crystal_drift(
    phase: &str,
    ticks: u64,
    pid: &mut Option<S60PID>,
    lattice: &mut Option<ResonantMatrix>,
) {
    let mut clock = IsochronousClock::new_internal();
    let start = Instant::now();

    for _ in 0..ticks {
        clock.tick_internal();

        if let (Some(p), Some(l)) = (pid.as_mut(), lattice.as_mut()) {
            let lattice_errors: Vec<i64> = l.get_phases().iter().map(|ph| ph.to_raw()).collect();
            let measured_raw = i64::try_from(clock.ticks).expect("tick fuera de i64");
            let dt_raw = 1;
            let _ = p.update_with_history_internal(measured_raw, dt_raw, lattice_errors);
        }
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

fn run_phase(phase: &str, use_kernel: bool, ticks: u64) {
    println!("\n=== FASE: {} (kernel={}) ===", phase, use_kernel);
    let (b0, t0) = cpu_busy_total();
    let initial_temp = cpu_temp_millicelsius();
    println!(
        "[{}] temp_inicial={}.{:03}C",
        phase,
        initial_temp / 1000,
        initial_temp.abs() % 1000
    );

    let mut pid = None;
    let mut lattice = None;

    if use_kernel {
        // Configuración PID para cristal 41.77Hz
        let kp = SPA::new(0, 30, 0, 0, 0).to_raw(); // 0.5
        let ki = SPA::new(0, 10, 0, 0, 0).to_raw(); // 0.166...
        let kd = SPA::new(0, 5, 0, 0, 0).to_raw(); // 0.083...
        pid = Some(S60PID::new(kp, ki, kd, 0));
        lattice = Some(ResonantMatrix::new(64));
    }

    crystal_latency(phase, ticks, &mut pid, &mut lattice);
    crystal_drift(phase, ticks, &mut pid, &mut lattice);
    lattice_io(phase, 50_000);

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
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let phase = args.get(1).map(|s| s.as_str()).unwrap_or("idle");
    let use_kernel = args.get(2).map(|s| s == "kernel").unwrap_or(false);
    let ticks = 600;

    println!(
        "=== SENTINEL BENCH SALTO-17 [{}] kernel={} ===",
        phase, use_kernel
    );

    // Calentar
    for _ in 0..10 {
        thread::sleep(Duration::from_millis(1));
    }

    run_phase(phase, use_kernel, ticks);

    println!("\n=== FIN {} ===", phase);
}
