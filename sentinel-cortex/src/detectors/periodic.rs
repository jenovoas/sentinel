// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ DETECTOR DE RESONANCIA PERIÓDICA (FFT + Q-FACTOR) EN S60 🛡️
//!
//! Monitorea streams de telemetría / entropía ring-buffer en busca de balizas
//! o patrones sintéticos periódicos altamente resonantes (Q-factor elevado),
//! ejecutando análisis espectral FFT en base-60 sin punto flotante.

use crate::math::s60::S60;
use crate::math::s60_math::{fft_s60, q_factor_s60, ComplexS60};
use serde::{Deserialize, Serialize};

#[allow(dead_code)]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PeriodicAlert {
    pub q_factor: S60,
    pub peak_frequency_hz: S60,
    pub sample_count: usize,
    pub description: String,
}

#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct PeriodicDetector {
    buffer: Vec<S60>,
    capacity: usize,
    sample_rate_hz: S60,
    q_threshold: S60,
}

#[allow(dead_code)]
impl PeriodicDetector {
    pub fn new(capacity: usize, sample_rate_hz: S60, q_threshold: S60) -> Self {
        assert!(
            capacity.is_power_of_two() && capacity >= 8,
            "Capacity must be a power of two and >= 8 for FFT"
        );
        Self {
            buffer: Vec::with_capacity(capacity),
            capacity,
            sample_rate_hz,
            q_threshold,
        }
    }

    /// Crea un detector periódico con umbrales estándar (100 Hz, Q >= 50).
    pub fn with_defaults(capacity: usize) -> Self {
        Self::new(
            capacity,
            S60::from_int(100),
            S60::from_int(50),
        )
    }

    /// Ingresa una muestra S60 al detector.
    /// Si el buffer alcanza su capacidad, ejecuta FFT y cálculo de Q-factor en S60.
    pub fn push(&mut self, sample: S60) -> Option<PeriodicAlert> {
        self.buffer.push(sample);
        if self.buffer.len() > self.capacity {
            self.buffer.drain(0..self.buffer.len() - self.capacity);
        }

        if self.buffer.len() == self.capacity {
            let spectrum = fft_s60(&self.buffer).ok()?;
            let q = q_factor_s60(&spectrum, self.sample_rate_hz).ok()?;
            if q >= self.q_threshold {
                let peak_freq = Self::find_peak_freq(&spectrum, self.sample_rate_hz, self.capacity);
                return Some(PeriodicAlert {
                    q_factor: q,
                    peak_frequency_hz: peak_freq,
                    sample_count: self.capacity,
                    description: format!(
                        "Resonancia periódica crítica detectada: Q-Factor={} >= Umbral={}",
                        q, self.q_threshold
                    ),
                });
            }
        }
        None
    }

    /// Ingresa una muestra raw (entero) escalada a S60.
    pub fn push_raw(&mut self, raw_sample: i64) -> Option<PeriodicAlert> {
        self.push(S60::from_raw(raw_sample))
    }

    /// Restablece el buffer del detector.
    pub fn reset(&mut self) {
        self.buffer.clear();
    }

    pub fn len(&self) -> usize {
        self.buffer.len()
    }

    pub fn is_empty(&self) -> bool {
        self.buffer.is_empty()
    }

    pub fn capacity(&self) -> usize {
        self.capacity
    }

    pub fn q_threshold(&self) -> S60 {
        self.q_threshold
    }

    fn find_peak_freq(spectrum: &[ComplexS60], sample_rate: S60, n: usize) -> S60 {
        let mut peak_idx = 0;
        let mut peak_mag = S60::ZERO;
        for (i, spec) in spectrum.iter().enumerate().take(n / 2) {
            let mag = spec.magnitude_squared();
            if mag > peak_mag {
                peak_mag = mag;
                peak_idx = i;
            }
        }
        let n_s60 = S60::from_int(n as i32);
        let idx_s60 = S60::from_int(peak_idx as i32);
        match idx_s60 / n_s60 {
            Ok(ratio) => ratio * sample_rate,
            Err(_) => S60::ZERO,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_detector_buffer_capacity() {
        let mut detector = PeriodicDetector::with_defaults(16);
        assert_eq!(detector.capacity(), 16);
        assert!(detector.is_empty());

        for i in 0..20 {
            detector.push(S60::from_int(i));
        }
        assert_eq!(detector.len(), 16);
    }

    #[test]
    fn test_detector_clean_noise_no_alert() {
        let mut detector = PeriodicDetector::with_defaults(32);
        // Señal aperiódica / ruido plano
        for i in 0..32 {
            let sample = S60::from_raw((i * 137 % 23) * S60::SCALE_0);
            let alert = detector.push(sample);
            if i < 31 {
                assert!(alert.is_none());
            }
        }
    }

    #[test]
    fn test_detector_periodic_resonance_alert() {
        // Para N=64 y bin=8, el ancho de banda es 2 bins -> Q = 8/2 = 4.
        let mut detector = PeriodicDetector::new(
            64,
            S60::from_int(64), // 64 Hz
            S60::from_int(3),  // Umbral Q >= 3
        );

        let mut alert_found = None;
        // Inyectar onda periódica pura de período 8 (frecuencia = 8 Hz)
        for i in 0..64 {
            let sample = if i % 8 == 0 {
                S60::from_int(10)
            } else if i % 8 == 4 {
                S60::from_int(-10)
            } else {
                S60::ZERO
            };
            if let Some(alert) = detector.push(sample) {
                alert_found = Some(alert);
            }
        }

        assert!(
            alert_found.is_some(),
            "Debe disparar PeriodicAlert ante resonancia periódica sostenida"
        );
        let alert = alert_found.unwrap();
        assert!(alert.q_factor >= S60::from_int(3));
        assert_eq!(alert.sample_count, 64);
    }

    #[test]
    fn test_detector_high_q_synthetic_beacon() {
        // Baliza sintética de alta frecuencia en ventana de 256 muestras
        // bin = 64 -> Q = 64/2 = 32
        let mut detector = PeriodicDetector::new(
            256,
            S60::from_int(256),
            S60::from_int(25), // Umbral Q >= 25
        );

        let mut alert_found = None;
        // Período 4 -> bin = 256 / 4 = 64
        for i in 0..256 {
            let sample = if i % 4 == 0 {
                S60::from_int(10)
            } else if i % 4 == 2 {
                S60::from_int(-10)
            } else {
                S60::ZERO
            };
            if let Some(alert) = detector.push(sample) {
                alert_found = Some(alert);
            }
        }

        assert!(
            alert_found.is_some(),
            "Debe detectar baliza sintética con Q alto (Q >= 25)"
        );
        let alert = alert_found.unwrap();
        assert!(alert.q_factor >= S60::from_int(25));
    }
}
