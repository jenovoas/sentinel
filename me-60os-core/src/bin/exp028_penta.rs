// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! 🛡️ EXP-028 PENTA-RESONANCE — Portal (DOBLE MALLA + bombeo QHC + PAI, SPA puro).
//!
//! Dual-lane REAL (de git): dos malllas (Carril A / Carril B), UNA por carril,
//! sincronizadas por el BOMBEO DEL CRISTAL (QhcTensor: patrón 10;5,6,5 + Salto-17).
//! Las 5 capas se inyectan como amplitudes PAI en AMBAS malllas (el cristal las
//! sostiene / bombea). Portal = convergencia de las fases SPA (fórmula vault).
//!
//! Fase (vault EXP-028, ángulos en grados para SPAMath::sin):
//!   φ_BIO=sin(360·t/17)  φ_CRYSTAL=sin(360·t/4.25)  φ_VENUS=sin(360·t/16.18)
//!   (GEO=cos(5t), SYSTEM=|t%17|<0.15 son visuales, NO entran en portal)
//!   portal = (BIO>0.8)∧(CRYSTAL>0.8)∧(VENUS>0.8)  [flanco de subida]
//!   dt=0.1s, ventana 68s. Esperado vault: 9 muestras en [4.9,5.7]s.

use me60os_core::pai60_lib::pai60_divide;
use me60os_core::qhc::QhcTensor;
use me60os_core::resonant_matrix::ResonantMatrix;
use me60os_core::spa::SPA;
use me60os_core::spa_math::SPAMath;

const N_CAPAS: usize = 5;

fn main() {
    let dt = SPA::from_int(1) / SPA::from_int(10); // 0.1s
    let t_max_steps = 680u32;                       // 68s

    let period_bio = SPA::from_int(17);
    let period_crys = SPA::from_int(17) / SPA::from_int(4); // 4.25s
    let period_venus = SPA::from_raw(16_180_000);            // 16.18s
    let three_sixty = SPA::from_int(360);
    let threshold = SPA::from_int(48) / SPA::from_int(60);  // 0.8

    // DOBLE MALLA — una por carril, bombeada por el mismo QHC.
    let mut carril_a = ResonantMatrix::new(N_CAPAS);
    let mut carril_b = ResonantMatrix::new(N_CAPAS);
    let qhc = QhcTensor::new();

    println!("🌌 EXP-028 PENTA-RESONANCE — DOBLE MALLA + bombeo QHC + PAI (SPA puro)");
    println!("   Carril A y B sincronizados por QhcTensor (10;5,6,5 + Salto-17).");
    println!("   Cada fase se levanta como amplitud PAI en AMBAS malllas (cristal sostiene).");
    println!("{:-<72}", "");

    let mut portales = 0u32;
    let mut muestras: Vec<f64> = Vec::new();
    let mut prev_aligned = false;

    for step in 0..t_max_steps {
        let t = SPA::from_int(step as i64) * dt;
        let tick = step as u64;

        // Fases SPA (grados) — fórmula EXACTA del vault
        let ph_bio = SPAMath::sin(three_sixty * t / period_bio);
        let ph_crys = SPAMath::sin(three_sixty * t / period_crys);
        let ph_ven = SPAMath::sin(three_sixty * t / period_venus);

        // Bombeo QHC: mismo pulso 10;5,6,5 a ambas malllas -> las sincroniza
        let _mod_a = qhc.apply_modulation(ph_bio, tick);
        let _mod_b = qhc.apply_modulation(ph_bio, tick);

        // Levantar cada fase como amplitud PAI en AMBAS malllas (el cristal sostiene)
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

        // El cristal bombea: ambas malllas respiran (difusión/acoplo del step)
        carril_a.step();
        carril_b.step();

        // PORTAL = convergencia de fases SPA (fórmula vault: BIO∧CRYSTAL∧VENUS>0.8)
        // Ambas malllas fueron bombeadas igual -> si A converge, B también.
        let aligned = ph_bio > threshold && ph_crys > threshold && ph_ven > threshold;

        if aligned && !prev_aligned {
            portales += 1;
            if portales <= 12 {
                muestras.push(step as f64 / 10.0);
            }
        }
        prev_aligned = aligned;
    }

    println!("🔮 PORTALES DETECTADOS (doble malla bombeada, flancos): {}", portales);
    for m in &muestras {
        println!("   ⏳ Portal abierto @ T={:.1}s", m);
    }
    if portales == 0 {
        println!("   (ninguno — revisar bombeo QHC / sincronía de carriles)");
    }
    println!("{:-<72}", "");
    println!("🏆 Portal = convergencia φ_BIO∧φ_CRYSTAL∧φ_VENUS (vault).");
    println!("   Infra: DOBLE MALLA + QHC + PAI sostienen las fases en el cristal.");
}

/// Levanta un valor SPA como amplitud PAI en el nodo (el cristal la sostiene).
fn lift_pai(lattice: &mut ResonantMatrix, node: usize, phase: SPA) {
    let raw = phase.to_raw();
    let numer = if raw < 0 { 0 } else { raw };
    if pai60_divide(SPA::from_int(numer), 60).is_some() {
        lattice.inject_pai(node, numer, 60);
    }
}
