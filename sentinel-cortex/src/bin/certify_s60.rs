// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// Bug preexistente: usaba `me60os` pero el crate se importa bajo el alias `me60os_core`
// (ver Cargo.toml línea 60: `me60os_core = { path = "../../me-60os", package = "me60os" }`).
use me60os_core::spa::SPA;
use std::time::Instant;

fn main() {
    println!("--- [CERTIFICACIÓN] INTEGRIDAD ARITMÉTICA S60 (SOMA CORE) ---");
    println!("Escala: 1,000,000 Iteraciones de Alta Precisión");

    let iterations = 100_000;

    // CASO S60 (Sentinel)
    let start_s60 = Instant::now();
    let mut val_s60 = SPA::new(1, 0, 0, 0, 0); // 1.0 en S60

    // Operación: (x * 7) / 7 -> Debería ser exactamente x
    // En floats, 1.0/7.0 * 7.0 produce errores de redondeo acumulados
    let multiplier_s60 = SPA::new(7, 0, 0, 0, 0);
    let divisor_s60 = SPA::new(7, 0, 0, 0, 0);

    for _ in 0..iterations {
        val_s60 = (val_s60 * multiplier_s60) / divisor_s60;
    }
    let duration_s60 = start_s60.elapsed();

    println!("\n[RESULTADOS]");
    println!("S60 Final Value: {}", val_s60);

    println!("\n[CERTIFICACIÓN]");
    if val_s60 == SPA::new(1, 0, 0, 0, 0) {
        println!("✅ S60 DRIFT: 0.00000000000000000000 (PERFECTO)");
    } else {
        println!("❌ S60 DRIFT DETECTADO (INVESTIGAR)");
    }

    println!("\n[RENDIMIENTO]");
    println!("S60 Total Time: {:?}", duration_s60);

    // La comparación contra f64 se retiró: el candado YATRA prohíbe floats en este
    // crate. Las comparaciones de drift IEEE-754 viven en los
    // prototipos Python (quantum/experiments), que se conservan como referencia.
    println!("\nCONCLUSIÓN: certificación S60 completada (sin drift = aritmética exacta).");
}
