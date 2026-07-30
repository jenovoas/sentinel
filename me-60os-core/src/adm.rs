// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/adm.rs
//! 🍄 ME-60OS: MYCNET RESONANT LATTICE (RUST)  mushroom
//! ---------------------------------------------------------------------------
//! Implementación de la red micelial hexagonal bio-inspirada.

use crate::spa::SPA;
use std::collections::HashMap;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct AxialCoord {
    pub q: i32,
    pub r: i32,
}

impl AxialCoord {
    pub fn new(q: i32, r: i32) -> Self {
        Self { q, r }
    }

    /// Obtiene los 6 vecinos hexagonales
    pub fn neighbors(&self) -> [AxialCoord; 6] {
        [
            AxialCoord::new(self.q + 1, self.r),
            AxialCoord::new(self.q + 1, self.r - 1),
            AxialCoord::new(self.q, self.r - 1),
            AxialCoord::new(self.q - 1, self.r),
            AxialCoord::new(self.q - 1, self.r + 1),
            AxialCoord::new(self.q, self.r + 1),
        ]
    }
}

pub struct MycNode {
    pub coord: AxialCoord,
    pub amplitude: SPA, // Salud del nodo (Latencia/Carga)
    pub phase: SPA,     // Sincronización con el TimeCrystal
    pub signals: Vec<SPA>,
}

pub struct ADM {
    pub nodes: HashMap<AxialCoord, MycNode>,
    pub world_energy: SPA,
}

impl ADM {
    pub fn new() -> Self {
        Self {
            nodes: HashMap::new(),
            world_energy: SPA::zero(),
        }
    }

    /// Agrega un nodo a la lattice
    pub fn add_node(&mut self, q: i32, r: i32) {
        let coord = AxialCoord::new(q, r);
        self.nodes.insert(
            coord,
            MycNode {
                coord,
                amplitude: SPA::new(1, 0, 0, 0, 0), // Default saludable
                phase: SPA::zero(),
                signals: Vec::new(),
            },
        );
    }

    /// Propagación de señales (Crecimiento de Hifas)
    pub fn tick(&mut self, _dt: SPA) {
        let mut spikes = Vec::new();

        // 1. Percibir señales internas
        for (coord, node) in &mut self.nodes {
            if node.amplitude > SPA::new(1, 40, 0, 0, 0) {
                // Umbral de firing (reducido para mayor estabilidad)
                // Distribuimos la energía: cada vecino recibe una porción que sumada no exceda el total
                let spike_strength = node.amplitude / 12; // 6 vecinos * 2 = Factor de disipación
                for neighbor in coord.neighbors() {
                    spikes.push((neighbor, spike_strength));
                }
                node.amplitude = SPA::new(0, 20, 0, 0, 0); // Estado refractario (Hielo)
            }
        }

        // 2. Actuar (Distribuir energía)
        for (coord, strength) in spikes {
            if let Some(target) = self.nodes.get_mut(&coord) {
                target.amplitude = target.amplitude + strength;
            }
        }

        // 3. Normalizar energía global
        // TODO: Enlazar con eBPF para métricas reales
    }
}

impl Default for ADM {
    fn default() -> Self {
        Self::new()
    }
}
