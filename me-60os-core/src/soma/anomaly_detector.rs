// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::VecDeque;

#[cfg_attr(feature = "extension-module", pyclass(module = "me60os_core"))]
pub struct AnomalyDetectorCore {
    baseline_samples: usize,
    z_score_threshold: f64,

    cpu_window: VecDeque<f64>,
    memory_window: VecDeque<f64>,
    network_window: VecDeque<f64>,
    gpu_window: VecDeque<f64>,

    samples_processed: usize,
    learning_phase: bool,

    baseline_cpu_mean: f64,
    baseline_cpu_std: f64,
    baseline_mem_mean: f64,
    baseline_mem_std: f64,
    baseline_net_mean: f64,
    baseline_gpu_mean: f64,
    baseline_gpu_std: f64,
}

#[cfg(feature = "extension-module")]
#[pymethods]
impl AnomalyDetectorCore {
    #[new]
    #[pyo3(signature = (baseline_samples=100, z_score_threshold=3.0))]
    pub fn new(baseline_samples: usize, z_score_threshold: f64) -> Self {
        Self {
            baseline_samples,
            z_score_threshold,
            cpu_window: VecDeque::with_capacity(60),
            memory_window: VecDeque::with_capacity(60),
            network_window: VecDeque::with_capacity(60),
            gpu_window: VecDeque::with_capacity(60),
            samples_processed: 0,
            learning_phase: true,
            baseline_cpu_mean: 50.0,
            baseline_cpu_std: 15.0,
            baseline_mem_mean: 50.0,
            baseline_mem_std: 10.0,
            baseline_net_mean: 1_000_000.0,
            baseline_gpu_mean: 30.0,
            baseline_gpu_std: 20.0,
        }
    }

    #[pyo3(signature = (cpu, memory, network_bytes, gpu, db_connections, db_locks, memory_used_mb, memory_total_mb))]
    pub fn analyze_metrics<'py>(
        &mut self,
        py: Python<'py>,
        cpu: f64,
        memory: f64,
        network_bytes: f64,
        gpu: Option<f64>,
        db_connections: usize,
        db_locks: usize,
        memory_used_mb: f64,
        memory_total_mb: f64,
    ) -> PyResult<Vec<Bound<'py, PyDict>>> {
        AnomalyDetectorCore::add_to_window(&mut self.cpu_window, cpu, 60);
        AnomalyDetectorCore::add_to_window(&mut self.memory_window, memory, 60);
        AnomalyDetectorCore::add_to_window(&mut self.network_window, network_bytes, 60);
        if let Some(g) = gpu {
            AnomalyDetectorCore::add_to_window(&mut self.gpu_window, g, 60);
        }

        self.samples_processed += 1;

        if self.samples_processed == self.baseline_samples {
            self.learning_phase = false;
            self.update_baseline_stats();
        }

        let mut anomalies = Vec::new();

        if self.learning_phase {
            return Ok(anomalies);
        }

        // CPU Analysis
        let cpu_mean = self.baseline_cpu_mean;
        let cpu_std = self.baseline_cpu_std;
        let z_score = if cpu_std == 0.0 {
            0.0
        } else {
            (cpu - cpu_mean) / cpu_std
        };

        if z_score.abs() > self.z_score_threshold {
            let severity = if cpu > 90.0 { 3 } else { 2 }; // 3=Critical, 2=Warning
            anomalies.push(self.create_anomaly_dict(
                py,
                "CPU_SPIKE",
                severity,
                &format!("CPU Spike Detected: {:.1}%", cpu),
                &format!("CPU usage at {:.1}% (z-score: {:.2})", cpu, z_score),
                cpu,
                cpu_mean + (self.z_score_threshold * cpu_std),
            )?);
        }

        if self.cpu_window.len() >= 10 {
            let mut sustained = true;
            for i in self.cpu_window.len() - 10..self.cpu_window.len() {
                if self.cpu_window[i] <= 80.0 {
                    sustained = false;
                    break;
                }
            }
            if sustained {
                anomalies.push(self.create_anomaly_dict(
                    py,
                    "CPU_SPIKE",
                    3,
                    &format!("Sustained High CPU: {:.1}%", cpu),
                    "CPU sustained above 80% for last 10 samples (~2.5 minutes)",
                    cpu,
                    80.0,
                )?);
            }
        }

        // Memory Analysis
        if memory > 90.0 {
            anomalies.push(self.create_anomaly_dict(
                py,
                "MEMORY_SPIKE",
                3,
                &format!("Critical Memory Usage: {:.1}%", memory),
                &format!(
                    "Memory at {:.1}% ({:.0} MB / {:.0} MB)",
                    memory, memory_used_mb, memory_total_mb
                ),
                memory,
                90.0,
            )?);
        } else if memory > self.baseline_mem_mean {
            let mem_z = if self.baseline_mem_std == 0.0 {
                0.0
            } else {
                (memory - self.baseline_mem_mean) / self.baseline_mem_std
            };
            if mem_z.abs() > self.z_score_threshold {
                anomalies.push(self.create_anomaly_dict(
                    py,
                    "MEMORY_SPIKE",
                    2,
                    &format!("Memory Spike: {:.1}%", memory),
                    &format!("Memory usage at {:.1}% (z-score: {:.2})", memory, mem_z),
                    memory,
                    self.baseline_mem_mean + (self.z_score_threshold * self.baseline_mem_std),
                )?);
            }
        }

        // Network Analysis
        if self.network_window.len() >= 2 {
            let prev_bytes = self.network_window[self.network_window.len() - 2];
            if prev_bytes > 0.0 {
                let rate_change = (network_bytes - prev_bytes) / prev_bytes;
                if rate_change > 5.0 {
                    anomalies.push(self.create_anomaly_dict(
                        py,
                        "NETWORK_SPIKE",
                        2,
                        "Network Spike Detected",
                        &format!(
                            "Network traffic increased by {:.0}% in one sample",
                            rate_change * 100.0
                        ),
                        network_bytes,
                        prev_bytes * 5.0,
                    )?);
                }
            }
        }

        if self.network_window.len() >= 10 {
            let sum: f64 = self
                .network_window
                .iter()
                .skip(self.network_window.len() - 10)
                .sum();
            let avg = sum / 10.0;
            if avg > self.baseline_net_mean * 3.0 {
                anomalies.push(self.create_anomaly_dict(
                    py,
                    "NETWORK_SPIKE",
                    2,
                    "Sustained High Network Traffic",
                    &format!("Average network traffic {:.0} bytes/s (3x baseline)", avg),
                    avg,
                    self.baseline_net_mean * 3.0,
                )?);
            }
        }

        // GPU Analysis
        if let Some(g) = gpu {
            if g > 95.0 {
                anomalies.push(self.create_anomaly_dict(
                    py,
                    "GPU_OVERHEAT",
                    3,
                    &format!("GPU Overload: {:.1}%", g),
                    &format!("GPU usage at critical level {:.1}%", g),
                    g,
                    95.0,
                )?);
            }
        }

        // DB Analysis
        if db_connections > 50 {
            let severity = if db_connections < 100 { 2 } else { 3 };
            anomalies.push(self.create_anomaly_dict(
                py,
                "CONNECTION_SURGE",
                severity,
                &format!("DB Connection Surge: {}", db_connections),
                &format!("Database connections at {} (threshold: 50)", db_connections),
                db_connections as f64,
                50.0,
            )?);
        }

        if db_locks > 5 {
            anomalies.push(self.create_anomaly_dict(
                py,
                "LOCK_DETECTED",
                3,
                &format!("Database Lock Detected: {}", db_locks),
                &format!("Found {} active database locks", db_locks),
                db_locks as f64,
                5.0,
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
    fn add_to_window(window: &mut VecDeque<f64>, val: f64, max_len: usize) {
        if window.len() >= max_len {
            window.pop_front();
        }
        window.push_back(val);
    }

    fn mean_std(window: &VecDeque<f64>) -> (f64, f64) {
        if window.is_empty() {
            return (0.0, 0.0);
        }
        let mean = window.iter().sum::<f64>() / window.len() as f64;
        let var = window.iter().map(|v| (v - mean) * (v - mean)).sum::<f64>() / window.len() as f64;
        (mean, var.sqrt())
    }

    fn update_baseline_stats(&mut self) {
        if self.cpu_window.len() > 10 {
            let (m, s) = Self::mean_std(&self.cpu_window);
            self.baseline_cpu_mean = m;
            self.baseline_cpu_std = s;
        }
        if self.memory_window.len() > 10 {
            let (m, s) = Self::mean_std(&self.memory_window);
            self.baseline_mem_mean = m;
            self.baseline_mem_std = s;
        }
        if self.network_window.len() > 10 {
            let (m, _) = Self::mean_std(&self.network_window);
            self.baseline_net_mean = m;
        }
        if self.gpu_window.len() > 10 {
            let (m, s) = Self::mean_std(&self.gpu_window);
            self.baseline_gpu_mean = m;
            self.baseline_gpu_std = s;
        }
    }

    fn create_anomaly_dict<'py>(
        &self,
        py: Python<'py>,
        atype: &str,
        severity: usize,
        title: &str,
        desc: &str,
        metric: f64,
        threshold: f64,
    ) -> PyResult<Bound<'py, PyDict>> {
        let dict = PyDict::new(py);
        dict.set_item("anomaly_type", atype)?;
        dict.set_item("severity", severity)?;
        dict.set_item("title", title)?;
        dict.set_item("description", desc)?;
        dict.set_item("metric_value", metric)?;
        dict.set_item("threshold_value", threshold)?;
        Ok(dict)
    }
}
