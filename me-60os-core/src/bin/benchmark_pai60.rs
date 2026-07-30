// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
use me60os_core::pai60_lib::pai60_divide;
use me60os_core::spa::SPA;
use std::time::Instant;

fn main() {
    println!("🧪 ME-60OS: PAI-60 Micro-Benchmark (Rust Core)");
    println!("============================================");

    let num = SPA::new(100, 0, 0, 0, 0); // 100 degrees
    let denominators = [
        2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 25, 27, 30, 32, 36, 40, 45, 48, 50, 54, 60,
    ];

    let iterations = 10_000_000;
    println!(
        "Running {} iterations for each regular denominator...",
        iterations
    );

    for &den in &denominators {
        let start = Instant::now();

        // Use a black_box style loop to prevent compiler from optimizing the whole loop away
        let mut _sink = SPA::default();
        for _ in 0..iterations {
            _sink = pai60_divide(num, den).unwrap();
        }

        let duration = start.elapsed();
        let avg_ns = duration.as_nanos() as f64 / iterations as f64;

        println!(
            "Denominator {:>2}: Total {:>8?} | Avg: {:>8.3} ns",
            den, duration, avg_ns
        );
    }

    println!("============================================");
    println!("✅ Benchmark Complete");
}
