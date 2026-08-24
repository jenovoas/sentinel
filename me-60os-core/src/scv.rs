// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ TRUTHSYNC: SEMANTIC & ENTROPIC FIREWALL 🛡️
//!
//! Implementation of the Sentinel "SCV" architecture.
//! Acts as a membrane involved in filtering information before it reaches the Cognitive Core.
//!
//! Two Layers:
//! 1. **Semantic Firewall**: Regex-based pattern matching (Truth vs Falsehood).
//! 2. **Entropic Firewall**: Shannon Entropy validation (Signal vs Noise).

use crate::bio::SoulVerifier; // Reuse Entropy Logic
use crate::ebpf_cortex_bridge::CortexEvent;
use crate::spa::SPA;
use crate::spa_math::SPAMath;
use regex::RegexSet;

#[cfg(feature = "extension-module")]
#[cfg(feature = "extension-module")]
use pyo3::prelude::*;

pub struct SemanticFirewall {
    // Whitelist patterns (Constructive/Truthful)
    #[allow(dead_code)]
    allowed_patterns: RegexSet,
    // Blacklist patterns (Destructive/False/Noise)
    blocked_patterns: RegexSet,
}

impl SemanticFirewall {
    pub fn new() -> Self {
        // Default rules (Example - to be expanded)
        let allowed = RegexSet::new([
            r"ME-60OS",
            r"Resonance",
            r"Truth",
            r"Physics",
            r"System Stable",
        ])
        .unwrap();

        let blocked =
            RegexSet::new([r"Error", r"Failure", r"Corruption", r"Panic", r"Attack"]).unwrap();

        Self {
            allowed_patterns: allowed,
            blocked_patterns: blocked,
        }
    }

    pub fn has_keywords(&self, text: &str) -> bool {
        self.allowed_patterns.is_match(text)
    }

    /// Checks if content passes the semantic filter
    pub fn verify(&self, text: &str) -> bool {
        // Block if matches blacklist
        if self.blocked_patterns.is_match(text) {
            return false;
        }
        true
    }
}

impl Default for SemanticFirewall {
    fn default() -> Self {
        Self::new()
    }
}

pub struct EntropicFirewall;

impl EntropicFirewall {
    /// Verifies if the information density is sufficient (neither random noise nor static repetition).
    /// Uses Shannon Entropy from Bio-Resonator.
    pub fn verify(events: &[CortexEvent]) -> bool {
        // REVIEW: entropy_signal viene de eBPF como u64 (raw SPA), siempre cabe en i64.
        //         Valor máximo típico ~5e9, muy por debajo de i64::MAX (9.2e18).
        let spa_signals: Vec<SPA> = events
            .iter()
            .map(|e| {
                debug_assert!(
                    e.entropy_signal <= i64::MAX as u64,
                    "entropy_signal excede i64"
                );
                SPA::from_raw(e.entropy_signal as i64)
            })
            .collect();
        let metrics = SoulVerifier::analyze(&spa_signals);
        metrics.is_alive
    }

    /// Calculate Shannon Entropy in S60
    pub fn calculate_entropy(text: &str) -> SPA {
        if text.is_empty() {
            return SPA::zero();
        }

        let mut counts = [0usize; 256];
        let mut total = 0usize;

        for b in text.bytes() {
            counts[b as usize] += 1;
            total += 1;
        }

        let mut entropy_sum = SPA::zero();
        let total_spa = SPA::new(total as i64, 0, 0, 0, 0);

        for &count in &counts {
            if count == 0 {
                continue;
            }
            // p = count / total
            let p = SPA::new(count as i64, 0, 0, 0, 0) / total_spa;
            let ln_p = SPAMath::ln(p);
            // entropy -= p * ln(p)
            let term = p * ln_p;
            entropy_sum = entropy_sum - term;
        }

        // Convert to base 2 bits approximation: H / ln(2)
        let inv_ln2 = SPA::from_raw(SPAMath::INV_LN2);
        entropy_sum * inv_ln2
    }

    /// Calculate text entropy validation
    pub fn verify_text(text: &str) -> bool {
        let entropy = Self::calculate_entropy(text);
        // Valid range for human-readable technical text (2.0 to 6.0 bits)
        let min_e = SPA::new(2, 0, 0, 0, 0);
        let max_e = SPA::new(6, 0, 0, 0, 0);
        entropy > min_e && entropy < max_e
    }
}

#[cfg_attr(feature = "extension-module", pyclass(module = "me60os_core"))]
pub struct ScvEngine {
    semantic: SemanticFirewall,
    #[allow(dead_code)]
    entropic: EntropicFirewall,
}

impl ScvEngine {
    pub fn new() -> Self {
        Self {
            semantic: SemanticFirewall::new(),
            entropic: EntropicFirewall,
        }
    }

    pub fn verify(&self, text: &str) -> bool {
        self.analyze(text).0
    }

    /// Returns (is_valid, score (SPA), entropy (SPA), has_keywords)
    pub fn analyze(&self, text: &str) -> (bool, SPA, SPA, bool) {
        if text.trim().is_empty() {
            return (false, SPA::zero(), SPA::zero(), false);
        }

        let blocked = self.semantic.blocked_patterns.is_match(text);
        if blocked {
            return (false, SPA::new(0, 6, 0, 0, 0), SPA::zero(), false); // 0.1 score
        }

        let entropy = EntropicFirewall::calculate_entropy(text);
        let has_keywords = self.semantic.has_keywords(text);

        // Valid range constants
        let min_e = SPA::new(2, 0, 0, 0, 0);
        let max_e = SPA::new(6, 0, 0, 0, 0);

        let valid_entropy = if text.len() < 5 {
            true
        } else {
            entropy > min_e && entropy < max_e
        };

        // Scores in S60
        let mut score = SPA::new(0, 30, 0, 0, 0); // 0.5 (Neutral baseline)
        if has_keywords {
            score = score + SPA::new(0, 18, 0, 0, 0); // +0.3 (18/60)
        }
        if valid_entropy {
            score = score + SPA::new(0, 12, 0, 0, 0); // +0.2 (12/60)
        }

        // Cap at 1.0
        let one = SPA::one();
        if score > one {
            score = one;
        }

        let is_valid = !blocked && valid_entropy;

        (is_valid, score, entropy, has_keywords)
    }
}

impl Default for ScvEngine {
    fn default() -> Self {
        Self::new()
    }
}
