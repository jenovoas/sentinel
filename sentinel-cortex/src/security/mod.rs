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

// AIOPS SHIELD SEMANTIC FIREWALL (Claim 2): Cognitive & Prompt Injection Defense
pub mod semantic_firewall;

// FORENSIC-GRADE WAL (Claim 4): Cryptographic Write-Ahead Log & Anti-Replay
pub mod forensic_wal;

// DUAL-GUARDIAN MUTUAL SURVEILLANCE (Claim 3): eBPF Alpha ↔ Cortex Beta
pub mod mutual_surveillance;

#[allow(unused_imports)]
pub use semantic_firewall::{AIOpsSemanticFirewall, InjectionType, SemanticDetection};
#[allow(unused_imports)]
pub use forensic_wal::{DataLane, ForensicWal, WalRecord};
#[allow(unused_imports)]
pub use mutual_surveillance::{GuardianHealth, GuardianStatusReport, MutualSurveillance};

// Re-export production version as default

#[allow(unused_imports)]
pub use lfm_security_pipeline::{LfmSecurityError, LfmSecurityPipeline};
#[allow(unused_imports)]
pub use soul_verifier_s60_production::{
    BiometricError, BiometricProof, BiometricVerifier, LivenessChallenge,
};
