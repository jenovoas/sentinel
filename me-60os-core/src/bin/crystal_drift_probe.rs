// Prueba de deriva temporal del cristal frente a ruido térmico REAL.
// Fases: idle -> carga masiva -> enfriamiento.
// Mide IsochronousClock.get_nanos() vs perf_counter_ns() del SO.
// Todo en nanos enteros (S60), sin float en la lógica de medición.
use me60os_core::quantum_core::IsochronousClock;
use std::time::Instant;
use std::thread;
use std::time::Duration;

fn probe_phase(name: &str, ticks: u64, clock: &mut IsochronousClock) {
    let mut max_drift: i128 = 0;
    let mut sum_drift: i128 = 0;
    let mut samples: u64 = 0;
    let mut t0 = Instant::now();
    for _ in 0..ticks {
        clock.tick_internal();
        // nanos del cristal (cuenta desde su start_time)
        let crystal_ns = clock.get_nanos_internal() as i128;
        // nanos del SO (referencia externa)
        let os_ns = t0.elapsed().as_nanos() as i128;
        // drift = diferencia cristal vs SO (en nanos)
        let drift = (crystal_ns - os_ns).abs();
        if drift > max_drift { max_drift = drift; }
        sum_drift += drift;
        samples += 1;
        // refrescar t0 cada 256 ticks para no perder precisión del contador OS
        if samples.is_multiple_of(256) {
            t0 = Instant::now();
        }
    }
    let avg = if samples > 0 { sum_drift / samples as i128 } else { 0 };
    println!(
        "[{}] ticks={} max_drift_ns={} avg_drift_ns={} (tolerancia <1000000ns = 1ms)",
        name, samples, max_drift, avg
    );
}

fn main() {
    println!("💎 CRYSTAL DRIFT PROBE (ruido térmico REAL, sin PRNG)");
    let mut clock = IsochronousClock::new_internal();

    // FASE 1: IDLE (sin carga)
    println!("--- FASE 1: IDLE (cero carga, 120 ticks ~2.9s) ---");
    probe_phase("IDLE", 120, &mut clock);

    // FASE 2: CARGA MASIVA (la genera el padre vía `yes`/sha256 en paralelo)
    println!("--- FASE 2: CARGA MASIVA (120 ticks, CPU saturada por proceso externo) ---");
    probe_phase("CARGA", 120, &mut clock);

    // Dar un respiro para que enfríe
    thread::sleep(Duration::from_secs(2));

    // FASE 3: ENFRIAMIENTO (carga bajada, 120 ticks)
    println!("--- FASE 3: ENFRIAMIENTO (120 ticks, CPU liberada) ---");
    probe_phase("ENFRIA", 120, &mut clock);

    println!("✅ PROBE COMPLETO");
}
