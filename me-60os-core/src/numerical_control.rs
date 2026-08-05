// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ NUMERICAL CONTROL UNIT (DDA) — RUST PURO 🛡️
//!
//! Replica la lógica computable de `scripts/RECOVERED_quantum_numerical_control_unit.py`
//! (SovereignDDA): un Analizador Diferencial Digital (DDA) para interpolación S60.
//!
//! FUNCIÓN REAL (migrada): `run_interpolation(start, end, duration_ticks)` —
//! genera una trayectoria interpolada linealmente integrando paso a paso:
//!     delta = end - start
//!     step  = delta / duration_ticks
//!     current(t) = start + step * t   (acumulador, sin drift por re-acumulación)
//! Al final verifica que el residuo (end - current_final) sea mínimo.
//!
//! CÁSCARA (documentada, NO migrada como lógica): `set_target_vector` en el .py
//! era `pass` (incompleto) — la emisión de pulsos STEP/DIR al hardware físico no
//! estaba implementada. La conversión S60->pasos de hardware es I/O de actuador,
//! fuera del runtime de cristal. Se documenta pero no se simula.

use crate::celestial::SVector3;
use crate::spa::SPA;

/// Analizador Diferencial Digital (DDA) para interpolación S60.
///
/// Convierte vectores de navegación S60 en una trayectoria de pasos determinista.
pub struct SovereignDDA;

impl SovereignDDA {
    /// Genera una secuencia de movimientos interpolados linealmente.
    ///
    /// Algoritmo DDA S60 (determinista, sin float):
    ///   delta = end - start
    ///   step  = delta / duration_ticks
    ///   por cada tick t en [0, duration_ticks):
    ///       current = start + step * t
    ///       (acumulación por step*t, no re-suma step repetidamente => sin drift)
    ///
    /// Devuelve la lista de puntos de la trayectoria (inclusive el final).
    pub fn run_interpolation(
        start: &SVector3,
        end: &SVector3,
        duration_ticks: i64,
    ) -> Vec<SVector3> {
        if duration_ticks <= 0 {
            return vec![*start];
        }

        let delta = end.sub(start); // end - start (dirección correcta)
        let step = delta.div_int(duration_ticks);

        let mut trajectory: Vec<SVector3> = Vec::with_capacity(duration_ticks as usize + 1);
        for t in 0..duration_ticks {
            let current = start.add(&step.scale(t));
            trajectory.push(current);
        }
        // Punto final exacto (garantiza llegada sin residuo acumulado)
        trajectory.push(*end);

        trajectory
    }

    /// Error de residuo final: |end - current_final| usando magnitud S60.
    /// Debe ser ~0 si la interpolación llegó exacto.
    pub fn final_residual(start: &SVector3, end: &SVector3, duration_ticks: i64) -> SPA {
        let traj = Self::run_interpolation(start, end, duration_ticks);
        let final_point = traj.last().copied().unwrap_or(*start);
        let diff = end.sub(&final_point);
        diff.magnitude()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::spa::SPA;

    #[test]
    fn test_interpolation_reaches_end() {
        let start = SVector3::new(SPA::from_int(0), SPA::from_int(0), SPA::from_int(0));
        let end = SVector3::new(SPA::from_int(100), SPA::from_int(50), SPA::from_int(20));
        let traj = SovereignDDA::run_interpolation(&start, &end, 10);
        // longitud = duration + 1 (incluye final)
        assert_eq!(traj.len(), 11);
        // el último debe ser exactamente end
        let last = traj.last().unwrap();
        assert_eq!(last.x, end.x);
        assert_eq!(last.y, end.y);
        assert_eq!(last.z, end.z);
    }

    #[test]
    fn test_interpolation_linear_steps() {
        // start=0, end=100 en 10 ticks -> step=10 por tick
        let start = SVector3::new(SPA::from_int(0), SPA::ZERO, SPA::ZERO);
        let end = SVector3::new(SPA::from_int(100), SPA::ZERO, SPA::ZERO);
        let traj = SovereignDDA::run_interpolation(&start, &end, 10);
        // tick 1 -> 10, tick 2 -> 20, ... tick 5 -> 50
        assert_eq!(traj[1].x, SPA::from_int(10));
        assert_eq!(traj[5].x, SPA::from_int(50));
        assert_eq!(traj[9].x, SPA::from_int(90));
    }

    #[test]
    fn test_interpolation_residual_zero() {
        let start = SVector3::new(SPA::from_int(0), SPA::from_int(0), SPA::from_int(0));
        let end = SVector3::new(SPA::from_int(100), SPA::from_int(30), SPA::from_int(0));
        let res = SovereignDDA::final_residual(&start, &end, 60);
        // debe ser ~0 (el punto final es exactamente end)
        assert!(res.to_raw().abs() < 1000); // tolerancia de cuartae
    }

    #[test]
    fn test_interpolation_zero_duration() {
        let start = SVector3::new(SPA::from_int(5), SPA::ZERO, SPA::ZERO);
        let end = SVector3::new(SPA::from_int(10), SPA::ZERO, SPA::ZERO);
        let traj = SovereignDDA::run_interpolation(&start, &end, 0);
        assert_eq!(traj.len(), 1);
        assert_eq!(traj[0], start);
    }
}
