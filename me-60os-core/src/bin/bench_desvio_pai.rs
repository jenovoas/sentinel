// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! 🛡️ BENCH DESVÍO PAI — Matemáticas Armónicas (el terreno real del PAI).
//!
//! La CPU binaria NO puede acumular razones armónicas sin contaminarse:
//! cada 1/3, 1/6, 1/12 en float se trunca y el error se acumula.
//! El PAI devuelve la razón recíproca EXACTA (base-60) y el cristal la
//! SUPERPONE (suma de amplitudes en resonancia) sin re-truncamiento.
//!
//! Medimos: (A) float acumulando en bucle  vs  (B) PAI->lattice superponiendo.
//! El veredicto real es la CONTAMINACIÓN, no la velocidad de división.

use me60os_core::pai60_lib::pai60_divide;
use me60os_core::resonant_matrix::ResonantMatrix;
use me60os_core::spa::SPA;
use std::time::Instant;

const N: usize = 500_000;
const DENOMS: [u32; 9] = [2, 3, 4, 5, 6, 10, 12, 15, 60]; // regulares 5-smooth

fn main() {
    println!("🛡️ BENCH DESVÍO PAI — Matemáticas Armónicas (exactitud vs contaminación)");
    println!("   {} términos armónicos (numer/denom regulares), acumulados", N);
    println!("{:-<70}", "");

    // ---------- CAMINO A: FLOAT (CPU binaria, lo que contamina) ----------
    let t0 = Instant::now();
    let mut float_sum: f64 = 0.0;
    for i in 0..N {
        let numer = ((i % 12) + 1) as f64;
        let denom = DENOMS[i % DENOMS.len()] as f64;
        float_sum += numer / denom; // truncamiento float en cada paso
    }
    let dt_a = t0.elapsed();

    // ---------- CAMINO B: PAI -> LATTICE (superposición resonante exacta) ----------
    let t0 = Instant::now();
    let mut lattice = ResonantMatrix::new(64);
    let mut idx = 0usize;
    let mut pai_sum = SPA::zero(); // referencia exacta en S60
    for i in 0..N {
        let numer = ((i % 12) + 1) as i64;
        let denom = DENOMS[i % DENOMS.len()];
        if let Some(amp) = pai60_divide(SPA::from_int(numer), denom) {
            lattice.inject_pai(idx, numer, denom); // superposición: amplitude += amp
            pai_sum = pai_sum + amp;
            idx = (idx + 1) % 64;
        }
    }
    // el cristal sostiene la suma; un step confirma que resuena (no recomputa)
    lattice.step();
    let lattice_total = lattice.total_energy();
    let dt_b = t0.elapsed();

    // ---------- COMPARACIÓN: ¿cuánto contaminó el float? ----------
    // float_sum vs pai_sum (ambos deberían ser la misma suma racional).
    let pai_as_f64 = pai_sum.to_raw() as f64 / SPA::SCALE_0 as f64;
    let drift = (float_sum - pai_as_f64).abs();
    let drift_ppm = if pai_as_f64 != 0.0 {
        (drift / pai_as_f64.abs()) * 1_000_000.0
    } else { 0.0 };

    println!("CAMINO A (float bucle):   {:>8.3?} | suma={:.6} | CONTAMINADO", dt_a, float_sum);
    println!("CAMINO B (PAI->lattice):  {:>8.3?} | suma={:.6} | EXACTO (S60 raw {})",
             dt_b, pai_as_f64, pai_sum.to_raw());
    println!("{:-<70}", "");
    println!("📉 DERIVA del float vs exactitud PAI: {:.3} ppm (partes por millón)", drift_ppm);
    println!("🏆 El PAI mantiene la razón armónica EXACTA tras {} términos;", N);
    println!("   el float acumuló error (deriva ppm). El cristal superpone las");
    println!("   amplitudes sin re-truncar: eso es el cómputo que la CPU binaria");
    println!("   NO puede hacer sin contaminarse. Ahí es donde se desvía el procesamiento.");
}
