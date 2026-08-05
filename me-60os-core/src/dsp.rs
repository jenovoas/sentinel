// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ S60 DSP (HARDWARE MULTIPLIER) — RUST PURO 🛡️
//!
//! Replica la lógica de `scripts/RECOVERED_quantum_hardware_synthesis.py`
//! (S60DSP): un bloque DSP FPGA para aritmética S60.
//!
//! Pipeline de multiplicación hardware:
//!   1. Multiplicación raw: i64 * i64 -> i128 (acumulador de alta precisión)
//!   2. Scaling: división floor por SCALE (12960000 = 60^4, SPA::SCALE_0)
//!   3. Writeback: check de registro de destino (64-bit) o wide (128-bit)
//!
//! El aporte real sobre SPA: modelo de acumulador 128-bit y TRAPS de overflow
//! de hardware (DSPConstraintError). SPA no los tiene. Determinista, S60 puro.
//!
//! NOTA: la cáscara ("S60 HARDWARE SIMULATOR v2", "DSP MELTDOWN") es documentación;
//! la FUNCIÓN es el pipeline de mul + traps, que se replica aquí.

use crate::spa::SPA;

/// Límite de registro acumulador DSP (128-bit con signo).
const MAX_INT128: i128 = i128::MAX; // 2^127 - 1 approx; usamos i128 completo
const MIN_INT128: i128 = i128::MIN;

/// Error de restricción de hardware DSP.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DspConstraintError {
    /// El valor intermedio excede el acumulador de 128-bit.
    AccumulatorMeltdown(i128),
    /// El resultado excede el registro de destino de 64-bit.
    RegisterOverflow(i128),
}

impl std::fmt::Display for DspConstraintError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            DspConstraintError::AccumulatorMeltdown(v) => {
                write!(f, "🔥 DSP ACCUMULATOR MELTDOWN: {} excede 128-bit", v)
            }
            DspConstraintError::RegisterOverflow(v) => {
                write!(f, "🌊 REGISTER OVERFLOW: {} excede 64-bit", v)
            }
        }
    }
}

impl std::error::Error for DspConstraintError {}

/// Bloque DSP S60: multiplicación con acumulador 128-bit y traps de hardware.
pub struct S60DSP;

impl S60DSP {
    /// SCALE = 60^4 = 12,960,000 (SPA::SCALE_0). Evita ambigüedad de attr de clase.
    pub const SCALE: i64 = SPA::SCALE_0;

    /// Verifica que el valor intermedio cabe en el acumulador DSP (128-bit).
    #[inline]
    fn check_128(val: i128) -> Result<(), DspConstraintError> {
        if val > MAX_INT128 || val < MIN_INT128 {
            return Err(DspConstraintError::AccumulatorMeltdown(val));
        }
        Ok(())
    }

    /// Pipeline estándar: A * B -> resultado 64-bit (con trap de registro).
    ///
    /// Paso 1: raw = a.raw * b.raw (i64*i64 -> i128, acumulador)
    /// Paso 2: res = raw / SCALE (scaling floor)
    /// Paso 3: writeback con check 64-bit (antes del cast, para no enmascarar overflow)
    pub fn mul_pipeline(a: SPA, b: SPA) -> Result<SPA, DspConstraintError> {
        let raw_a = a.to_raw() as i128;
        let raw_b = b.to_raw() as i128;

        // Paso 1: acumulación de alta precisión
        let intermediate = raw_a * raw_b;
        Self::check_128(intermediate)?;

        // Paso 2: barrel shifter / divisor algebraico (floor div por SCALE)
        let res_raw = intermediate / (Self::SCALE as i128);

        // Paso 3: writeback a registro 64-bit.
        // CHECK antes del cast: el `as i64` enmascararia el overflow.
        if res_raw > i64::MAX as i128 || res_raw < i64::MIN as i128 {
            return Err(DspConstraintError::RegisterOverflow(res_raw));
        }
        let res_64 = res_raw as i64;

        Ok(SPA::from_raw(res_64))
    }

    /// Pipeline wide: salida a registro 128-bit simulado (Deep Space).
    /// No hace check 64; permite 128 bits de salida (satura a i64 para SPA).
    pub fn mul_wide_pipeline(a: SPA, b: SPA) -> Result<SPA, DspConstraintError> {
        let raw_a = a.to_raw() as i128;
        let raw_b = b.to_raw() as i128;
        let intermediate = raw_a * raw_b;
        Self::check_128(intermediate)?;

        let res_raw = intermediate / (Self::SCALE as i128);
        Self::check_128(res_raw)?; // check 128 de salida

        // SPA::from_raw espera i64; para wide saturamos al rango i64 si excede
        // (el check_128 garantiza que el cálculo intermedio fue válido).
        let res_64 = if res_raw > i64::MAX as i128 {
            i64::MAX
        } else if res_raw < i64::MIN as i128 {
            i64::MIN
        } else {
            res_raw as i64
        };
        Ok(SPA::from_raw(res_64))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_mul_pipeline_trivial() {
        let r = S60DSP::mul_pipeline(SPA::from_int(1), SPA::from_int(1)).unwrap();
        assert_eq!(r, SPA::from_int(1));
    }

    #[test]
    fn test_mul_pipeline_leo_momentum() {
        // r = 7,000,000 m ; v = 7,000 m/s -> r*v en raw
        // raw = (7e6 * SCALE) * (7e3 * SCALE) / SCALE = 7e6 * 7e3 * SCALE
        let r = SPA::from_int(7_000_000);
        let v = SPA::from_int(7_000);
        let ang = S60DSP::mul_pipeline(r, v).unwrap();
        // Esperado: 49e9 * SCALE raw -> SPA from_int(49_000_000_000)
        assert_eq!(ang, SPA::from_int(49_000_000_000));
    }

    #[test]
    fn test_mul_pipeline_overflow_64_trap() {
        // Para exceder i64 tras scaling: intermediate/SCALE > 9.22e18
        // -> intermediate > 1.19e26. Con raw_a = raw_b = 1.5e13:
        // intermediate = 2.25e26 -> /SCALE = 1.73e19 > i64::MAX (9.22e18). Trap.
        let a = SPA::from_raw(15_000_000_000_000); // 1.5e13
        let b = SPA::from_raw(15_000_000_000_000);
        let res = S60DSP::mul_pipeline(a, b);
        match res {
            Err(DspConstraintError::RegisterOverflow(_)) => {} // correcto
            other => panic!("se esperaba RegisterOverflow, got {:?}", other),
        }
    }

    #[test]
    fn test_mul_wide_pipeline_handles_large() {
        // Wide: mismo caso, intermedio 2.25e26 cabe en i128 (1.7e38) -> no falla
        // por acumulador. mul_wide no hace check_64, asi que devuelve SPA con
        // raw saturado a i64::MAX (por la representacion SPA de 64-bit).
        let a = SPA::from_raw(15_000_000_000_000);
        let b = SPA::from_raw(15_000_000_000_000);
        let res = S60DSP::mul_wide_pipeline(a, b);
        match res {
            Ok(s) => {
                assert_eq!(s.to_raw(), i64::MAX);
            }
            Err(DspConstraintError::AccumulatorMeltdown(_)) => {} // si excede 128
            other => panic!("wide pipeline inesperado: {:?}", other),
        }
    }

    #[test]
    fn test_scale_constant() {
        // SCALE debe ser 60^4
        assert_eq!(S60DSP::SCALE, 12_960_000);
    }

    #[test]
    fn test_mul_pipeline_zero() {
        let r = S60DSP::mul_pipeline(SPA::from_int(0), SPA::from_int(42)).unwrap();
        assert_eq!(r, SPA::from_int(0));
    }

    #[test]
    fn test_mul_pipeline_negative() {
        let r = S60DSP::mul_pipeline(SPA::from_int(-5), SPA::from_int(3)).unwrap();
        assert_eq!(r, SPA::from_int(-15));
    }
}
