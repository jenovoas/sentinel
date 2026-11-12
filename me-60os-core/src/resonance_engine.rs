// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
//! Estado compartido de coherencia para Cortex y SOMA.

use crate::spa::SPA;

const COHERENCE_MILLI_SCALE: u64 = 1_000;

pub struct ResonanceEngine {
    current_coherence: SPA,
    entropy_rate: SPA,
}

impl Default for ResonanceEngine {
    fn default() -> Self {
        Self::new()
    }
}

impl ResonanceEngine {
    pub fn new() -> Self {
        Self {
            current_coherence: SPA::zero(),
            entropy_rate: SPA::from_raw(SPA::SCALE_0 / 100),
        }
    }

    /// Carga progresivamente una coherencia observada, expresada como valor x1000.
    ///
    /// 600 representa 0.60 y 1000 representa 1.00. Cada llamada puede elevar
    /// el estado hasta una décima de SCALE_0, sin superar la medición recibida.
    pub fn charge_from_coherence_milli(&mut self, measured: u64) {
        let normalized = measured.min(COHERENCE_MILLI_SCALE) as i128;
        let target_raw = normalized * i128::from(SPA::SCALE_0) / i128::from(COHERENCE_MILLI_SCALE);
        let target = SPA::from_raw(target_raw as i64);

        if target > self.current_coherence {
            let step = SPA::from_raw(SPA::SCALE_0 / 10);
            let next = self.current_coherence + step;
            self.current_coherence = next.min(target).min(SPA::one());
        }
    }

    /// Carga la coherencia desde las energías medidas de las dos lanes del cristal.
    pub fn charge_from_crystal_energy(
        &mut self,
        energy_a_raw: i64,
        energy_b_raw: i64,
        node_count: usize,
    ) {
        let per_node = (node_count as i64).max(1);
        let mean = energy_a_raw.saturating_add(energy_b_raw) / 2;
        let mean_per_node = mean.saturating_div(per_node);
        let target = SPA::from_raw(mean_per_node.clamp(0, SPA::SCALE_0));

        if target > self.current_coherence {
            let step = SPA::from_raw(SPA::SCALE_0 / 10);
            let next = self.current_coherence + step;
            self.current_coherence = next.min(target).min(SPA::one());
        }
    }

    pub fn tick_entropy(&mut self) {
        if self.current_coherence > SPA::zero() {
            let next = self.current_coherence - self.entropy_rate;
            self.current_coherence = next.max(SPA::zero());
        }
    }

    pub fn is_coherent(&self) -> bool {
        self.current_coherence >= SPA::new(0, 54, 0, 0, 0)
    }

    pub fn current_coherence(&self) -> SPA {
        self.current_coherence
    }

    pub fn get_coherence_raw(&self) -> i64 {
        self.current_coherence.to_raw()
    }
}

#[cfg(test)]
mod tests {
    use super::ResonanceEngine;
    use crate::spa::SPA;

    #[test]
    fn coherencia_menor_a_noventa_por_ciento_no_abre_el_portal() {
        let mut engine = ResonanceEngine::new();
        for _ in 0..20 {
            engine.tick_entropy();
            engine.charge_from_coherence_milli(600);
        }

        assert_eq!(engine.get_coherence_raw(), SPA::SCALE_0 * 3 / 5);
        assert!(!engine.is_coherent());
    }

    #[test]
    fn medicion_completa_abre_el_portal_despues_de_carga_progresiva() {
        let mut engine = ResonanceEngine::new();
        for _ in 0..10 {
            engine.tick_entropy();
            engine.charge_from_coherence_milli(1_000);
        }

        assert!(engine.is_coherent());
    }

    #[test]
    fn medicion_superior_a_uno_se_limita_a_uno() {
        let mut engine = ResonanceEngine::new();
        for _ in 0..10 {
            engine.charge_from_coherence_milli(u64::MAX);
        }

        assert_eq!(engine.get_coherence_raw(), SPA::SCALE_0);
    }
}
