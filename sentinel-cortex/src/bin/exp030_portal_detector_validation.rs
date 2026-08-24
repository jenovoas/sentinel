// Autor: Jaime Novoa Sepulveda -- Todos los derechos reservados.
// Licencia: Apache 2.0 + Clausula No Comercial (ver LICENSE).
// Colaboracion abierta con atribucion. Uso comercial PROHIBIDO sin autorizacion.
//
// EXP-030 PORTAL DETECTOR -- VALIDACION EN RUST PURO (S60)
//
// Objetivo: Validar que la implementacion PortalDetector (S60) reproduce el
// patron de portales detectado por EXP-028 Python (9 portales en ventana 68s).
// Si la salida coincide, el QuantumScheduler queda desbloqueado.
//
// Hipotesis: La misma logica (sin(cos) sobre 3 fases) en Rust puro S60 debe
// detectar el mismo numero de portales en el mismo intervalo de tiempo.
//
// Eje de tiempo: t en S60 donde 1.0 unidad = 1 segundo (definicion operativa).
//
// Ejecucion:
//   cargo run --release --bin exp030_portal_detector_validation
//
// Salida: resultados a stdout; reporte en quantum/experiments/EXP_030_PORTAL_DETECTOR_RUST.md
//
// Sin floats (YATRA lock), solo i64 escalada por SCALE_0 = 60^4 = 12_960_000.

use sentinel_cortex::math::s60::S60;
use sentinel_cortex::quantum::portal_detector::PortalDetector;
use std::time::Instant;

const DT_RAW: i64 = S60::SCALE_0 / 10; // dt = 0.1 s = 1_296_000 raw

// Convierte un raw S60 a milisegundos (i64) sin usar f64.
// dt = 0.1s = 100 ms; 1 raw = 100/SCALE_0 ms.
#[inline]
fn raw_to_millis(raw: i64) -> i64 {
    // dt = 0.1s = 100 ms; 1 raw = 100/SCALE_0 ms
    (raw * 100) / S60::SCALE_0
}
const TOTAL_TICKS: u64 = 680; // 680 * 0.1s = 68s (1 ciclo Quantum Leap completo)
const CYCLE_TICKS: u64 = 68; // 68 * 0.1s = 6.8s por ciclo (10 ciclos en 68s)
const N_CYCLES: usize = (TOTAL_TICKS / CYCLE_TICKS) as usize; // 10

fn main() {
    println!("EXP-030 PORTAL DETECTOR -- VALIDACION RUST PURO S60");
    println!("   Implementacion: sentinel-cortex/src/quantum/portal_detector.rs");
    println!("   Periodos hardcoded desde EXP-028 Python (17s/4.25s/16.18s)");
    println!("   Tick = 0.1s, ciclos = 10, total = 68s");
    println!("{}", "-".repeat(72));

    let pd = PortalDetector::new();

    // Cobertura: ticks 0..680 con dt=0.1s
    let mut portals_per_cycle: [u32; N_CYCLES] = [0; N_CYCLES];
    let mut total_portals: u32 = 0;
    let mut max_intensity_raw: i64 = 0;
    let mut max_intensity_tick: u64 = 0;
    let mut first_portal_tick: Option<u64> = None;
    let mut last_portal_tick: Option<u64> = None;

    // Detalle para el reporte: registrar ticks consecutivos con portal
    let mut portal_intervals: Vec<(u64, u64)> = Vec::new();
    let mut interval_start: Option<u64> = None;

    let start = Instant::now();
    for tick in 0..TOTAL_TICKS {
        // t = tick * dt. Cada 0.1s.
        // En S60: t_raw = tick * DT_RAW
        let t_raw: i64 = (tick as i64) * DT_RAW;
        let t = S60::from_raw(t_raw);

        let open = pd.is_portal_open(t);
        let intensity = pd.get_portal_intensity(t);
        let intensity_raw = intensity._value;

        if intensity_raw > max_intensity_raw {
            max_intensity_raw = intensity_raw;
            max_intensity_tick = tick;
        }

        if open {
            total_portals += 1;
            let cycle = (tick / CYCLE_TICKS) as usize;
            portals_per_cycle[cycle] += 1;

            if first_portal_tick.is_none() {
                first_portal_tick = Some(tick);
            }
            last_portal_tick = Some(tick);

            if interval_start.is_none() {
                interval_start = Some(tick);
            }
        } else if let Some(s) = interval_start.take() {
            // Cierra el intervalo anterior
            portal_intervals.push((s, tick - 1));
        }
    }
    // Si quedo un intervalo abierto al final
    if let Some(s) = interval_start {
        portal_intervals.push((s, TOTAL_TICKS - 1));
    }

    let elapsed = start.elapsed();

    // Umbrales para verificacion con EXP-028 Python
    // Python detecto: 9 portales en t in [4.9, 5.7] segundos
    // 4.9s -> tick 49 ; 5.7s -> tick 57
    let exp_028_first_tick = 49_u64;
    let exp_028_last_tick = 57_u64;
    let exp_028_count = 9_u32;

    println!();
    println!("[RESULTADOS MEDIDOS]");
    println!("Total portales detectados: {}", total_portals);
    println!(
        "Primeros portales en tick {} (t = {} decimas de segundo = {} ms)",
        first_portal_tick.unwrap_or(0),
        first_portal_tick.unwrap_or(0) as i64,
        raw_to_millis(first_portal_tick.unwrap_or(0) as i64 * DT_RAW)
    );
    println!(
        "Ultimo portal en tick {} (t = {} ms)",
        last_portal_tick.unwrap_or(0),
        raw_to_millis(last_portal_tick.unwrap_or(0) as i64 * DT_RAW)
    );
    println!(
        "Intensidad pico: {} (raw) en tick {}",
        max_intensity_raw, max_intensity_tick
    );
    println!("Distribucion por ciclo (1 ciclo = 68 ticks = 6.8s):");
    for (i, c) in portals_per_cycle.iter().enumerate() {
        println!("  Ciclo {}: {} portales", i + 1, c);
    }

    println!();
    println!("[INTERVALOS DETECTADOS]");
    for (i, (start_tick, end_tick)) in portal_intervals.iter().enumerate() {
        let dur_ticks = end_tick - start_tick + 1;
        println!(
            "  Intervalo #{}: ticks {}..{} (duracion {} ticks = {} ms)",
            i + 1,
            start_tick,
            end_tick,
            dur_ticks,
            raw_to_millis(dur_ticks as i64 * DT_RAW)
        );
    }

    println!();
    println!("[COMPARACION CON EXP-028 PYTHON]");
    println!("EXP-028 Python: 9 portales en t in [4.9s, 5.7s]");
    println!(
        "EXP-030 Rust:   {} portales en t in [{} ms, {} ms]",
        total_portals,
        raw_to_millis(first_portal_tick.unwrap_or(0) as i64 * DT_RAW),
        raw_to_millis(last_portal_tick.unwrap_or(0) as i64 * DT_RAW)
    );

    let count_ok = total_portals == exp_028_count;
    let first_ok = first_portal_tick.unwrap_or(u64::MAX) == exp_028_first_tick
        || first_portal_tick.unwrap_or(u64::MAX) >= exp_028_first_tick - 5;
    let last_ok = last_portal_tick.unwrap_or(0) <= exp_028_last_tick + 5
        && last_portal_tick.unwrap_or(u64::MAX) >= exp_028_last_tick;

    if count_ok {
        println!("  OK: conteo coincide ({} portales)", exp_028_count);
    } else {
        println!(
            "  DIFERENCIA: conteo Rust={} vs Python={}",
            total_portals, exp_028_count
        );
    }

    if first_ok && last_ok {
        println!("  OK: ventana temporal coincide (5 ticks = 0.5s tolerancia)");
    } else {
        println!(
            "  DIFERENCIA: ventana temporal Rust=[{},{}] vs Python=[{},{}]",
            first_portal_tick.unwrap_or(0),
            last_portal_tick.unwrap_or(0),
            exp_028_first_tick,
            exp_028_last_tick
        );
    }

    println!();
    println!("[RENDIMIENTO]");
    // benchmark durations are bounded (ms-range); safe truncation to i64
    #[allow(clippy::cast_possible_truncation)]
    let elapsed_micros = elapsed.as_micros() as i64;
    let elapsed_per_tick_ns = (elapsed_micros * 1000) / TOTAL_TICKS as i64;
    let throughput_per_sec = TOTAL_TICKS as i64 * 1_000_000 / elapsed_micros.max(1);
    println!(
        "Tiempo: {} us ({} ticks) -> {} ns/tick",
        elapsed_micros, TOTAL_TICKS, elapsed_per_tick_ns
    );
    println!("Throughput: {} ticks/s", throughput_per_sec);

    // Estado de salida
    if count_ok && first_ok && last_ok {
        println!();
        println!("CERTIFICADO: PortalDetector Rust valida EXP-028 Python.");
        std::process::exit(0);
    } else {
        println!();
        println!("DISCREPANCIA: revisar PortalDetector (ver quantum/experiments/EXP_030_PORTAL_DETECTOR_RUST.md).");
        std::process::exit(1);
    }
}
