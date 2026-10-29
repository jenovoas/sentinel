// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
//
// buffer.rs — PREDICTOR DE RÁFAGAS (memoria no-Markoviana)
//
// Migración de quantum/ai_buffer_cascade.py a Rust puro (sin la cáscara
// vimana/akáshica, que era inflado de la IA temprana). El núcleo real es un
// kernel de correlación temporal Ornstein-Uhlenbeck:
//
//   K(t,s) = (1 / 2τ) · exp(-|t - s| / τ)
//
// Integrado sobre el historial reciente de coherencia para anticipar el
// colapso de una ráfaga antes de que ocurra. S60 puro, sin float.

use crate::hexagonal_control::HexagonalController;
use crate::spa::SPA;
use crate::spa_math::SPAMath;
use std::collections::BTreeMap;

/// Kernel Ornstein-Uhlenbeck en S60. tau_c es la escala de correlación temporal.
/// Devuelve (1/2τ)·exp(-|t-s|/τ).
pub fn ou_kernel(t: SPA, s: SPA, tau_c: SPA) -> SPA {
    let dt = if t > s { t - s } else { s - t };
    let two_tau = SPA::new(2, 0, 0, 0, 0) * tau_c;
    let prefactor = SPA::new(1, 0, 0, 0, 0) / two_tau;
    let exponent = -(dt / tau_c);
    prefactor * SPAMath::exp(exponent)
}

/// Estado de coherencia registrado en un instante.
#[derive(Clone, Copy, Debug)]
pub struct CoherenceRecord {
    pub coherence: SPA,
}

/// Buffer de cascada: mantiene historial de coherencia y proyecta el futuro.
#[derive(Clone, Debug)]
pub struct BufferCascade {
    hex: HexagonalController,
    /// Historial: timestamp (S60) -> registro. BTreeMap da orden temporal.
    history: BTreeMap<SPA, CoherenceRecord>,
    tau_c: SPA,
    /// Límite soberano de coherencia (58/60 en el original).
    limit: SPA,
}

impl BufferCascade {
    pub fn new(hex: HexagonalController, tau_c: SPA, limit: SPA) -> Self {
        Self {
            hex,
            history: BTreeMap::new(),
            tau_c,
            limit,
        }
    }

    /// Crea la cascada compartida de red con la topología hexagonal por defecto.
    pub fn with_default_hex() -> Self {
        Self::new(
            HexagonalController::new(7),
            SPA::new(1, 0, 0, 0, 0),
            SPA::new(58, 0, 0, 0, 0),
        )
    }

    pub fn history(&self) -> &BTreeMap<SPA, CoherenceRecord> {
        &self.history
    }

    /// Límite de coherencia usado para normalizar puntuaciones del verificador.
    pub fn limit(&self) -> SPA {
        self.limit
    }

    pub fn len(&self) -> usize {
        self.history.len()
    }

    pub fn is_empty(&self) -> bool {
        self.history.is_empty()
    }

    /// Registra el estado de coherencia actual.
    pub fn record(&mut self, t: SPA, coherence: SPA) {
        self.history.insert(t, CoherenceRecord { coherence });
    }

    /// Efecto de memoria ponderado por coherencia registrada normalizada.
    pub fn memory_effect(&self, now: SPA, window: usize) -> SPA {
        let recent: Vec<(SPA, SPA)> = self
            .history
            .iter()
            .rev()
            .take(window)
            .map(|(timestamp, record)| (*timestamp, record.coherence))
            .collect();
        let unit = SPA::from_int(1);
        let mut acc = SPA::zero();
        for (timestamp, coherence) in recent {
            let kernel = ou_kernel(now, timestamp, self.tau_c);
            let weight = if self.limit == SPA::zero() {
                unit
            } else {
                coherence / self.limit
            };
            acc = acc + (kernel * weight * SPA::new(0, 30, 0, 0, 0));
        }
        acc
    }

    /// Predice la coherencia futura integrando la memoria ambiental.
    /// Devuelve (coherencia_actual, objetivo_futuro, mitigado).
    /// `mitigado` es verdadero solo si el control geométrico del rift (Pilar 2)
    /// retorna estado 1 (`SEXAGESIMAL_STABILITY_LOCKED`); colapso de vacío (-1)
    /// o índice inválido (Err) dan falso.
    pub fn cascade(&mut self, now: SPA, window: usize) -> (SPA, SPA, bool) {
        let memory = self.memory_effect(now, window);

        // Estabilizar geometría (Pilar 2): frenar propagación de rift en el centro.
        let center = self.hex.n_nodes / 2;
        let mitigated = matches!(self.hex.control_rift_propagation(center), Ok((1, _, _)));

        // Coherencia actual = min(base + memory*22, limit)
        let base = SPA::new(42, 30, 0, 0, 0); // 42;30
        let boost = SPA::new(22, 0, 0, 0, 0);
        let boosted = base + (memory * boost);
        let current = if boosted < self.limit {
            boosted
        } else {
            self.limit
        };

        // Objetivo futuro = min(base + memory*20, 60)
        let future_target = base + (memory * SPA::new(20, 0, 0, 0, 0));
        let future = if future_target < SPA::new(60, 0, 0, 0, 0) {
            future_target
        } else {
            SPA::new(60, 0, 0, 0, 0)
        };

        // Backflow: conserva la medición si el timestamp ya tiene registro
        // (no reemplaza el score de TruthSync con la proyección).
        self.history
            .entry(now)
            .or_insert(CoherenceRecord { coherence: current });

        (current, future, mitigated)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::spa::SPA;

    fn ts(sec: i64, frac: i64) -> SPA {
        // frac en sesentavos (0..60)
        SPA::new(sec, frac, 0, 0, 0)
    }

    #[test]
    fn test_ou_kernel_monotonic_decay() {
        // El kernel debe decrecer conforme |t-s| crece.
        let tau = SPA::new(1, 0, 0, 0, 0);
        let k0 = ou_kernel(ts(10, 0), ts(10, 0), tau); // dt=0 => máximo
        let k1 = ou_kernel(ts(10, 0), ts(10, 6), tau); // dt=6/60
        let k2 = ou_kernel(ts(10, 0), ts(11, 0), tau); // dt=60/60=1
        assert!(k0 >= k1);
        assert!(k1 > k2, "kernel debe decaer con la distancia temporal");
    }

    #[test]
    fn test_cascade_predicts_higher_coherence_with_history() {
        // Sin historia => memoria ~0 => coherencia en base (42;30).
        let hex = HexagonalController::new(7);
        let mut bc = BufferCascade::new(hex, SPA::new(1, 0, 0, 0, 0), SPA::new(58, 0, 0, 0, 0));
        let (cur_empty, _f_empty, _) = bc.cascade(ts(100, 0), 10);
        assert_eq!(cur_empty, SPA::new(42, 30, 0, 0, 0));

        // Con historial reciente estable, la memoria empuja la coherencia hacia arriba.
        let hex2 = HexagonalController::new(7);
        let mut bc2 = BufferCascade::new(hex2, SPA::new(1, 0, 0, 0, 0), SPA::new(58, 0, 0, 0, 0));
        // Inyectar historia: 5 registros a 0;6 de distancia, coherencia 42;30.
        let base = SPA::new(42, 30, 0, 0, 0);
        for i in 0..5 {
            let t = ts(200, 0) - (SPA::new(0, 6, 0, 0, 0) * SPA::from_int(5 - i));
            bc2.record(t, base);
        }
        let (cur_hist, _f_hist, mitig) = bc2.cascade(ts(200, 0), 10);
        assert!(mitig, "rift debe mitigarse");
        assert!(
            cur_hist > SPA::new(42, 30, 0, 0, 0),
            "historia estable debe elevar la coherencia proyectada (cur={})",
            cur_hist
        );
    }

    #[test]
    fn test_cascade_respects_limit() {
        // Mucha memoria no debe superar el límite soberano 58/60.
        let hex = HexagonalController::new(7);
        let mut bc = BufferCascade::new(hex, SPA::new(1, 0, 0, 0, 0), SPA::new(58, 0, 0, 0, 0));
        // Inyectar mucha historia para saturar la memoria.
        for i in 0..50 {
            let t = ts(300 + i as i64, 0);
            bc.record(t, SPA::new(60, 0, 0, 0, 0));
        }
        let (cur, _f, _) = bc.cascade(ts(400, 0), 50);
        assert!(
            cur <= SPA::new(58, 0, 0, 0, 0),
            "coherencia no debe superar el límite soberano (cur={})",
            cur
        );
    }

    #[test]
    fn test_cascade_projection_reflects_recorded_trust() {
        // Misma cadencia temporal, distinta confianza (mapeo de borde:
        // `trust × límite`, igual que `verify_node_text`). Mayor confianza
        // debe proyectar mayor coherencia.
        let limit = SPA::new(58, 0, 0, 0, 0);
        let hi = SPA::from_raw(SPA::SCALE_0 * 9 / 10) * limit;
        let lo = SPA::from_raw(SPA::SCALE_0 * 2 / 10) * limit;
        let mut bc_hi =
            BufferCascade::new(HexagonalController::new(7), SPA::new(1, 0, 0, 0, 0), limit);
        let mut bc_lo =
            BufferCascade::new(HexagonalController::new(7), SPA::new(1, 0, 0, 0, 0), limit);
        for i in 0..5 {
            let t = ts(200, 0) - (SPA::new(0, 6, 0, 0, 0) * SPA::from_int(5 - i));
            bc_hi.record(t, hi);
            bc_lo.record(t, lo);
        }
        let (cur_hi, _, _) = bc_hi.cascade(ts(200, 0), 10);
        let (cur_lo, _, _) = bc_lo.cascade(ts(200, 0), 10);
        assert!(
            cur_hi > cur_lo,
            "mayor confianza debe proyectar mayor coherencia (hi={}, lo={})",
            cur_hi,
            cur_lo
        );
        assert!(
            cur_lo >= SPA::new(42, 30, 0, 0, 0),
            "incluso con poca confianza no se baja de la base (lo={})",
            cur_lo
        );
    }
}
