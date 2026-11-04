// Benchmark entero de acumulación PAI-60.
use me60os_core::pai60_lib::pai60_divide;
use me60os_core::spa::SPA;
use std::time::Instant;

const N_STEPS: u32 = 100_000;

fn main() {
    println!("SENTINEL CPU BENCH: acumulación S60 mediante PAI-60");
    println!("Iteraciones: {N_STEPS}");

    let start = Instant::now();
    let mut total = SPA::from_int(1);
    let mut exact_ops = 0u64;

    for index in 1..=N_STEPS {
        let numerator = i64::from((index % 7) + 1);
        if let Some(amplitude) = pai60_divide(SPA::from_int(numerator), 7) {
            total = total + amplitude;
            exact_ops += 1;
        }
    }

    let elapsed = start.elapsed();
    println!("Tiempo de ejecución: {elapsed:?}");
    println!("Resultado raw S60: {}", total.to_raw());
    println!("Operaciones PAI-60: {exact_ops}");
}
