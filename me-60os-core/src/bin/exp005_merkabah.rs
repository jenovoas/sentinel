// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! 🛡️ EXP-005 MERKABAH G-ZERO — Réplica en runtime Rust (SPA, sin float).
//! Lógica tomada del prototipo Python quantum/experiments/EXP_005_MERKABAH_G_ZERO.py
//! (ese .py guarda la física; el wrapper S60 quedó roto por la migración a Rust).
//!
//! Fórmula (base-60 pura):
//!   resonance = (cp^2 * coherence * tuning) / phi^2
//!   M_eff = M_static / (1 + resonance / 200)
//! Objetivo: reducción de masa > 95% a potencia máxima.

#![allow(
    clippy::float_arithmetic,
    clippy::cast_precision_loss,
    clippy::cast_possible_truncation
)] // BIN bench/exp: medicion y estadisticas en f64; conversiones acotadas por construccion
use me60os_core::spa::SPA;

fn main() {
    // Constantes físicas (S60 = [deg, min, sec, ...])
    let m_static = SPA::new(2, 30, 0, 0, 0); // 2.5 kg
    let phi = SPA::new(1, 37, 4, 0, 0); // ~1.618 (áureo)
    let tuning = SPA::new(1, 21, 57, 0, 0); // ~1.366 (scalar tuning)
    let base_scale = SPA::new(200, 0, 0, 0, 0);
    let coherence = SPA::ONE; // 100%

    println!("🚀 EXP-005 (Rust SPA): MERKABAH G-ZERO VALIDATION");
    println!("   Masa Estática: {} (2.5 kg)", m_static);
    println!(
        "   PHI: {} | TUNING: {} | BASE_SCALE: {}",
        phi, tuning, base_scale
    );
    println!("{:-<60}", "");
    println!(
        "{:<10} | {:<28} | {:<10}",
        "POWER %", "M_EFF (S60)", "REDUC %"
    );
    println!("{:-<60}", "");

    let mut best_reduction = 0i64;

    for power in (0..=100).step_by(10) {
        let cp = SPA::new(power as i64, 0, 0, 0, 0);

        // resonance_factor = cp^2 * coherence * tuning / phi^2
        let cp_sq = cp * cp;
        let num = cp_sq * coherence * tuning;
        let den = phi * phi;
        let resonance = num / den; // SPA / SPA (sobrecarga Div, sin float)

        // M_eff = M_static / (1 + resonance / 200)
        let divisor_term = resonance / base_scale;
        let total_divisor = SPA::ONE + divisor_term;
        let m_eff = m_static / total_divisor;

        // reducción % = (M_static - M_eff) / M_static * 100
        let diff = m_static - m_eff;
        let reduction = (diff * SPA::new(100, 0, 0, 0, 0)) / m_static;

        // reducción como entero % (parte grados de SPA = % entero)
        let reduction_pct = reduction.components[0];
        best_reduction = best_reduction.max(reduction_pct);

        println!(
            "{:<10} | {:<28} | {:<10}",
            power,
            format!("{}", m_eff),
            format!("{}%", reduction_pct)
        );
    }

    println!("{:-<60}", "");
    if best_reduction >= 95 {
        println!(
            "🏆 CONCLUSIÓN: protocolo Merkabah VÁLIDO (reducción pico {}% >= 95%).",
            best_reduction
        );
    } else {
        println!(
            "⚠️ CONCLUSIÓN: reducción pico {}% < 95%. Requiere más sintonía/coherencia.",
            best_reduction
        );
    }
}
