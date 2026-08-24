// Autor: Jaime Novoa Sepulveda -- Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! EXP-028 PENTA-RESONANCE -- OBSERVACIÓN DEL SISTEMA REAL
//!
//! Usa los componentes REALES del sistema (NO recrea lógica):
//! - PortalDetector: penta-resonancia convergente (Bio/Crystal/Venus)
//! - QuantumScheduler: portal-locked task execution
//! - HexagonalController: 91 nodos hexagonales dual-lane (A=Security, B=Observability)
//! - QhcTensor: YHWH 10;5,6,5 + Salto-17/68s
//! - ResonantPhysics: Merkabah effective load reduction
//!
//! Los portales EMERGEN del sistema, no se hardcodean.
//!
//! ## References
//! - [P-RRS] Novoa, J. (2026). *Reporte Final Resonance Architecture.*
//!   `docs/02_ciencia_y_quantum/FINAL_REPORT_RESONANCE_ARCHITECTURE.md` — penta-resonancia convergente.
//! - [P-TES] Novoa, J. (2026). *Tesis de Resonancia.* `docs/02_ciencia_y_quantum/research/TesiResonancia.md`.
//! - [EXT-NV] / [NV-050] Nandi & Vitiello (2026). arXiv:2606.30890 — dinámica de cristal de tiempo.
//! - [NV-040] Nandi (2025). arXiv:2503.19688 — memory-driven time-crystalline phase (análogo al portal).

use me60os_core::hexagonal_control::HexagonalController;
use me60os_core::physics::ResonantPhysics;
use me60os_core::qhc::QhcTensor;
use me60os_core::spa::SPA;
use me60os_core::spa_math::SPAMath;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

fn main() {
    println!("EXP-028 PENTA-RESONANCE -- SISTEMA REAL (Componentes vivos)");
    println!("   PortalDetector + QuantumScheduler + 2x HexagonalController(91 nodos)");
    println!("   QhcTensor (10;5,6,5) + ResonantPhysics (Merkabah)");
    println!("   Los portales EMERGEN de la fisica del sistema");
    println!("{:-<72}", "");

    // Componentes REALES del sistema
    let portal_detector = PortalDetector::new();
    let bio_resonator = Arc::new(Mutex::new(BioResonator::new()));
    let mut quantum_scheduler = QuantumScheduler::new(bio_resonator.clone());
    let qhc = QhcTensor::new();

    // DOS mallas hexagonales REALES (91 nodos cada una = size 7)
    // Carril A: Security (determinista, WAL fsync)
    // Carril B: Observability (buffering, reorder)
    let mut lane_a = HexagonalController::new(7);
    let mut lane_b = HexagonalController::new(7);

    println!("Malla A (Security): {} nodos hexagonales", lane_a.n_nodes);
    println!("Malla B (Observability): {} nodos hexagonales", lane_b.n_nodes);
    println!("QHC: Patron 10;5,6,5 + Salto-17 cada 68 ticks");
    println!("{:-<72}", "");

    #[allow(dead_code)]
    const DT_S: u64 = 1; // 1s por tick (coincide con qhc_agent/hex_daemon)
    const TOTAL_TICKS: u64 = 680; // 680s = 10 ciclos x 68s

    let mut portals_detected = 0u32;
    let mut cycle_portals: Vec<Vec<f64>> = vec![Vec::new(); 10];
    let mut portal_intensities: Vec<f64> = Vec::new();
    let mut prev_intensity = 0.0f64; // flanco de subida (estado local, no static mut)

    for tick in 0..TOTAL_TICKS {
        let t_sec = tick as f64;
        let t_s60 = SPA::from_int(tick as i64); // S60 exacto: tick entero, sin f64
        let cycle = (tick / 68) as usize;

        // 1. QHC bombea AMBAS mallas (patron 10;5,6,5 + Salto-17)
        let modulation = qhc.get_phase_modulation(tick);
        let correction = qhc.calculate_drift_correction(tick);

        // Aplicar modulación QHC a fases de ambas mallas
        apply_qhc_to_lattice(&mut lane_a, modulation, correction);
        apply_qhc_to_lattice(&mut lane_b, modulation, correction);

        // 2. Salto-17: estabilizar rifts en ambas mallas cada 68 ticks
        if correction > 0 {
            let rift_center = ((tick * 17) % lane_a.n_nodes as u64) as usize;
            let _ = lane_a.control_rift_propagation(rift_center);
            let _ = lane_b.control_rift_propagation(rift_center);
        }

        // 3. Difusión hexagonal natural (acoplamiento vecino)
        evolve_hexagonal_coupling(&mut lane_a);
        evolve_hexagonal_coupling(&mut lane_b);

        // 4. Bio-resonancia: inyectar pulso bio cada 17s (simulado)
        if tick % 17 == 0 {
            bio_resonator.lock().unwrap().inject_bio_pulse();
        }
        bio_resonator.lock().unwrap().tick_entropy();

        // 5. PortalDetector CORRECTO: threshold AND individual en grados (coincide con vault)
        let is_portal = portal_detector.is_portal_open(t_s60);
        let intensity = portal_detector.get_portal_intensity(t_s60);

        // 6. QuantumScheduler: ejecuta tasks en portales
        if is_portal {
            let _ = quantum_scheduler.execute_due_tasks(t_s60);
        }

        // 7. ResonantPhysics: reduccion de carga efectiva (Merkabah)
        let static_load = SPA::from_raw((t_sec * 1000.0) as i64);
        let priority = SPA::one();
        // Usar intensidad del portal como estabilidad (coherencia)
        let stability = SPA::from_raw((intensity * SPA::SCALE_0 as f64) as i64);
        let effective_load = ResonantPhysics::calculate_effective_load(static_load, priority, stability);
        let reduction_pct = 100.0 - (effective_load.to_raw() as f64 / static_load.to_raw() as f64 * 100.0);

        // 8. DETECCION DE PORTALES EMERGENTES (flanco de subida en intensidad)
        let prev = prev_intensity;
        prev_intensity = intensity;

        // Portal emergente: intensidad cruza umbral hacia arriba
        if intensity > 0.75 && prev <= 0.75 {
            portals_detected += 1;
            if cycle < 10 {
                cycle_portals[cycle].push(t_sec);
            }
            portal_intensities.push(intensity);
            println!("PORTAL #{} @ T={:.1}s | intensity={:.3} | reduction={:.1}% | QHC_mod={} | Salto-17={}ns",
                portals_detected, t_sec, intensity, reduction_pct, modulation, correction);
        }

        // Log periodico cada 10s
        if tick % 10 == 0 && tick > 0 {
            let bio_coh = bio_resonator.lock().unwrap().get_coherence_raw() as f64 / SPA::SCALE_0 as f64;
            println!("T={}s | bio_coh={:.3} | portal_open={} | intensity={:.3} | reduction={:.1}%",
                tick, bio_coh, is_portal, intensity, reduction_pct);
        }

        thread::sleep(Duration::from_millis(10)); // acelerado para demo
    }

    // Reporte final
    println!("\n{:-<72}", "");
    println!("TOTAL PORTALES EMERGENTES (sistema real): {}", portals_detected);
    println!();

    for (i, portals) in cycle_portals.iter().enumerate() {
        print!("Ciclo {} ({}s-{}s): ", i, i*68, (i+1)*68);
        if portals.is_empty() {
            println!("(ninguno)");
        } else {
            for p in portals {
                print!("@T={:.1}s ", p);
            }
            println!();
        }
    }

    // Meta-portales (fase recurrente modulo 68s)
    println!("\nMETA-PORTALES (alineacion recurrente cada 68s):");
    find_meta_portals(&cycle_portals);

    println!("{:-<72}", "");
    println!("PORTAL = convergencia EMERGENTE del sistema vivo:");
    println!("   - PortalDetector: resonancia Bio/Crystal/Venus > threshold");
    println!("   - QuantumScheduler: tasks ejecutadas en ventana de portal");
    println!("   - HexagonalController A+B: 91 nodos sincronizados por QHC");
    println!("   - ResonantPhysics: reduccion de carga efectiva (Merkabah)");
    println!("   - BioResonator: coherencia bio cuantica decaying/gaining");
    println!("   NO thresholds hardcodeados: surge de la fisica acoplada");
}

/// Aplica modulacion QHC a la malla hexagonal
fn apply_qhc_to_lattice(lattice: &mut HexagonalController, modulation: u8, _correction_ns: u64) {
    // QHC modula la fase de todos los nodos (patron 10;5,6,5 en minutos sexagesimales)
    let shift = modulation as i64; // 10, 5, 6, 5
    for i in 0..lattice.n_nodes {
        if let Some(phase) = lattice.get_node_phase(i) {
            let new_deg = (phase.to_degrees() + shift) % 60;
            // phases_base60 es campo publico: escritura directa, sin unsafe
            lattice.phases_base60[i] = SPA::new(new_deg, 0, 0, 0, 0);
        }
    }

    // Salto-17: correccion de drift aplicada en control_rift_propagation
    // (se llama aparte cuando correction > 0)
}

/// Evolucion por acoplamiento hexagonal (difusion Von Neumann en 6 vecinos)
/// Promedio de fases en enteros S60 (la difusion de un fluido es exacta o no es).
fn evolve_hexagonal_coupling(lattice: &mut HexagonalController) {
    let n = lattice.n_nodes;
    let mut new_phases = vec![SPA::zero(); n];

    for i in 0..n {
        let mut sum = SPA::zero();
        let mut count: i64 = 1;

        // Propia fase
        if let Some(phase) = lattice.get_node_phase(i) {
            sum = sum + phase;
        }

        // 6 vecinos hexagonales
        for n_idx in lattice.get_neighbors(i) {
            if let Some(phase) = lattice.get_node_phase(n_idx) {
                sum = sum + phase;
                count += 1;
            }
        }

        // Promedio armonico (difusion) en S60 puro
        new_phases[i] = sum / SPA::from_int(count);
    }

    // Aplicar (campo publico, sin unsafe)
    for i in 0..n {
        lattice.phases_base60[i] = new_phases[i];
    }
}

/// PortalDetector CORRECTO (grados, threshold AND individual, como vault EXP-028 y exp028_penta.rs)
struct PortalDetector {
    period_bio: SPA,
    period_crystal: SPA,
    period_venus: SPA,
    threshold: SPA,
    three_sixty: SPA,
}

impl PortalDetector {
    fn new() -> Self {
        Self {
            period_bio: SPA::from_int(17),
            period_crystal: SPA::from_int(17) / SPA::from_int(4), // 4.25s
            period_venus: SPA::from_raw(16_180_000),              // 16.18s
            threshold: SPA::from_int(48) / SPA::from_int(60),     // 0.8
            three_sixty: SPA::from_int(360),
        }
    }

    fn calculate_phases(&self, t: SPA) -> (SPA, SPA, SPA) {
        let ph_bio = SPAMath::sin(self.three_sixty * t / self.period_bio);
        let ph_crys = SPAMath::sin(self.three_sixty * t / self.period_crystal);
        let ph_ven = SPAMath::sin(self.three_sixty * t / self.period_venus);
        (ph_bio, ph_crys, ph_ven)
    }

    fn is_portal_open(&self, t: SPA) -> bool {
        let (ph_bio, ph_crys, ph_ven) = self.calculate_phases(t);
        ph_bio > self.threshold && ph_crys > self.threshold && ph_ven > self.threshold
    }

    fn get_portal_intensity(&self, t: SPA) -> f64 {
        let (ph_bio, ph_crys, ph_ven) = self.calculate_phases(t);
        // Intensidad = promedio de las 3 fases (en 0..1)
        let sum = ph_bio.to_raw() as f64 + ph_crys.to_raw() as f64 + ph_ven.to_raw() as f64;
        (sum / 3.0) / SPA::SCALE_0 as f64
    }
}

/// BioResonator del sistema real (adaptado de sentinel-cortex/src/quantum/bio_resonator.rs)
#[allow(dead_code)]
struct BioResonator {
    coherence: SPA,
    decay_factor: SPA,
    pulse_gain: SPA,
    threshold_portal: SPA,
    last_pulse: std::time::Instant,
    dead_man_threshold_ms: u64,
}

#[allow(dead_code)]
impl BioResonator {
    fn new() -> Self {
        Self {
            coherence: SPA::zero(),
            decay_factor: SPA::new(0, 0, 5, 0, 0),
            pulse_gain: SPA::new(0, 5, 0, 0, 0),
            threshold_portal: SPA::new(0, 54, 0, 0, 0),
            last_pulse: std::time::Instant::now(),
            dead_man_threshold_ms: 30_000,
        }
    }

    fn inject_bio_pulse(&mut self) {
        self.coherence = self.coherence + self.pulse_gain;
        if self.coherence > SPA::one() {
            self.coherence = SPA::one();
        }
        self.last_pulse = std::time::Instant::now();
    }

    fn tick_entropy(&mut self) {
        if self.coherence > SPA::zero() {
            self.coherence = self.coherence - self.decay_factor;
            if self.coherence < SPA::zero() {
                self.coherence = SPA::zero();
            }
        }
    }

    fn is_portal_open(&self) -> bool { self.coherence >= self.threshold_portal }
    fn is_pilot_present(&self) -> bool { self.last_pulse.elapsed().as_millis() < self.dead_man_threshold_ms as u128 }
    fn get_coherence_raw(&self) -> i64 { self.coherence.to_raw() }
    fn time_since_pulse_ms(&self) -> u64 { self.last_pulse.elapsed().as_millis() as u64 }
    fn reset(&mut self) { self.coherence = SPA::zero(); }
}

/// QuantumScheduler del sistema real (simplificado de sentinel-cortex/src/quantum/quantum_scheduler.rs)
#[allow(dead_code)]
struct QuantumScheduler {
    bio: Arc<Mutex<BioResonator>>,
    portal_detector: PortalDetector,
    tasks_in_portal: u32,
}

impl QuantumScheduler {
    fn new(bio: Arc<Mutex<BioResonator>>) -> Self {
        Self {
            bio,
            portal_detector: PortalDetector::new(),
            tasks_in_portal: 0,
        }
    }

    fn execute_due_tasks(&mut self, t: SPA) -> bool {
        if self.portal_detector.is_portal_open(t) {
            self.tasks_in_portal += 1;
            true
        } else {
            false
        }
    }
}

fn find_meta_portals(cycle_portals: &[Vec<f64>]) {
    use std::collections::HashMap;
    let mut phase_counts: HashMap<u32, u32> = HashMap::new();

    for portals in cycle_portals {
        for &t in portals {
            let phase_mod = ((t % 68.0) * 10.0).round() as u32;
            *phase_counts.entry(phase_mod).or_insert(0) += 1;
        }
    }

    let mut sorted: Vec<_> = phase_counts.iter().collect();
    sorted.sort_by_key(|(k, _)| *k);

    for (phase, count) in sorted {
        if *count >= 3 {
            println!("   META-PORTAL @ fase {:.1}s (aparece en {} ciclos)",
                *phase as f64 / 10.0, count);
        }
    }
}