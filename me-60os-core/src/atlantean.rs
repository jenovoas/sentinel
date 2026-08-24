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
///
/// YATRA-LOCKED: aritmética entera pura. La latencia se maneja en
/// MILÉSIMAS DE MILISEGUNDO (i64) para evitar cualquier `f64`.
///
/// Ley (fiel a `quantum/gpu_controller.py` legacy):
///   scale = TARGET / (latency + 0.1ms), clamp a [0.5, 1.5].
///   new_batch = batch * scale.
///   Alta latencia (latencia > target) => scale < 1 => REDUCE batch.
///   Baja latencia (latencia < target) => scale > 1 => AUMENTA batch.
pub struct GpuController {
    /// Target de latencia en milésimas de ms (20000 = 20.0 ms = 50 FPS).
    pub target_latency_msx1000: i64,
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
            target_latency_msx1000: 20_000, // 20.0 ms = 50 FPS
            current_batch_size: 1000,
            min_batch: 100,
            max_batch: 65536,
        }
    }

    /// Ajusta el tamaño de lote según la latencia medida (milésimas de ms).
    /// Control multiplicativo P, 100% entero (sin float).
    pub fn adjust_batch_size(&mut self, latency_msx1000: i64) -> usize {
        // evitar división por cero: +100 milésimas (0.1 ms), igual que el legacy (+0.1)
        let denom = latency_msx1000 + 100;
        // scale_factor en milésimas: 1000 = 1.0; clamp [500, 1500] = [0.5, 1.5]
        let scale_x1000 = ((self.target_latency_msx1000 * 1000) / denom).clamp(500, 1500);
        // new_batch = batch * scale / 1000, entero
        let new_batch = (self.current_batch_size as i64 * scale_x1000) / 1000;
        let new_batch = new_batch.clamp(self.min_batch as i64, self.max_batch as i64) as usize;

        self.current_batch_size = new_batch;
        self.current_batch_size
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::spa::SPA;

    // --- MAAT STABILIZER (valores legacy: target 57/60=95%, pure 59.24/60=99%, max 31) ---

    #[test]
    fn test_maat_throttle_below_95() {
        // Truth = 80% (48/60) < target 95% => debe sacrificar velocidad
        let maat = MaatStabilizer::new();
        let truth = SPA::new(0, 48, 0, 0, 0);
        let speed = SPA::new(20, 0, 0, 0, 0);
        let (new_speed, status) = maat.regulate(truth, speed);
        assert_eq!(status, "VELOCITY SACRIFICE (MAAT)");
        assert!(new_speed < speed, "speed debe bajar bajo 95% verdad");
        assert!(new_speed >= SPA::one(), "speed nunca baja de 1;0");
    }

    #[test]
    fn test_maat_accel_above_99() {
        // Truth = 100% (59.30/60) > pure 99% => debe acelerar
        let maat = MaatStabilizer::new();
        let truth = SPA::new(0, 59, 30, 0, 0);
        let speed = SPA::new(10, 0, 0, 0, 0);
        let (new_speed, status) = maat.regulate(truth, speed);
        assert!(
            status == "CRYSTAL PURE (ACCEL)" || status == "MAX RESONANCE",
            "status inesperado: {status}"
        );
        assert!(new_speed >= speed, "speed no debe bajar en resonancia pura");
    }

    #[test]
    fn test_maat_harmonic_band() {
        // Truth = 96.6% (58/60) => banda estable (el valor que usa main.rs)
        let maat = MaatStabilizer::new();
        let truth = SPA::new(0, 58, 0, 0, 0);
        let speed = SPA::new(15, 0, 0, 0, 0);
        let (new_speed, status) = maat.regulate(truth, speed);
        assert_eq!(status, "MAAT HARMONIC");
        assert_eq!(new_speed, speed, "en banda 95-99% la velocidad es estable");
    }

    // --- GPU CONTROLLER (entero, milésimas de ms) ---

    #[test]
    fn test_gpu_high_latency_reduces_batch() {
        // latencia 50.0 ms (50000) >> target 20.0 ms => batch debe bajar
        let mut gpu = GpuController::new();
        gpu.current_batch_size = 1000;
        let new_batch = gpu.adjust_batch_size(50_000);
        assert!(new_batch < 1000, "alta latencia debe reducir el batch");
    }

    #[test]
    fn test_gpu_low_latency_increases_batch() {
        // latencia 5.0 ms (5000) << target 20.0 ms => batch debe subir (hasta clamp 1.5x)
        let mut gpu = GpuController::new();
        gpu.current_batch_size = 1000;
        let new_batch = gpu.adjust_batch_size(5_000);
        assert!(new_batch > 1000, "baja latencia debe aumentar el batch");
        assert!(new_batch <= 1500, "clamp superior 1.5x");
    }

    #[test]
    fn test_gpu_clamp_min_max() {
        let mut gpu = GpuController::new();
        gpu.current_batch_size = 100; // min
        // latencia bajísima empuja al clamp superior, no debe pasar max
        let b = gpu.adjust_batch_size(100);
        assert!(b >= gpu.min_batch, "respeta min_batch");
        let mut gpu2 = GpuController::new();
        gpu2.current_batch_size = 65536; // max
        let b2 = gpu2.adjust_batch_size(100_000); // latencia altísima => scale bajo
        assert!(b2 <= gpu2.max_batch, "respeta max_batch");
        assert!(b2 >= gpu2.min_batch, "nunca baja de min_batch");
    }
}
