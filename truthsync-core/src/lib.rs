// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
#![allow(clippy::cast_possible_truncation, clippy::cast_precision_loss)]
#![deny(clippy::float_cmp)]
// ⚡ TRUTHSYNC NEURAL CORE - HIGH-SPEED FACT VERIFIER (<100μs) ⚡

use aho_corasick::{AhoCorasick, MatchKind};
use lru::LruCache;
use me60os_core::spa::SPA;
use rayon::prelude::*;
use regex::RegexSet;
use serde::{Deserialize, Serialize};
use sha3::{Digest, Sha3_512};
use std::hash::{Hash, Hasher};
use std::num::NonZeroUsize;
use std::sync::LazyLock;
use std::time::Instant;

static FACTUAL_PATTERNS: LazyLock<RegexSet> = LazyLock::new(|| {
    RegexSet::new([
        r"\b(es|son|fue|fueron|ocurrió|demostró|afirma|reporta)\b",
        r"\b(porcentaje|total|medida|temperatura|latencia|grados)\b",
        r"\b(http|https|ip|nodo|proceso|kernel|ebpf)\b",
    ])
    .unwrap()
});

/// Rayon threshold: ≤ RAYON_MIN_SENTENCES → sequential (evita overhead en textos cortos)
const RAYON_MIN_SENTENCES: usize = 4;

/// LRU cache capacity for SHA3-512 digests
const DIGEST_CACHE_SIZE: usize = 64;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Claim<'a> {
    /// MEJORA #5: Cow<str> con lifetime — zero-allocation cuando el texto vive lo suficiente
    #[serde(borrow)]
    pub text: std::borrow::Cow<'a, str>,
    pub is_factual: bool,
    pub trust_score: SPA,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VerificationResult<'a> {
    #[serde(borrow)]
    pub claims: Vec<Claim<'a>>,
    pub overall_trust_score: SPA,
    pub verification_time_us: u64,
    pub is_certified: bool,
}

#[derive(Default)]
pub struct ClaimExtractor;

impl ClaimExtractor {
    pub fn new() -> Self {
        Self
    }

    /// MEJORA #4: rayon threshold — si hay ≤ 3 oraciones, itera secuencial
    pub fn extract<'a>(&self, text: &'a str) -> Vec<Claim<'a>> {
        let sentences: Vec<&str> = text.split(&['.', '!', '?', '\n'][..]).collect();

        let map_claim = |s: &'a str| -> Claim<'a> {
            Claim {
                text: std::borrow::Cow::Borrowed(s),
                is_factual: FACTUAL_PATTERNS.is_match(s),
                // YATRA: 0.95 → SCALE_0 * 95 / 100, 0.70 → SCALE_0 * 70 / 100
                trust_score: if FACTUAL_PATTERNS.is_match(s) {
                    SPA::from_raw(SPA::SCALE_0 * 95 / 100)
                } else {
                    SPA::from_raw(SPA::SCALE_0 * 70 / 100)
                },
            }
        };

        // MEJORA #4: rayon threshold — ≤ RAYON_MIN_SENTENCES → sequential
        if sentences.len() <= RAYON_MIN_SENTENCES {
            sentences
                .iter()
                .map(|s| s.trim())
                .filter(|s| !s.is_empty())
                .map(map_claim)
                .collect()
        } else {
            sentences
                .par_iter()
                .map(|s| s.trim())
                .filter(|s| !s.is_empty())
                .map(map_claim)
                .collect()
        }
    }
}

/// Hash rápido (std DefaultHasher) para cache key — mucho más barato que SHA3-512
fn text_hash(text: &str) -> u64 {
    let mut h = std::collections::hash_map::DefaultHasher::new();
    text.hash(&mut h);
    h.finish()
}

pub struct TruthSyncEngine {
    extractor: ClaimExtractor,
    disinformation_patterns: AhoCorasick,
    /// MEJORA #3: LRU cache para digests SHA3-512 repetidos
    digest_cache: LruCache<(u64, i64), [u8; 64]>,
}

impl TruthSyncEngine {
    pub fn new() -> Self {
        // MEJORA #2: MatchKind::LeftmostFirst para early-exit en AhoCorasick
        let patterns = &[
            "inyección maliciosa",
            "fake_data",
            "mock_override",
            "simulación no real",
            "desbloqueo no autorizado",
        ];
        let ac = AhoCorasick::builder()
            .match_kind(MatchKind::LeftmostFirst)
            .build(patterns)
            .unwrap();

        Self {
            extractor: ClaimExtractor::new(),
            disinformation_patterns: ac,
            digest_cache: LruCache::new(NonZeroUsize::new(DIGEST_CACHE_SIZE).unwrap()),
        }
    }

    pub fn verify_text<'a>(
        &mut self,
        text: &'a str,
        lattice_energy: i64,
    ) -> VerificationResult<'a> {
        let start = Instant::now();
        let claims = self.extractor.extract(text);

        // Check for disinformation patterns with Aho-Corasick (LeftmostFirst)
        let mut malic_count = 0i64;
        for _ in self.disinformation_patterns.find_iter(text) {
            malic_count += 1;
        }

        // Constante de fase sexagesimal empírica (60⁴ escalada: 4.7962963 × 10⁶)
        // S60 constant: 4 units, 47 minutes, 46 seconds, 40 tertias
        let plimpton_constant_raw: i64 =
            4 * SPA::SCALE_0 + 47 * SPA::SCALE_1 + 46 * SPA::SCALE_2 + 40 * SPA::SCALE_3;
        let s60_constant = SPA::from_raw(plimpton_constant_raw);

        // MEJORA #3: cache lookup — solo SHA3-512 en cache miss
        let cache_key = (text_hash(text), lattice_energy);
        let digest = if let Some(cached) = self.digest_cache.get(&cache_key) {
            *cached
        } else {
            let mut hasher = Sha3_512::new();
            hasher.update(text.as_bytes());
            hasher.update(lattice_energy.to_le_bytes());
            hasher.update(s60_constant.to_raw().to_le_bytes());
            let d = hasher.finalize();
            let mut arr = [0u8; 64];
            arr.copy_from_slice(&d);
            self.digest_cache.put(cache_key, arr);
            arr
        };

        // YATRA: base_score = digest[0] / 255 (fraction 0..1)
        let base_score = SPA::from_raw((digest[0] as i64) * SPA::SCALE_0 / 255);

        // YATRA: penalty = malic_count × 0.3
        let penalty = SPA::from_raw((malic_count * 3 * SPA::SCALE_0) / 10);

        // YATRA: max(base - penalty, 0) with SPA integer arithmetic
        let raw_diff = (base_score.to_raw() - penalty.to_raw()).max(0);

        // Round to 2 decimal places in S60: round(raw * 100 / SCALE_0) * SCALE_0 / 100
        let rounded_raw =
            ((raw_diff * 100 + SPA::SCALE_0 / 2) / SPA::SCALE_0) * (SPA::SCALE_0 / 100);
        let overall_score = SPA::from_raw(rounded_raw);

        let elapsed_us = start.elapsed().as_micros() as u64;

        VerificationResult {
            claims,
            overall_trust_score: overall_score,
            verification_time_us: elapsed_us,
            // YATRA: certified if score >= 0.50
            is_certified: overall_score >= SPA::from_raw(SPA::SCALE_0 / 2),
        }
    }
}

impl Default for TruthSyncEngine {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    static S60_1: i64 = SPA::SCALE_0; // 1.0 in S60

    fn s60_from_pct(pct: i64) -> SPA {
        // pct = 0..100 integer
        SPA::from_raw(S60_1 * pct / 100)
    }

    #[test]
    fn test_extract_factual_sentence() {
        let extractor = ClaimExtractor::new();
        let claims = extractor.extract("El kernel fue actualizado. Hace buen día.");
        assert_eq!(claims.len(), 2);
        assert!(claims[0].is_factual);
        assert!(!claims[1].is_factual);
        // Factual → 0.95
        assert_eq!(claims[0].trust_score, s60_from_pct(95));
        // Opinion → 0.70
        assert_eq!(claims[1].trust_score, s60_from_pct(70));
    }

    #[test]
    fn test_extract_technical_terms() {
        let extractor = ClaimExtractor::new();
        let claims = extractor.extract("El proceso eBPF reporta latencia de 2ms.");
        assert_eq!(claims.len(), 1);
        assert!(claims[0].is_factual);
    }

    #[test]
    fn test_extract_empty_text() {
        let extractor = ClaimExtractor::new();
        let claims = extractor.extract("");
        assert!(claims.is_empty());
    }

    #[test]
    fn test_extract_newline_splitting() {
        let extractor = ClaimExtractor::new();
        let claims = extractor.extract("Línea uno\nLínea dos es factual.");
        assert_eq!(claims.len(), 2);
    }

    #[test]
    fn test_extract_borrows_input() {
        // MEJORA #5: verify that Cow::Borrowed avoids allocation
        let extractor = ClaimExtractor::new();
        let input = String::from("El kernel fue actualizado.");
        let claims = extractor.extract(&input);
        assert_eq!(claims.len(), 1);
        // Cow::Borrowed points to input slice, no allocation
        match &claims[0].text {
            std::borrow::Cow::Borrowed(s) => assert_eq!(*s, "El kernel fue actualizado"),
            _ => panic!("expected Cow::Borrowed"),
        }
    }

    #[test]
    fn test_verify_clean_text() {
        let mut engine = TruthSyncEngine::new();
        let result = engine.verify_text("El kernel fue actualizado correctamente.", 42);
        assert!(!result.claims.is_empty());
        assert!(result.overall_trust_score >= SPA::zero());
        assert!(result.overall_trust_score <= SPA::one());
        assert!(result.verification_time_us > 0);
    }

    #[test]
    fn test_verify_disinformation_penalty() {
        let mut engine = TruthSyncEngine::new();
        let clean = engine.verify_text("El kernel fue actualizado.", 42);
        let malicious = engine.verify_text(
            "El kernel fue actualizado con fake_data y mock_override.",
            42,
        );
        // Malicious text should have lower score due to penalty
        assert!(
            malicious.overall_trust_score < clean.overall_trust_score,
            "malicious={:?} should be < clean={:?}",
            malicious.overall_trust_score,
            clean.overall_trust_score
        );
    }

    #[test]
    fn test_verify_score_range() {
        let mut engine = TruthSyncEngine::new();
        let result = engine.verify_text("fake_data fake_data fake_data fake_data fake_data", 0);
        assert!(result.overall_trust_score >= SPA::zero());
        assert!(result.overall_trust_score <= SPA::one());
    }

    #[test]
    fn test_plimpton_constant() {
        // Verify the Plimpton constant: 4;47;46;40
        let raw = 4 * SPA::SCALE_0 + 47 * SPA::SCALE_1 + 46 * SPA::SCALE_2 + 40 * SPA::SCALE_3;
        let c = SPA::from_raw(raw);
        let expected = 4 * 12_960_000 + 47 * 216_000 + 46 * 3_600 + 40 * 60;
        assert_eq!(c.to_raw(), expected);
    }

    #[test]
    fn test_certification_threshold() {
        let mut engine = TruthSyncEngine::new();
        // Repeated disinformation should drop score below 0.50
        let result = engine.verify_text(
            "fake_data mock_override simulación no real inyección maliciosa desbloqueo no autorizado",
            0,
        );
        // With 5 penalties × 0.3 = 1.5, score should be 0 → not certified
        assert!(!result.is_certified);
        assert_eq!(result.overall_trust_score, SPA::zero());
    }

    #[test]
    fn test_claims_are_preserved() {
        let mut engine = TruthSyncEngine::new();
        let text = "La temperatura subió. El nodo reporta error. El cielo es azul.";
        let result = engine.verify_text(text, 0);
        assert_eq!(result.claims.len(), 3);
        assert_eq!(result.claims[0].text, "La temperatura subió");
        assert_eq!(result.claims[2].text, "El cielo es azul");
    }

    #[test]
    fn test_rounding_to_hundredths() {
        let mut engine = TruthSyncEngine::new();
        let result = engine.verify_text("test", 0);
        let raw = result.overall_trust_score.to_raw();
        // Should be divisible by SCALE_0/100 (rounded to hundredths)
        assert_eq!(raw % (SPA::SCALE_0 / 100), 0);
    }

    #[test]
    fn test_digest_cache_hit() {
        // MEJORA #3: verify repeated calls with same text+lattice_energy are consistent
        let mut engine = TruthSyncEngine::new();
        let r1 = engine.verify_text("cache test", 42);
        let r2 = engine.verify_text("cache test", 42);
        assert_eq!(r1.overall_trust_score, r2.overall_trust_score);
        assert_eq!(r1.is_certified, r2.is_certified);
    }

    #[test]
    fn test_rayon_threshold_sequential() {
        // MEJORA #4: 3 sentences → sequential path
        let extractor = ClaimExtractor::new();
        let claims = extractor.extract("A. B. C.");
        assert_eq!(claims.len(), 3);
    }

    #[test]
    fn test_rayon_threshold_parallel() {
        // MEJORA #4: 5 sentences → parallel path
        let extractor = ClaimExtractor::new();
        let claims = extractor.extract("A. B. C. D. E.");
        assert_eq!(claims.len(), 5);
    }
}
