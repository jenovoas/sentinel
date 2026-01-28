// pub mod rbac_biological; // Missing file

// DEPRECATED: Float-based version (kept for historical reference)
// pub mod soul_verifier; // Missing file

// S60 validation functions (used by production version)
pub mod soul_verifier_s60;

// PRODUCTION: Pure S60 implementation for physical model safety
pub mod soul_verifier_s60_production;

// BIO-RESONANCE: The Human Anchor (Phase 6)
pub mod bio_resonance;

// Re-export production version as default
pub use soul_verifier_s60_production::{
    BiometricError, BiometricProof, BiometricVerifier, LivenessChallenge,
};
