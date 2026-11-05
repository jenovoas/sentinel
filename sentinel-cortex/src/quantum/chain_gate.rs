// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
//! # Compuerta del portal de la cadena DTC → lattice
//!
//! La cadena productiva es: tick DTC → inyección de la energía medida del cristal en el
//! retículo → `step()` del retículo → coherencia medida → esta compuerta → scheduler.
//!
//! La compuerta NO inventa señal: sólo decide con magnitudes medidas del retículo
//! (energía total y coherencia de fase). No hay temporizadores, ni flancos sintéticos,
//! ni lecturas de reloj: si el retículo está en el estado fundamental, el portal está
//! cerrado aunque la coherencia sea alta (no hay nada que despachar).

use crate::math::s60::S60;

/// Umbral por defecto: 0,75 de coherencia (`54/60` en S60), el mismo umbral que usan
/// `PortalDetector` y `BioResonator` en los experimentos EXP-028/EXP-029.
pub const DEFAULT_THRESHOLD_RAW: i64 = 9_720_000;

/// Compuerta del portal basada en el estado medido del retículo.
#[derive(Clone, Copy, Debug)]
pub struct ChainGate {
    threshold_raw: i64,
}

impl ChainGate {
    pub fn new() -> Self {
        Self {
            threshold_raw: DEFAULT_THRESHOLD_RAW,
        }
    }

    /// Construye la compuerta con un umbral explícito (raw S60). Un umbral negativo se
    /// trata como cero: la compuerta nunca acepta valores fuera de rango.
    pub fn with_threshold_raw(threshold_raw: i64) -> Self {
        Self {
            threshold_raw: threshold_raw.max(0),
        }
    }

    pub fn threshold_raw(&self) -> i64 {
        self.threshold_raw
    }

    /// Decide la apertura del portal con magnitudes medidas.
    ///
    /// - `energy_raw`: energía total del retículo (`total_energy_raw`).
    /// - `coherence_raw`: coherencia de fase medida (`measure_coherence_raw`).
    /// - `nodes`: tamaño del retículo; un retículo vacío no puede abrir portal.
    pub fn is_open(&self, energy_raw: i64, coherence_raw: i64, nodes: usize) -> bool {
        nodes > 0 && energy_raw > 0 && coherence_raw >= self.threshold_raw
    }

    /// Fracción entera de coherencia respecto de 1,0 (`SCALE_0`), para métricas.
    pub fn coherence_percent(&self, coherence_raw: i64) -> u64 {
        if coherence_raw <= 0 {
            return 0;
        }
        let clamped = coherence_raw.min(S60::SCALE_0);
        (u128::from(clamped as u64) * 100 / S60::SCALE_0 as u128).min(100) as u64
    }
}

impl Default for ChainGate {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn el_estado_fundamental_nunca_abre_portal() {
        let gate = ChainGate::new();
        // Coherencia máxima pero sin energía: no hay trabajo que despachar.
        assert!(!gate.is_open(0, S60::SCALE_0, 64));
    }

    #[test]
    fn un_retículo_vacio_nunca_abre_portal() {
        let gate = ChainGate::new();
        assert!(!gate.is_open(1_000, S60::SCALE_0, 0));
    }

    #[test]
    fn coherencia_bajo_umbral_cierra_el_portal() {
        let gate = ChainGate::new();
        assert!(!gate.is_open(1_000, DEFAULT_THRESHOLD_RAW - 1, 64));
    }

    #[test]
    fn coherencia_en_el_umbral_abre_el_portal() {
        let gate = ChainGate::new();
        assert!(gate.is_open(1_000, DEFAULT_THRESHOLD_RAW, 64));
        assert!(gate.is_open(1_000, S60::SCALE_0, 64));
    }

    #[test]
    fn energia_negativa_o_nula_cierra_el_portal() {
        let gate = ChainGate::new();
        assert!(!gate.is_open(-1, S60::SCALE_0, 64));
    }

    #[test]
    fn el_umbral_es_configurable_y_se_acota_a_cero() {
        let gate = ChainGate::with_threshold_raw(-5);
        assert_eq!(gate.threshold_raw(), 0);
        assert!(gate.is_open(1, 0, 8));

        let estricto = ChainGate::with_threshold_raw(S60::SCALE_0);
        assert!(!estricto.is_open(1, S60::SCALE_0 - 1, 8));
        assert!(estricto.is_open(1, S60::SCALE_0, 8));
    }

    #[test]
    fn el_porcentaje_de_coherencia_es_entero_y_acotado() {
        let gate = ChainGate::new();
        assert_eq!(gate.coherence_percent(0), 0);
        assert_eq!(gate.coherence_percent(-10), 0);
        assert_eq!(gate.coherence_percent(S60::SCALE_0), 100);
        assert_eq!(gate.coherence_percent(S60::SCALE_0 * 3), 100);
        assert_eq!(gate.coherence_percent(S60::SCALE_0 / 2), 50);
    }
}
