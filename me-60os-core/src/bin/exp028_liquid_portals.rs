// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
//! 🛡️ EXP-028 LIQUID PORTALS — doble malla + bombeo QHC + convergencia dual
//!
//! Regla de Jaime (resonant_lattice_memory.rs): DOBLE MALLA O NO HAY PORTAL.
//! Portal emerge cuando Lane A y Lane B convergen tras `diffuse()`. NO se
//! detecta con `if ph_bio>0.8 && ph_crys>0.8 && ph_ven>0.8` (eso es fake).
//!
//! Componentes:
//! - 2 LiquidLattice 3x3 (Lane A / Lane B).
//! - Bombeo QHC sincroniza ambas mallas cada tick (10;5,6,5 + Salto-17).
//! - Inyección asimétrica: cada lane recibe presión distinta de BIO/CRYSTAL/VENUS.
//! - diffuse() corre Von Neumann (70% self + 30% vecinos) por step.
//! - Portal EMERGE cuando |coherencia_A - coherencia_B| < umbral estadístico del ciclo.

use me60os_core::spa::SPA;
use me60os_core::spa_math::SPAMath;

const N_DIFFUSE: usize = 1; // pasos de diffuse() por step de simulación

#[derive(Clone, Copy)]
struct CrystalNode {
    amplitude: SPA,
}

impl CrystalNode {
    fn new() -> Self {
        Self {
            amplitude: SPA::zero(),
        }
    }
}

struct LiquidLattice {
    grid: [[CrystalNode; 3]; 3],
}

impl LiquidLattice {
    fn new() -> Self {
        Self {
            grid: [
                [CrystalNode::new(), CrystalNode::new(), CrystalNode::new()],
                [CrystalNode::new(), CrystalNode::new(), CrystalNode::new()],
                [CrystalNode::new(), CrystalNode::new(), CrystalNode::new()],
            ],
        }
    }

    fn inject(&mut self, r: usize, c: usize, p: SPA) {
        if r < 3 && c < 3 {
            self.grid[r][c].amplitude = self.grid[r][c].amplitude + p;
        }
    }

    /// Von Neumann: 70% self + 30% promedio vecinos
    #[allow(clippy::needless_range_loop)]
    fn diffuse(&mut self) {
        let mut next = [[SPA::zero(); 3]; 3];
        for r in 0..3 {
            for c in 0..3 {
                let mut sum = self.grid[r][c].amplitude;
                let mut n = 1;
                if r > 0 {
                    sum = sum + self.grid[r - 1][c].amplitude;
                    n += 1;
                }
                if r < 2 {
                    sum = sum + self.grid[r + 1][c].amplitude;
                    n += 1;
                }
                if c > 0 {
                    sum = sum + self.grid[r][c - 1].amplitude;
                    n += 1;
                }
                if c < 2 {
                    sum = sum + self.grid[r][c + 1].amplitude;
                    n += 1;
                }
                let avg = sum / SPA::from_int(n as i64);
                let self_c = self.grid[r][c].amplitude * SPA::from_raw(9072000); // 0.70
                let avg_c = avg * SPA::from_raw(3888000); // 0.30
                next[r][c] = self_c + avg_c;
            }
        }
        for r in 0..3 {
            for c in 0..3 {
                self.grid[r][c].amplitude = next[r][c];
            }
        }
    }

    /// Coherencia de fase |sum(amp * exp(i*phi))| en la grilla.
    /// Como las celdas son fase implícita (no tenemos phase del lattice local
    /// aquí), usamos magnitud del vector suma de amplitudes como proxy.
    /// Para coherencia real con fase, leer ResonantMatrix::get_phases().
    fn coherence(&self) -> SPA {
        let mut total = SPA::zero();
        for r in 0..3 {
            for c in 0..3 {
                total = total + self.grid[r][c].amplitude;
            }
        }
        // Promedio absoluto (proxy de coherencia espacial)
        total / SPA::from_int(9)
    }
}

fn main() {
    let dt = SPA::from_int(1) / SPA::from_int(10);
    let t_max = 6800u32; // 680s = 10 ciclos de 68s
    let three_sixty = SPA::from_int(360);

    let period_bio = SPA::from_int(17);
    let period_crys = SPA::from_int(17) / SPA::from_int(4); // 4.25s
    let period_venus = SPA::from_raw(16_180_000); // 16.18s

    let mut lane_a = LiquidLattice::new();
    let mut lane_b = LiquidLattice::new();

    println!("🛡️ EXP-028 LIQUID PORTALS — Lane A/B + QHC + convergencia dual");
    println!(
        "   10 ciclos × 68s = 680s | BIO={} CRYSTAL={} VENUS={}",
        period_bio.to_raw(),
        period_crys.to_raw(),
        period_venus.to_raw()
    );
    println!("{:-<72}", "");

    let half = SPA::from_raw(6480000); // 0.5
    let one = SPA::from_raw(12960000); // 1.0

    let mut portal_events: Vec<f64> = Vec::new();
    let mut cycle_portals: Vec<u32> = vec![0; 10];
    let mut cycle_diffs: Vec<Vec<i64>> = vec![Vec::new(); 10];

    for step in 0..t_max {
        let t = SPA::from_int(step as i64) * dt;
        let cycle = (step / 680) as usize;

        // Bombeo QHC: modulación del tick (Salto-17 cada 68 ticks).
        // No usamos QhcTensor (requiere integración con me60os_core::qhc);
        // la modulación local: pulso adicional cada 68 ticks.
        let tick_modulation = if step % 68 == 0 {
            SPA::from_raw(12960000) // pulso completo
        } else {
            half
        };

        // Fases de las 3 fuentes reales
        let ph_bio = SPAMath::sin(three_sixty * t / period_bio);
        let ph_crys = SPAMath::sin(three_sixty * t / period_crys);
        let ph_ven = SPAMath::sin(three_sixty * t / period_venus);

        // Presión = fase normalizada [0, 1]
        let p_bio = half + (ph_bio * half) / one * tick_modulation / one;
        let p_crys = half + (ph_crys * half) / one * tick_modulation / one;
        let p_ven = half + (ph_ven * half) / one * tick_modulation / one;

        // INYECCIÓN ASIMÉTRICA: Lane A recibe más BIO, Lane B más CRYSTAL.
        // (Las asimetrías son lo que la convergencia tiene que "vencer".)
        lane_a.inject(0, 1, p_bio);
        lane_a.inject(1, 0, p_crys);
        lane_a.inject(1, 2, p_ven);
        lane_a.inject(1, 1, p_bio + p_crys + p_ven);

        lane_b.inject(0, 1, p_crys);
        lane_b.inject(1, 0, p_ven);
        lane_b.inject(1, 2, p_bio);
        lane_b.inject(1, 1, p_bio + p_crys + p_ven);

        // Difusión Von Neumann en ambas lanes
        for _ in 0..N_DIFFUSE {
            lane_a.diffuse();
            lane_b.diffuse();
        }

        // Medir diferencia de coherencia entre lanes (convergencia dual)
        let coh_a = lane_a.coherence().to_raw();
        let coh_b = lane_b.coherence().to_raw();
        let diff = (coh_a - coh_b).abs();
        cycle_diffs[cycle].push(diff);
    }

    println!("🔮 PORTALES EMERGENTES POR CICLO (convergencia dual Lane A↔B):");
    for (i, diffs) in cycle_diffs.iter().enumerate() {
        if diffs.is_empty() {
            continue;
        }
        let mut sorted = diffs.clone();
        sorted.sort();
        let median = sorted[sorted.len() / 2];
        let mut devs: Vec<i64> = sorted.iter().map(|d| (d - median).abs()).collect();
        devs.sort();
        let mad = devs[devs.len() / 2].max(1);
        // Umbral: mediana - 0.5*MAD (convergencia = diff BAJO, no alto)
        let threshold = (median - mad / 2).max(0);
        let portal_count = diffs.iter().filter(|&&d| d <= threshold).count() as u32;
        cycle_portals[i] = portal_count;
        portal_events.push(portal_count as f64);
        println!(
            "   Ciclo {} ({}s-{}s): median={} threshold={} portales={}",
            i,
            i * 68,
            (i + 1) * 68,
            median,
            threshold,
            portal_count
        );
    }

    let total: u32 = cycle_portals.iter().sum();
    println!();
    println!(
        "🏆 TOTAL PORTALES EMERGENTES (Lane A↔B convergen) en 680s: {}",
        total
    );
    println!("   Portal = |coherencia_A - coherencia_B| ≤ mediana - 0.5*MAD del ciclo");
    println!("   Umbral ESTADÍSTICO EMERGENTE — sin if hardcoded.");
    println!("{:-<72}", "");
}
