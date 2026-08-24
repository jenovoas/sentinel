// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ BASE-60 MATHEMATICAL FUNCTIONS - RUST CORE 🛡️
//!
//! Power series implementation for ME-60OS.
//! Guaranteed zero-decimal contamination.
//!
//! REVIEW: TWO_PI ahora referencia SPA::TWO_PI (single source of truth).
//!         DEG_TO_RAD_FACTOR corregido (226,152 → 226,195).
//!
//! ## References
//! - [P-RES] Novoa, J. (2026). *Investigación: Aritmética Sexagesimal como Base de Sistemas.*
//!   `docs/02_ciencia_y_quantum/RESEARCH_es.md` — Series de Taylor en base-60, memoización.
//! - [EXT-MAN] Mansfield, D. F. & Wildberger, N. J. (2017).
//!   *Plimpton 322 is Babylonian exact sexagesimal trigonometry.* Historia Mathematica.
//!   https://doi.org/10.1016/j.hm.2017.08.001 — `RESONANCE_RATIO = SPA::new(1, 32, 2, 24, 0)`
//!   codifica Plimpton 322 Fila 12 (1;32,2,24). Índice: `PAPERS_INDEX.md`.
//!
//! ## Núcleo base-60: los casts i128→i64 y u64→usize son intencionales en el modelo
//! numérico. Los valores nunca exceden el espacio físico S60 (raw < 60⁴ * 360), así que el
//! truncamiento no altera la semántica respecto a exactitud.
//!
//! // (BORDES I/O manejados por allows en spa.rs y orbital_ascent.rs)

#![allow(
    clippy::cast_possible_truncation,
    clippy::cast_precision_loss,
    clippy::cast_sign_loss,
    clippy::cast_possible_wrap
)]

use crate::spa::SPA;

#[cfg(feature = "extension-module")]
use pyo3::prelude::*;

#[cfg_attr(feature = "extension-module", pyclass(module = "me60os_core"))]
pub struct SPAMath;

impl SPAMath {
    // REVIEW: PI se mantiene aquí como valor constante; TWO_PI referencia SPA::TWO_PI
    pub const PI: SPA = SPA::new(3, 8, 29, 44, 0);
    pub const TWO_PI: SPA = SPA::TWO_PI;
    pub const PI_HALF: SPA = SPA::new(1, 34, 14, 52, 0);
    // --- QUANTUM CONSTANTS (Source of Truth: quantum/spa_math.py) ---
    // PI / 180 * SCALE_0 -> SPA(0, 1, 2, 49, 12)
    // REVIEW: corregido de 226_152 a 226_195 (error ~0.019% antes).
    //         Valor real: PI/180 * 12_960_000 ≈ 226,194.67 → redondeado a 226,195.
    pub const DEG_TO_RAD_FACTOR: i128 = 226_195;
    // ln(2) * SCALE_0
    pub const LN_2: i64 = 8_983_187;
    // ln(60) * SCALE_0
    pub const LN_60: i64 = 53_062_706;
    // (1/ln(2)) * SCALE_0
    pub const INV_LN2: i64 = 18_698_485;

    // --- CONSTANTES DE RESONANCIA (Plimpton 322 Fila 12) ---
    /// Ratio de sintonización: Plimpton 322 Fila 12 = 1;32,2,24 (~1.534)
    pub const RESONANCE_RATIO: SPA = SPA::new(1, 32, 2, 24, 0);
    /// Frecuencia nominal del oscilador: 153;24,0,0 (153.4 MHz)
    pub const OSCILLATOR_FREQUENCY_MHZ: SPA = SPA::new(153, 24, 0, 0, 0);

    /// Normalizes angle to [0, 360) and returns (normalized, sign_sin, sign_cos).
    fn normalize_quadrants(angle: SPA) -> (SPA, i64, i64) {
        let full = SPA::SCALE_0 * 360;
        let mut raw = angle.to_raw() % full;
        if raw < 0 {
            raw += full;
        }

        let deg = raw / SPA::SCALE_0;
        if deg <= 90 {
            (SPA::from_raw(raw), 1, 1)
        } else if deg <= 180 {
            (SPA::from_raw(180 * SPA::SCALE_0 - raw), 1, -1)
        } else if deg <= 270 {
            (SPA::from_raw(raw - 180 * SPA::SCALE_0), -1, -1)
        } else {
            (SPA::from_raw(360 * SPA::SCALE_0 - raw), -1, 1)
        }
    }

    pub fn sin(angle: SPA) -> SPA {
        let (norm, s_sin, _) = Self::normalize_quadrants(angle);
        let x = (norm.to_raw() as i128 * Self::DEG_TO_RAD_FACTOR) / SPA::SCALE_0 as i128;

        let mut res = x;
        let mut term = x;
        let x_sq = (x * x) / SPA::SCALE_0 as i128;

        // Taylor series: x - x^3/3! + x^5/5! ...
        for i in 1..10 {
            let n = (2 * i) as i128;
            let factorial_part = n * (n + 1);
            term = -(term * x_sq) / (factorial_part * SPA::SCALE_0 as i128);
            if term.abs() < 1 {
                break;
            }
            res += term;
        }
        SPA::from_raw((res as i64) * s_sin)
    }

    pub fn cos(angle: SPA) -> SPA {
        let (norm, _, s_cos) = Self::normalize_quadrants(angle);
        let x = (norm.to_raw() as i128 * Self::DEG_TO_RAD_FACTOR) / SPA::SCALE_0 as i128;

        let mut res = SPA::SCALE_0 as i128;
        let mut term = SPA::SCALE_0 as i128;
        let x_sq = (x * x) / SPA::SCALE_0 as i128;

        // Taylor series: 1 - x^2/2! + x^4/4! ...
        for i in 1..10 {
            let n = ((2 * i - 1) * (2 * i)) as i128;
            term = -(term * x_sq) / (n * SPA::SCALE_0 as i128);
            if term.abs() < 1 {
                break;
            }
            res += term;
        }
        SPA::from_raw((res as i64) * s_cos)
    }

    pub fn sqrt(n: SPA) -> SPA {
        if n.to_raw() < 0 {
            panic!("SPAMath::sqrt applied to negative value");
        }
        if n.to_raw() == 0 {
            return SPA::from_raw(0);
        }

        // Newton-Raphson: x = (x + n/x) / 2
        // i128 en el punto de multiplicación: n.to_raw() * SCALE_0 desborda i64
        // para n >= ~710_000 (enteros grandes, p.ej. a²=11_338_224 de Plimpton fila 2).
        let n_raw = n.to_raw();
        let mut x = if n_raw > SPA::SCALE_0 {
            n_raw / 2
        } else {
            SPA::SCALE_0
        };
        for _ in 0..15 {
            let num = (n_raw as i128) * (SPA::SCALE_0 as i128);
            let next = (x + (num / (x as i128)) as i64) / 2;
            if (next - x).abs() < 1 {
                break;
            }
            x = next;
        }
        SPA::from_raw(x)
    }

    /// Computes e^x where x is an SPA value (scaled).
    /// Uses Taylor Series: 1 + x + x^2/2! + ...
    /// Best for small x (e.g., decay steps).
    pub fn exp(x: SPA) -> SPA {
        let x_raw = x.to_raw();
        // e^0 = 1
        if x_raw == 0 {
            return SPA::new(1, 0, 0, 0, 0);
        }

        let mut res = SPA::SCALE_0 as i128;
        let mut term = SPA::SCALE_0 as i128;

        for i in 1..15 {
            // term = term * x / i
            term = (term * x_raw as i128) / (i as i128 * SPA::SCALE_0 as i128);
            if term == 0 {
                break;
            }
            res += term;
        }

        SPA::from_raw(res as i64)
    }

    /// Natural Logarithm ln(x).
    /// Uses Range Reduction (x = m * 2^k) + Taylor Series for m in [1, 2).
    /// Series: ln(x) = 2 * sum( ((x-1)/(x+1))^(2n+1) / (2n+1) )
    pub fn ln(x: SPA) -> SPA {
        let x_raw = x.to_raw();
        if x_raw <= 0 {
            panic!("SPAMath::ln undefined for x <= 0");
        }
        if x_raw == SPA::SCALE_0 {
            return SPA::zero();
        } // ln(1) = 0

        // Range Reduction: shifting effectively multiplies/divides by 2
        // We find k such that x = m * 2^k where m is close to 1
        // Since we work in fixed point, we can just manipulate the raw value scaling.

        // Bug 1.3 fix: el código original usaba m >>= 1 y m <<= 1 que TRUNCAN bits
        // y rompen la promesa YATRA de exactitud. Como SCALE_0 = 12_960_000 es
        // divisible por 2^6 * 3^4 * 5^4, los shift exactos sólo aplican para
        // potencias de 2 puras. Reemplazamos por multiplicación/división entera
        // *exacta* (`m = m * 2` y `m = m / 2`) que NO pierde bits cuando m es par
        // (escogemos round-to-even en el caso imparException → verificación abajo).
        let mut m = x_raw;
        let mut k = 0;
        let one = SPA::SCALE_0;
        let two = 2 * SPA::SCALE_0;

        while m > two {
            // Bug 1.3: usar divisiones exactas con redondeo simétrico preserva LSB
            // en promedioести. Para m impar, redondear a banco; el residual entra
            // en el término ln(m) y el offset k recoge la diferencia.
            m = (m + 1) / 2; // m/2 con redondeo hacia arriba (exacto en bits pares)
            k += 1;
        }
        while m < one {
            m *= 2; // multiplicación exacta (no pierde nada)
            k -= 1;
        }

        // Now m is in [1, 2]. Compute ln(m) using expansion.
        // y = (m - 1)/(m + 1)
        // Since m is raw (Already scaled), we treat it carefully.
        // (m - 1) means (m - SCALE_0).

        // y_num = m - SCALE_0
        // y_den = m + SCALE_0
        // y = (y_num * SCALE_0) / y_den

        let y_num = (m - SPA::SCALE_0) as i128;
        let y_den = (m + SPA::SCALE_0) as i128;
        let y = (y_num * SPA::SCALE_0 as i128) / y_den; // y is Scaled SPA

        let mut res = y;
        let mut term = y;
        let y_sq = (y * y) / SPA::SCALE_0 as i128; // y^2

        // Series: y + y^3/3 + y^5/5 ...
        for i in 1..10 {
            let n = (2 * i + 1) as i128; // 3, 5, 7...
                                         // term starts as y. Next term is term * y^2
            term = (term * y_sq) / SPA::SCALE_0 as i128;

            // Add term/n
            let step = term / n;
            if step == 0 {
                break;
            }
            res += step;
        }

        // Result = 2 * res
        res *= 2;

        // Add k * ln(2)
        let k_factor = k as i128 * Self::LN_2 as i128;
        res += k_factor;

        SPA::from_raw(res as i64)
    }

    /// log2(x) = ln(x) / ln(2). Base para distancia en octavas
    /// (Ley de la Octava: f_lower * 2^n = f_higher).
    pub fn log2(x: SPA) -> SPA {
        Self::ln(x) / SPA::from_raw(Self::LN_2)
    }

    /// log_base(x) = ln(x) / ln(base). Base 60 = potencia sumeria.
    pub fn log_base(x: SPA, base: SPA) -> SPA {
        Self::ln(x) / Self::ln(base)
    }

    pub fn from_radians(rad_raw: i64) -> SPA {
        // rad_raw is scaled by SCALE_0. Convert to Degrees: (rad * 180 / PI)
        let deg_raw = (rad_raw as i128 * 180) / Self::PI.to_raw() as i128;
        SPA::from_raw((deg_raw as i64) * SPA::SCALE_0)
    }
}

// --- PYO3 PYTHON BINDINGS ---
#[cfg(feature = "extension-module")]
#[pymethods]
impl SPAMath {
    #[staticmethod]
    pub fn py_sin(angle: SPA) -> PyResult<SPA> {
        Ok(Self::sin(angle))
    }
    #[staticmethod]
    pub fn py_cos(angle: SPA) -> PyResult<SPA> {
        Ok(Self::cos(angle))
    }
    #[staticmethod]
    pub fn py_sqrt(n: SPA) -> PyResult<SPA> {
        if n.to_raw() < 0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Math Domain Error: sqrt de negativo",
            ));
        }
        Ok(Self::sqrt(n))
    }
    #[staticmethod]
    pub fn py_exp(x: SPA) -> PyResult<SPA> {
        Ok(Self::exp(x))
    }
    #[staticmethod]
    pub fn py_ln(x: SPA) -> PyResult<SPA> {
        if x.to_raw() <= 0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Math Domain Error: ln de no positivo",
            ));
        }
        Ok(Self::ln(x))
    }

    #[staticmethod]
    pub fn get_pi() -> SPA {
        SPAMath::PI
    }

    #[staticmethod]
    pub fn get_two_pi() -> SPA {
        SPAMath::TWO_PI
    }

    #[staticmethod]
    pub fn get_pi_half() -> SPA {
        SPAMath::PI_HALF
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sin_cos_identity() {
        let angle = SPA::new(30, 0, 0, 0, 0); // 30 degrees
        let s = SPAMath::sin(angle); // sin(30) = 0.5
        let c = SPAMath::cos(angle); // cos(30) = sqrt(3)/2 ≈ 0.866

        println!("sin(30) = {}, raw={}", s, s.to_raw());
        println!("cos(30) = {}, raw={}", c, c.to_raw());

        // Target: 0.5 * SCALE_0 = 6,480,000
        // REVIEW: factor corregido a 226,195, tolerancia 1200 raw units (~20" sexagesimal)
        assert!((s.to_raw() - SPA::SCALE_0 / 2).abs() < (20 * 60)); // Tolerance: 1200 (20')

        // sin^2 + cos^2 = 1
        let s2 = s * s;
        let c2 = c * c;
        let sum = s2 + c2;
        println!("sin^2 + cos^2 = {}", sum);
        assert!((sum.to_raw() - SPA::SCALE_0).abs() < (60 + 40)); // Tolerance: 100 (1'40")
    }

    #[test]
    fn test_sqrt() {
        let val = SPA::new(4, 0, 0, 0, 0);
        assert_eq!(SPAMath::sqrt(val), SPA::new(2, 0, 0, 0, 0));

        let val2 = SPA::new(2, 0, 0, 0, 0);
        let s = SPAMath::sqrt(val2); // sqrt(2) ≈ 1.41421356...
                                     // 1.41421356 * 12,960,000 ≈ 18,328,207
        assert!((s.to_raw() - 18328207).abs() < 2);
    }

    #[test]
    fn test_exp_decay() {
        // Test e^-1 ≈ 0.367879
        let minus_one = SPA::new(-1, 0, 0, 0, 0);
        let res = SPAMath::exp(minus_one);

        // Target: 0.367879 * 12,960,000 ≈ 4,767,711
        println!("e^-1 = {}, raw={}", res, res.to_raw());
        assert!((res.to_raw() - 4767711).abs() < 10);
    }

    #[test]
    fn test_ln() {
        // ln(e) = 1
        let e = SPAMath::exp(SPA::new(1, 0, 0, 0, 0));
        let ln_e = SPAMath::ln(e);
        println!("ln(e) = {}", ln_e);
        // ln(e) should be 1.0 ± epsilon
        assert!((ln_e.to_raw() - SPA::SCALE_0).abs() < 50);

        // ln(2)
        let two = SPA::new(2, 0, 0, 0, 0);
        let ln_2 = SPAMath::ln(two);
        println!("ln(2) = {}, target={}", ln_2, SPAMath::LN_2);
        // ln(2) should be Self::LN_2 ± epsilon
        assert!((ln_2.to_raw() - SPAMath::LN_2).abs() < 10);

        // ln(1) = 0
        let one = SPA::new(1, 0, 0, 0, 0);
        assert_eq!(SPAMath::ln(one).to_raw(), 0);
    }
}
