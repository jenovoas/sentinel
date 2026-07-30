// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # ⚖️ ATLANTEAN REGULATOR (MAAT STABILIZER) & GPU CONTROLLER ⚖️
//!
//! Reemplazo en Rust de `quantum/atlantic_regulator.py` y `quantum/gpu_controller.py`.
//! Regulador Maat: Garantiza la veracidad (Purity >= 95% = 0;57,0,0,0,0).
//! GPU Controller: Control P adaptativo de latencia fluida (Target: 20ms = 50 FPS).

use crate::spa::SPA;

/// Regulador Atlanteano (Maat Stabilizer)
pub struct MaatStabilizer {
    /// 95% Verdad = 57/60 arcminutos (0;57,0,0,0,0)
    pub target_truth: SPA,
    /// 99% Verdad = 59.4/60 arcminutos
    pub pure_truth: SPA,
    /// Máxima velocidad permitida
    pub max_speed: SPA,
}

impl Default for MaatStabilizer {
    fn default() -> Self {
        Self::new()
    }
}

impl MaatStabilizer {
    pub fn new() -> Self {
        Self {
            target_truth: SPA::new(0, 57, 0, 0, 0),
            pure_truth: SPA::new(0, 59, 24, 0, 0),
            max_speed: SPA::new(31, 0, 0, 0, 0),
        }
    }

    /// Regula la velocidad en función de la veracidad actual
    pub fn regulate(&self, current_truth: SPA, current_speed: SPA) -> (SPA, &'static str) {
        if current_truth < self.target_truth {
            // ⚠️ SACRIFICIO ARMÓNICO (Truth < 95%)
            let ratio = (current_truth * SPA::one()) / self.target_truth;
            let mut new_speed = (current_speed * ratio) / SPA::one();
            if new_speed < SPA::one() {
                new_speed = SPA::one();
            }
            (new_speed, "VELOCITY SACRIFICE (MAAT)")
        } else if current_truth > self.pure_truth {
            // 💎 RESONANCIA PURA (Truth > 99%)
            if current_speed < self.max_speed {
                let accel = current_speed / SPA::new(10, 0, 0, 0, 0);
                let mut new_speed = current_speed + accel;
                if new_speed > self.max_speed {
                    new_speed = self.max_speed;
                }
                (new_speed, "CRYSTAL PURE (ACCEL)")
            } else {
                (current_speed, "MAX RESONANCE")
            }
        } else {
            // ✅ ESTABILIDAD (95% <= Truth <= 99%)
            (current_speed, "MAAT HARMONIC")
        }
    }
}

/// Control Adaptativo de GPU (GPU Controller)
pub struct GpuController {
    pub target_latency_ms: f64,
    pub current_batch_size: usize,
    pub min_batch: usize,
    pub max_batch: usize,
}

impl Default for GpuController {
    fn default() -> Self {
        Self::new()
    }
}

impl GpuController {
    pub fn new() -> Self {
        Self {
            target_latency_ms: 20.0, // 50 FPS
            current_batch_size: 1000,
            min_batch: 100,
            max_batch: 65536,
        }
    }

    /// Control P: ajusta el tamaño de lote según la latencia medida
    pub fn adjust_batch_size(&mut self, latency_ms: f64) -> usize {
        let error = self.target_latency_ms - latency_ms;
        let gain = 0.1610; // K_GAIN original

        let delta = (error * gain * 100.0) as i64;
        let new_batch = (self.current_batch_size as i64 + delta)
            .clamp(self.min_batch as i64, self.max_batch as i64) as usize;

        self.current_batch_size = new_batch;
        self.current_batch_size
    }
}
