// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/pai60_lib.rs
//! Rust implementation of the PAI‑60 reciprocal table and helper functions.
//! Designed for ultra‑low latency usage by the neural memory daemon.
//! Uses the shared `SPA` type from `src/spa.rs`.
//!
//! ## References (tabla recíproca babilónica / Plimpton 322)
//! - [P-RES] Novoa, J. (2026). *Aritmética Sexagesimal como Base de Sistemas.* `RESEARCH_es.md`.
//! - [EXT-MAN] Mansfield, D. F. & Wildberger, N. J. (2017).
//!   *Plimpton 322 is Babylonian exact sexagesimal trigonometry.* Historia Mathematica.
//!   https://doi.org/10.1016/j.hm.2017.08.001 — Los denominadores 5-smooth
//!   (2,3,4,5,6,8,9,10,12,15,...,60) son precisamente aquellos con recíproco finito exacto en
//!   base-60; `RECIPROCAL_TABLE` implementa el mismo concepto de las tablas babilónicas.

use crate::spa::SPA;
use phf::Map;

/// Returns true if `n` is *5‑smooth* (only prime factors 2, 3, 5).
pub fn is_regular(n: u32) -> bool {
    let mut m = n;
    for p in &[2, 3, 5] {
        while m % p == 0 {
            m /= p;
        }
    }
    m == 1
}

/// Compile‑time generated reciprocal table for regular denominators.
/// We store the raw `i64` value to ensure `phf` compatibility.
static RECIPROCAL_TABLE: Map<u32, i64> = phf::phf_map! {
    2u32 => 6480000,
    3u32 => 4320000,
    4u32 => 3240000,
    5u32 => 2592000,
    6u32 => 2160000,
    8u32 => 1620000,
    9u32 => 1440000,
    10u32 => 1296000,
    12u32 => 1080000,
    15u32 => 864000,
    16u32 => 810000,
    18u32 => 720000,
    20u32 => 648000,
    24u32 => 540000,
    25u32 => 518400,
    27u32 => 480000,
    30u32 => 432000,
    32u32 => 405000,
    36u32 => 360000,
    40u32 => 324000,
    45u32 => 288000,
    48u32 => 270000,
    50u32 => 259200,
    54u32 => 240000,
    60u32 => 216000,
};

/// Direct lookup in the static table.
pub fn reciprocal_direct(denominator: u32) -> Option<SPA> {
    RECIPROCAL_TABLE
        .get(&denominator)
        .map(|&v| SPA::from_raw(v))
}

/// Perform PAI‑60 division: `numerator / denominator`.
/// Uses the lookup table for regular denominators.
pub fn pai60_divide(numerator: SPA, denominator: u32) -> Option<SPA> {
    if let Some(rec) = reciprocal_direct(denominator) {
        // numerator * reciprocal
        Some(numerator * rec)
    } else if is_regular(denominator) {
        // Regular but not in table - could implement factorization here.
        None
    } else {
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_is_regular() {
        assert!(is_regular(30));
        assert!(!is_regular(7));
    }
    #[test]
    fn test_lookup() {
        let r = reciprocal_direct(3).unwrap();
        // 1/3 = 20 minutes = [0, 20, 0, 0, 0]
        assert_eq!(r.to_components(), [0, 20, 0, 0, 0]);
    }
    #[test]
    fn test_divide() {
        let num = SPA::new(10, 0, 0, 0, 0); // 10°
        let res = pai60_divide(num, 3).unwrap();
        // 10 / 3 = 3.333... = 3° 20' = [3, 20, 0, 0, 0]
        assert_eq!(res.to_components(), [3, 20, 0, 0, 0]);
    }
}
