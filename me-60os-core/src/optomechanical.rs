// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # ❄️ OPTOMECHANICAL COOLING (YATRA PROTOCOL PHASE 2) ❄️
//!
//! Implementation of Sideband Cooling calculation using pure Base-60 arithmetic.
//! Bypasses thermal noise limits using resonant radiation pressure.
//!
//! ## References
//! - [EXT-005] High-purity quantum optomechanics at room temperature. arXiv:2412.14117.
//! - [EXT-013] Coherent Feedback Cooling of an Ultracoherent Phononic-Crystal Membrane at Room Temperature. arXiv:2605.20902.
//! - [EXT-012] Optomechanical disk resonator in the quantum ground state of motion. arXiv:2511.15492.
//! - [NV-037] Nandi (2024). arXiv:2410.03808 — quantum thermodynamics.
//! - [P-BEK] Novoa, J. (2026). *Bekenstein Base-60.* `docs/02_ciencia_y_quantum/quantum/WHITE_PAPER_BEKENSTEIN_BASE60.md`.

use crate::spa::SPA;
use crate::spa_math::SPAMath;
#[cfg(feature = "extension-module")]
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
            omega_m: SPA::new(1, 0, 0, 0, 0),  // 1 Natural unit (10 MHz físicos)
            gamma_m: SPA::new(0, 0, 0, 13, 0), // ~ 1e-4
            kappa: SPA::new(0, 3, 0, 0, 0),    // 0.05 (kappa/omega_m = 0.05, sideband-resolved)
            // n_th = k_B * T / (hbar * omega_m) para T=300K, omega_m=10MHz
            // = 3,927,610 fonones (calibrado contra paper Filho 2026: 5.5e6 a ~7 MHz)
            n_th_env: SPA::new(3_927_610, 0, 0, 0, 0), // n_th físico real a 300K
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
        let step = SPA::new(0, 0, 36, 0, 0); // Paso fino
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

// =============================================================================
// OPTOMECHANICAL SYSTEM (migración de quantum/optomechanical_simulator.py)
// Rotación simpléctica de fase en S60 puro (sin ODEs, sin scipy, sin floats).
// Solo la parte real: parámetros físicos + evolve resonante + detector de rift.
// Se dejan fuera los placeholders axion/entanglement/visibility (fake en el .py).
// =============================================================================

/// Parámetros físicos de la membrana nanomecánica (S60, unidades escaladas).
#[derive(Clone, Debug)]
pub struct MembraneParameters {
    pub mass: SPA,
    pub frequency: SPA,
    pub quality_factor: SPA,
    pub temperature: SPA,
}

impl Default for MembraneParameters {
    fn default() -> Self {
        Self {
            mass: SPA::new(1000, 0, 0, 0, 0),                  // 1e-15 kg
            frequency: SPA::new(1_000_000, 0, 0, 0, 0),        // 1 MHz
            quality_factor: SPA::new(100_000_000, 0, 0, 0, 0), // 10^8
            temperature: SPA::new(300, 0, 0, 0, 0),            // 300 K
        }
    }
}

impl MembraneParameters {
    /// omega_m = 2 * PI * f
    pub fn omega_m(&self) -> SPA {
        SPAMath::TWO_PI * self.frequency
    }
    /// gamma_m = omega_m / Q
    pub fn gamma_m(&self) -> SPA {
        self.omega_m() / self.quality_factor
    }
    /// Número térmico de fonones (aprox S60)
    pub fn thermal_phonons(&self) -> SPA {
        self.temperature * SPA::new(0, 10, 0, 0, 0)
    }
}

/// Parámetros de la cavidad óptica (S60).
#[derive(Clone, Debug)]
pub struct OpticalParameters {
    pub wavelength_nm: SPA,
    pub finesse: SPA,
    pub length_mm: SPA,
    pub power_mw: SPA,
}

impl Default for OpticalParameters {
    fn default() -> Self {
        Self {
            wavelength_nm: SPA::new(1550, 0, 0, 0, 0),
            finesse: SPA::new(1000, 0, 0, 0, 0),
            length_mm: SPA::new(1, 0, 0, 0, 0),
            power_mw: SPA::new(1, 0, 0, 0, 0),
        }
    }
}

impl OpticalParameters {
    /// omega_c = 2 * PI * c / lambda (c escalado 299792)
    pub fn omega_c(&self) -> SPA {
        let c = SPA::new(299_792, 0, 0, 0, 0);
        SPAMath::TWO_PI * (c / self.wavelength_nm)
    }
    /// kappa = 2 * PI * c / (finesse * length)
    pub fn kappa(&self) -> SPA {
        let c = SPA::new(299_792, 0, 0, 0, 0);
        SPAMath::TWO_PI * (c / (self.finesse * self.length_mm))
    }
    pub fn photon_number(&self) -> SPA {
        self.power_mw * SPA::new(1000, 0, 0, 0, 0)
    }
}

/// Sistema optomecánico acoplado. Estado: [x, p, n_ph] en S60.
#[derive(Clone, Debug)]
pub struct OptomechanicalSystem {
    pub membrane: MembraneParameters,
    pub optical: OpticalParameters,
    pub g0: SPA,
    pub state: [SPA; 3],
    pub bath_memory: Vec<[SPA; 3]>,
    pub memory_depth: usize,
}

impl OptomechanicalSystem {
    pub fn new(membrane: MembraneParameters, optical: OpticalParameters) -> Self {
        let g0 = Self::calculate_coupling(&membrane, &optical);
        let n_ph = optical.photon_number();
        Self {
            membrane,
            optical,
            g0,
            state: [SPA::zero(), SPA::zero(), n_ph],
            bath_memory: Vec::new(),
            memory_depth: 100,
        }
    }

    /// g0 = (omega_c / length) * zero_point * ratio[1;32,2,24] / (2*PI)
    fn calculate_coupling(_mem: &MembraneParameters, opt: &OpticalParameters) -> SPA {
        let sexagesimal_ratio = SPA::new(1, 32, 2, 24, 0);
        let zero_point = SPA::new(0, 0, 1, 0, 0);
        let g0_base = (opt.omega_c() / opt.length_mm) * zero_point;
        let g0_harmonic = g0_base * sexagesimal_ratio;
        g0_harmonic / SPAMath::TWO_PI
    }

    /// Evoluciona el sistema con rotación simpléctica de fase (resonancia S60).
    /// theta = 6 grados exactos por paso (resonancia axial).
    pub fn evolve(&mut self, steps: usize, noise: bool) -> Vec<[SPA; 3]> {
        let theta = SPA::new(6, 0, 0, 0, 0);
        let sin_t = SPAMath::sin(theta);
        let cos_t = SPAMath::cos(theta);
        let omega_m = self.membrane.omega_m();
        let m_omega = self.membrane.mass * omega_m;

        let mut x = self.state[0];
        let mut p = self.state[1];
        let n_ph = self.state[2];

        let mut states = Vec::with_capacity(steps);
        states.push([x, p, n_ph]);

        for _ in 1..steps {
            // Espacio de fase adimensional
            let p_dim = if m_omega.to_raw() != 0 {
                p / m_omega
            } else {
                SPA::zero()
            };
            let x_new = (x * cos_t) - (p_dim * sin_t);
            let p_new_dim = (x * sin_t) + (p_dim * cos_t);
            let mut p_new = p_new_dim * m_omega;

            // Acoplamiento optomecánico (kick simpléctico conservativo)
            if self.g0.to_raw() > 0 {
                p_new = p_new - (self.g0 * n_ph / SPA::new(1000, 0, 0, 0, 0));
            }

            // Ruido determinista (carga del sistema, sin RNG)
            if noise {
                let load = (self.bath_memory.len() % 10) as i64;
                p_new = p_new + SPA::new(0, 0, 0, load, 0);
            }

            x = x_new;
            p = p_new;
            states.push([x, p, n_ph]);

            if self.bath_memory.len() >= self.memory_depth {
                self.bath_memory.remove(0);
            }
            self.bath_memory.push([x, p, n_ph]);
        }

        self.state = *states.last().unwrap();
        states
    }

    /// Visibilidad de interferencia: V = (P_corr - P_anti) / (P_corr + P_anti).
    /// Mide el grado de coherencia cuántica desde una matriz de densidad 4x4
    /// (dos modos acoplados). P_corr = P_00 + P_11 (diagonal),
    /// P_anti = P_01 + P_10 (anti-diagonal).
    /// Retorna 0 si total = 0 (sin información). S60 puro, sin floats.
    /// Migrado de quantum/optomechanical_simulator.py:237-256.
    pub fn calculate_visibility(&self, rho: &[[SPA; 4]; 4]) -> SPA {
        let p_corr = rho[0][0] + rho[3][3];
        let p_anti = rho[1][1] + rho[2][2];
        let total = p_corr + p_anti;
        if total.to_raw() == 0 {
            return SPA::zero();
        }
        // visibility = (P_corr - P_anti) / total
        // En raw: ((P_corr - P_anti) * SCALE_0) / total_raw
        // El operador / en SPA ya aplica la escala internamente.
        (p_corr - p_anti) / total
    }

    // ─────────────────────────────────────────────────────────────
    // PLACEHOLDERS INTENCIONALES (no migrados — ver optomechanical_simulator.py)
    // ─────────────────────────────────────────────────────────────
    // measure_quality_factor() → en Python retorna el Q nominal, no mide nada
    //   real (ring-down simulado). Equivalente: self.membrane.quality_factor.
    //   Si se necesita Q medido de verdad, implementar decay de amplitud tras
    //   evolve() y calcular Q = omega * tau_decay / ln(2).
    //
    // simulate_axion_detection() → en Python evoluciona con noise=True y
    //   calcula desviación media como proxy de SNR, pero la confianza es
    //   hardcoded (S60(0,59) = 98% placeholder). No es físicamente real.
    //   Para implementarlo bien: añadir fuerza periódica en el loop evolve()
    //   a la frecuencia de axión esperada y medir transferencia de energía.
}

/// Detector de rift cuántico: matriz de correlación entre nodos + umbral.
/// Equivalente eBPF-guardian para la red optomecánica.
pub struct QuantumRiftDetector {
    pub n_nodes: usize,
    pub systems: Vec<OptomechanicalSystem>,
    pub threshold: SPA,
}

impl QuantumRiftDetector {
    pub fn new(n_nodes: usize, threshold: SPA) -> Self {
        let systems = (0..n_nodes)
            .map(|_| {
                OptomechanicalSystem::new(
                    MembraneParameters::default(),
                    OpticalParameters::default(),
                )
            })
            .collect();
        Self {
            n_nodes,
            systems,
            threshold,
        }
    }

    /// Correlación de fase media entre nodos i,j: promedio de cos(phi_i - phi_j).
    pub fn correlation_matrix(&self, states_list: &[Vec<[SPA; 3]>]) -> Vec<Vec<SPA>> {
        let n = states_list.len();
        let mut c = vec![vec![SPA::zero(); n]; n];
        for i in 0..n {
            for j in (i + 1)..n {
                let steps = states_list[i].len().min(states_list[j].len());
                if steps == 0 {
                    continue;
                }
                let mut total = SPA::zero();
                for (si, sj) in states_list[i].iter().zip(states_list[j].iter()).take(steps) {
                    let dphi = si[0] - sj[0];
                    total = total + SPAMath::cos(dphi);
                }
                let avg = total / SPA::from_int(steps as i64);
                c[i][j] = avg;
                c[j][i] = avg;
            }
        }
        c
    }

    /// Detecta rift donde la correlación supera el umbral.
    pub fn detect_rift(&self, matrix: &[Vec<SPA>]) -> (bool, Vec<usize>) {
        let mut rift_nodes = std::collections::HashSet::new();
        let mut detected = false;
        for i in 0..self.n_nodes {
            for j in (i + 1)..self.n_nodes {
                if i < matrix.len() && j < matrix.len() && matrix[i][j] > self.threshold {
                    detected = true;
                    rift_nodes.insert(i);
                    rift_nodes.insert(j);
                }
            }
        }
        let mut nodes: Vec<usize> = rift_nodes.into_iter().collect();
        nodes.sort();
        (detected, nodes)
    }
}

#[cfg(test)]
mod opto_tests {
    use super::*;

    #[test]
    fn test_coupling_positive() {
        let sys =
            OptomechanicalSystem::new(MembraneParameters::default(), OpticalParameters::default());
        assert!(sys.g0.to_raw() > 0, "g0 debe ser > 0 (acoplamiento real)");
    }

    #[test]
    fn test_evolve_runs_and_stays_finite() {
        // El `evolve` usa rotación de fase de theta=6° fijo (aproximación del
        // Python original). Verificamos que: (1) corre 600 pasos sin panic,
        // (2) el estado final es finito (no satura a infinito), y (3) respeta
        // la estructura [x, p, n_ph] conservando n_ph.
        // NOTA: no es un integrador simpléctico exacto, por lo que la energía
        // no se conserva estrictamente (igual que el original Python).
        let mut sys =
            OptomechanicalSystem::new(MembraneParameters::default(), OpticalParameters::default());
        sys.state[0] = SPA::new(1000, 0, 0, 0, 0);
        let n_ph0 = sys.state[2];
        let states = sys.evolve(600, false);
        assert_eq!(states.len(), 600);
        let last = states.last().unwrap();
        // p en unidades de momentum escala con m_omega; bajo rotación de fase
        // fija de 6° el esquema amplifica (es aproximación, no simpléctico
        // exacto). Lo que verificamos es que NO hace overflow/panic en 600 pasos.
        assert!(
            last[0].to_raw().abs() <= 12_960_000_000_000_000,
            "x en rango S60"
        );
        // n_ph se conserva (no se toca en evolve).
        assert_eq!(last[2], n_ph0);
    }

    #[test]
    fn test_rift_detection_threshold() {
        let det = QuantumRiftDetector::new(3, SPA::new(0, 48, 0, 0, 0));
        // Matriz con correlación alta en (0,1)
        let mut m = vec![vec![SPA::zero(); 3]; 3];
        m[0][1] = SPA::new(0, 55, 0, 0, 0); // > umbral 0;48
        m[1][0] = SPA::new(0, 55, 0, 0, 0);
        let (detected, nodes) = det.detect_rift(&m);
        assert!(detected);
        assert_eq!(nodes, vec![0, 1]);
    }

    #[test]
    fn test_visibility_max_coherent() {
        // Estado totalmente correlacionado: P_corr=1, P_anti=0 → V=1
        let sys =
            OptomechanicalSystem::new(MembraneParameters::default(), OpticalParameters::default());
        let mut rho = [[SPA::zero(); 4]; 4];
        rho[0][0] = SPA::new(1, 0, 0, 0, 0);
        rho[3][3] = SPA::new(0, 0, 0, 0, 0);
        let v = sys.calculate_visibility(&rho);
        assert_eq!(
            v.to_raw(),
            SPA::new(1, 0, 0, 0, 0).to_raw(),
            "V debe ser 1 (correlacion total)"
        );
    }

    #[test]
    fn test_visibility_anticorrelated() {
        // Estado anti-correlacionado: P_corr=0, P_anti=1 → V=-1
        let sys =
            OptomechanicalSystem::new(MembraneParameters::default(), OpticalParameters::default());
        let mut rho = [[SPA::zero(); 4]; 4];
        rho[1][1] = SPA::new(1, 0, 0, 0, 0);
        rho[2][2] = SPA::new(0, 0, 0, 0, 0);
        let v = sys.calculate_visibility(&rho);
        assert!(v.to_raw() < 0, "V debe ser negativo (anti-correlacion)");
    }

    #[test]
    fn test_visibility_zero_total() {
        // Matriz vacía → V = 0
        let sys =
            OptomechanicalSystem::new(MembraneParameters::default(), OpticalParameters::default());
        let rho = [[SPA::zero(); 4]; 4];
        let v = sys.calculate_visibility(&rho);
        assert_eq!(v.to_raw(), 0, "V debe ser 0 sin informacion");
    }

    #[test]
    fn test_visibility_linearity_intermediate() {
        // V ≈ 0.5: P_corr = 3, P_anti = 1 → V = (3-1)/(3+1) = 0.5
        let sys =
            OptomechanicalSystem::new(MembraneParameters::default(), OpticalParameters::default());
        let mut rho = [[SPA::zero(); 4]; 4];
        // P_corr = P_00 + P_33 = 3
        rho[0][0] = SPA::new(2, 0, 0, 0, 0);
        rho[3][3] = SPA::new(1, 0, 0, 0, 0);
        // P_anti = P_11 + P_22 = 1
        rho[1][1] = SPA::new(1, 0, 0, 0, 0);
        let v = sys.calculate_visibility(&rho);
        // V = (3-1)/4 = 0.5 → raw = SCALE_0/2 = 6_480_000
        let expected_half = SPA::new(0, 30, 0, 0, 0); // 30/60 = 0.5 in S60
        assert_eq!(
            v.to_raw(),
            expected_half.to_raw(),
            "V debe ser ~0.5 (linealidad intermedia)"
        );
    }
}
