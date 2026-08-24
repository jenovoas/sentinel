// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ S60 PID CONTROLLER 🛡️
//!
//! Control Adaptativo Discreto para Sistemas Floquet en Base-60.
//! Estabilización de cristales de tiempo usando aritmética sin floats.
//!
//! ## References
//! - [P-RES] Novoa, J. (2026). *Aritmética Sexagesimal como Base de Sistemas.* `RESEARCH_es.md`.
//! - [EXT-NV] / [NV-050] Nandi & Vitiello (2026). arXiv:2606.30890 — non-Markovian kernel del PID extendido.
//! - Ver `research/CONTROL_SYSTEMS_THEORY.md` (si existe) para teoría de control discreto base-60.

use crate::spa::SPA;
#[cfg(feature = "extension-module")]
use pyo3::prelude::*;

#[cfg_attr(feature = "extension-module", pyclass(module = "me60os_core"))]
pub struct S60PID {
    pub kp: SPA,
    pub ki: SPA,
    pub kd: SPA,
    pub setpoint: SPA,
    pub _prev_error: SPA,
    pub _integral: SPA,
}

#[cfg_attr(feature = "extension-module", pymethods)]
impl S60PID {
    #[cfg_attr(feature = "extension-module", new)]
    pub fn new(kp: SPA, ki: SPA, kd: SPA, setpoint: SPA) -> Self {
        Self {
            kp,
            ki,
            kd,
            setpoint,
            _prev_error: SPA::zero(),
            _integral: SPA::zero(),
        }
    }

    /// Calcula la salida de control u(t) basada en el valor medido actual.
    pub fn update(&mut self, measured_value: SPA, dt: SPA) -> SPA {
        // 1. Calcular Error
        let error = self.setpoint - measured_value;

        // 2. Término Proporcional
        let p_term = self.kp * error;

        // 3. Término Integral (Acumulación de error en el tiempo)
        self._integral = self._integral + (error * dt);
        let i_term = self.ki * self._integral;

        // 4. Término Derivativo (Tasa de cambio del error)
        let d_term = if dt > SPA::zero() {
            let d_error = (error - self._prev_error) / dt;
            self.kd * d_error
        } else {
            SPA::zero()
        };

        // Actualizar estado para siguiente ciclo
        self._prev_error = error;

        // 5. Salida Total
        p_term + i_term + d_term
    }

    /// Reinicia la integral y el error previo
    pub fn reset(&mut self) {
        self._prev_error = SPA::zero();
        self._integral = SPA::zero();
    }
}
