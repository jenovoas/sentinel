// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # ⚛️ RESONANT PHYSICS ENGINE ⚛️
//!
//! Implementation of Advanced Resource Physics.
//! Provides SPA-based logic for "Load Reduction" (Inertial Damping) and "Priority Feedback".
//!
//! **Application in ME-60OS:**
//! - **Static Load**: Base computational cost.
//! - **Stability (Coherence)**: System health/scvfulness.
//! - **Priority (Power)**: Allocated CPU cycles.
//!
//! A "Stable" process (high coherence) has REDUCED Effective Load, optimizing schedule latency.

use crate::spa::SPA;

pub struct ResonantPhysics;

impl ResonantPhysics {
    // Constants from Sentinel Research
    // PHI = 1.618...
    // SCALAR_TUNING = 1.366

    /// Calculates Effective Load (Computational Mass)
    /// `Load_eff = Load_static / (1 + (Priority^2 * Stability * Tuning) / Phi^2_div_S)`
    ///
    /// Bug 1.1 fix: scaling 216 → 200 para preservar la fórmula Merkabah original
    /// (ver EXP-005: `M_eff = M_static / (1 + RF/200)`). 200 fue la constante de diseño;
    /// el cambio a 216 hecho por una IA previa modificaba los resultados ~8% sin re-calibrar
    /// el umbral de éxito. Si en el futuro se quiere "armonizar a 60³=216", debe
    /// re-validarse el experimento equivalente y actualizar documentación.
    ///
    /// Bug 4.2 fix: se eliminan las divisiones redundantes por SPA::one().
    /// (a / SPA::one() == a en aritmética SPA porque SPA/SPA=(a*S)/S=a).
    pub fn calculate_effective_load(static_load: SPA, priority: SPA, stability: SPA) -> SPA {
        // Tuning = 1.366 = SPA(1;21,57,36) (60^4 precise)
        let tuning = SPA::new(1, 21, 57, 36, 0);
        // Harmonic stabilizer: Plimpton 322 Row 11 ratio (1.5625 = 1;33,45)
        // sustituye al irracional Phi (1.618...) para eliminar phase drift.
        let phi_harmonic = SPA::new(1, 33, 45, 0, 0);
        let phi_sq = phi_harmonic * phi_harmonic; // abstract phi²

        let p_sq = priority * priority; // abstract P²

        // Numerador: P² * Stability * Tuning
        let num = p_sq * stability * tuning;

        // Factor = Num / Phi²
        let resonance_factor = num / phi_sq;

        // Denom = 1 + Factor / 200 (constante Merkabah original, ver Bug 1.1)
        let scaling = SPA::new(200, 0, 0, 0, 0);
        let denom_add = resonance_factor / scaling;
        let denom = SPA::one() + denom_add;

        if denom.to_raw() == 0 {
            return static_load;
        }

        static_load / denom
    }

    /// Priority Feedback Check
    /// Returns "Priority Gain" based on demand.
    /// In ME-60OS: Returns "Dynamic Boost".
    pub fn priority_feedback(demand: SPA) -> SPA {
        // dynamic_recharge = base + (demand * 5/6)
        // Using 5/6 (0;50) instead of 0.8 for harmonic resonance with 24ms cycles
        let base = SPA::new(600, 0, 0, 0, 0); 
        let feedback = demand * SPA::new(0, 50, 0, 0, 0);
        base + feedback
    }
}
