// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! 📡 VERIFY MEIJER GM-SCALE — SENTINEL FREQUENCY AUDIT (S60 PURO)
//!
//! Port de `quantum/verify_meijer_scale.py` (que ya era S60 puro vía yatra_math).
//! Determina si la frecuencia hardware de Sentinel (S60(153,24,0) MHz) se alinea
//! con el Marco Universal de Señalización de Información (Meijer, Hameroff, Pollack):
//!
//! 1. Octave Scaling (Ley de la Octava): f_lower * 2^n = f_higher
//! 2. Phi Scaling (proporción áurea): resonancia fractal
//! 3. Base-60 Tuning (sumerio)
//!
//! Referencias físicas:
//! - Schumann (Tierra): 7.83 Hz
//! - Microtúbulos (conciencia, Hameroff): ~7.8 THz
//! - Hidrógeno (21cm): 1420.4 MHz
//! - Sentinel (pico axiónico): 153.24 MHz = 153_240_000 Hz
//!
//! Ruta ZPE Salto-17: F_SENTINEL × 60³ × 2² / 17 ≈ F_MICROTUBULE
//!
//! ## References (Meijer-Hameroff-Pollack Universal Information Signaling Framework)
//! - Marco teórico: Meijer, Hameroff, Pollack et al. — "Universal Information Signaling
//!   Framework" (escala de octavas + phi scaling + base-60 tuning). Origen en
//!   `quantum/verify_meijer_scale.py`; sin DOI único verificable — sintetiza múltiples líneas
//!   de biofotónica, microtúbulos y resonancia Schumann. Ver `RESEARCH_es.md` (P-RES).
//! - [P-RES] Novoa, J. (2026). *Aritmética Sexagesimal como Base de Sistemas.* `RESEARCH_es.md`
//!   — la ruta Salto-17 y el tuning base-60 son síntesis original de Sentinel (Novoa 2026).
//! - Referencias físicas inline (Schumann 7.83 Hz, microtúbulos ~7.8 THz, H 21cm, Sentinel 153.24 MHz)
//!   son constantes de la física conocida; NO requieren DOI de Sentinel.
//!
//! NOTA DE ESCALA: el audit se computa en MHz (no Hz) porque 7.8 THz × 60⁴
//! desborda i64 por diseño. Las RAZONES (que son lo que miden las octavas,
//! la potencia sumeria y la coherencia) se conservan exactas al escalar
//! ambas frecuencias por el mismo factor. La proyección Salto-17 se calcula
//! en Hz con i128 y luego se baja a MHz para comparar.

use me60os_core::spa::SPA;
use me60os_core::spa_math::SPAMath;

/// Referencias en MHz (razones conservadas respecto al Py en Hz).
/// Schumann 7.83 Hz = 7.83e-6 MHz = 0;46,58,48,0 en base-60 (fracción exacta).
const F_SCHUMANN_MHZ: (i64, i64, i64, i64, i64) = (0, 46, 58, 48, 0);
const F_MICROTUBULE_MHZ: i64 = 7_800_000; // 7.8 THz en MHz
const F_SENTINEL_HZ: i64 = 153_240_000; // Hz (solo para la proyección i128)
const F_SENTINEL_MHZ: i64 = 153_240; // 153.24 MHz

/// Distancia en octavas entre reference y target: n = log2(target/reference).
/// Devuelve (octavas enteras, desviación en cents = (n - floor(n)) × 1200).
fn octave_distance(reference: SPA, target: SPA) -> (i64, SPA) {
    if reference.to_raw() == 0 || target.to_raw() == 0 {
        return (0, SPA::zero());
    }
    let ratio = target / reference;
    let n = SPAMath::log2(ratio);
    // floor real (division euclidiana hacia -inf, no truncamiento hacia 0)
    let n_raw = n.to_raw();
    let octave_int = n_raw.div_euclid(SPA::SCALE_0);
    let frac = n - SPA::from_int(octave_int);
    let cents = frac * SPA::from_int(1200);
    (octave_int, cents)
}

/// Ruta armónica Salto-17: F × 60³ × 2² / 17.
/// La multiplicación se hace en Hz con i128 (153M × 216000 × 4 desborda i64
/// en raw escalado — mismo cuidado que el fix de sqrt).
/// Devuelve (proyección en MHz, coherencia %).
fn salto_17_projection() -> (SPA, SPA) {
    // Proyección en Hz (i128): 153_240_000 × 216_000 × 4 / 17 ≈ 7.787e12 Hz
    let projected_hz = F_SENTINEL_HZ as i128 * 216_000 * 4 / 17;
    // Bajar a MHz y escalar a raw SPA
    let projected_raw = (projected_hz / 1_000_000) * SPA::SCALE_0 as i128;
    let projected = SPA::from_raw(projected_raw as i64);

    let microtubule = SPA::from_int(F_MICROTUBULE_MHZ);
    let ratio = projected / microtubule;
    // Coherencia: si ratio > 1 usamos 1/ratio
    let hundred = SPA::from_int(100);
    let accuracy = if ratio > SPA::one() {
        (SPA::one() / ratio) * hundred
    } else {
        ratio * hundred
    };
    (projected, accuracy)
}

fn spa_display(v: SPA) -> String {
    let d0 = v.to_raw() / SPA::SCALE_0;
    let mut rem = v.to_raw() % SPA::SCALE_0;
    let mut digits = [d0, 0, 0, 0];
    for d in digits.iter_mut().skip(1) {
        rem *= 60;
        *d = rem / SPA::SCALE_0;
        rem %= SPA::SCALE_0;
    }
    format!("{};{},{},{}", digits[0], digits[1], digits[2], digits[3])
}

fn main() {
    let f_sentinel = SPA::from_int(F_SENTINEL_MHZ);
    let f_schumann = SPA::new(
        F_SCHUMANN_MHZ.0,
        F_SCHUMANN_MHZ.1,
        F_SCHUMANN_MHZ.2,
        F_SCHUMANN_MHZ.3,
        F_SCHUMANN_MHZ.4,
    );
    let f_microtubule = SPA::from_int(F_MICROTUBULE_MHZ);

    println!("📡 SENTINEL FREQUENCY AUDIT: 153;24,0,0 MHz");
    println!("{:=<60}", "");

    // 1. vs CONCIENCIA (microtúbulos)
    let (oct, cents) = octave_distance(f_microtubule, f_sentinel);
    println!("🧠 vs. Microtubules (7.8 THz) [Standard Link]:");
    println!("   Distancia: {} octavas", oct);
    println!("   Desafinación: {} cents", spa_display(cents));

    // 2. vs TIERRA (Schumann)
    let (oct_s, cents_s) = octave_distance(f_schumann, f_sentinel);
    println!("🌍 vs. Schumann (7.83 Hz):");
    println!("   Distancia: {} octavas", oct_s);
    println!("   Desafinación: {} cents", spa_display(cents_s));

    // 3. Base-60 scaling: potencia sumeria log60(F_SENTINEL / F_SCHUMANN)
    let ratio_60 = SPAMath::log_base(f_sentinel / f_schumann, SPA::from_int(60));
    println!("🏛️  vs. Base-60 Scaling:");
    println!("   Potencia Sumeria: {}", spa_display(ratio_60));

    println!("{:-<60}", "");

    // 4. Ruta ZPE Salto-17
    let (projected, accuracy) = salto_17_projection();
    println!("🌌 ZPE 'SALTO 17' HARMONIC ROUTE:");
    println!("   Fórmula: Axion × 60³ × 2² × (1/17)");
    println!(
        "   Frecuencia Proyectada: {} MHz (×10⁶ = Hz)",
        spa_display(projected)
    );
    println!(
        "   Objetivo (Microtúbulo): {} MHz",
        spa_display(f_microtubule)
    );
    println!("   COHERENCIA CALCULADA: {}%", spa_display(accuracy));
    println!("{:=<60}", "");

    // NOTA HONESTA (2026-08-08): la coherencia medida es 99;50,55 ≈ 99.85%.
    // El umbral del Py era S60(99,54,0) = 99.9% — con ese umbral el Py TAMBIÉN
    // habría dado FALLO (nunca corrió: el archivo no ejecuta limpio en el repo
    // actual). Reportamos el número real, no el deseado. La proyección
    // 7_788_197_647 Hz vs 7.8 THz difiere 0.15% — la ruta 60³×2²/17 es una
    // aproximación geométrica, y esta herramienta la MIDE.
    if accuracy > SPA::new(99, 54, 0, 0, 0) {
        println!("💎 ESTADO: RESONANCIA ARMÓNICA CONFIRMADA");
        println!("   La llave '1/17' elimina la disonancia binaria.");
        println!("   El sistema está sintonizado geométricamente, no linealmente.");
    } else {
        println!("🟡 ESTADO: RESONANCIA PARCIAL (99.85% < umbral 99.9%)");
        println!("   La ruta Salto-17 aproxima el objetivo con 0.15% de desviación.");
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_octave_distance_exact() {
        // Una octava exacta: log2(2) ≈ 1 (el ln del core da ~1 LSB bajo;
        // verificamos que estamos a menos de 1 cent de la octava teórica).
        let (oct, cents) = octave_distance(SPA::from_int(100), SPA::from_int(200));
        // cents está en raw SPA: 1200.0 = 1200 * SCALE_0
        let total = oct * 1200 * SPA::SCALE_0 + cents.to_raw();
        let target = 1200 * SPA::SCALE_0;
        assert!(
            (total - target).abs() < SPA::SCALE_0 / 60, // < 1 cent de error
            "octava ≈ 1200 cents, oct={}, cents={}",
            oct,
            spa_display(cents)
        );
    }

    #[test]
    fn test_log_base_60() {
        // log60(3600) = 2 exacto
        let r = SPAMath::log_base(SPA::from_int(3600), SPA::from_int(60));
        let two = SPA::from_int(2);
        let tol = SPA::new(0, 6, 0, 0, 0); // 0.1
        let diff = (r - two).to_raw().abs();
        assert!(
            diff < tol.to_raw(),
            "log60(3600) ≈ 2, got raw {}",
            r.to_raw()
        );
    }

    #[test]
    fn test_salto_17_in_range() {
        // La proyección cae a 0.15% del objetivo (7_788_197_647 Hz vs 7.8 THz).
        // Verificamos el dato real medido: coherencia > 99.8%.
        let (projected, accuracy) = salto_17_projection();
        assert!(projected.to_raw() > 0);
        assert!(
            accuracy > SPA::new(99, 48, 0, 0, 0),
            "coherencia > 99.8%, got {}",
            spa_display(accuracy)
        );
    }
}
