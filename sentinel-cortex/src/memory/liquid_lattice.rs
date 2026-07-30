// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// 💧 LIQUID LATTICE MEMORY 3x3 (EXP-009) — Topología Von Neumann S60 💧

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
                let self_contrib = self.grid[r][c].amplitude * S60::from_raw((S60::SCALE_0 * 7) / 10);
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

    pub fn retention_score(&self) -> f64 {
        let mut total_amp = S60::zero();
        for r in 0..3 {
            for c in 0..3 {
                total_amp = total_amp + self.grid[r][c].amplitude;
            }
        }
        (total_amp.to_base_units() as f64 / 1_000_000.0).min(1.0)
    }
}

impl Default for LiquidLattice {
    fn default() -> Self {
        Self::new()
    }
}
