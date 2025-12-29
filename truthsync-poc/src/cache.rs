use rustc_hash::FxHashMap;
use std::time::{Duration, Instant};
use aho_corasick::AhoCorasick;

/// Predictive cache for claim extraction results
pub struct PredictiveCache {
    // FxHashMap for ultra-fast lookups (10-20ns)
    cache: FxHashMap<u64, CachedResult>,
    
    // Prediction engine
    predictor: ClaimPredictor,
    
    // Configuration
    max_entries: usize,
    ttl: Duration,
}

/// Cached result with metadata
#[derive(Clone)]
pub struct CachedResult {
    pub claims: Vec<String>,
    pub timestamp: Instant,
    pub hit_count: u32,
    pub confidence: f32,
}

/// Claim predictor using pattern analysis
pub struct ClaimPredictor {
    // Fast pattern matcher (Aho-Corasick)
    factual_matcher: AhoCorasick,
    opinion_matcher: AhoCorasick,
    
    // Pattern frequency tracking
    pattern_freq: FxHashMap<String, u32>,
    
    // Prediction model
    prediction_threshold: f32,
}

impl PredictiveCache {
    pub fn new(max_entries: usize, ttl_secs: u64) -> Self {
        Self {
            cache: FxHashMap::default(),
            predictor: ClaimPredictor::new(),
            max_entries,
            ttl: Duration::from_secs(ttl_secs),
        }
    }
    
    /// Get cached result or predict likelihood
    pub fn get(&mut self, key: u64) -> Option<&Vec<String>> {
        // Check cache (O(1) lookup)
        if let Some(result) = self.cache.get_mut(&key) {
            result.hit_count += 1;
            return Some(&result.claims);
        }
        None
    }
    
    /// Store result in cache
    pub fn put(&mut self, key: u64, claims: Vec<String>, confidence: f32) {
        // Simple eviction: clear if full (O(1) amortized)
        if self.cache.len() >= self.max_entries {
            self.cache.clear();
        }
        
        // Insert new entry
        self.cache.insert(key, CachedResult {
            claims,
            timestamp: Instant::now(),
            hit_count: 0,
            confidence,
        });
    }
    
    /// Predict if text will contain claims (for pre-caching)
    pub fn predict_claims(&self, text: &str) -> f32 {
        self.predictor.predict_claim_likelihood(text)
    }
    
    /// Pre-warm cache with predicted content
    pub fn prewarm(&mut self, texts: &[(u64, String)]) {
        for (_key, text) in texts {
            let likelihood = self.predict_claims(text);
            
            // Only pre-cache high-likelihood content
            if likelihood > 0.7 {
                // This would trigger async processing in real implementation
            }
        }
    }
    
    /// Get cache statistics
    pub fn stats(&self) -> CacheStats {
        let total_hits: u32 = self.cache.values().map(|r| r.hit_count).sum();
        let avg_confidence: f32 = if self.cache.is_empty() {
            0.0
        } else {
            self.cache.values().map(|r| r.confidence).sum::<f32>() / self.cache.len() as f32
        };
        
        CacheStats {
            entries: self.cache.len(),
            total_hits,
            avg_confidence,
            hit_rate: if total_hits > 0 {
                total_hits as f32 / (total_hits + self.cache.len() as u32) as f32
            } else {
                0.0
            },
        }
    }
}

impl ClaimPredictor {
    pub fn new() -> Self {
        // High-confidence factual indicators
        let factual_patterns = vec![
            "is", "are", "was", "were", "has", "have",
            "announced", "reported", "confirmed", "stated",
            "according to", "data shows", "statistics",
            "%", "percent", "million", "billion",
        ];
        
        // Opinion indicators
        let opinion_patterns = vec![
            "think", "believe", "feel", "should", "could",
            "probably", "maybe", "perhaps", "might",
            "in my opinion", "I believe", "seems like",
        ];
        
        Self {
            factual_matcher: AhoCorasick::new(factual_patterns).unwrap(),
            opinion_matcher: AhoCorasick::new(opinion_patterns).unwrap(),
            pattern_freq: FxHashMap::default(),
            prediction_threshold: 0.6,
        }
    }
    
    /// Predict likelihood of text containing verifiable claims
    pub fn predict_claim_likelihood(&self, text: &str) -> f32 {
        let text_lower = text.to_lowercase();
        
        // Count factual indicators
        let factual_count = self.factual_matcher.find_iter(&text_lower).count() as f32;
        
        // Count opinion indicators
        let opinion_count = self.opinion_matcher.find_iter(&text_lower).count() as f32;
        
        // Calculate likelihood score
        let factual_score = (factual_count / (text.len() as f32 / 100.0)).min(1.0);
        let opinion_penalty = (opinion_count / (text.len() as f32 / 100.0)).min(0.5);
        
        (factual_score - opinion_penalty).max(0.0).min(1.0)
    }
}

#[derive(Debug)]
pub struct CacheStats {
    pub entries: usize,
    pub total_hits: u32,
    pub avg_confidence: f32,
    pub hit_rate: f32,
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_cache_basic() {
        let mut cache = PredictiveCache::new(10, 60);
        let key = 123;
        let claims = vec!["Test claim".to_string()];
        cache.put(key, claims.clone(), 0.9);
        let result = cache.get(key);
        assert!(result.is_some());
        assert_eq!(result.unwrap(), &claims);
    }
}
