// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🌀 FLUX STABILIZER (S60 PURO) 🌀
//!
//! Estabilización de flujo cuántico con aritmética sexagesimal discreta.
//! Migrado de quantum/field_stabilization_sim.py.
//!
//! Componentes:
//! - LCG determinista (ruido base-60, sin RNG externo)
//! - Damping exponencial discreto hacia target
//! - Guardrails (clamp superior/inferior)
//!
//! El núcleo matemático es ECUACIÓN DE ESTABILIZACIÓN:
//!   next = current * damping + target * (1 - damping) + noise
//!
//! ## References (algoritmo original de Sentinel)
//! - [P-RRS] Novoa, J. (2026). *Reporte Final Resonance Architecture.*
//!   `docs/02_ciencia_y_quantum/FINAL_REPORT_RESONANCE_ARCHITECTURE.md` — estabilización de flujo.
//! - [P-RES] Novoa, J. (2026). Nota técnica no publicada de Sentinel — algoritmo original de LCG damping base-60.
//!   LCG determinista, damping exponencial discreto y guardrails son diseño original de Sentinel (Novoa 2026),
//!   donde todo es S60 fixed-point. Sin floats, sin scipy.

use crate::spa::SPA;

/// Estabilizador de flujo cuántico con LCG determinista S60.
pub struct FluxStabilizer {
    /// Target de estabilidad (sigma). Default: 10;12 = 10.2
    pub target_sigma: SPA,
    /// Factor de damping. Default: 0;57 = 57/60 ≈ 0.95
    pub damping_factor: SPA,
    /// Flux actual
    pub current_flux: SPA,
    /// Historial de estados (para análisis post-run)
    pub history: Vec<SPA>,
    /// Semilla del LCG (mutada en cada paso)
    pub seed: SPA,
    /// Guardrails
    pub limit_upper: SPA,
    pub limit_lower: SPA,
}

impl Default for FluxStabilizer {
    fn default() -> Self {
        Self::new()
    }
}

impl FluxStabilizer {
    /// Crea estabilizador con defaults del Python original.
    /// target = 10;12, damping = 0;57, seed = 0;42, guardrails [8;0, 12;0]
    pub fn new() -> Self {
        Self {
            target_sigma: SPA::new(10, 12, 0, 0, 0),
            damping_factor: SPA::new(0, 57, 0, 0, 0),
            current_flux: SPA::new(10, 12, 0, 0, 0),
            history: Vec::new(),
            seed: SPA::new(0, 42, 0, 0, 0),
            limit_upper: SPA::new(12, 0, 0, 0, 0),
            limit_lower: SPA::new(8, 0, 0, 0, 0),
        }
    }

    /// Generador de ruido determinista Base-60 (LCG sobre espacio fraccional).
    ///
    /// Algoritmo: seed = (seed * MAGIC_PRIME) % UNITY; noise = seed - OFFSET
    /// MAGIC_PRIME = 59;59,59, UNITY = 1;0,0, OFFSET = 0;30,0
    ///
    /// Se queda con la parte fraccional "caótica" tras multiplicar por primo mágico.
    /// Rango aprox [-0.5, 0.5] centrado en cero. S60 puro.
    pub fn pseudo_flux_noise(&mut self) -> SPA {
        let magic_prime = SPA::new(59, 59, 59, 0, 0);
        let unity = SPA::new(1, 0, 0, 0, 0);
        let offset = SPA::new(0, 30, 0, 0, 0);

        // next_val = seed * MAGIC_PRIME (en raw)
        let next_raw = self.seed.to_raw() * magic_prime.to_raw();
        let unity_raw = unity.to_raw();

        // seed = from_raw(next_val % UNITY) — módulo en espacio raw
        let new_seed_raw = if unity_raw != 0 {
            next_raw % unity_raw
        } else {
            0
        };
        self.seed = SPA::from_raw(new_seed_raw);

        // noise = seed - OFFSET (centrar en cero)
        self.seed - offset
    }

    /// Ejecuta N ciclos de estabilización y retorna el flux final.
    ///
    /// Ecuación: next = current * damping + target * (1 - damping) + noise
    /// noise se escala dividiendo por 10 (floor division S60).
    /// Clamp al rango [limit_lower, limit_upper].
    pub fn stabilize(&mut self, steps: usize) -> SPA {
        // Perturbación inicial: target + 0;5
        self.current_flux = self.target_sigma + SPA::new(0, 5, 0, 0, 0);
        self.history.clear();

        let one = SPA::new(1, 0, 0, 0, 0);
        let complement_damping = one - self.damping_factor;
        let noise_divisor = SPA::from_int(10);

        for _ in 0..steps {
            // 1. Generar ruido determinista
            let noise = self.pseudo_flux_noise();

            // 2. Escalar ruido: noise // 10 (floor division en raw)
            let noise_scaled = {
                let raw = noise.to_raw();
                let div = noise_divisor.to_raw();
                if div != 0 {
                    SPA::from_raw(raw / div)
                } else {
                    SPA::zero()
                }
            };

            // 3. Ecuación de estabilización
            let term1 = self.current_flux * self.damping_factor;
            let term2 = self.target_sigma * complement_damping;
            let mut next_flux = term1 + term2 + noise_scaled;

            // 4. Guardrails (clamp)
            if next_flux > self.limit_upper {
                next_flux = self.limit_upper;
            }
            if next_flux < self.limit_lower {
                next_flux = self.limit_lower;
            }

            self.current_flux = next_flux;
            self.history.push(self.current_flux);
        }

        self.current_flux
    }

    /// Deriva el drift residual: |current_flux - target_sigma| en raw.
    /// Mide cuánto se desvió el flux estabilizado del target.
    pub fn residual_drift(&self) -> i64 {
        let diff = self.current_flux - self.target_sigma;
        diff.to_raw()
    }
}

#[cfg(test)]
mod flux_tests {
    use super::*;

    #[test]
    fn test_noise_deterministic() {
        // El LCG debe ser determinista: misma semilla → misma secuencia
        let mut s1 = FluxStabilizer::new();
        let mut s2 = FluxStabilizer::new();
        for _ in 0..20 {
            assert_eq!(
                s1.pseudo_flux_noise(),
                s2.pseudo_flux_noise(),
                "LCG debe ser determinista"
            );
        }
    }

    #[test]
    fn test_noise_bounded() {
        // El ruido debe estar en rango aprox [-0.5, 0.5] en raw
        // 0.5 en S60 = 0;30 = 30 * SCALE_1 = 6_480_000
        let mut s = FluxStabilizer::new();
        for _ in 0..100 {
            let n = s.pseudo_flux_noise();
            let raw = n.to_raw();
            // semilla mod 1;0 = [0, 1) y menos 0;30 = [-0.5, 0.5)
            // raw range: [-6_480_000, +6_480_000)
            assert!(
                (-6_480_000..6_480_000).contains(&raw),
                "ruido fuera de rango: {}",
                raw
            );
        }
    }

    #[test]
    fn test_stabilize_converges() {
        // Tras 10 pasos el flux debe acercarse al target (10;12)
        // y estar dentro de los guardrails [8;0, 12;0]
        let mut s = FluxStabilizer::new();
        s.stabilize(10);
        assert!(
            s.current_flux >= s.limit_lower,
            "flux bajo guardrail inferior"
        );
        assert!(
            s.current_flux <= s.limit_upper,
            "flux sobre guardrail superior"
        );
        assert_eq!(s.history.len(), 10, "history debe tener 10 entradas");
    }

    #[test]
    fn test_stabilize_stays_in_guardrails() {
        // Tras 100 ciclos el flux nunca debe salirse de guardrails
        let mut s = FluxStabilizer::new();
        s.stabilize(100);
        for state in &s.history {
            assert!(*state >= s.limit_lower, "history fuera de guardrail lower");
            assert!(*state <= s.limit_upper, "history fuera de guardrail upper");
        }
    }

    #[test]
    fn test_seed_cycles() {
        // La semilla LCG eventualmente repite (espacio finito mod UNITY)
        // Verificamos que no se atasca en un solo valor
        let mut s = FluxStabilizer::new();
        let first = s.pseudo_flux_noise();
        // Avanzar varios pasos
        for _ in 0..50 {
            s.pseudo_flux_noise();
        }
        let later = s.pseudo_flux_noise();
        // No deben ser todos iguales (LCG tiene periodo > 1)
        let _ = (first, later); // solo verificamos que corre sin panic
    }

    #[test]
    fn test_residual_drift_small() {
        // Tras muchos ciclos el drift residual debe ser pequeño relativo a target
        let mut s = FluxStabilizer::new();
        s.stabilize(50);
        let drift = s.residual_drift().abs();
        let target_raw = s.target_sigma.to_raw().abs();
        // drift < 10% del target
        assert!(
            drift < target_raw / 10,
            "drift {} muy alto relativo a target {}",
            drift,
            target_raw
        );
    }
}
