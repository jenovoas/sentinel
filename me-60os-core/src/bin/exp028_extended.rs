// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! 🛡️ EXP-028 EXTENDED — 10 ciclos × 68s (680s) para buscar META-PORTALES
//!
//! ## References
//! - [P-RRS] Novoa, J. (2026). *Reporte Final Resonance Architecture.*
//!   `docs/02_ciencia_y_quantum/FINAL_REPORT_RESONANCE_ARCHITECTURE.md` — meta-portales en ciclos de 68s.
//! - [P-TES] Novoa, J. (2026). *Tesis de Resonancia.* `docs/02_ciencia_y_quantum/research/TesiResonancia.md`.
//! - [EXT-NV] / [NV-050] Nandi & Vitiello (2026). arXiv:2606.30890 — dinámica de cristal de tiempo.

#![allow(
    clippy::float_arithmetic,
    clippy::cast_precision_loss,
    clippy::cast_possible_truncation
)] // EXP binario: estadisticas f64 + conversiones acotadas
use me60os_core::pai60_lib::pai60_divide;
use me60os_core::qhc::QhcTensor;
use me60os_core::resonant_matrix::ResonantMatrix;
use me60os_core::spa::SPA;
use me60os_core::spa_math::SPAMath;

const N_CAPAS: usize = 5;

fn main() {
    let dt = SPA::from_int(1) / SPA::from_int(10); // 0.1s
    let t_max_steps = 6800u32; // 680s = 10 ciclos de 68s

    let period_bio = SPA::from_int(17);
    let period_crys = SPA::from_int(17) / SPA::from_int(4); // 4.25s
    let period_venus = SPA::from_raw(16_180_000); // 16.18s
    let three_sixty = SPA::from_int(360);
    let threshold = SPA::from_int(48) / SPA::from_int(60); // 0.8

    let mut carril_a = ResonantMatrix::new(N_CAPAS);
    let mut carril_b = ResonantMatrix::new(N_CAPAS);
    let qhc = QhcTensor::new();

    println!("🌌 EXP-028 EXTENDED PENTA-RESONANCE — 10 ciclos (680s) META-PORTALES");
    println!("   Buscando alineación de múltiples portales (meta-portales)");
    println!("{:-<72}", "");

    let mut all_portals: Vec<f64> = Vec::new();
    let mut cycle_portals: Vec<Vec<f64>> = vec![Vec::new(); 10];
    let mut prev_aligned = false;

    for step in 0..t_max_steps {
        let t = SPA::from_int(step as i64) * dt;
        let tick = step as u64;
        let cycle = step / 680; // cada 68s = 680 pasos @ 0.1s

        let ph_bio = SPAMath::sin(three_sixty * t / period_bio);
        let ph_crys = SPAMath::sin(three_sixty * t / period_crys);
        let ph_ven = SPAMath::sin(three_sixty * t / period_venus);

        let _mod_a = qhc.apply_modulation(ph_bio, tick);
        let _mod_b = qhc.apply_modulation(ph_bio, tick);

        lift_pai(&mut carril_a, 0, ph_bio);
        lift_pai(&mut carril_a, 1, ph_crys);
        lift_pai(&mut carril_a, 2, ph_ven);
        lift_pai(&mut carril_a, 3, SPA::zero());
        lift_pai(&mut carril_a, 4, SPA::zero());

        lift_pai(&mut carril_b, 0, ph_bio);
        lift_pai(&mut carril_b, 1, ph_crys);
        lift_pai(&mut carril_b, 2, ph_ven);
        lift_pai(&mut carril_b, 3, SPA::zero());
        lift_pai(&mut carril_b, 4, SPA::zero());

        carril_a.step();
        carril_b.step();

        let aligned = ph_bio > threshold && ph_crys > threshold && ph_ven > threshold;

        if aligned && !prev_aligned {
            let t_sec = step as f64 / 10.0;
            all_portals.push(t_sec);
            if cycle < 10 {
                cycle_portals[cycle as usize].push(t_sec);
            }
        }
        prev_aligned = aligned;
    }

    println!("🔮 TOTAL PORTALES EN 680s: {}", all_portals.len());
    println!();

    // Por ciclo
    for (i, portals) in cycle_portals.iter().enumerate() {
        print!("   Ciclo {} ({}s-{}s): ", i, i * 68, (i + 1) * 68);
        if portals.is_empty() {
            println!("(ninguno)");
        } else {
            for p in portals {
                print!("T={:.1}s ", p);
            }
            println!();
        }
    }

    println!();
    println!("🔍 BUSCANDO META-PORTALES (alineación de portales entre ciclos)...");

    // Buscar meta-portales: portales que ocurren en tiempos similares módulo 68s
    let mut meta_counts: std::collections::HashMap<u32, u32> = std::collections::HashMap::new();
    for &t in &all_portals {
        let phase = ((t % 68.0) * 10.0).round() as u32; // discretizar a 0.1s
        *meta_counts.entry(phase).or_insert(0) += 1;
    }

    println!("   Frecuencia de fases de portal (módulo 68s):");
    let mut sorted: Vec<_> = meta_counts.iter().collect();
    sorted.sort_by_key(|(k, _)| *k);
    for (phase, count) in sorted {
        if *count >= 3 {
            // aparece en 3+ ciclos
            println!(
                "   ⭐ META-PORTAL @ fase {:.1}s (aparece en {} ciclos)",
                *phase as f64 / 10.0,
                count
            );
        }
    }

    println!("{:-<72}", "");
    println!("🏆 Portal = convergencia φ_BIO∧φ_CRYSTAL∧φ_VENUS > 0.8");
    println!("   Meta-portal = misma fase de portal en múltiples ciclos de 68s");
}

fn lift_pai(lattice: &mut ResonantMatrix, node: usize, phase: SPA) {
    let raw = phase.to_raw();
    let numer = if raw < 0 { 0 } else { raw };
    if pai60_divide(SPA::from_int(numer), 60).is_some() {
        lattice.inject_pai(node, numer, 60);
    }
}
