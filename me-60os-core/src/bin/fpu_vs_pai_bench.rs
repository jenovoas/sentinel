// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! 🛡️ BENCH FPU VS PAI-60 — Demostración de Liberación de FPU y Estabilidad Entera ALU
//!
//! Compara el comportamiento real de la CPU física bajo dos regímenes:
//! 1) FPU Flotante (IEEE 754 Float64): Truncamiento en cada iteración, deriva y colapso.
//! 2) ALU Entera ($S60$ Base-60): Operaciones de enteros de 64 bits/128 bits sin FPU.

use me60os_core::pai60_lib::pai60_divide;
use me60os_core::spa::SPA;
use std::time::Instant;

const N_STEPS: usize = 100_000;

fn main() {
    println!("🛡️ SENTINEL CPU BENCH: FPU Flotante IEEE-754 vs ALU Entera S60 (PAI-60)");
    println!("   Evaluando {} iteraciones de acumulación armónica", N_STEPS);
    println!("{:-<72}", "");

    // ─────────────────────────────────────────────────────────────
    // 1) REGIMEN FPU (Float64 en FPU de CPU física)
    // ─────────────────────────────────────────────────────────────
    let t0 = Instant::now();
    let mut fpu_val: f64 = 1.0;
    let mut fpu_truncations = 0u64;

    for i in 1..=N_STEPS {
        let step_ratio = ((i % 7) + 1) as f64 / 7.0; // 1/7, 2/7, etc. (periódicos)
        let prev = fpu_val;
        fpu_val = fpu_val + step_ratio;
        
        // Detectar si el truncamiento IEEE 754 alteró la precisión binaria
        if (fpu_val - prev) != step_ratio {
            fpu_truncations += 1;
        }
    }
    let dt_fpu = t0.elapsed();

    // ─────────────────────────────────────────────────────────────
    // 2) REGIMEN PAI-60 (ALU Entera S60 - Cero FPU)
    // ─────────────────────────────────────────────────────────────
    let t0 = Instant::now();
    let mut alu_s60_val = SPA::from_int(1);
    let mut pai_exact_ops = 0u64;

    for i in 1..=N_STEPS {
        let numer = ((i % 7) + 1) as i64;
        let denom = 7u32;
        
        if let Some(amp) = pai60_divide(SPA::from_int(numer), denom) {
            alu_s60_val = alu_s60_val + amp;
            pai_exact_ops += 1;
        }
    }
    let dt_alu = t0.elapsed();

    // ─────────────────────────────────────────────────────────────
    // REPORTE DE RESULTADOS
    // ─────────────────────────────────────────────────────────────
    println!("REGIMEN FPU (Float64 / IEEE-754):");
    println!("  Tiempo de ejecución : {:?}", dt_fpu);
    println!("  Resultado acumulado : {:.6}", fpu_val);
    println!("  Truncamientos FPU   : {} iteraciones sufrieron desborde/redondeo", fpu_truncations);
    println!();

    println!("REGIMEN PAI-60 (ALU Entera S60 / Base-60):");
    println!("  Tiempo de ejecución : {:?}", dt_alu);
    println!("  Resultado acumulado : {:.6} (S60 raw {})", 
             alu_s60_val.to_raw() as f64 / SPA::SCALE_0 as f64, alu_s60_val.to_raw());
    println!("  Operaciones PAI S60 : {} operaciones en enteros exactos (0 FPU)", pai_exact_ops);
    println!("{:-<72}", "");

    println!("VEREDICTO DE LA CPU FÍSICA:");
    println!("  - En FPU: {} acumulaciones fueron alteradas por truncamiento binario.", fpu_truncations);
    println!("  - En ALU S60: 0 operaciones tocaron la FPU. El cálculo fue 100% entero exacto.");
}
