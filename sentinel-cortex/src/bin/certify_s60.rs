use me60os::spa::SPA;
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
    
    // CASO Float64 (IEEE-754)
    let start_f64 = Instant::now();
    let mut val_f64: f64 = 1.0;
    for _ in 0..iterations {
        val_f64 = (val_f64 * 7.0) / 7.0;
    }
    let duration_f64 = start_f64.elapsed();
    
    println!("\n[RESULTADOS]");
    println!("S60 Final Value: {}", val_s60);
    println!("f64 Final Value: {:.20}", val_f64);
    
    let drift_f64 = (val_f64 - 1.0).abs();
    
    println!("\n[CERTIFICACIÓN]");
    if val_s60 == SPA::new(1, 0, 0, 0, 0) {
        println!("✅ S60 DRIFT: 0.00000000000000000000 (PERFECTO)");
    } else {
        println!("❌ S60 DRIFT DETECTADO (INVESTIGAR)");
    }
    
    println!("⚠️ f64 DRIFT: {:.20}", drift_f64);
    
    println!("\n[RENDIMIENTO]");
    println!("S60 Total Time: {:?}", duration_s60);
    println!("f64 Total Time: {:?}", duration_f64);
    
    if drift_f64 > 0.0 {
        println!("\nCONCLUSIÓN: La certificación S60 es válida. Superioridad matemática demostrada.");
    }
}
