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

        let s1 = SPAMath::sin_rad(angle1);
        let s2 = SPAMath::sin_rad(angle2);
        let s3 = SPAMath::sin_rad(angle3);

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
    pub fn is_portal_open(time: SPA) -> bool {
        let t_norm = time.to_raw().rem_euclid(T_CYCLE_RAW);
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
    pub fn efficiency(&self) -> SPA {
        let total = self.stats_portal.saturating_add(self.stats_overflow);
        if total == 0 {
            return SPA::zero();
        }
        let raw = (self.stats_portal as u128) * SPA::SCALE_0 as u128 / total as u128;
        SPA::from_raw(i64::try_from(raw).expect("eficiencia SPA fuera de rango"))
    }
}

#[cfg_attr(feature = "extension-module", pyclass(module = "me60os_core"))]
pub struct QuantumSchedulerDaemon {
    buffer: Py<QuantumBuffer>,
    process_fn: Py<PyAny>,
    dt_ms: u64,
    name: String,
    running: Arc<Mutex<bool>>,
}

#[cfg(feature = "extension-module")]
#[pymethods]
impl QuantumSchedulerDaemon {
    #[new]
    #[pyo3(signature = (buffer, process_fn, dt_ms=100, name="quantum-daemon".to_string()))]
    pub fn new(buffer: Py<QuantumBuffer>, process_fn: Py<PyAny>, dt_ms: u64, name: String) -> Self {
        Self {
            buffer,
            process_fn,
            dt_ms,
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
        let dt_duration = Duration::from_millis(self.dt_ms);
        let start_time = Instant::now();
        let buffer_ref = self.buffer.clone_ref(py);

        println!(
            "[{}] Quantum Scheduler (SOMA C++) iniciado en Fenix.",
            self.name
        );

        thread::spawn(move || {
            loop {
                // Check if still running
                if !*running_flag.lock().unwrap() {
                    break;
                }

                let elapsed_ns = start_time.elapsed().as_nanos();
                let t_raw = i64::try_from(elapsed_ns * SPA::SCALE_0 as u128 / 1_000_000_000)
                    .expect("tiempo monotónico SPA fuera de i64");
                let t_norm = t_raw.rem_euclid(T_CYCLE_RAW);
                let resonance = QuantumSchedulerCore::phi(SPA::from_raw(t_norm)).to_raw();

                let portal_open = resonance > THETA_RAW;

                let (q_size, is_overflow) = Python::attach(|py| {
                    let buf = buffer_ref.borrow(py);
                    (buf.size(), buf.is_overflow())
                });

                const THETA_HIGH: i64 = (90 * SPA::SCALE_0) / 100; // 0.90
                const THETA_MED: i64 = (85 * SPA::SCALE_0) / 100; // 0.85
                const THETA_LOW: i64 = (80 * SPA::SCALE_0) / 100; // 0.80

                if portal_open && q_size > 0 {
                    let batch_n = if resonance > THETA_HIGH {
                        5
                    } else if resonance > THETA_MED {
                        4
                    } else if resonance > THETA_LOW {
                        3
                    } else {
                        2
                    };

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

#[cfg(test)]
mod tests {
    use super::*;

    /// Muestreo del ciclo maestro a resolución de 0,1 s.
    fn muestreo_ciclo() -> impl Iterator<Item = i64> {
        let paso = SPA::SCALE_0 / 10;
        (0..=(T_CYCLE_RAW / paso)).map(move |i| i * paso)
    }

    #[test]
    fn phi_es_cero_en_el_origen_del_ciclo() {
        assert_eq!(QuantumSchedulerCore::phi(SPA::zero()).to_raw(), 0);
    }

    /// `phi` es una media de tres senos: nunca puede salir del intervalo [-1, 1].
    /// Si esto falla, hay una doble escala en `SPA / SPA` o en `SPA * SPA`.
    #[test]
    fn phi_permanece_dentro_de_la_amplitud_unitaria() {
        for t in muestreo_ciclo() {
            let raw = QuantumSchedulerCore::phi(SPA::from_raw(t)).to_raw();
            assert!(
                raw.abs() <= SPA::SCALE_0,
                "phi fuera de rango en t_raw={t}: {raw}"
            );
        }
    }

    /// Determinismo exigido por el contrato S60: misma entrada, mismo entero.
    #[test]
    fn phi_es_determinista_bit_a_bit() {
        for t in [0i64, 1, 216_000, 4_320_000, 33_000_000, 68_000_000] {
            let a = QuantumSchedulerCore::phi(SPA::from_raw(t));
            let b = QuantumSchedulerCore::phi(SPA::from_raw(t));
            assert_eq!(a.to_raw(), b.to_raw(), "phi no determinista en t={t}");
        }
    }

    /// `is_portal_open` debe ser exactamente el umbral aplicado sobre `phi`
    /// del tiempo normalizado al ciclo maestro.
    #[test]
    fn is_portal_open_es_el_umbral_sobre_phi_normalizado() {
        for t in muestreo_ciclo().step_by(37) {
            let normalizado = t.rem_euclid(T_CYCLE_RAW);
            let esperado =
                QuantumSchedulerCore::phi(SPA::from_raw(normalizado)).to_raw() > THETA_RAW;
            assert_eq!(
                QuantumSchedulerCore::is_portal_open(SPA::from_raw(t)),
                esperado,
                "discrepancia de portal en t_raw={t}"
            );
        }
    }

    /// El portal debe abrir dentro del ciclo maestro con senos en radianes.
    /// (Antes del 2026-11-04 `phi` usaba `sin` en grados y la amplitud máxima
    /// era 0,6175: el portal de 0,75 no abría nunca.)
    #[test]
    fn el_portal_abre_al_menos_una_vez_en_el_ciclo_maestro() {
        let abiertos = muestreo_ciclo()
            .filter(|t| QuantumSchedulerCore::is_portal_open(SPA::from_raw(*t)))
            .count();
        assert!(
            abiertos > 0,
            "ningún portal abierto en 68 s: revisar unidades de phi"
        );
    }

    /// Relaciones enteras del ciclo maestro: 68 s = 4·T_BIO = 16·T_CRYS.
    #[test]
    fn el_ciclo_maestro_es_multiplo_entero_de_bio_y_cristal() {
        assert_eq!(T_CYCLE_RAW, 4 * T_BIO_RAW);
        assert_eq!(T_CYCLE_RAW, 16 * T_CRYS_RAW);
        assert_eq!(T_CRYS_RAW, 4 * SPA::SCALE_0 + 15 * SPA::SCALE_1);
    }

    /// (Caracterización.) T_VENUS = 16,18 s no divide 68 s (68/16,18 = 4,2027…),
    /// por lo que el ciclo no es período común de las tres componentes: `phi` no
    /// vuelve al valor inicial al cerrar el ciclo. Esto invalida hablar de un
    /// "ciclo completo" cerrado mientras no se ajuste T_VENUS o T_CYCLE.
    #[test]
    fn el_ciclo_maestro_no_es_periodo_comun_por_la_componente_venus() {
        assert_ne!(T_CYCLE_RAW % T_VENUS_RAW, 0);
        assert_ne!(
            QuantumSchedulerCore::phi(SPA::from_raw(T_CYCLE_RAW)),
            QuantumSchedulerCore::phi(SPA::zero())
        );
    }
}
