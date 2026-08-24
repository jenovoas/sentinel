// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// 💧 LIQUID LATTICE MEMORY 3x3 (EXP-009) — Topología Von Neumann S60 💧
//
// Liquid lattice memory simulation. Silenced at module level.
#![allow(dead_code)]

use crate::math::s60::S60;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CrystalNode {
    pub amplitude: S60,
    pub phase: S60,
    pub retention: S60,
}

impl Default for CrystalNode {
    fn default() -> Self {
        Self {
            amplitude: S60::zero(),
            phase: S60::zero(),
            retention: S60::from_int(1),
        }
    }
}

pub struct LiquidLattice {
    pub grid: [[CrystalNode; 3]; 3],
    pub coupling_strength: S60,
}

impl LiquidLattice {
    pub fn new() -> Self {
        Self {
            grid: Default::default(),
            coupling_strength: S60::from_raw(S60::SCALE_0 / 6), // 10/60 coupling
        }
    }

    /// Difusión de estado Von Neumann (Arriba, Abajo, Izquierda, Derecha)
    /// Retención objetivo >72% (EXP-009)
    // Fixed 3x3 grid indexed by r/c for Von Neumann neighbor arithmetic; iterators would obscure indices
    #[allow(clippy::needless_range_loop)]
    pub fn diffuse(&mut self) {
        let mut new_grid = self.grid.clone();

        for r in 0..3 {
            for c in 0..3 {
                let mut sum_amp = self.grid[r][c].amplitude;
                let mut neighbors = 1;

                if r > 0 {
                    sum_amp = sum_amp + self.grid[r - 1][c].amplitude;
                    neighbors += 1;
                }
                if r < 2 {
                    sum_amp = sum_amp + self.grid[r + 1][c].amplitude;
                    neighbors += 1;
                }
                if c > 0 {
                    sum_amp = sum_amp + self.grid[r][c - 1].amplitude;
                    neighbors += 1;
                }
                if c < 2 {
                    sum_amp = sum_amp + self.grid[r][c + 1].amplitude;
                    neighbors += 1;
                }

                // Average Von Neumann coupling
                let avg_amp = (sum_amp / S60::from_int(neighbors)).unwrap_or(S60::ZERO);
                let self_contrib =
                    self.grid[r][c].amplitude * S60::from_raw((S60::SCALE_0 * 7) / 10);
                let avg_contrib = avg_amp * S60::from_raw((S60::SCALE_0 * 3) / 10);
                new_grid[r][c].amplitude = self_contrib + avg_contrib;
            }
        }

        self.grid = new_grid;
    }

    pub fn inject_entropy(&mut self, row: usize, col: usize, pressure: i64) {
        if row < 3 && col < 3 {
            let pressure_s60 = S60::from_base_units(pressure);
            self.grid[row][col].amplitude = self.grid[row][col].amplitude + pressure_s60;
        }
    }

    // Boundary metric for dashboards/telemetry: float conversion is the display contract,
    // not part of the S60 compute core (YATRA: float only at I/O edge).
    #[allow(clippy::float_arithmetic, clippy::cast_precision_loss)]
    pub fn retention_score(&self) -> f64 {
        let mut total_amp = S60::zero();
        for r in 0..3 {
            for c in 0..3 {
                total_amp = total_amp + self.grid[r][c].amplitude;
            }
        }
        (total_amp.to_base_units() as f64 / 1_000_000.0).min(1.0)
    }

    /// Retención total en S60 puro (suma de amplitudes). Para asserts sin float.
    pub fn total_amplitude(&self) -> S60 {
        let mut total_amp = S60::zero();
        for r in 0..3 {
            for c in 0..3 {
                total_amp = total_amp + self.grid[r][c].amplitude;
            }
        }
        total_amp
    }
}

impl Default for LiquidLattice {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_diffuse_spreads_to_neighbors() {
        // EXP-009: difusión Von Neumann debe propagar energía a celdas vecinas.
        let mut lat = LiquidLattice::new();
        // Inyectar presión solo en la esquina (0,0)
        lat.inject_entropy(0, 0, 1_000_000); // 1.0 unidad S60 en crudo
        lat.diffuse();

        // Tras una difusión, la celda (0,1) y (1,0) deben haber recibido energía.
        let neighbor_right = lat.grid[0][1].amplitude;
        let neighbor_down = lat.grid[1][0].amplitude;
        assert!(
            neighbor_right > S60::zero(),
            "energía debe propagar a (0,1)"
        );
        assert!(neighbor_down > S60::zero(), "energía debe propagar a (1,0)");
    }

    #[test]
    fn test_retention_above_72_percent() {
        // EXP-009: retención objetivo > 72%. Medido en S60 puro (sin float).
        let mut lat = LiquidLattice::new();
        let injected = 1_000_000; // 1.0 unidad S60
        lat.inject_entropy(1, 1, injected); // celda central

        // Difundir varios pasos (el tejido líquido reparte el daño)
        for _ in 0..10 {
            lat.diffuse();
        }

        let retained = lat.total_amplitude().to_base_units();
        // > 72% de lo inyectado (1.0 unidad). Nota: el Rust usa 0.7 self + 0.3 avg,
        // así que la energía NO se conserva exacta pero se retiene bien.
        let threshold = (injected as i64 * 72) / 100;
        assert!(
            retained > threshold,
            "retención debe superar 72%: retenido={}, umbral={}",
            retained,
            threshold
        );
    }

    #[test]
    fn test_inject_isolated_cell_stays_put_before_diffuse() {
        // Antes de difundir, la energía inyectada no se filtra a vecinos.
        let mut lat = LiquidLattice::new();
        lat.inject_entropy(2, 2, 1_000_000);
        assert_eq!(lat.grid[2][2].amplitude, S60::from_base_units(1_000_000));
        assert_eq!(
            lat.grid[1][2].amplitude,
            S60::zero(),
            "vecino no debe tener energía aún"
        );
    }
}
