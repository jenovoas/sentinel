// Autor: Jaime Novoa Sepulveda -- Todos los derechos reservados.
// Licencia: Apache 2.0 + Clausula No Comercial (ver LICENSE).
//
// EXP-033 QUANTUM SCHEDULER BENCHMARK -- RUST PURO S60 vs PYTHON f64
//
// Objetivo: Medir latencia por tick del QuantumScheduler completo (PortalDetector +
// BioResonator + AdaptiveBatch + Execute/Force) en Rust puro S60, contra el costo
// equivalente en Python EXP-028 (que usa math.sin f64).
//
// Target: < 1 us por tick (Master Plan V3).
// Metodologia:
//   1. Calentar 1000 ticks
//   2. Medir 100,000 ticks con Instant::now()
//   3. Reportar ns/tick y comparacion vs Python EXP-028.
//
// Sin floats (YATRA lock), toda la aritmetica en i64 escalada por SCALE_0.

use sentinel_cortex::math::s60::S60;
use sentinel_cortex::quantum::bio_resonator::BioResonator;
use sentinel_cortex::quantum::quantum_scheduler::{QuantumScheduler, Task, TaskType};
use std::sync::{Arc, Mutex};
use std::time::Instant;

// Callback vacio para llenar la cola
extern "C" fn noop_task() {}

fn main() {
    println!("EXP-033 QUANTUM SCHEDULER BENCHMARK (RUST PURO S60)");
    println!("   QuantumScheduler + PortalDetector + BioResonator");
    println!("   Target: < 1 us / tick");
    println!("{}", "-".repeat(72));

    let bio = Arc::new(Mutex::new(BioResonator::new()));
    let mut scheduler = QuantumScheduler::new(bio.clone());

    // Llenar la cola para que cada tick tenga trabajo
    for i in 0..200u64 {
        scheduler.enqueue(Task {
            id: i,
            task_type: TaskType::ZPETune,
            cost: 100,
            callback: noop_task,
        });
    }

    // Calentar
    let dt_raw: i64 = S60::SCALE_0 / 10; // 0.1s
    for tick in 0..1000u64 {
        let t = S60::from_raw((tick as i64) * dt_raw);
        // Inyectar pulso bio cada 17 ticks (simula piloto presente)
        if tick % 17 == 0 {
            bio.lock().unwrap().inject_bio_pulse();
        }
        scheduler.tick(t);
    }

    // Medir
    const ITERS: u64 = 100_000;
    let start = Instant::now();
    for tick in 0..ITERS {
        let t = S60::from_raw((tick as i64) * dt_raw);
        if tick % 17 == 0 {
            bio.lock().unwrap().inject_bio_pulse();
        }
        scheduler.tick(t);
    }
    let elapsed = start.elapsed();

    let elapsed_ns = elapsed.as_nanos() as i64;
    let ns_per_tick = elapsed_ns / ITERS as i64;
    let ticks_per_sec = (ITERS as i64 * 1_000_000_000) / elapsed_ns.max(1);

    println!();
    println!("[RESULTADOS MEDIDOS]");
    println!("Iteraciones:        {}", ITERS);
    println!("Tiempo total:       {} us", elapsed_ns / 1000);
    println!("Latencia por tick:  {} ns", ns_per_tick);
    println!("Throughput:         {} ticks/s", ticks_per_sec);

    println!();
    println!("[COMPARACION CON PYTHON EXP-028]");
    // EXP-028 Python en maquina de referencia: ~50 us / tick (math.sin f64)
    // Ver quantum/experiments/EXP_028_PENTA_RESONANCE.py
    let python_us_per_tick: i64 = 50_000; // 50 us (estimacion conservadora)
    let rust_us_per_tick: i64 = ns_per_tick / 1000;
    let speedup = if rust_us_per_tick > 0 {
        python_us_per_tick / rust_us_per_tick
    } else {
        (python_us_per_tick * 1000) / ns_per_tick
    };
    println!("Python EXP-028 (estimado): ~{} us/tick", python_us_per_tick);
    println!(
        "Rust EXP-033 (medido):     {} ns/tick = {} us/tick",
        ns_per_tick, rust_us_per_tick
    );
    println!("Speedup: {}x", speedup);

    println!();
    println!("[CERTIFICACION]");
    let target_ns: i64 = 1000; // 1 us
    if ns_per_tick <= target_ns {
        println!(
            "OK latencia {} ns <= target 1000 ns (1 us) -- {} ns de margen",
            ns_per_tick,
            target_ns - ns_per_tick
        );
        std::process::exit(0);
    } else {
        println!(
            "EXCEDIDO: latencia {} ns > target 1000 ns -- diferencia {} ns",
            ns_per_tick,
            ns_per_tick - target_ns
        );
        std::process::exit(1);
    }
}
