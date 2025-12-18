use crate::buffer::{SharedBuffer, MessageType};
use crate::cache::PredictiveCache;
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

/// Sub-buffer manager with predictive pre-caching
pub struct SubBufferManager {
    // Input sub-buffers (multiple for parallel ingestion)
    input_buffers: Vec<SharedBuffer>,
    
    // Output sub-buffers (multiple for parallel consumption)
    output_buffers: Vec<SharedBuffer>,
    
    // Predictive cache layer
    cache: PredictiveCache,
    
    // Current buffer index (round-robin)
    current_input: usize,
    current_output: usize,
}

impl SubBufferManager {
    /// Create new sub-buffer manager
    pub fn new(
        num_input_buffers: usize,
        num_output_buffers: usize,
        buffer_size: usize,
    ) -> Result<Self, String> {
        let mut input_buffers = Vec::new();
        let mut output_buffers = Vec::new();
        
        // Create input sub-buffers
        for i in 0..num_input_buffers {
            let name = format!("truthsync_input_{}", i);
            let buffer = SharedBuffer::create(&name, buffer_size)?;
            input_buffers.push(buffer);
        }
        
        // Create output sub-buffers
        for i in 0..num_output_buffers {
            let name = format!("truthsync_output_{}", i);
            let buffer = SharedBuffer::create(&name, buffer_size)?;
            output_buffers.push(buffer);
        }
        
        Ok(Self {
            input_buffers,
            output_buffers,
            cache: PredictiveCache::new(10000, 300), // 10k entries, 5min TTL
            current_input: 0,
            current_output: 0,
        })
    }
    
    /// Write to next available input buffer (round-robin)
    pub fn write_input(&mut self, text: &str) -> Result<u64, String> {
        // Calculate hash for cache key
        let key = self.hash_text(text);
        
        // Check cache first
        if let Some(cached_claims) = self.cache.get(key) {
            // Cache hit! Clone and write directly to output
            let claims_clone = cached_claims.clone();
            self.write_output_cached(key, &claims_clone)?;
            return Ok(key);
        }
        
        // Cache miss - predict likelihood
        let likelihood = self.cache.predict_claims(text);
        
        // Write to input buffer
        let buffer_idx = self.current_input;
        self.input_buffers[buffer_idx].write(
            MessageType::PROCESS_TEXT,
            text.as_bytes(),
        )?;
        
        // Round-robin to next buffer
        self.current_input = (self.current_input + 1) % self.input_buffers.len();
        
        Ok(key)
    }
    
    /// Read from next available output buffer
    pub fn read_output(&mut self) -> Result<(u16, Vec<u8>), String> {
        let buffer_idx = self.current_output;
        let result = self.output_buffers[buffer_idx].read()?;
        
        // Round-robin to next buffer
        self.current_output = (self.current_output + 1) % self.output_buffers.len();
        
        Ok(result)
    }
    
    /// Write cached result to output buffer
    fn write_output_cached(&mut self, key: u64, claims: &[String]) -> Result<(), String> {
        let buffer_idx = self.current_output;
        
        // Serialize claims (simple format for POC)
        let data = claims.join("\n");
        
        self.output_buffers[buffer_idx].write(
            MessageType::GET_RESULTS,
            data.as_bytes(),
        )?;
        
        self.current_output = (self.current_output + 1) % self.output_buffers.len();
        
        Ok(())
    }
    
    /// Update cache with processed result
    pub fn update_cache(&mut self, key: u64, claims: Vec<String>, confidence: f32) {
        self.cache.put(key, claims, confidence);
    }
    
    /// Pre-warm cache with predicted content
    pub fn prewarm_batch(&mut self, texts: Vec<String>) {
        let keyed_texts: Vec<(u64, String)> = texts
            .into_iter()
            .map(|t| (self.hash_text(&t), t))
            .collect();
        
        self.cache.prewarm(&keyed_texts);
    }
    
    /// Get cache statistics
    pub fn cache_stats(&self) -> String {
        let stats = self.cache.stats();
        format!(
            "Cache: {} entries, {} hits, {:.1}% hit rate, {:.2} avg confidence",
            stats.entries,
            stats.total_hits,
            stats.hit_rate * 100.0,
            stats.avg_confidence
        )
    }
    
    /// Hash text for cache key
    fn hash_text(&self, text: &str) -> u64 {
        let mut hasher = DefaultHasher::new();
        text.hash(&mut hasher);
        hasher.finish()
    }
    
    /// Get number of input buffers
    pub fn num_input_buffers(&self) -> usize {
        self.input_buffers.len()
    }
    
    /// Get number of output buffers
    pub fn num_output_buffers(&self) -> usize {
        self.output_buffers.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_sub_buffer_creation() {
        let manager = SubBufferManager::new(4, 4, 1024 * 1024);
        assert!(manager.is_ok());
        
        let mgr = manager.unwrap();
        assert_eq!(mgr.num_input_buffers(), 4);
        assert_eq!(mgr.num_output_buffers(), 4);
    }
}
