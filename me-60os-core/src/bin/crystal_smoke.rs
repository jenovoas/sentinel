// Smoke test del cristal de tiempo (Rust puro, sin Python, sin kernel).
// Verifica que IsochronousClock late con intervalo ~23.9ms y que los ticks avanzan.
use me60os_core::quantum_core::IsochronousClock;
use std::time::Instant;

fn main() {
    let mut clock = IsochronousClock::new_internal();
    println!(
        "💎 CRYSTAL SMOKE (Rust): intervalo {} ns (~41 Hz)",
        clock.tick_interval_ns
    );

    let n = 60u64;
    let t0 = Instant::now();
    for _ in 0..n {
        clock.tick_internal();
    }
    let elapsed = t0.elapsed().as_nanos() as u64;
    let ideal = n * clock.tick_interval_ns;
    let diff = (elapsed as i128 - ideal as i128).unsigned_abs();

    println!("Ticks ejecutados: {}", clock.ticks);
    println!("Total real:   {} ns", elapsed);
    println!("Total ideal:  {} ns", ideal);
    println!("Desviación:   {} ns", diff);

    let stable = clock.ticks == n && diff < 1_000_000;
    if stable {
        println!("✅ CRISTAL ESTABLE (S60, sin floats)");
        std::process::exit(0);
    } else {
        println!("⚠️ CRISTAL INESTABLE");
        std::process::exit(1);
    }
}
