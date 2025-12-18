use std::collections::{HashMap, VecDeque};
use std::time::{Duration, Instant};
use aho_corasick::AhoCorasick;

/// Predictive cache for claim extraction results
pub struct PredictiveCache {
    // LRU cache for recent results
    cache: HashMap<u64, CachedResult>,
    access_order: VecDeque<u64>,
    
    // Prediction engine
    predictor: ClaimPredictor,
    
    // Configuration
    max_entries: usize,
    ttl: Duration,
}

/// Cached result with metadata
struct CachedResult {
    claims: Vec<String>,
    timestamp: Instant,
    hit_count: u32,
    confidence: f32,
}

/// Claim predictor using pattern analysis
pub struct ClaimPredictor {
    // Fast pattern matcher (Aho-Corasick)
    factual_matcher: AhoCorasick,
    opinion_matcher: AhoCorasick,
    
    // Pattern frequency tracking
    pattern_freq: HashMap<String, u32>,
    
    // Prediction model
    prediction_threshold: f32,
}

impl PredictiveCache {
    pub fn new(max_entries: usize, ttl_secs: u64) -> Self {
        Self {
            cache: HashMap::new(),
            access_order: VecDeque::new(),
            predictor: ClaimPredictor::new(),
            max_entries,
            ttl: Duration::from_secs(ttl_secs),
        }
    }
    
    /// Get cached result or predict likelihood
    pub fn get(&mut self, key: u64) -> Option<&Vec<String>> {
        // Check cache
        if let Some(result) = self.cache.get_mut(&key) {
            // Update access time and hit count
            result.timestamp = Instant::now();
            result.hit_count += 1;
            
            // Move to front of LRU
            self.access_order.retain(|&k| k != key);
            self.access_order.push_front(key);
            
            return Some(&result.claims);
        }
        
        None
    }
    
    /// Store result in cache
    pub fn put(&mut self, key: u64, claims: Vec<String>, confidence: f32) {
        // Evict if at capacity
        if self.cache.len() >= self.max_entries {
            if let Some(oldest_key) = self.access_order.pop_back() {
                self.cache.remove(&oldest_key);
            }
        }
        
        // Insert new entry
        self.cache.insert(key, CachedResult {
            claims,
            timestamp: Instant::now(),
            hit_count: 0,
            confidence,
        });
        
        self.access_order.push_front(key);
    }
    
    /// Predict if text will contain claims (for pre-caching)
    pub fn predict_claims(&self, text: &str) -> f32 {
        self.predictor.predict_claim_likelihood(text)
    }
    
    /// Pre-warm cache with predicted content
    pub fn prewarm(&mut self, texts: &[(u64, String)]) {
        for (key, text) in texts {
            let likelihood = self.predict_claims(text);
            
            // Only pre-cache high-likelihood content
            if likelihood > 0.7 {
                // This would trigger async processing in real implementation
                // For now, just mark as high priority
            }
        }
    }
    
    /// Evict expired entries
    pub fn evict_expired(&mut self) {
        let now = Instant::now();
        let ttl = self.ttl;
        
        self.cache.retain(|key, result| {
            let keep = now.duration_since(result.timestamp) < ttl;
            if !keep {
                self.access_order.retain(|k| k != key);
            }
            keep
        });
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
            pattern_freq: HashMap::new(),
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
        // More factual indicators + fewer opinion indicators = higher likelihood
        let factual_score = (factual_count / (text.len() as f32 / 100.0)).min(1.0);
        let opinion_penalty = (opinion_count / (text.len() as f32 / 100.0)).min(0.5);
        
        (factual_score - opinion_penalty).max(0.0).min(1.0)
    }
    
    /// Learn from processed text (update prediction model)
    pub fn learn(&mut self, text: &str, had_claims: bool) {
        // Extract patterns from text
        let patterns = self.extract_patterns(text);
        
        // Update frequency based on outcome
        for pattern in patterns {
            let freq = self.pattern_freq.entry(pattern).or_insert(0);
            if had_claims {
                *freq += 1;
            }
        }
    }
    
    fn extract_patterns(&self, text: &str) -> Vec<String> {
        // Simple pattern extraction (can be enhanced)
        text.split_whitespace()
            .take(10)
            .map(|s| s.to_lowercase())
            .collect()
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
    
    #[test]
    fn test_predictor() {
        let predictor = ClaimPredictor::new();
        
        // High likelihood text
        let factual = "The unemployment rate is 3.5% according to statistics.";
        let score1 = predictor.predict_claim_likelihood(factual);
        
        // Low likelihood text
        let opinion = "I think maybe we should probably consider this.";
        let score2 = predictor.predict_claim_likelihood(opinion);
        
        assert!(score1 > score2);
        assert!(score1 > 0.5);
    }
}
