use rayon::prelude::*;

pub mod buffer;
pub mod cache;
pub mod subbuffer;
use aho_corasick::AhoCorasick;
pub mod verifier;

/// Optimized claim extractor using Aho-Corasick
pub struct ClaimExtractor {
    factual_matcher: AhoCorasick,
    opinion_matcher: AhoCorasick,
}

impl ClaimExtractor {
    pub fn new() -> Self {
        // Factual indicators (expanded list)
        let factual_patterns = vec![
            "is", "are", "was", "were", "has", "have",
            "announced", "reported", "confirmed", "stated",
            "according to", "data shows", "statistics",
            "%", "percent", "million", "billion",
            "increased", "decreased", "rose", "fell",
        ];
        
        // Opinion indicators (expanded list)
        let opinion_patterns = vec![
            "think", "believe", "feel", "should", "could",
            "probably", "maybe", "perhaps", "might",
            "in my opinion", "I believe", "seems like",
            "likely", "possibly", "allegedly",
        ];
        
        Self {
            factual_matcher: AhoCorasick::new(factual_patterns).unwrap(),
            opinion_matcher: AhoCorasick::new(opinion_patterns).unwrap(),
        }
    }
    
    /// Extract claims from text (optimized with Aho-Corasick)
    pub fn extract(&self, text: &str) -> Vec<String> {
        // Split into sentences
        let sentences: Vec<&str> = text
            .split(&['.', '!', '?'][..])
            .filter(|s| !s.trim().is_empty())
            .collect();
        
        // Process in parallel with Rayon
        sentences
            .par_iter()
            .filter_map(|sentence| {
                if self.is_verifiable(sentence) {
                    Some(sentence.trim().to_string())
                } else {
                    None
                }
            })
            .collect()
    }
    
    /// Extract claims from batch of texts (optimized batch processing)
    pub fn extract_batch(&self, texts: &[&str]) -> Vec<Vec<String>> {
        texts
            .par_iter()
            .map(|text| self.extract(text))
            .collect()
    }
    
    fn is_verifiable(&self, sentence: &str) -> bool {
        let sentence_lower = sentence.to_lowercase();
        
        // Use Aho-Corasick for fast pattern matching
        let has_factual = self.factual_matcher.is_match(&sentence_lower);
        let has_opinion = self.opinion_matcher.is_match(&sentence_lower);
        
        // Verifiable if has factual pattern and no opinion
        has_factual && !has_opinion
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_claim_extraction() {
        let extractor = ClaimExtractor::new();
        let text = "The sky is blue. I think it's beautiful. The earth is round.";
        let claims = extractor.extract(text);
        
        assert_eq!(claims.len(), 2); // "sky is blue" and "earth is round"
        assert!(claims.contains(&"The sky is blue".to_string()));
        assert!(claims.contains(&"The earth is round".to_string()));
    }
}
