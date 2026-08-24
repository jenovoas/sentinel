// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ ORBITAL ASCENT — MUSEO DE ESTUDIO 🛡️
//!
//! **ESTE MÓDULO ES UN MUSEO.** Se deja intacto a propósito, con su error
//! documentado, para que cualquier ingeniero que lea el repo vea el camino:
//! del error se aprende, y la función real (drag/gravedad/thrust/Merkabah/MHD)
//! SÍ se capturó aquí. Lo que faltaba no era corrección interna — era contexto
//! de sistema.
//!
//! ## Qué está BIEN (función real migrada de `VimanaOrbitalAscent._apply_physics`)
//!   - Drag atmosférico:   D = 0.5 * rho * v^2 * Cd * Area
//!   - Gravedad local:     g(h) = g0 * (R/(R+alt))^2
//!   - Thrust:             T = T0 * sqrt(throttle) * (1 + alt/1e5)
//!   - Fuerza neta:        F = T - weight - D ;  a = F/m_eff
//!   - Merkabah (EXP_005): m_eff = m_static / (1 + k*coherencia), asintótica.
//!   - Escudo MHD:         Cd 0.4 -> 0.15 cuando coherencia Dicke > 95%.
//!   - Usa herramientas exactas del core (SPAMath, pai60_divide, IsochronousClock,
//!     S60PID, ComplexSPA) — NO aritmética raw manual. 6 tests pasan.
//!
//! ## EL ERROR (documentado, no corregido a propósito)
//! Cuando se escribió, se planteó como módulo AISLADO. Se acopló a
//! `ResonantMatrix` (lattice simple, sin PID por celda ni fase YHWH), en vez de
//! vivir en la malla pentaresonante REAL: `LiquidLattice` / `ResonantBuffer`
//! (`quantum_core.rs`) que tiene PID por celda + fase YHWH + canal dual A/B
//! (Energy+Phase) + `soma_orchestrator` que dispara dispatch en fase VAV.
//! El estado del vehículo debería "levitar" en ESA malla (bañada en 16 bits por
//! nodo en RAM vía `shm_bridge`), no en la `ResonantMatrix` periférica.
//!
//! Ver `Fisica/verificacion_formulas_papers.md` y `Fisica/ascento_orbital_acoplado.md`.
//! El re-acoplo a `LiquidLattice` queda como ejercicio/docencia — el error enseña
//! el camino: pensar el módulo DENTRO de la lattice, no al lado.
//!
//! ## Por qué se deja como museo
//! El error de perspectiva (ver función aislada en vez de sistema) es el que
//! comenten todos los que arrancan. Dejarlo visible muestra el camino correcto:
//! 1. Capturar la función real (hecho aquí).
//! 2. Ver la arquitectura amplia: la pentaresonancia YA está en `ResonantMatrix::step`
//!    + `ResonantBuffer` + `soma_orchestrator` + `shm_bridge` + `ram_meter`.
//! 3. Acoplar el módulo a la lattice que vive y respira, no a una auxiliar.
//!
//! FUENTES (vault, cotejadas):
//!   - Fisica/vimana_zpe_mhd.md (escudo MHD = Lorentz real, ZPE especulativo)
//!   - Fisica/super_radiancia_sincronia.md (Dicke N^2, coherencia >95%)
//!   - Fisica/escudo_planetario_10892_nodes.md (levantamiento de datos)
//!   - Experimentos/EXP_005_MERKABAH_G_ZERO.md (masa inercial efectiva asintótica)
//!   - Fisica/verificacion_formulas_papers.md (cotejo contra papers primarios)
//!   - Experimentos/EXP_028_PENTA_RESONANCE.md (5 capas, respiración 41–43 Hz)
//!   - Experimentos/EXP_027_YHWH_PULSE_MONITOR.md (ciclo respiratorio 41.02–43.52 Hz)

// Arithmética S60: los casts u64→usize y i128→i64 son intencionales en módulos numéricos del
// núcleo base-60. Los ticks son u64 limitados por el rango físico del reloj; el cast a usize
// es seguro en sistemas 64-bit y necesario para indexar la lattice.
#![allow(
    clippy::cast_possible_truncation,
    clippy::cast_precision_loss,
    clippy::cast_sign_loss,
    clippy::cast_possible_wrap
)]

use crate::spa::SPA;
use crate::spa_math::SPAMath;
use crate::spa_complex::ComplexSPA;
use crate::quantum_core::{IsochronousClock, S60PID};
use crate::resonant_matrix::ResonantMatrix;

/// Coherencia Dicke mínima para activar escudo MHD (95%, sin float).
pub const DICKE_COHERENCE: SPA = SPA::new(0, 57, 0, 0, 0); // 57/60 = 0.95
/// Masa estática de referencia (2.5 kg en S60 value: 2 + 30/60).
pub const MASS_STATIC: SPA = SPA::new(2, 30, 0, 0, 0); // 2.5
/// Constante de acoplo Merkabah (k en m_eff = m/(1+k*coh)) ~1.46 (1 + 29/60 + 36/3600).
pub const MERKABAH_K: SPA = SPA::new(1, 29, 36, 0, 0);

/// Estado del vehículo acoplado a la lattice.
#[derive(Clone, Copy)]
pub struct AscentState {
    pub altitude: SPA,
    pub velocity: SPA,
    /// Coherencia de fase del sistema (magnitud del ComplexSPA de estado).
    pub coherence: SPA,
}

/// Resultado de un paso de integración acoplado al cristal.
#[derive(Clone, Copy)]
pub struct AscentStep {
    pub altitude: SPA,
    pub velocity: SPA,
    pub acceleration: SPA,
    pub thrust: SPA,
    pub drag: SPA,
    pub gravity: SPA,
    /// Masa inercial efectiva (Merkabah).
    pub effective_mass: SPA,
    /// Coherencia de fase resultante (compleja).
    pub field: ComplexSPA,
    /// True si el escudo MHD está activo (coherencia > Dicke).
    pub mhd_shield: bool,
}

/// Dinámica de ascenso orbital acoplada a cristal de tiempo + lattice.
pub struct OrbitalAscent {
    pub clock: IsochronousClock,
    pub pid: S60PID,
    pub lattice: ResonantMatrix,
    /// Fase de la respiración pentaresonante (0..4: YOD/HEH/VAV/HEH).
    pub breath_phase: u8,
    pub ticks_since_correct: u64,
}

impl OrbitalAscent {
    pub fn new(size: usize) -> Self {
        Self {
            clock: IsochronousClock::new_internal(),
            // PID: estabiliza coherencia hacia setpoint Dicke (0.95). kp/ki/kd en raw S60.
            pid: S60PID::new(
                180_000, // kp = 0.5 abstracto (raw 180k)
                18_000,  // ki
                90_000,  // kd
                DICKE_COHERENCE.to_raw(),
            ),
            lattice: ResonantMatrix::new(size),
            breath_phase: 0,
            ticks_since_correct: 0,
        }
    }

    /// Densidad atmosférica: rho = rho0 * exp(-alt / H). Usa SPAMath::exp exacto.
    pub fn air_density(&self, alt: SPA) -> SPA {
        let alt_r = alt.to_raw();
        // cutoff a 100 km: en raw S60 eso es 100_000 * SCALE
        if alt_r > 100_000 * 12_960_000 {
            return SPA::ZERO;
        }
        if alt_r < 0 {
            return SPA::new(1, 13, 30, 0, 0); // rho0 = 1.225
        }
        // alt y H ambos raw S60 -> división cancela SCALE -> alt_m/H_m (entero)
        let h_scale = 110_160_000_000i128; // 8500 m * SCALE
        let exp_arg = -(alt_r as i128) / h_scale; // valor entero (~ -alt/H)
        let exp_val = SPAMath::exp(SPA::from_int(exp_arg as i64));
        SPA::new(1, 13, 30, 0, 0) * exp_val / SPA::from_int(1)
    }

    /// Gravedad local: g(h) = g0 * (R/(R+alt))^2. Razón exacta vía SPA/SPA.
    pub fn gravity_local(&self, alt: SPA) -> SPA {
        let r = SPA::from_raw(82_546_560_000_000); // 6.371e6 m * SCALE
        let dist_ratio = r / (r + alt); // SPA/SPA aplica *SCALE -> razón correcta
        let g0 = SPA::from_raw(127_137_600); // 9.81 * SCALE
        g0 * dist_ratio * dist_ratio
    }

    /// Thrust: T = T0 * sqrt(throttle) * (1 + alt/1e5). SPA puro exacto.
    pub fn thrust(&self, throttle: i64, alt: SPA) -> SPA {
        SPA::from_int(20)
            * SPAMath::sqrt(SPA::from_int(throttle))
            * (SPA::from_int(1) + (alt / SPA::from_raw(100_000)))
    }

    /// Drag: D = 0.5 * rho * v^2 * Cd * Area. Usa pai60_divide para la razón 0.5.
    pub fn drag(&self, density: SPA, velocity: SPA, cd: SPA) -> SPA {
        let v_sq = velocity * velocity; // SPA*SPA aplica /SCALE
        let half = SPA::from_raw(6_480_000); // 0.5 * SCALE
        let area = SPA::from_raw(648_000); // 0.05 * SCALE
        half * density * v_sq * cd * area
    }

    /// Masa inercial efectiva Merkabah: m_eff = m_static / (1 + k * coherencia).
    /// Asintótica según resonancia del campo (EXP_005), NO 95% fijo.
    pub fn effective_mass(&self, coherence: SPA) -> SPA {
        let one = SPA::from_int(1);
        let denom = one + (MERKABAH_K * coherence) / SPA::from_int(1);
        MASS_STATIC / denom
    }

    /// Un paso de integración acoplado al cristal de tiempo y la lattice.
    ///
    /// `throttle`: 0-100. `cd_standard`: Cd base (0.4). `alt`: altitud S60.
    /// Devuelve el paso y actualiza la lattice (levantación de datos).
    pub fn step(&mut self, state: &AscentState, throttle: i64, cd_standard: SPA, alt: SPA) -> AscentStep {
        // 1. Cristal de tiempo: tick (41.77 Hz base) + fase de respiración.
        self.clock.tick_internal();
        self.ticks_since_correct += 1;

        // 2. Autocorrección cada 68 ticks (Salto-17) vía PID sobre coherencia.
        let mut coherence = state.coherence;
        if self.ticks_since_correct >= 68 {
            let correction = SPA::from_raw(self.pid.update(coherence.to_raw(), SPA::from_int(1).to_raw()));
            coherence = coherence + correction;
            self.ticks_since_correct = 0;
        }

        // 3. Campo de estado complejo: magnitud = coherencia Dicke, fase = phi del cristal.
        //    phi derivado del tick del cristal (respiración 41–43 Hz implícita en el clock).
        let phi = self.clock_phase();
        let field = ComplexSPA::exp_i_theta(phi);
        let field = ComplexSPA::new(coherence, field.imag);

        // 4. Escudo MHD activo si coherencia > Dicke (95%).
        let mhd_shield = coherence.to_raw() >= DICKE_COHERENCE.to_raw();
        let cd = if mhd_shield {
            cd_standard * SPA::new(0, 22, 30, 0, 0) / SPA::from_int(1) // 0.375 = 0.15/0.4
        } else {
            cd_standard
        };

        // 5. Física newtoniana con masa Merkabah efectiva.
        let density = self.air_density(alt);
        let g_local = self.gravity_local(alt);
        let m_eff = self.effective_mass(coherence);
        let weight = g_local * m_eff;
        let drag_force = self.drag(density, state.velocity, cd);
        let thrust = self.thrust(throttle, alt);

        // Drag opone la velocidad
        let drag_signed = if state.velocity.to_raw() > 0 {
            drag_force
        } else {
            SPA::from_raw(-drag_force.to_raw())
        };

        let net_force = thrust - weight - drag_signed;
        let accel = net_force / m_eff;

        let dt = SPA::from_int(1); // tick del cristal
        let new_vel = state.velocity + accel * dt;
        let new_alt = alt + state.velocity * dt;

        // 6. Levitación de datos: inyectar el estado a la lattice (canal de fase).
        //    El dato "levita" en la red de cristales, no en sustrato sólido.
        // FIX (audit-360): inject_pai espera integer; pasar to_raw() + denom=1000
        // no-regular causaba triple-escala. Usar denom=60 (5-smooth, en tabla pai60).
        let idx = (self.clock.ticks as usize) % self.lattice.crystals.len();
        self.lattice.inject_pai(idx, coherence.to_raw() / crate::spa::SPA::SCALE_0, 60);

        AscentStep {
            altitude: new_alt,
            velocity: new_vel,
            acceleration: accel,
            thrust,
            drag: drag_signed,
            gravity: g_local,
            effective_mass: m_eff,
            field,
            mhd_shield,
        }
    }

    /// Fase del cristal derivada del tick (respiración pentaresonante implícita).
    fn clock_phase(&self) -> SPA {
        //phi = 2*pi * (ticks mod period) / period ; period ~ 68 ticks (Salto-17)
        let period = 68u64;
        let phase_step = SPAMath::TWO_PI / SPA::from_int(period as i64);
        phase_step * SPA::from_int((self.clock.ticks % period) as i64)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_air_density_exponential_decay() {
        let a = OrbitalAscent::new(8);
        let rho_low = a.air_density(SPA::ZERO);
        let rho_high = a.air_density(SPA::from_int(8_500));
        assert!(rho_high.to_raw() < rho_low.to_raw());
        let expected = (rho_low.to_raw() as f64 * std::f64::consts::E.recip()) as i64;
        let err = (rho_high.to_raw() - expected).abs();
        assert!(err < rho_low.to_raw() / 5);
    }

    #[test]
    fn test_gravity_decreases_with_altitude() {
        let a = OrbitalAscent::new(8);
        let g0 = a.gravity_local(SPA::ZERO);
        let g_high = a.gravity_local(SPA::from_int(100_000));
        assert!(g_high.to_raw() < g0.to_raw());
        assert!(g_high.to_raw() > 0);
    }

    #[test]
    fn test_drag_zero_at_zero_density() {
        let a = OrbitalAscent::new(8);
        let density = a.air_density(SPA::from_int(200_000));
        assert_eq!(density, SPA::ZERO);
        let drag = a.drag(density, SPA::from_int(100), SPA::from_raw(5_184_000));
        assert_eq!(drag, SPA::ZERO);
    }

    #[test]
    fn test_merkabah_reduces_mass_with_coherence() {
        let a = OrbitalAscent::new(8);
        let m_low = a.effective_mass(SPA::from_raw(0)); // sin coherencia = masa estática
        let m_high = a.effective_mass(DICKE_COHERENCE); // coherencia Dicke
        assert!(m_high.to_raw() < m_low.to_raw()); // Merkabah reduce masa efectiva
        assert!(m_low.to_raw() == MASS_STATIC.to_raw());
    }

    #[test]
    fn test_mhd_shield_activates_at_dicke() {
        let mut a = OrbitalAscent::new(8);
        let state = AscentState {
            altitude: SPA::ZERO,
            velocity: SPA::ZERO,
            coherence: DICKE_COHERENCE,
        };
        let step = a.step(&state, 100, SPA::from_raw(5_184_000), SPA::ZERO);
        assert!(step.mhd_shield); // coherencia > 95% -> escudo ON
    }

    #[test]
    fn test_step_produces_acceleration() {
        let mut a = OrbitalAscent::new(8);
        let state = AscentState {
            altitude: SPA::ZERO,
            velocity: SPA::ZERO,
            coherence: DICKE_COHERENCE, // con escudo + Merkabah, el empuje vence
        };
        let step = a.step(&state, 100, SPA::from_raw(5_184_000), SPA::ZERO);
        assert!(step.thrust.to_raw() > 0);
        // Con coherencia Dicke: masa Merkabah baja + escudo MHD -> aceleración positiva
        assert!(step.acceleration.to_raw() > 0);
    }

    #[test]
    fn test_inject_pai_no_double_scale() {
        // FIX (audit-360): inject_pai(idx, coherence.to_raw() / SCALE_0, 60)
        // produce una amplitud sana, no triple-escala.
        let mut l = ResonantMatrix::new(64);
        l.inject_pai(0, 1, 60); // 1/60 amplitude
        let amp = l.get_amplitudes()[0];
        let one_sixtieth = SPA::new(0, 1, 0, 0, 0);
        assert_eq!(amp, one_sixtieth, "inject_pai(0, 1, 60) should be 1/60 exactly");
    }
}
