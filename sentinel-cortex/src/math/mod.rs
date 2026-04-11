// src/math/s60.rs
//!! # 🛡️ SENTINEL CORTEX — Módulo de Matemática Soberana 🛡️
//!
//! S60: Aritmética sexagesimal interna del Cortex (60^3 / Tertia).
//! SCALE_0 = 216,000. Tipo soberano para el Soul Verifier y BCI.
//!
//! harmonic_logic opera con SPA (me60os_core) directamente.
//! Ambos dominios son válidos y NO deben mezclarse sin bridge.
//!
//! YATRA Protocolo: CERO CONTAMINACIÓN DECIMAL.

/// Lógica armónica — usa SPA de me60os_core directamente
pub mod harmonic_logic;

/// Tipo S60: Aritmética sexagesimal soberana del Cortex (60^3)
pub mod s60;

/// Funciones matemáticas S60: ln, entropy, fft, sqrt, sin
pub mod s60_math;
