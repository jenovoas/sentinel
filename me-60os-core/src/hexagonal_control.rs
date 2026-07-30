// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ HEXAGONAL GEOMETRY BASE-60 🛡️
//!
//! Pilar 2 de la Trinidad Sentinel: Control Geométrico Hexagonal en Base-60.
//! Implementa la red de nodos (Lattice), el "Salto 17" (Axiomatic Key)
//! y la estabilización de "rifts" (rupturas de red).

use crate::spa::SPA;
use pyo3::prelude::*;
// use std::collections::HashMap; // Removed unused import

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct HexNode {
    pub q: i64,
    pub r: i64,
}

#[cfg_attr(feature = "extension-module", pyclass(module = "me60os_core"))]
pub struct HexagonalController {
    pub size: i64,
    // (q, r) tuples
    nodes_coords: Vec<(i64, i64)>,
    pub n_nodes: usize,
    pub base60_units: i64,
    pub step_key: i64,
    pub phases_base60: Vec<SPA>,
    pub plasma_shield_active: bool,
}

#[cfg(feature = "extension-module")]
#[pymethods]
impl HexagonalController {
    #[new]
    pub fn py_new(size: i64) -> Self {
        Self::new(size)
    }

    pub fn py_control_rift_propagation(&mut self, rift_center_idx: usize) -> pyo3::PyResult<(i64, SPA, usize)> {
        self.control_rift_propagation(rift_center_idx)
            .map_err(|e| pyo3::exceptions::PyIndexError::new_err(e))
    }
}

impl HexagonalController {
    pub fn new(size: i64) -> Self {
        let nodes_coords = Self::build_hex_lattice(size);
        let n_nodes = nodes_coords.len();
        let step_key = 17;
        
        // Inicializar fases
        let mut phases_base60 = vec![SPA::zero(); n_nodes];
        for (n, phase) in phases_base60.iter_mut().enumerate() {
            let val = ((n as i64) * step_key) % 60;
            *phase = SPA::new(val, 0, 0, 0, 0);
        }

        Self {
            size,
            nodes_coords,
            n_nodes,
            base60_units: 60,
            step_key,
            phases_base60,
            plasma_shield_active: true,
        }
    }

    pub fn get_n_nodes(&self) -> usize {
        self.n_nodes
    }
    
    pub fn get_plasma_shield_active(&self) -> bool {
        self.plasma_shield_active
    }

    /// Retorna la coordenada de un nodo dado su índice
    pub fn get_node_coord(&self, index: usize) -> Option<(i64, i64)> {
        if index < self.n_nodes {
            Some(self.nodes_coords[index])
        } else {
            None
        }
    }

    /// Retorna la fase actual de un nodo
    pub fn get_node_phase(&self, index: usize) -> Option<SPA> {
        if index < self.n_nodes {
            Some(self.phases_base60[index])
        } else {
            None
        }
    }

    /// Estabiliza la propagación de un rift usando rotación Base-60.
    /// Retorna (status_code, coherence_score_SPA, affected_count)
    pub fn control_rift_propagation(&mut self, rift_center_idx: usize) -> Result<(i64, SPA, usize), &'static str> {
        if !self.plasma_shield_active {
            // Error Code: -1 (VOID_COLLAPSE)
            return Ok((-1, SPA::zero(), 0));
        }

        if rift_center_idx >= self.n_nodes {
            return Err("Invalid rift center index");
        }

        let neighbors = self.get_neighbors(rift_center_idx);
        let affected_count = neighbors.len();
        
        let center_deg = self.phases_base60[rift_center_idx].to_degrees();

        for (i, neighbor_idx) in neighbors.iter().enumerate() {
            let new_val = (center_deg + (i as i64 + 1) * 10) % 60;
            self.phases_base60[*neighbor_idx] = SPA::new(new_val, 0, 0, 0, 0);
        }

        // Status 1: SEXAGESIMAL_STABILITY_LOCKED, Coherence: 60
        Ok((1, SPA::new(60, 0, 0, 0, 0), affected_count))
    }

    /// 💎 DERIVACIÓN DE CLAVE DINÁMICA DE CIFRADO ACOPLADA AL CRISTAL DE TIEMPO
    ///
    /// Deriva la clave dinámica Base-60 combinando:
    /// 1. Energía armónica total acumulada del cristal (S60 raw energy)
    /// 2. Constante trigonométrica Plimpton 322 Fila 17 (psi = 4.7962963 -> scaled 4796296)
    /// 3. Pulso YHWH (26)
    pub fn compute_crystal_coupled_key(&self, lattice_energy_raw: i64, tick: u64) -> i64 {
        let psi_scaled: i64 = 4_796_296; // Ratio trigonométrico exacto Plimpton 322 Fila 17
        let yhwh_pulse: i64 = 26;        // Constante de fase resonante
        
        let phase_contribution = (lattice_energy_raw.abs() % 3600) * psi_scaled / 1_000_000;
        let coupled_entropy = phase_contribution + (tick as i64 * 17) + yhwh_pulse;
        
        (coupled_entropy % 60).abs()
    }
}

impl HexagonalController {
    // Genera red hexagonal con coordenadas axiales (q, r)
    fn build_hex_lattice(size: i64) -> Vec<(i64, i64)> {
        let mut nodes = Vec::new();
        for q in -size + 1..size {
            let r1 = std::cmp::max(-size + 1, -q - size + 1);
            let r2 = std::cmp::min(size - 1, -q + size - 1);
            for r in r1..r2 + 1 {
                nodes.push((q, r));
            }
        }
        nodes
    }

    // Calcula los índices de los 6 vecinos en la red hexagonal
    fn get_neighbors(&self, node_idx: usize) -> Vec<usize> {
        let (q, r) = self.nodes_coords[node_idx];
        let neighbor_coords = [
            (q + 1, r), (q + 1, r - 1), (q, r - 1),
            (q - 1, r), (q - 1, r + 1), (q, r + 1)
        ];

        let mut indices = Vec::new();
        for nc in &neighbor_coords {
            if let Some(pos) = self.nodes_coords.iter().position(|&c| c == *nc) {
                indices.push(pos);
            }
        }
        indices
    }
}
