// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # ❄️ OPTOMECHANICAL COOLING (YATRA PROTOCOL PHASE 2) ❄️
//!
//! Implementation of Sideband Cooling calculation using pure Base-60 arithmetic.
//! Bypasses thermal noise limits using resonant radiation pressure.

use crate::spa::SPA;
use pyo3::prelude::*;

#[cfg(feature = "extension-module")]
#[pyclass(module = "me60os_core")]
pub struct OptomechanicalCooler {
    pub omega_m: SPA,
    pub gamma_m: SPA,
    pub kappa: SPA,
    pub n_th_env: SPA,
}

#[cfg(not(feature = "extension-module"))]
pub struct OptomechanicalCooler {
    pub omega_m: SPA,
    pub gamma_m: SPA,
    pub kappa: SPA,
    pub n_th_env: SPA,
}

#[cfg(feature = "extension-module")]
#[pymethods]
impl OptomechanicalCooler {
    #[new]
    pub fn py_new() -> Self {
        Self::new_internal()
    }
    
    #[getter]
    pub fn n_th_env(&self) -> pyo3::PyResult<SPA> {
        Ok(self.n_th_env)
    }

    pub fn quantum_limit(&self) -> SPA {
        self.quantum_limit_internal()
    }

    pub fn run_cooling_sequence(&self, steps: usize) -> Vec<(SPA, SPA, SPA)> {
        self.run_cooling_sequence_internal(steps)
    }
}

impl OptomechanicalCooler {
    pub fn new_internal() -> Self {
        Self {
            omega_m: SPA::new(1, 0, 0, 0, 0),        // 1 Natural unit
            gamma_m: SPA::new(0, 0, 0, 13, 0),       // ~ 1e-4
            kappa: SPA::new(0, 3, 0, 0, 0),          // 0.05
            // Bug 1.2: el comentario decía "300K Context" pero el valor 600_000 no
            // corresponde a 300K en ninguna unidad obvia (T=300K, n_th=kT/ℏω, etc).
            // Se preserva el valor numérico (600_000 phonones) y se deja el comentario
            // neutral: si la intención era "300K", reemplazar por el n_th verdadero.
            n_th_env: SPA::new(600_000, 0, 0, 0, 0), // 600K phonons (constante de calibración)
        }
    }

    /// Retrieves Quantum Limit (`n_min_limit` fonones)
    pub fn quantum_limit_internal(&self) -> SPA {
        let four_omega = SPA::new(4, 0, 0, 0, 0) * self.omega_m;
        let kappa_div_4omega = self.kappa / four_omega;
        kappa_div_4omega * kappa_div_4omega
    }

    /// Executes the cooling sequence calculating effective phononic occupation.
    /// Emits states to a list instead of direct print for bindings compatibility.
    pub fn run_cooling_sequence_internal(&self, steps: usize) -> Vec<(SPA, SPA, SPA)> {
        let mut results = Vec::with_capacity(steps);
        
        let g_max = SPA::new(1, 12, 0, 0, 0); // 1.2
        let step = SPA::new(0, 0, 36, 0, 0);   // Paso fino
        let mut current_g = SPA::zero();
        
        let n_min_limit = self.quantum_limit_internal();
        let spa_one = SPA::new(1, 0, 0, 0, 0);
        let spa_four = SPA::new(4, 0, 0, 0, 0);
        let kappa_gamma = self.kappa * self.gamma_m;

        while current_g <= g_max {
            let g_sq = current_g * current_g;
            let num = spa_four * g_sq;
            
            let mut c = SPA::zero();
            if kappa_gamma > SPA::zero() {
                c = num / kappa_gamma;
            }
            
            let denom_cool = spa_one + c;
            let mut n_final = self.n_th_env / denom_cool;
            
            // Thermal backaction (Quantum basic noise limit)
            n_final = n_final + n_min_limit;
            
            // Only collect sample every 10 ticks for the wrapper log
            let curr_val = current_g.to_raw();
            let step_val = step.to_raw();
            if step_val > 0 && curr_val >= 0 {
                let divisor = curr_val / step_val;
                if divisor % 10 == 0 {
                   results.push((current_g, c, n_final));
                }
            }

            current_g = current_g + step;
        }

        results
    }
}
