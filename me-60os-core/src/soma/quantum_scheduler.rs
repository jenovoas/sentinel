// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ QUANTUM SCHEDULER - SOMA RUST 🛡️
//!
//! Motor de Resonancia Armónica nativo en Base-60.
//! Migrado desde Python para operar en Ring 0 puro sin flotantes y evadiendo el GIL de Python 
//! durante lapsos de espera.
//!

use crate::spa::SPA;
use crate::spa_math::SPAMath;
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyList};
use std::collections::VecDeque;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

const T_BIO_RAW: i64 = 17 * SPA::SCALE_0;
const T_CRYS_RAW: i64 = 4 * SPA::SCALE_0 + 15 * SPA::SCALE_1; // 4.25
const T_VENUS_RAW: i64 = 209_692_800; // 16.18 * 12,960,000
const T_CYCLE_RAW: i64 = 68 * SPA::SCALE_0;
const THETA_RAW: i64 = 9_720_000; // 0.75 * 12,960,000

#[cfg_attr(feature = "extension-module", pyclass(module = "me60os_core"))]
pub struct QuantumSchedulerCore;

impl QuantumSchedulerCore {
    pub fn phi(t: SPA) -> SPA {
        let two_pi = SPAMath::TWO_PI;
        
        let t_bio = t / SPA::from_raw(T_BIO_RAW);
        let angle1 = two_pi * t_bio;
        
        let t_crys = t / SPA::from_raw(T_CRYS_RAW);
        let angle2 = two_pi * t_crys;

        let t_venus = t / SPA::from_raw(T_VENUS_RAW);
        let angle3 = two_pi * t_venus;

        let s1 = SPAMath::sin(angle1);
        let s2 = SPAMath::sin(angle2);
        let s3 = SPAMath::sin(angle3);

        (s1 + s2 + s3) / 3
    }
}

#[cfg(feature = "extension-module")]
#[pymethods]
impl QuantumSchedulerCore {
    #[staticmethod]
    pub fn static_phi(t: SPA) -> PyResult<SPA> {
        Ok(Self::phi(t))
    }

    #[staticmethod]
    #[allow(clippy::float_arithmetic, clippy::cast_precision_loss, clippy::cast_possible_truncation)]
    pub fn is_portal_open(time_monotonic_s: f64) -> bool {
        // BORDE I/O: entrada externa decimal/tiempo -> raw S60 (YATRA: float solo en bordes)
        let t_raw = (time_monotonic_s * SPA::SCALE_0 as f64).round() as i64;
        let t_norm = t_raw % T_CYCLE_RAW;
        let resonance = Self::phi(SPA::from_raw(t_norm));
        resonance.to_raw() > THETA_RAW
    }
}

#[cfg_attr(feature = "extension-module", pyclass(module = "me60os_core"))]
pub struct QuantumBuffer {
    overflow_limit: usize,
    buffer: Arc<Mutex<VecDeque<Py<PyAny>>>>,
    pub stats_portal: usize,
    pub stats_overflow: usize,
    pub stats_dropped: usize,
}

#[cfg(feature = "extension-module")]
#[pymethods]
impl QuantumBuffer {
    #[new]
    #[pyo3(signature = (overflow_limit=20))]
    pub fn new(overflow_limit: usize) -> Self {
        Self {
            overflow_limit,
            buffer: Arc::new(Mutex::new(VecDeque::new())),
            stats_portal: 0,
            stats_overflow: 0,
            stats_dropped: 0,
        }
    }

    pub fn push(&mut self, event: Py<PyAny>) -> bool {
        let mut q = self.buffer.lock().unwrap();
        if q.len() >= self.overflow_limit * 2 {
            self.stats_dropped += 1;
            return false;
        }
        q.push_back(event);
        true
    }

    pub fn pop_batch(&mut self, py: Python, max_size: usize) -> Py<PyList> {
        let mut q = self.buffer.lock().unwrap();
        let list = PyList::empty(py);
        let mut count = 0;
        while let Some(event) = q.pop_front() {
            list.append(event).unwrap();
            count += 1;
            if count >= max_size {
                break;
            }
        }
        list.into()
    }

    pub fn pop_one(&mut self) -> Option<Py<PyAny>> {
        let mut q = self.buffer.lock().unwrap();
        q.pop_front()
    }

    #[getter]
    pub fn size(&self) -> usize {
        self.buffer.lock().unwrap().len()
    }

    #[getter]
    pub fn is_overflow(&self) -> bool {
        self.buffer.lock().unwrap().len() >= self.overflow_limit
    }

    pub fn record_portal(&mut self, n: usize) {
        self.stats_portal += n;
    }

    pub fn record_overflow(&mut self) {
        self.stats_overflow += 1;
    }

    #[getter]
    #[allow(clippy::float_arithmetic, clippy::cast_precision_loss)]
    pub fn efficiency(&self) -> f64 {
        // BORDE I/O: ratio de estadísticas (usize->f64) para telemetría externa.
        let total = self.stats_portal + self.stats_overflow;
        if total > 0 {
            self.stats_portal as f64 / total as f64
        } else {
            0.0
        }
    }
}

#[cfg_attr(feature = "extension-module", pyclass(module = "me60os_core"))]
pub struct QuantumSchedulerDaemon {
    buffer: Py<QuantumBuffer>,
    process_fn: Py<PyAny>,
    dt: f64,
    name: String,
    running: Arc<Mutex<bool>>,
}

#[cfg(feature = "extension-module")]
#[pymethods]
impl QuantumSchedulerDaemon {
    #[new]
    #[pyo3(signature = (buffer, process_fn, dt=0.1, name="quantum-daemon".to_string()))]
    pub fn new(buffer: Py<QuantumBuffer>, process_fn: Py<PyAny>, dt: f64, name: String) -> Self {
        Self {
            buffer,
            process_fn,
            dt,
            name,
            running: Arc::new(Mutex::new(false)),
        }
    }

    pub fn run(&mut self, py: Python) -> PyResult<()> {
        let mut running_guard = self.running.lock().unwrap();
        *running_guard = true;
        drop(running_guard);

        let running_flag = Arc::clone(&self.running);
        let process_fn = self.process_fn.clone_ref(py);
        let dt_duration = Duration::from_secs_f64(self.dt);
        let start_time = Instant::now();
        let buffer_ref = self.buffer.clone_ref(py);

        println!("[{}] Quantum Scheduler (SOMA C++) iniciado en Fenix.", self.name);

        thread::spawn(move || {
            loop {
                // Check if still running
                if !*running_flag.lock().unwrap() {
                    break;
                }

                let elapsed_s = start_time.elapsed().as_secs_f64();
                let t_raw = (elapsed_s * SPA::SCALE_0 as f64).round() as i64;
                let t_norm = t_raw % T_CYCLE_RAW;
                let resonance = QuantumSchedulerCore::phi(SPA::from_raw(t_norm)).to_raw();
                
                let portal_open = resonance > THETA_RAW;
                
                let (q_size, is_overflow) = Python::attach(|py| {
                    let buf = buffer_ref.borrow(py);
                    (buf.size(), buf.is_overflow())
                });

                // REVIEW: umbrales convertidos a constantes SPA (antes usaba float: 0.90 * SCALE_0 as f64)
                const THETA_HIGH: i64 = (90 * SPA::SCALE_0) / 100;  // 0.90
                const THETA_MED: i64  = (85 * SPA::SCALE_0) / 100;  // 0.85
                const THETA_LOW: i64  = (80 * SPA::SCALE_0) / 100;  // 0.80

                if portal_open && q_size > 0 {
                    let batch_n = if resonance > THETA_HIGH { 5 }
                                  else if resonance > THETA_MED { 4 }
                                  else if resonance > THETA_LOW { 3 }
                                  else { 2 };

                    Python::attach(|py| {
                        let mut buf = buffer_ref.borrow_mut(py);
                        let mut batch = Vec::new();
                        for _ in 0..batch_n {
                            if let Some(ev) = buf.pop_one() {
                                batch.push(ev);
                            }
                        }
                        
                        let batch_len = batch.len();
                        for event in batch {
                            let _ = process_fn.call1(py, (event,));
                        }
                        buf.record_portal(batch_len);
                    });
                } else if !portal_open && is_overflow {
                    Python::attach(|py| {
                        let mut buf = buffer_ref.borrow_mut(py);
                        if let Some(event) = buf.pop_one() {
                            let _ = process_fn.call1(py, (event,));
                            buf.record_overflow();
                        }
                    });
                }

                thread::sleep(dt_duration);
            }
        });

        Ok(())
    }

    pub fn stop(&mut self) -> PyResult<()> {
        let mut running_guard = self.running.lock().unwrap();
        *running_guard = false;
        Ok(())
    }
}
