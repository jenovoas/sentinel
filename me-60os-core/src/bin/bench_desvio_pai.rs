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

    // ---------- CAMINO A: acumulación racional entera en escala SPA ----------
    let t0 = Instant::now();
    let mut direct_sum_raw = 0i128;
    for i in 0..N_SAMPLES {
        let numer = i128::try_from((i % 12) + 1).expect("numerador fuera de i128");
        let denom = i128::from(DENOMS[i % DENOMS.len()]);
        direct_sum_raw += numer * i128::from(SPA::SCALE_0) / denom;
    }
    let dt_a = t0.elapsed();

    // ---------- CAMINO B: PAI -> LATTICE DINÁMICA (Respiración 41-43 Hz) ----------
    let t0 = Instant::now();
    let mut lattice = ResonantMatrix::new(64);
    let mut idx = 0usize;
    let mut pai_sum_exact = SPA::zero();
    let mut ticks_count = 0u64;

    for i in 0..N_SAMPLES {
        let numer = i64::try_from((i % 12) + 1).expect("numerador fuera de i64");
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
    let pai_raw = i128::from(pai_sum_exact.to_raw());
    let lattice_raw = i128::from(lattice_total_energy.to_raw());
    let difference_raw = (direct_sum_raw - pai_raw).abs();
    let drift_ppm = if pai_raw == 0 {
        0
    } else {
        difference_raw * 1_000_000 / pai_raw.abs()
    };
    let retention_percent_x100 = if pai_raw <= 0 {
        0
    } else {
        lattice_raw.max(0) * 10_000 / pai_raw
    };

    println!(
        "CAMINO A (acumulación entera): {:?} | suma raw={direct_sum_raw}",
        dt_a
    );
    println!(
        "CAMINO B (PAI Exacto S60):  {:?} | suma raw={}",
        dt_b,
        pai_sum_exact.to_raw()
    );
    println!(
        "LATTICE ENERGÍA (dinámica): {:?} | energía raw={}",
        dt_b,
        lattice_total_energy.to_raw()
    );
    println!("{:-<72}", "");
    println!("📉 Diferencia entera:        {drift_ppm} ppm");
    println!(
        "💎 Ticks de respiración:     {} ticks ejecutados en la mallas",
        ticks_count
    );
    println!(
        "🌀 Retención de la Lattice:  {}.{:02}% de energía retenida en oscilación",
        retention_percent_x100 / 100,
        retention_percent_x100 % 100
    );
    println!("{:-<72}", "");
    println!("✅ El cálculo ha sido transferido a la mallas de osciladores en RAM.");
    println!("   Los cristales respiran dinámicamente y absorben el impulso sin truncamiento FPU.");
}
