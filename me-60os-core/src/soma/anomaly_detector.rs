// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.

use crate::spa::SPA;
use crate::spa_math::SPAMath;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::VecDeque;

#[cfg_attr(feature = "extension-module", pyclass(module = "me60os_core"))]
pub struct AnomalyDetectorCore {
    baseline_samples: usize,
    z_score_threshold_raw: i64,
    cpu_window: VecDeque<i64>,
    memory_window: VecDeque<i64>,
    network_window: VecDeque<u64>,
    samples_processed: usize,
    learning_phase: bool,
    baseline_cpu_mean: i64,
    baseline_cpu_std: i64,
    baseline_mem_mean: i64,
    baseline_mem_std: i64,
    baseline_net_mean: u64,
}

#[cfg(feature = "extension-module")]
#[pymethods]
impl AnomalyDetectorCore {
    #[new]
    #[pyo3(signature = (baseline_samples=100, z_score_threshold_raw=38_880_000))]
    pub fn new(baseline_samples: usize, z_score_threshold_raw: i64) -> Self {
        Self {
            baseline_samples,
            z_score_threshold_raw,
            cpu_window: VecDeque::with_capacity(60),
            memory_window: VecDeque::with_capacity(60),
            network_window: VecDeque::with_capacity(60),
            samples_processed: 0,
            learning_phase: true,
            baseline_cpu_mean: SPA::from_raw(50 * SPA::SCALE_0).to_raw(),
            baseline_cpu_std: SPA::from_raw(15 * SPA::SCALE_0).to_raw(),
            baseline_mem_mean: SPA::from_raw(50 * SPA::SCALE_0).to_raw(),
            baseline_mem_std: SPA::from_raw(10 * SPA::SCALE_0).to_raw(),
            baseline_net_mean: 1_000_000,
        }
    }

    #[pyo3(signature = (cpu_memory_raw, network_gpu, db_counts, memory_bytes))]
    pub fn analyze_metrics<'py>(
        &mut self,
        py: Python<'py>,
        cpu_memory_raw: (i64, i64),
        network_gpu: (u64, Option<i64>),
        db_counts: (u64, u64),
        memory_bytes: (u64, u64),
    ) -> PyResult<Vec<Bound<'py, PyDict>>> {
        let (cpu_raw, memory_raw) = cpu_memory_raw;
        let (network_bytes, gpu_raw) = network_gpu;
        let (db_connections, db_locks) = db_counts;
        let (memory_used_bytes, memory_total_bytes) = memory_bytes;
        Self::add_to_window(&mut self.cpu_window, cpu_raw);
        Self::add_to_window(&mut self.memory_window, memory_raw);
        Self::add_to_window_u64(&mut self.network_window, network_bytes);
        self.samples_processed += 1;
        if self.samples_processed == self.baseline_samples {
            self.learning_phase = false;
            self.update_baseline_stats()?;
        }
        if self.learning_phase {
            return Ok(Vec::new());
        }

        let mut anomalies = Vec::new();
        let cpu_limit = Self::threshold(
            self.baseline_cpu_mean,
            self.z_score_threshold_raw,
            self.baseline_cpu_std,
        )?;
        if Self::deviation_exceeds(
            cpu_raw,
            self.baseline_cpu_mean,
            self.baseline_cpu_std,
            self.z_score_threshold_raw,
        ) {
            anomalies.push(Self::create_anomaly_dict(
                py,
                "CPU_SPIKE",
                if cpu_raw > 90 * SPA::SCALE_0 { 3 } else { 2 },
                &format!("CPU Spike Detected: {}", SPA::from_raw(cpu_raw)),
                &format!("CPU usage at {}", SPA::from_raw(cpu_raw)),
                cpu_raw,
                cpu_limit,
            )?);
        }
        if self.cpu_window.len() >= 10
            && self
                .cpu_window
                .iter()
                .rev()
                .take(10)
                .all(|&v| v > 80 * SPA::SCALE_0)
        {
            anomalies.push(Self::create_anomaly_dict(
                py,
                "CPU_SPIKE",
                3,
                "Sustained High CPU",
                "CPU sustained above 80% for 10 samples",
                cpu_raw,
                80 * SPA::SCALE_0,
            )?);
        }

        if memory_raw > 90 * SPA::SCALE_0 {
            anomalies.push(Self::create_anomaly_dict(
                py,
                "MEMORY_SPIKE",
                3,
                "Critical Memory Usage",
                &format!(
                    "Memory usage exceeded 90%: {} / {} bytes",
                    memory_used_bytes, memory_total_bytes
                ),
                memory_raw,
                90 * SPA::SCALE_0,
            )?);
        } else if memory_raw > self.baseline_mem_mean
            && Self::deviation_exceeds(
                memory_raw,
                self.baseline_mem_mean,
                self.baseline_mem_std,
                self.z_score_threshold_raw,
            )
        {
            let threshold = Self::threshold(
                self.baseline_mem_mean,
                self.z_score_threshold_raw,
                self.baseline_mem_std,
            )?;
            anomalies.push(Self::create_anomaly_dict(
                py,
                "MEMORY_SPIKE",
                2,
                "Memory Spike",
                "Memory usage exceeded its learned baseline",
                memory_raw,
                threshold,
            )?);
        }

        if self.network_window.len() >= 2 {
            let previous = self.network_window[self.network_window.len() - 2];
            if previous > 0 && u128::from(network_bytes) > u128::from(previous) * 6 {
                let threshold = previous.saturating_mul(6);
                anomalies.push(Self::create_anomaly_dict(
                    py,
                    "NETWORK_SPIKE",
                    2,
                    "Network Spike Detected",
                    "Network traffic increased by more than 500%",
                    i64::try_from(network_bytes).unwrap_or(i64::MAX),
                    i64::try_from(threshold).unwrap_or(i64::MAX),
                )?);
            }
        }
        if self.network_window.len() >= 10 {
            let sum: u128 = self
                .network_window
                .iter()
                .rev()
                .take(10)
                .map(|&v| u128::from(v))
                .sum();
            let average = sum / 10;
            if average > u128::from(self.baseline_net_mean) * 3 {
                let metric = i64::try_from(average).unwrap_or(i64::MAX);
                let threshold =
                    i64::try_from(u128::from(self.baseline_net_mean) * 3).unwrap_or(i64::MAX);
                anomalies.push(Self::create_anomaly_dict(
                    py,
                    "NETWORK_SPIKE",
                    2,
                    "Sustained High Network Traffic",
                    "Average traffic exceeded three times baseline",
                    metric,
                    threshold,
                )?);
            }
        }

        if let Some(value) = gpu_raw {
            if value > 95 * SPA::SCALE_0 {
                anomalies.push(Self::create_anomaly_dict(
                    py,
                    "GPU_OVERHEAT",
                    3,
                    "GPU Overload",
                    "GPU usage exceeded 95%",
                    value,
                    95 * SPA::SCALE_0,
                )?);
            }
        }
        if db_connections > 50 {
            anomalies.push(Self::create_anomaly_dict(
                py,
                "CONNECTION_SURGE",
                if db_connections < 100 { 2 } else { 3 },
                "DB Connection Surge",
                "Database connections exceeded 50",
                i64::try_from(db_connections).unwrap_or(i64::MAX),
                50,
            )?);
        }
        if db_locks > 5 {
            anomalies.push(Self::create_anomaly_dict(
                py,
                "LOCK_DETECTED",
                3,
                "Database Lock Detected",
                "Database locks exceeded 5",
                i64::try_from(db_locks).unwrap_or(i64::MAX),
                5,
            )?);
        }
        Ok(anomalies)
    }

    #[getter]
    pub fn is_learning(&self) -> bool {
        self.learning_phase
    }
}

impl AnomalyDetectorCore {
    fn add_to_window(window: &mut VecDeque<i64>, value: i64) {
        if window.len() == 60 {
            window.pop_front();
        }
        window.push_back(value);
    }

    fn add_to_window_u64(window: &mut VecDeque<u64>, value: u64) {
        if window.len() == 60 {
            window.pop_front();
        }
        window.push_back(value);
    }

    fn mean_std(window: &VecDeque<i64>) -> PyResult<(i64, i64)> {
        if window.is_empty() {
            return Ok((0, 0));
        }
        let count = i128::try_from(window.len())
            .map_err(|_| pyo3::exceptions::PyOverflowError::new_err("muestra demasiado grande"))?;
        let sum = window
            .iter()
            .try_fold(0_i128, |sum, &value| sum.checked_add(i128::from(value)))
            .ok_or_else(|| {
                pyo3::exceptions::PyOverflowError::new_err("suma estadística fuera de rango")
            })?;
        let mean = i64::try_from(sum / count)
            .map_err(|_| pyo3::exceptions::PyOverflowError::new_err("media fuera de rango"))?;
        let squared = window
            .iter()
            .try_fold(0_i128, |sum, &value| {
                let delta = i128::from(value) - i128::from(mean);
                sum.checked_add(delta.checked_mul(delta)?)
            })
            .ok_or_else(|| pyo3::exceptions::PyOverflowError::new_err("varianza fuera de rango"))?;
        let variance_raw =
            i64::try_from(squared / count / i128::from(SPA::SCALE_0)).map_err(|_| {
                pyo3::exceptions::PyOverflowError::new_err("varianza SPA fuera de rango")
            })?;
        Ok((mean, SPAMath::sqrt(SPA::from_raw(variance_raw)).to_raw()))
    }

    fn deviation_exceeds(value: i64, mean: i64, std: i64, threshold: i64) -> bool {
        if std == 0 {
            return false;
        }
        i128::from(value).abs_diff(i128::from(mean)) * SPA::SCALE_0 as u128
            > u128::try_from(threshold.max(0)).expect("umbral no negativo")
                * u128::try_from(std.max(0)).expect("desviación no negativa")
    }

    fn threshold(mean: i64, z_raw: i64, std: i64) -> PyResult<i64> {
        let offset = i128::from(z_raw) * i128::from(std) / i128::from(SPA::SCALE_0);
        i64::try_from(i128::from(mean) + offset)
            .map_err(|_| pyo3::exceptions::PyOverflowError::new_err("umbral SPA fuera de rango"))
    }

    fn update_baseline_stats(&mut self) -> PyResult<()> {
        if self.cpu_window.len() > 10 {
            (self.baseline_cpu_mean, self.baseline_cpu_std) = Self::mean_std(&self.cpu_window)?;
        }
        if self.memory_window.len() > 10 {
            (self.baseline_mem_mean, self.baseline_mem_std) = Self::mean_std(&self.memory_window)?;
        }
        if self.network_window.len() > 10 {
            let sum = self
                .network_window
                .iter()
                .try_fold(0_u128, |sum, &value| sum.checked_add(u128::from(value)))
                .ok_or_else(|| {
                    pyo3::exceptions::PyOverflowError::new_err("tráfico de red fuera de rango")
                })?;
            let count = u128::try_from(self.network_window.len()).map_err(|_| {
                pyo3::exceptions::PyOverflowError::new_err("muestra demasiado grande")
            })?;
            self.baseline_net_mean = u64::try_from(sum / count).map_err(|_| {
                pyo3::exceptions::PyOverflowError::new_err("media de red fuera de rango")
            })?;
        }
        Ok(())
    }

    fn create_anomaly_dict<'py>(
        py: Python<'py>,
        atype: &str,
        severity: usize,
        title: &str,
        desc: &str,
        metric_raw: i64,
        threshold_raw: i64,
    ) -> PyResult<Bound<'py, PyDict>> {
        let dict = PyDict::new(py);
        dict.set_item("anomaly_type", atype)?;
        dict.set_item("severity", severity)?;
        dict.set_item("title", title)?;
        dict.set_item("description", desc)?;
        dict.set_item("metric_value_raw", metric_raw)?;
        dict.set_item("threshold_value_raw", threshold_raw)?;
        Ok(dict)
    }
}
