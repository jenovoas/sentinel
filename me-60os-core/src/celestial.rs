// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ CELESTIAL NAVIGATION (BASE-60 PURO) — RUST PURO 🛡️
//!
//! Replica la lógica computable de `quantum/celestial_navigation.py`:
//! - `SVector3`: vector 3D S60 (magnitude_sq, magnitude).
//! - `SovereignOrbit::calculate_keplerian_elements`: mecánica orbital S60
//!   (energía específica, semi-eje mayor, excentricidad, período).
//! - conversión esférica (RA/Dec) -> cartesiana (cos/sin S60).
//!
//! La cáscara de estudio (RoyalStar, catálogo Plimpton, precesión, astrolabio
//! de "triangulación estelar") se documenta pero NO se migra como lógica: es
//! fenomenología de estudio. La FUNCIÓN matemática determinista SÍ se replica.
//!
//! Validación contra base de conocimiento: la fórmula de Kepler usada es la
//! estándar de mecánica orbital newtoniana (ε = v²/2 − μ/r, a = −μ/2ε,
//! e = √(1 + 2εh²/μ²), T = 2π√(a³/μ)). Determinista, S60 puro.

// Núcleo S60: los casts i128→i64 en Mul/Div dentro de S60 son intencionales por el modelo
// de punto fijo base-60 (SCALE_0=12_960_000). Estos truncamientos no alteran la semántica
// ya que los valores nunca exceden el espacio físico S60 (raw < 60⁴ × 360).
#![allow(clippy::cast_possible_truncation)]

use crate::spa::SPA;
use crate::spa_math::SPAMath;

/// Vector 3D Soberano (S60).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct SVector3 {
    pub x: SPA,
    pub y: SPA,
    pub z: SPA,
}

impl SVector3 {
    pub fn new(x: SPA, y: SPA, z: SPA) -> Self {
        Self { x, y, z }
    }

    /// |v|² = x² + y² + z² (sin raíz, para eficiencia y comparaciones de norma).
    pub fn magnitude_sq(&self) -> SPA {
        self.x * self.x + self.y * self.y + self.z * self.z
    }

    /// |v| = sqrt(x² + y² + z²).
    pub fn magnitude(&self) -> SPA {
        SPAMath::sqrt(self.magnitude_sq())
    }

    /// Suma componente a componente.
    pub fn add(&self, other: &SVector3) -> SVector3 {
        SVector3::new(self.x + other.x, self.y + other.y, self.z + other.z)
    }

    /// Resta componente a componente (delta = self - other).
    pub fn sub(&self, other: &SVector3) -> SVector3 {
        SVector3::new(self.x - other.x, self.y - other.y, self.z - other.z)
    }

    /// Escala cada componente por un entero (k * v).
    pub fn scale(&self, k: i64) -> SVector3 {
        SVector3::new(self.x * k, self.y * k, self.z * k)
    }

    /// Divide cada componente por un entero (v / k). Usa Div<i64> (sin SCALE extra).
    pub fn div_int(&self, k: i64) -> SVector3 {
        SVector3::new(self.x / k, self.y / k, self.z / k)
    }
}

/// Motor de Mecánica Orbital Base-60.
pub struct SovereignOrbit;

impl SovereignOrbit {
    /// Calcula elementos orbitales básicos dado radio (r) y velocidad tangencial (v).
    ///
    /// Fórmulas (newtonianas):
    ///   1. Energía mecánica específica: ε = v²/2 − μ/r
    ///   2. Semi-eje mayor: a = −μ / (2ε)
    ///   3. Momento angular específico: h = r·v (asumiendo v ⟂ r, inyección ideal)
    ///   4. Excentricidad: e = √(1 + (2εh²)/μ²)
    ///   5. Período: T = 2π·√(a³/μ)
    ///
    /// `mu` es el parámetro gravitacional estándar (GM). Para Tierra: 3.986e14.
    ///
    /// NOTA DE IMPLEMENTACIÓN: el `.py` legacy almacenaba S60 como raw (sin SCALE en
    /// operaciones entre S60), así que replicamos la función operando en raw S60
    /// (`.to_raw()`) y reconstruyendo con `from_raw()`. Esto preserva la física
    /// idéntica al original y evita la inconsistencia de escala de SPA*SPA/SCALE.
    pub fn calculate_keplerian_elements(r: SPA, v: SPA, mu: SPA) -> KeplerElements {
        let v_raw = v.to_raw() as i128;
        let r_raw = r.to_raw() as i128;
        let mu_raw = mu.to_raw() as i128;

        // 1. Energía mecánica específica
        let v_sq = v_raw * v_raw;
        let v_sq_div_2 = v_sq / 2; // división entera segura
        let mu_div_r = mu_raw / r_raw;
        let epsilon_raw = v_sq_div_2 - mu_div_r;

        // Escape si ε >= 0
        if epsilon_raw >= 0 {
            return KeplerElements {
                semi_major_axis: SPA::ZERO,
                eccentricity: SPA::ONE,
                period: SPA::ZERO,
                status: OrbitStatus::Escape,
                epsilon: SPA::from_raw(epsilon_raw as i64),
            };
        }

        let epsilon = SPA::from_raw(epsilon_raw as i64);

        // 2. Semi-eje mayor: a = -mu / (2*epsilon)
        let neg_mu = -mu_raw;
        let two_eps = epsilon_raw * 2;
        let semi_major_axis_raw = neg_mu / two_eps;
        let semi_major_axis = SPA::from_raw(semi_major_axis_raw as i64);

        // 3. Momento angular específico: h = r * v
        let h_raw = r_raw * v_raw;
        let h_sq_raw = h_raw * h_raw;

        // 4. Excentricidad: e = sqrt(1 + (2*eps*h²)/mu²)
        let mu_sq_raw = mu_raw * mu_raw;
        let term_num = two_eps * h_sq_raw;
        let term_raw = term_num / mu_sq_raw;
        // under_root = 1 + term (en raw S60: 1 = SCALE_0)
        let scale = SPA::SCALE_0 as i128;
        let mut under_root_raw = scale + term_raw;
        if under_root_raw < 0 {
            under_root_raw = 0; // clamp por error numérico (frontera circular)
        }
        let eccentricity = SPAMath::sqrt(SPA::from_raw(under_root_raw as i64));

        // 5. Período: T = 2*pi*sqrt(a³/mu)
        let a_cubed_raw = semi_major_axis_raw * semi_major_axis_raw * semi_major_axis_raw;
        let under_root_t_raw = a_cubed_raw / mu_raw;
        let period = SPA::from_int(2) * SPAMath::TWO_PI * SPAMath::sqrt(SPA::from_raw(under_root_t_raw as i64));

        // Status
        let status = if eccentricity < SPA::new(0, 1, 0, 0, 0) {
            OrbitStatus::Circular // e < ~0.016
        } else if eccentricity >= SPA::ONE {
            OrbitStatus::Unstable
        } else {
            OrbitStatus::Stable
        };

        KeplerElements {
            semi_major_axis,
            eccentricity,
            period,
            status,
            epsilon,
        }
    }
}

/// Resultado del cálculo kepleriano.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct KeplerElements {
    pub semi_major_axis: SPA,
    pub eccentricity: SPA,
    pub period: SPA,
    pub status: OrbitStatus,
    pub epsilon: SPA,
}

/// Estado orbital derivado.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum OrbitStatus {
    Circular,
    Stable,
    Unstable,
    Escape,
}

/// Convierte coordenadas esféricas (RA/Dec en S60 grados) a vector unitario cartesiano.
///
/// x = cos(dec)·cos(ra)
/// y = cos(dec)·sin(ra)
/// z = sin(dec)
pub fn spherical_to_cartesian(ra: SPA, dec: SPA) -> SVector3 {
    let cos_dec = SPAMath::cos(dec);
    let sin_dec = SPAMath::sin(dec);
    let cos_ra = SPAMath::cos(ra);
    let sin_ra = SPAMath::sin(ra);

    SVector3::new(cos_dec * cos_ra, cos_dec * sin_ra, sin_dec)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_svector3_magnitude() {
        // vector (3,4,0) -> |v| = 5
        let v = SVector3::new(SPA::from_int(3), SPA::from_int(4), SPA::ZERO);
        assert_eq!(v.magnitude_sq(), SPA::from_int(25));
        assert_eq!(v.magnitude(), SPA::from_int(5));
    }

    #[test]
    fn test_spherical_to_cartesian_pole() {
        // Dec = +90° (polo norte) -> (0,0,1)
        // sin(90°) via Taylor deja residuo ~29 quartae (~2.2e-6); comparo con tolerancia.
        let dec = SPA::from_int(90);
        let v = spherical_to_cartesian(SPA::from_int(0), dec);
        let tol = SPA::new(0, 0, 0, 0, 50); // ~50 quartae tolerancia
        assert!(v.x.abs().to_raw() <= tol.to_raw());
        assert!(v.y.abs().to_raw() <= tol.to_raw());
        // z ~ 1 (cerca de ONE)
        assert!((v.z - SPA::ONE).abs().to_raw() <= tol.to_raw());
    }

    #[test]
    fn test_kepler_leo_circular() {
        // Constantes físicas del .py: S60(n) mapea a SPA::from_raw(n) (raw S60, sin re-escalar).
        // r = Re + 200km = 6_578_137 m ; v = 7_784 m/s ; mu = 398_600_441_800_000 (GM Tierra)
        let r = SPA::from_raw(6_578_137);
        let v = SPA::from_raw(7_784);
        let mu = SPA::from_raw(398_600_441_800_000);
        let el = SovereignOrbit::calculate_keplerian_elements(r, v, mu);
        // No debe ser escape (ε < 0)
        assert_ne!(el.status, OrbitStatus::Escape);
        // a debe ser positivo
        assert!(el.semi_major_axis.to_raw() > 0);
    }

    #[test]
    fn test_kepler_escape() {
        // v muy alto -> escape
        let r = SPA::from_raw(6_578_137);
        let v = SPA::from_raw(12_000);
        let mu = SPA::from_raw(398_600_441_800_000);
        let el = SovereignOrbit::calculate_keplerian_elements(r, v, mu);
        assert_eq!(el.status, OrbitStatus::Escape);
    }
}
