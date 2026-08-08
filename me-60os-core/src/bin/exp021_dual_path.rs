// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! 🧪 EXP-021: S60 DUAL-PATH VALIDATION TEST (RUST NATIVO)
//!
//! Port de `quantum/experiments/EXP_021_S60_DUAL_PATH_TEST.py` con la
//! corrección que el propio Py pedía en comentarios: la rama S60 del Py
//! hacía trampa — convertía a float para `math.log` ("Aproximación,
//! producción usaría Taylor series"). Aquí la rama S60 usa
//! `SPAMath::ln` (Taylor entero, i128) de verdad.
//!
//! OBJETIVO: validar que los cálculos S60 producen resultados comparables
//! a f64 sin comprometer el modelo físico (preparación dual-path Soul Verifier).
//!
//! MÉTODO:
//! 1. Señal rPPG DETERMINISTA (LCG base-60 — el Py usaba /dev/urandom,
//!    irreproducible; misma estadística, resultado repetible)
//! 2. Lyapunov + Entropía Shannon en ambos caminos (float vs S60 puro)
//! 3. Divergencia Δ < 0.1 y rangos físicos (Lyap [0.1, 2.5], Entropía [0.5, 3.5])

use me60os_core::spa::SPA;
use me60os_core::spa_math::SPAMath;

/// Señal rPPG determinista: LCG base-60 con la misma receta del FluxStabilizer
/// (primo 59;59,59 mod 1) mapeada a [60, 100] BPM — el rango del Py.
struct RppgLcg {
    seed: i64, // raw SPA en [0, SCALE_0)
}

impl RppgLcg {
    fn new() -> Self {
        Self {
            seed: SPA::new(0, 42, 0, 0, 0).to_raw(),
        }
    }
    /// Siguiente valor entero en [60, 100]
    fn next_bpm(&mut self) -> i64 {
        let magic = SPA::new(59, 59, 59, 0, 0).to_raw();
        let unity = SPA::SCALE_0;
        self.seed = (self.seed.wrapping_mul(magic)).rem_euclid(unity);
        60 + (self.seed.rem_euclid(41 * (unity / 41))) / (unity / 41)
    }
}

/// Lyapunov rama float (verbatim del Py: abs(ln(d2/d1)), escala 0.5, clamp [0.1, 2.5])
fn lyapunov_float(signal: &[f64]) -> f64 {
    let mut sum_div = 0.0f64;
    let mut count = 0u32;
    for i in 0..signal.len().saturating_sub(2) {
        let d1 = (signal[i + 1] - signal[i]).abs();
        let d2 = (signal[i + 2] - signal[i + 1]).abs();
        if d1 > 0.0001 {
            let ratio = d2 / d1;
            if ratio > 0.0 {
                sum_div += ratio.ln().abs();
                count += 1;
            }
        }
    }
    if count == 0 {
        return 0.0;
    }
    (sum_div / count as f64 * 0.5).clamp(0.1, 2.5)
}

/// Lyapunov rama S60 PURA (ln por Taylor entero — lo que el Py dejó como TODO)
fn lyapunov_s60(signal: &[SPA]) -> SPA {
    let mut sum_div = SPA::zero();
    let mut count: i64 = 0;
    let threshold = SPA::new(0, 0, 0, 1, 0); // 0.0001

    for i in 0..signal.len().saturating_sub(2) {
        let d1 = (signal[i + 1] - signal[i]).abs();
        let d2 = (signal[i + 2] - signal[i + 1]).abs();
        if d1 > threshold {
            let ratio = d2 / d1;
            if ratio > SPA::zero() {
                let ln_val = SPAMath::ln(ratio).abs();
                sum_div = sum_div + ln_val;
                count += 1;
            }
        }
    }
    if count == 0 {
        return SPA::zero();
    }
    let raw_lambda = sum_div / SPA::from_int(count);
    let scaled = raw_lambda * SPA::new(0, 30, 0, 0, 0); // × 0.5
    let min_val = SPA::new(0, 6, 0, 0, 0); // 0.1
    let max_val = SPA::new(2, 30, 0, 0, 0); // 2.5
    if scaled < min_val {
        min_val
    } else if scaled > max_val {
        max_val
    } else {
        scaled
    }
}

/// Entropía de Shannon rama float (buckets ×100, verbatim del Py)
fn entropy_float(signal: &[f64]) -> f64 {
    use std::collections::HashMap;
    let mut counts: HashMap<i64, usize> = HashMap::new();
    for v in signal {
        *counts.entry((v * 100.0) as i64).or_insert(0) += 1;
    }
    let total = signal.len() as f64;
    let mut entropy = 0.0f64;
    for &count in counts.values() {
        let p = count as f64 / total;
        if p > 0.0 {
            entropy -= p * p.ln();
        }
    }
    entropy
}

/// Entropía de Shannon rama S60 PURA (buckets ×100, ln por Taylor entero)
fn entropy_s60(signal: &[SPA]) -> SPA {
    use std::collections::HashMap;
    let bucket_scale = SPA::SCALE_0 / 100;
    let mut counts: HashMap<i64, usize> = HashMap::new();
    for v in signal {
        *counts.entry(v.to_raw() / bucket_scale).or_insert(0) += 1;
    }
    let total = SPA::from_int(signal.len() as i64);
    let mut entropy = SPA::zero();
    for &count in counts.values() {
        if count == 0 {
            continue;
        }
        let p = SPA::from_int(count as i64) / total;
        if p > SPA::zero() {
            // h = -p * ln(p) — ln S60 puro (el Py usaba math.log float)
            let h = p * SPAMath::ln(p).abs();
            entropy = entropy + h;
        }
    }
    entropy
}

fn spa_to_f64(v: SPA) -> f64 {
    v.to_raw() as f64 / SPA::SCALE_0 as f64
}

fn main() {
    println!("🧪 EXP-021: S60 DUAL-PATH VALIDATION TEST (RUST NATIVO)");
    println!("{:=<60}", "");

    // PARTE 1: señal determinista 300 muestras
    let signal_count = 300;
    let mut lcg = RppgLcg::new();
    let signal_int: Vec<i64> = (0..signal_count).map(|_| lcg.next_bpm()).collect();
    let signal_s60: Vec<SPA> = signal_int.iter().map(|&v| SPA::from_int(v)).collect();
    let signal_float: Vec<f64> = signal_int.iter().map(|&v| v as f64).collect();
    println!(
        "📊 Señal rPPG: {} muestras, rango [{}-{}] BPM (LCG base-60 determinista)",
        signal_count,
        signal_int.iter().min().unwrap(),
        signal_int.iter().max().unwrap()
    );

    // PARTE 2: Lyapunov
    let lyap_float = lyapunov_float(&signal_float);
    let lyap_s60 = lyapunov_s60(&signal_s60);
    let lyap_s60_f = spa_to_f64(lyap_s60);
    let lyap_diff = (lyap_float - lyap_s60_f).abs();
    println!("\n📈 Lyapunov:");
    println!("   float: {:.4}", lyap_float);
    println!("   S60:   {:.4}", lyap_s60_f);
    println!(
        "   Divergencia: Δ = {:.4} ({})",
        lyap_diff,
        if lyap_diff < 0.1 { "PASS" } else { "WARN" }
    );

    // PARTE 3: Entropía
    let entr_float = entropy_float(&signal_float);
    let entr_s60 = entropy_s60(&signal_s60);
    let entr_s60_f = spa_to_f64(entr_s60);
    let entr_diff = (entr_float - entr_s60_f).abs();
    println!("\n🎲 Entropía Shannon:");
    println!("   float: {:.4}", entr_float);
    println!("   S60:   {:.4}", entr_s60_f);
    println!(
        "   Divergencia: Δ = {:.4} ({})",
        entr_diff,
        if entr_diff < 0.1 { "PASS" } else { "WARN" }
    );

    // PARTE 4: rangos físicos
    let in_range = |v: f64, lo: f64, hi: f64| v >= lo && v <= hi;
    println!("\n🎯 Rangos físicos:");
    println!(
        "   Lyapunov [0.1, 2.5]: float {} | S60 {}",
        if in_range(lyap_float, 0.1, 2.5) { "✅" } else { "❌" },
        if in_range(lyap_s60_f, 0.1, 2.5) { "✅" } else { "❌" }
    );
    println!(
        "   Entropía [0.5, 3.5]: float {} | S60 {}",
        if in_range(entr_float, 0.5, 3.5) { "✅" } else { "❌" },
        if in_range(entr_s60_f, 0.5, 3.5) { "✅" } else { "❌" }
    );

    let all_pass = lyap_diff < 0.1
        && entr_diff < 0.1
        && in_range(lyap_float, 0.1, 2.5)
        && in_range(lyap_s60_f, 0.1, 2.5)
        && in_range(entr_float, 0.5, 3.5)
        && in_range(entr_s60_f, 0.5, 3.5);

    println!("\n{:=<60}", "");
    if all_pass {
        println!("✅ TODAS LAS PRUEBAS PASARON — S60 seguro para dual-path");
    } else {
        println!("⚠️  ALGUNAS PRUEBAS FUERA DE RANGO — ver números arriba");
    }
    println!("   (rama S60 con SPAMath::ln Taylor entero, sin trampa float)");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lcg_deterministic_and_ranged() {
        let mut a = RppgLcg::new();
        let mut b = RppgLcg::new();
        for _ in 0..100 {
            let va = a.next_bpm();
            assert_eq!(va, b.next_bpm(), "LCG determinista");
            assert!((60..=100).contains(&va), "BPM en rango [60,100]");
        }
    }

    #[test]
    fn test_lyapunov_s60_pure_path_in_physical_range() {
        let mut lcg = RppgLcg::new();
        let signal: Vec<SPA> = (0..300).map(|_| SPA::from_int(lcg.next_bpm())).collect();
        let lyap = lyapunov_s60(&signal);
        // Rango físico del modelo: [0.1, 2.5]
        assert!(lyap >= SPA::new(0, 6, 0, 0, 0), "lyap >= 0.1");
        assert!(lyap <= SPA::new(2, 30, 0, 0, 0), "lyap <= 2.5");
    }

    #[test]
    fn test_entropy_s60_pure_path_positive() {
        let mut lcg = RppgLcg::new();
        let signal: Vec<SPA> = (0..300).map(|_| SPA::from_int(lcg.next_bpm())).collect();
        let entr = entropy_s60(&signal);
        assert!(entr > SPA::zero(), "entropía positiva");
    }
}
