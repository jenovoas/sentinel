use crate::cache::PredictiveCache;
use std::collections::HashMap;
use std::time::Instant;

/// TruthSync self-verification layer
/// Validates cache predictions and adjusts confidence scores
pub struct TruthSyncVerifier {
    // Prediction accuracy tracking
    predictions: HashMap<u64, Prediction>,
    
    // Verification statistics
    total_predictions: u64,
    correct_predictions: u64,
    
    // Adaptive thresholds
    confidence_threshold: f32,
    min_accuracy_required: f32,
}

/// Prediction record for verification
struct Prediction {
    predicted_likelihood: f32,
    actual_had_claims: Option<bool>,
    timestamp: Instant,
    verified: bool,
}

impl TruthSyncVerifier {
    pub fn new() -> Self {
        Self {
            predictions: HashMap::new(),
            total_predictions: 0,
            correct_predictions: 0,
            confidence_threshold: 0.7,
            min_accuracy_required: 0.85,
        }
    }
    
    /// Record a prediction for later verification
    pub fn record_prediction(&mut self, key: u64, likelihood: f32) {
        self.predictions.insert(key, Prediction {
            predicted_likelihood: likelihood,
            actual_had_claims: None,
            timestamp: Instant::now(),
            verified: false,
        });
        
        self.total_predictions += 1;
    }
    
    /// Verify prediction with actual result
    pub fn verify(&mut self, key: u64, had_claims: bool) -> VerificationResult {
        if let Some(prediction) = self.predictions.get_mut(&key) {
            prediction.actual_had_claims = Some(had_claims);
            prediction.verified = true;
            
            // Check if prediction was correct
            let predicted_positive = prediction.predicted_likelihood > self.confidence_threshold;
            let was_correct = predicted_positive == had_claims;
            let predicted_likelihood = prediction.predicted_likelihood;
            
            if was_correct {
                self.correct_predictions += 1;
            }
            
            // Calculate current accuracy
            let accuracy = self.accuracy();
            
            // Adjust confidence threshold if accuracy is low
            if accuracy < self.min_accuracy_required {
                self.adjust_threshold();
            }
            
            VerificationResult {
                was_correct,
                predicted_likelihood,
                actual_had_claims: had_claims,
                current_accuracy: accuracy,
                adjusted_confidence: self.calculate_adjusted_confidence(predicted_likelihood, was_correct),
            }
        } else {
            VerificationResult::default()
        }
    }
    
    /// Calculate current prediction accuracy
    pub fn accuracy(&self) -> f32 {
        if self.total_predictions == 0 {
            return 1.0;
        }
        
        self.correct_predictions as f32 / self.total_predictions as f32
    }
    
    /// Adjust confidence threshold based on accuracy
    fn adjust_threshold(&mut self) {
        let accuracy = self.accuracy();
        
        if accuracy < self.min_accuracy_required {
            // Lower threshold if we're missing too many positives
            self.confidence_threshold *= 0.95;
        } else if accuracy > 0.95 {
            // Raise threshold if we're too permissive
            self.confidence_threshold *= 1.05;
        }
        
        // Keep threshold in reasonable bounds
        self.confidence_threshold = self.confidence_threshold.clamp(0.5, 0.9);
    }
    
    /// Calculate adjusted confidence based on historical accuracy
    fn calculate_adjusted_confidence(&self, raw_confidence: f32, was_correct: bool) -> f32 {
        let accuracy = self.accuracy();
        
        // Boost confidence if we're accurate, reduce if not
        let adjustment = if was_correct {
            1.0 + (accuracy - 0.85) * 0.5
        } else {
            1.0 - (0.85 - accuracy) * 0.5
        };
        
        (raw_confidence * adjustment).clamp(0.0, 1.0)
    }
    
    /// Get verification statistics
    pub fn stats(&self) -> VerificationStats {
        VerificationStats {
            total_predictions: self.total_predictions,
            correct_predictions: self.correct_predictions,
            accuracy: self.accuracy(),
            current_threshold: self.confidence_threshold,
        }
    }
    
    /// Clean up old predictions (older than 1 hour)
    pub fn cleanup_old(&mut self) {
        let now = Instant::now();
        let max_age = std::time::Duration::from_secs(3600);
        
        self.predictions.retain(|_, pred| {
            now.duration_since(pred.timestamp) < max_age
        });
    }
}

#[derive(Debug, Clone)]
pub struct VerificationResult {
    pub was_correct: bool,
    pub predicted_likelihood: f32,
    pub actual_had_claims: bool,
    pub current_accuracy: f32,
    pub adjusted_confidence: f32,
}

impl Default for VerificationResult {
    fn default() -> Self {
        Self {
            was_correct: false,
            predicted_likelihood: 0.0,
            actual_had_claims: false,
            current_accuracy: 0.0,
            adjusted_confidence: 0.0,
        }
    }
}

#[derive(Debug)]
pub struct VerificationStats {
    pub total_predictions: u64,
    pub correct_predictions: u64,
    pub accuracy: f32,
    pub current_threshold: f32,
}

/// Integrated TruthSync system with verification
pub struct TruthSyncEngine {
    cache: PredictiveCache,
    verifier: TruthSyncVerifier,
}

impl TruthSyncEngine {
    pub fn new(cache_size: usize, ttl_secs: u64) -> Self {
        Self {
            cache: PredictiveCache::new(cache_size, ttl_secs),
            verifier: TruthSyncVerifier::new(),
        }
    }
    
    /// Process text with prediction and verification
    pub fn process_with_verification(&mut self, key: u64, text: &str) -> ProcessingDecision {
        // Predict likelihood
        let likelihood = self.cache.predict_claims(text);
        
        // Record prediction for verification
        self.verifier.record_prediction(key, likelihood);
        
        // Check cache
        if let Some(cached) = self.cache.get(key) {
            return ProcessingDecision::CacheHit(cached.clone());
        }
        
        // Decide whether to process based on likelihood
        if likelihood > self.verifier.confidence_threshold {
            ProcessingDecision::Process(likelihood)
        } else {
            ProcessingDecision::Skip(likelihood)
        }
    }
    
    /// Update with actual result and verify prediction
    pub fn update_and_verify(&mut self, key: u64, claims: Vec<String>) -> VerificationResult {
        let had_claims = !claims.is_empty();
        
        // Verify prediction
        let verification = self.verifier.verify(key, had_claims);
        
        // Update cache with adjusted confidence
        self.cache.put(key, claims, verification.adjusted_confidence);
        
        verification
    }
    
    /// Get combined statistics
    pub fn stats(&self) -> String {
        let cache_stats = self.cache.stats();
        let verify_stats = self.verifier.stats();
        
        format!(
            "TruthSync Stats:\n\
             Cache: {} entries, {:.1}% hit rate\n\
             Predictions: {}/{} correct ({:.1}% accuracy)\n\
             Threshold: {:.2}",
            cache_stats.entries,
            cache_stats.hit_rate * 100.0,
            verify_stats.correct_predictions,
            verify_stats.total_predictions,
            verify_stats.accuracy * 100.0,
            verify_stats.current_threshold
        )
    }
}

#[derive(Debug)]
pub enum ProcessingDecision {
    CacheHit(Vec<String>),
    Process(f32),  // likelihood
    Skip(f32),     // likelihood too low
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_verifier_accuracy() {
        let mut verifier = TruthSyncVerifier::new();
        
        // Record predictions
        verifier.record_prediction(1, 0.9);
        verifier.record_prediction(2, 0.3);
        
        // Verify
        let result1 = verifier.verify(1, true);  // Correct
        let result2 = verifier.verify(2, false); // Correct
        
        assert!(result1.was_correct);
        assert!(result2.was_correct);
        assert_eq!(verifier.accuracy(), 1.0);
    }
    
    #[test]
    fn test_threshold_adjustment() {
        let mut verifier = TruthSyncVerifier::new();
        let initial_threshold = verifier.confidence_threshold;
        
        // Make many incorrect predictions
        for i in 0..100 {
            verifier.record_prediction(i, 0.9);
            verifier.verify(i, false); // All wrong
        }
        
        // Threshold should have adjusted
        assert_ne!(verifier.confidence_threshold, initial_threshold);
    }
}
