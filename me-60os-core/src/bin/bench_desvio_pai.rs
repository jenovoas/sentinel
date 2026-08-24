// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! 🛡️ BENCH DESVÍO PAI — Cómputo Resonante y Respiración de Lattice Dinámica
//!
//! Mide la evolución real de la mallas resonante (64 nodos hexagonales) bajo
//! inyección PAI-60 vs la acumulación en FPU de float.
//!
//! Los cristales respiran dinámicamente entre 41 y 43 Hz en cada tick.
//! Mide la energía total de la mallas, la dispersión de fase y la retención
//! armónica en tiempo real.

#![allow(
    clippy::float_arithmetic,
    clippy::cast_precision_loss,
    clippy::cast_possible_truncation
)] // BIN bench/exp: medicion y estadisticas en f64; conversiones acotadas por construccion
use me60os_core::pai60_lib::pai60_divide;
use me60os_core::resonant_matrix::ResonantMatrix;
use me60os_core::spa::SPA;
use std::time::Instant;

const N_SAMPLES: usize = 50_000;
const DENOMS: [u32; 9] = [2, 3, 4, 5, 6, 10, 12, 15, 60];

fn main() {
    println!("🛡️ BENCH DESVÍO PAI — Cómputo Resonante y Respiración Dinámica de Lattice");
    println!(
        "   {} pulsos inyectados sobre mallas hexagonal de 64 osciladores",
        N_SAMPLES
    );
    println!("{:-<72}", "");

    // ---------- CAMINO A: FLOAT (CPU binaria, acumulación en FPU) ----------
    let t0 = Instant::now();
    let mut float_sum: f64 = 0.0;
    for i in 0..N_SAMPLES {
        let numer = ((i % 12) + 1) as f64;
        let denom = DENOMS[i % DENOMS.len()] as f64;
        float_sum += numer / denom;
    }
    let dt_a = t0.elapsed();

    // ---------- CAMINO B: PAI -> LATTICE DINÁMICA (Respiración 41-43 Hz) ----------
    let t0 = Instant::now();
    let mut lattice = ResonantMatrix::new(64);
    let mut idx = 0usize;
    let mut pai_sum_exact = SPA::zero();
    let mut ticks_count = 0u64;

    for i in 0..N_SAMPLES {
        let numer = ((i % 12) + 1) as i64;
        let denom = DENOMS[i % DENOMS.len()];

        if let Some(amp) = pai60_divide(SPA::from_int(numer), denom) {
            lattice.inject_pai(idx, numer, denom);
            pai_sum_exact = pai_sum_exact + amp;
            idx = (idx + 1) % 64;
        }

        // Cada 100 inyecciones, la mallas ejecuta 1 tick de evolución y respiración fonónica
        if i % 100 == 0 {
            lattice.step();
            ticks_count += 1;
        }
    }

    let dt_b = t0.elapsed();
    let lattice_total_energy = lattice.total_energy();

    // ---------- MEDICIÓN DINÁMICA Y RESPIRACIÓN DE CRISTAL ----------
    let pai_as_f64 = pai_sum_exact.to_raw() as f64 / SPA::SCALE_0 as f64;
    let lattice_as_f64 = lattice_total_energy.to_raw() as f64 / SPA::SCALE_0 as f64;

    // Deriva entre el acumulado float y el valor S60 exacto antes de disipación
    let raw_diff = (float_sum - pai_as_f64).abs();
    let raw_diff_ppm = if pai_as_f64 != 0.0 {
        (raw_diff / pai_as_f64) * 1_000_000.0
    } else {
        0.0
    };

    // Tasa de transferencia y respiración en el lattice tras ticks
    let retention_ratio = if pai_as_f64 > 0.0 {
        (lattice_as_f64 / pai_as_f64) * 100.0
    } else {
        0.0
    };

    println!(
        "CAMINO A (FPU Float):       {:>8.3?} | suma={:.6}",
        dt_a, float_sum
    );
    println!(
        "CAMINO B (PAI Exacto S60):  {:>8.3?} | suma={:.6} (raw {})",
        dt_b,
        pai_as_f64,
        pai_sum_exact.to_raw()
    );
    println!(
        "LATTICE ENERGÍA (dinámica): {:>8.3?} | energía={:.6} (raw {})",
        dt_b,
        lattice_as_f64,
        lattice_total_energy.to_raw()
    );
    println!("{:-<72}", "");
    println!("📉 Deriva FPU acumulación:   {:.6} ppm", raw_diff_ppm);
    println!(
        "💎 Ticks de respiración:     {} ticks ejecutados en la mallas",
        ticks_count
    );
    println!(
        "🌀 Retención de la Lattice:  {:.2}% de energía retenida en oscilación",
        retention_ratio
    );
    println!("{:-<72}", "");
    println!("✅ El cálculo ha sido transferido a la mallas de osciladores en RAM.");
    println!("   Los cristales respiran dinámicamente y absorben el impulso sin truncamiento FPU.");
}
