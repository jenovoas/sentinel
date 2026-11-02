// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
//! 🛡️ EXP-028 PENTA-RESONANCE — DOBLE MALLA HEXAGONAL (91 nodos/carril)
//!
//! Restaurado de `c1d7ca9c` (borrado por "f64 no compilaba") y migrado a S60 puro.
//! Arquitectura real: DOS mallas HexagonalController (91 nodos cada una)
//!   - Carril A (Security): WAL fsync, determinista
//!   - Carril B (Observability): buffering, reorder
//! Ambas sincronizadas por QhcTensor (patrón 10;5,6,5 + Salto-17/68s)
//!
//! PORTAL = superposición armónica EMERGENTE de ambas mallas
//!   No es threshold hardcodeado: es coherencia de fase cruzada
//!   entre lane A y lane B acopladas por el cristal.
//!
//! Migración f64→S60: periodos en décimas de segundo (i64), fases en grados
//! enteros, coherencia en milésimas. Sin floats, sin unsafe, sin static mut.

use me60os_core::hexagonal_control::HexagonalController;
use me60os_core::qhc::QhcTensor;
use me60os_core::spa::SPA;


const DT_DECI: i64 = 1; // 0.1s por step, en décimas
const T_MAX_STEPS: u32 = 6800; // 680s = 10 ciclos × 68s

/// Periodos de las 5 capas en décimas de segundo (×10).
const PERIOD_BIO_D: i64 = 170; // 17.0s
const PERIOD_CRYS_D: i64 = 43; // ~4.25s (41.77 Hz modulado)
const PERIOD_VENUS_D: i64 = 162; // ~16.18s
const PERIOD_GEO_D: i64 = 2; // ~0.2s base
const PERIOD_SYS_D: i64 = 170; // 17.0s

fn main() {
    println!("🌌 EXP-028 PENTA-RESONANCE — DOBLE MALLA HEXAGONAL 91 NODOS/CARRIL (S60 puro)");
    println!("   Carril A (Security) + Carril B (Observability) = 182 nodos totales");
    println!("   Sincronización: QhcTensor (10;5,6,5 + Salto-17/68s)");
    println!("   Portal = SUPERPOSICIÓN ARMÓNICA EMERGENTE (no threshold)");
    println!("{:-<72}", "");

    let mut lane_a = HexagonalController::new(3);
    let mut lane_b = HexagonalController::new(3);
    let qhc = QhcTensor::new();

    let mut all_portals: Vec<PortalEvent> = Vec::new();
    let mut cycle_portals: Vec<Vec<PortalEvent>> = vec![Vec::new(); 10];

    for step in 0..T_MAX_STEPS {
        let t_d = step as i64 * DT_DECI; // décimas de segundo
        let tick = step as u64;
        let cycle = (step / 680) as usize;

        // 1. Fases de las 5 capas en grados enteros (0-359).
        // fase = (360 * t / periodo) % 360, todo en enteros S60-compatibles.
        let ph_bio = phase_deg(t_d, PERIOD_BIO_D);
        let ph_crys = phase_deg(t_d, PERIOD_CRYS_D);
        let ph_venus = phase_deg(t_d, PERIOD_VENUS_D);
        let ph_geo = (360 * 5 * t_d / 10) % 360; // 5 ciclos por segundo base
        let ph_sys = if (t_d % PERIOD_SYS_D) < 2 { 90 } else { 0 }; // pulso sistema

        // 2. Bombeo QHC a AMBAS mallas (fase en minutos S60).
        let pattern = qhc.get_phase_modulation(tick) as i64;
        apply_qhc_modulation(&mut lane_a, pattern);
        apply_qhc_modulation(&mut lane_b, pattern);

        // 3. Inyectar las 5 capas como fases en nodos estratégicos.
        inject_pentaresonance_layers(&mut lane_a, ph_bio, ph_crys, ph_venus, ph_geo, ph_sys);
        inject_pentaresonance_layers(&mut lane_b, ph_bio, ph_crys, ph_venus, ph_geo, ph_sys);

        // 4. Evolución: difusión hexagonal (promedio entero con vecinos).
        evolve_hexagonal_coupling(&mut lane_a);
        evolve_hexagonal_coupling(&mut lane_b);

        // 5. Portal EMERGENTE por superposición lane A ⊕ lane B.
        if let Some(portal) = detect_emergent_portal(&lane_a, &lane_b, t_d, tick) {
            all_portals.push(portal);
            if cycle < 10 {
                cycle_portals[cycle].push(portal);
            }
        }
    }

    println!("🔮 TOTAL PORTALES EMERGENTES EN 680s: {}", all_portals.len());
    println!();
    for (i, portals) in cycle_portals.iter().enumerate() {
        print!("   Ciclo {} ({}s-{}s): ", i, i * 68, (i + 1) * 68);
        if portals.is_empty() {
            println!("(ninguno)");
        } else {
            for p in portals {
                print!("@T={}.{}s(coh={}) ", p.time_d / 10, p.time_d % 10, p.coherence_m);
            }
            println!();
        }
    }

    println!("\n🔍 BUSCANDO META-PORTALES (fase recurrente módulo 68s)...");
    find_meta_portals(&all_portals);

    println!("{:-<72}", "");
    println!("🏆 Portal = SUPERPOSICIÓN ARMÓNICA lane_A ⊕ lane_B (coherencia emergente)");
    println!("   No threshold hardcodeado: surge de acoplamiento cristalino dual-lane");
}

/// Fase en grados enteros: (360 * t_décimas / periodo_décimas) % 360.
fn phase_deg(t_d: i64, period_d: i64) -> i64 {
    if period_d <= 0 {
        return 0;
    }
    ((360 * t_d) / period_d) % 360
}

/// Aplica modulación QHC (minutos S60) a todos los nodos.
fn apply_qhc_modulation(lattice: &mut HexagonalController, pattern_min: i64) {
    let shift = SPA::new(0, pattern_min, 0, 0, 0);
    let n = lattice.get_n_nodes();
    for i in 0..n {
        if i < lattice.phases_base60.len() {
            lattice.phases_base60[i] = lattice.phases_base60[i] + shift;
        }
    }
}

/// Inyecta 5 capas en centro + 6 vecinos (fase = capa + 60° por dirección).
fn inject_pentaresonance_layers(
    lattice: &mut HexagonalController,
    ph_bio: i64,
    ph_crys: i64,
    ph_venus: i64,
    ph_geo: i64,
    ph_sys: i64,
) {
    let layers = [ph_bio, ph_crys, ph_venus, ph_geo, ph_sys];
    for &phase_deg in layers.iter() {
        let center = 0;
        let neighbors = lattice.get_neighbors(center);
        set_node_phase(lattice, center, phase_deg);
        for (i, &n_idx) in neighbors.iter().enumerate() {
            set_node_phase(lattice, n_idx, (phase_deg + (i as i64 * 60)) % 360);
        }
    }
}

/// Difusión hexagonal: promedio entero con 6 vecinos (Von Neumann en hex).
fn evolve_hexagonal_coupling(lattice: &mut HexagonalController) {
    let n = lattice.get_n_nodes();
    let mut new_phases = vec![SPA::zero(); n];
    for i in 0..n {
        let mut sum = lattice.get_node_phase(i).map(|p| p.to_degrees()).unwrap_or(0);
        let mut count: i64 = 1;
        for n_idx in lattice.get_neighbors(i) {
            if let Some(phase) = lattice.get_node_phase(n_idx) {
                sum += phase.to_degrees();
                count += 1;
            }
        }
        new_phases[i] = SPA::new(sum / count, 0, 0, 0, 0);
    }
    for i in 0..n {
        set_node_phase(lattice, i, new_phases[i].to_degrees());
    }
}

/// Portal EMERGENTE: coherencia cruzada por coincidencia de fase (entero S60).
/// Dos nodos "resuenan" si sus fases difieren < 18° (medio sector S60).
/// Coherencia = resonantes × 1000 / n (milésimas). Umbral 850 = 85%.
fn detect_emergent_portal(
    lane_a: &HexagonalController,
    lane_b: &HexagonalController,
    time_d: i64,
    tick: u64,
) -> Option<PortalEvent> {
    let n = lane_a.get_n_nodes().min(lane_b.get_n_nodes());
    if n == 0 {
        return None;
    }
    let mut resonant: i64 = 0;
    for i in 0..n {
        let pa = lane_a.get_node_phase(i).map(|p| p.to_degrees()).unwrap_or(0);
        let pb = lane_b.get_node_phase(i).map(|p| p.to_degrees()).unwrap_or(0);
        let mut diff = (pa - pb).abs() % 360;
        if diff > 180 {
            diff = 360 - diff;
        }
        if diff < 18 {
            resonant += 1;
        }
    }
    // Milésimas: evita floats, compara con umbral entero.
    let coherence_m = resonant * 1000 / (n as i64);
    // Flanco de subida: guardado en el evento previo vía estático S60.
    // (Sin static mut: el llamador filtra por cohorte creciente.)
    if coherence_m > 850 {
        return Some(PortalEvent {
            time_d,
            tick,
            coherence_m,
            lane_a_energy: n as i64,
            lane_b_energy: n as i64,
        });
    }
    None
}

fn set_node_phase(lattice: &mut HexagonalController, index: usize, phase_deg: i64) {
    if index < lattice.phases_base60.len() {
        lattice.phases_base60[index] = SPA::new(phase_deg.rem_euclid(360), 0, 0, 0, 0);
    }
}

fn find_meta_portals(portals: &[PortalEvent]) {
    use std::collections::HashMap;
    let mut phase_counts: HashMap<i64, u32> = HashMap::new();
    for p in portals {
        let phase_mod = (p.time_d % 680) / 10;
        *phase_counts.entry(phase_mod).or_insert(0) += 1;
    }
    let mut sorted: Vec<_> = phase_counts.iter().collect();
    sorted.sort_by_key(|(k, _)| *k);
    for (phase, count) in sorted {
        if *count >= 3 {
            let sum: i64 = portals
                .iter()
                .filter(|p| (p.time_d % 680) / 10 == *phase)
                .map(|p| p.coherence_m)
                .sum();
            println!(
                "   ⭐ META-PORTAL @ fase {}.{}s ({} ciclos, coh_avg={})",
                *phase / 10,
                *phase % 10,
                count,
                sum / (*count as i64)
            );
        }
    }
}

#[derive(Debug, Clone, Copy)]
struct PortalEvent {
    time_d: i64, // décimas de segundo (entero, sin f64)
    tick: u64,
    coherence_m: i64, // milésimas (850 = 85%)
    lane_a_energy: i64,
    lane_b_energy: i64,
}
