// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// pub mod rbac_biological; // Missing file

// DEPRECATED: Float-based version (kept for historical reference)
// pub mod soul_verifier; // Missing file

// S60 validation functions (used by production version)
pub mod soul_verifier_s60;

// PRODUCTION: Pure S60 implementation for physical model safety
pub mod soul_verifier_s60_production;

// BIO-RESONANCE: The Human Anchor (Phase 6)
pub mod bio_resonance;

// TELEMETRY SANITIZER: Pure Rust Defense Against Telemetry Poisoning & Prompt Injection
pub mod telemetry_sanitizer;

// LFM PIPELINE: Ingress Sanitization & TruthSync Egress Certification (<100μs)
pub mod lfm_security_pipeline;

// Re-export production version as default

#[allow(unused_imports)]
pub use soul_verifier_s60_production::{
    BiometricError, BiometricProof, BiometricVerifier, LivenessChallenge,
};
// pipeline preparado: integracion pendiente
#[allow(unused_imports)]
pub use lfm_security_pipeline::{LfmSecurityError, LfmSecurityPipeline};
