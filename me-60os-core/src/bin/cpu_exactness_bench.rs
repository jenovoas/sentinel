// Benchmark de recurrencia S60 entera.
use me60os_core::spa::SPA;
use std::time::Instant;

const N: u32 = 200_000;

fn main() {
    println!("=== CPU EXACTNESS: recurrencia S60 x = x * (98/60) ===");
    println!("N = {N} pasos\n");

    let phi = SPA::new(1, 38, 0, 0, 0);
    let mut value = SPA::from_int(1);
    let start = Instant::now();
    for _ in 0..N {
        value = value * phi;
    }
    let elapsed_ns = start.elapsed().as_nanos();
    let average_ns = elapsed_ns / u128::from(N);

    println!("[S] SPA base-60, razón 98/60");
    println!("  resultado raw : {}", value.to_raw());
    println!("  tiempo total  : {elapsed_ns} ns");
    println!("  tiempo por op : {average_ns} ns");
    println!("La recurrencia usa operaciones S60 enteras sin conversiones de punto flotante.");
}
