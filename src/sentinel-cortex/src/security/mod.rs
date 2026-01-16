pub mod rbac_biological;

// DEPRECATED: Float-based version (kept for historical reference)
#[deprecated(
    since = "7.1.0",
    note = "Use soul_verifier_s60_production for physical model deployment. This version uses floats which cause thermal noise and precision errors."
)]
pub mod soul_verifier;

// S60 validation functions (used by production version)
pub mod soul_verifier_s60;

// PRODUCTION: Pure S60 implementation for physical model safety
pub mod soul_verifier_s60_production;

// BIO-RESONANCE: The Human Anchor (Phase 6)
pub mod bio_resonance;

// Re-export production version as default
pub use soul_verifier_s60_production::{
    AlmaChallenge, ProofOfLife, SoulError, SoulVerifier as SoulVerifierProduction,
};
