#!/usr/bin/env python3
"""
Python baseline for claim extraction - for comparison with Rust
"""
import re
import time

class ClaimExtractor:
    def __init__(self):
        self.factual_pattern = re.compile(r'\b(is|are|was|were|has|have)\b')
        self.opinion_pattern = re.compile(r'\b(think|believe|feel|should)\b')
    
    def extract(self, text: str) -> list[str]:
        """Extract claims from text"""
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        
        # Filter verifiable claims
        claims = []
        for sentence in sentences:
            if self.is_verifiable(sentence):
                claims.append(sentence)
        
        return claims
    
    def is_verifiable(self, sentence: str) -> bool:
        """Check if sentence is verifiable"""
        has_factual = bool(self.factual_pattern.search(sentence))
        has_opinion = bool(self.opinion_pattern.search(sentence))
        return has_factual and not has_opinion


def benchmark():
    """Benchmark Python claim extraction"""
    extractor = ClaimExtractor()
    
    test_text = """The unemployment rate is 3.5% according to the Bureau of Labor Statistics. 
    This represents a significant improvement from last year. 
    I think the economy is doing well overall. 
    Tesla announced a new electric vehicle priced at $25,000. 
    The stock market was up 2% today on positive economic news. 
    Climate change is affecting weather patterns globally. 
    Many experts believe we need immediate action. 
    The new policy will take effect next month."""
    
    # Warm up
    for _ in range(100):
        extractor.extract(test_text)
    
    # Benchmark
    iterations = 10000
    start = time.perf_counter()
    for _ in range(iterations):
        claims = extractor.extract(test_text)
    end = time.perf_counter()
    
    total_time = end - start
    avg_time = (total_time / iterations) * 1_000_000  # microseconds
    
    print(f"Python Claim Extraction Benchmark")
    print(f"  Iterations: {iterations}")
    print(f"  Total time: {total_time:.4f}s")
    print(f"  Average time: {avg_time:.2f}μs")
    print(f"  Claims extracted: {len(claims)}")
    print(f"\nClaims:")
    for claim in claims:
        print(f"  - {claim}")


if __name__ == "__main__":
    benchmark()
