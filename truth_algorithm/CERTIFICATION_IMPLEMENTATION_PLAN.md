# Implementation Plan: Truth Algorithm Content Certification

## Goal

Implement the content certification system that takes text content, extracts claims, verifies them against multiple sources, and generates a Truth Score certificate.

## User Review Required

> [!IMPORTANT]
> **Design Decision**: The Claim Extractor will use simple regex patterns initially instead of NLP/LLM to avoid dependencies and costs. This means it will work best with structured content (bullet points, clear statements). For more complex text, we can upgrade to NLP later.

> [!NOTE]
> **Performance**: The system will search sources in parallel for multiple claims to optimize speed. With rate limiting of 10 req/min, we can verify ~10 claims per minute per provider.

---

## Proposed Changes

### Truth Algorithm Core

#### [NEW] [`truth_algorithm/claim_extractor.py`](file:///home/jnovoas/sentinel/truth_algorithm/claim_extractor.py)

Simple claim extraction using sentence splitting and filtering.

**Features**:
- Split text into sentences
- Filter out questions, commands, opinions
- Return list of verifiable claims
- Handle multiple languages (basic)

#### [NEW] [`truth_algorithm/source_verifier.py`](file:///home/jnovoas/sentinel/truth_algorithm/source_verifier.py)

Verifies each claim using Source Search Engine.

**Features**:
- Search multiple sources per claim
- Parallel search for multiple claims
- Cache results to avoid duplicate searches
- Return sources with confidence scores

#### [NEW] [`truth_algorithm/consensus_engine.py`](file:///home/jnovoas/sentinel/truth_algorithm/consensus_engine.py)

Calculates consensus score from multiple sources.

**Algorithm**:
```python
weights = {
    'official': 1.0,   # .gov, .gob
    'academic': 0.9,   # .edu
    'news': 0.7,       # reuters, bbc, etc
    'general': 0.5     # otros
}

consensus = sum(weight[source.type] * source.confidence) / num_sources
```

#### [NEW] [`truth_algorithm/truth_score_calculator.py`](file:///home/jnovoas/sentinel/truth_algorithm/truth_score_calculator.py)

Generates final Truth Score from all claim consensus scores.

**Formula**:
```python
truth_score = weighted_average(claim_scores)

# Con penalización por claims no verificables
if unverifiable_claims > 0:
    penalty = 0.1 * (unverifiable_claims / total_claims)
    truth_score -= penalty
```

#### [NEW] [`truth_algorithm/certification_generator.py`](file:///home/jnovoas/sentinel/truth_algorithm/certification_generator.py)

Creates verification certificate with metadata.

**Output**:
```python
{
    "content_hash": "sha256...",
    "truth_score": 0.87,
    "confidence_level": "high",  # low/medium/high
    "claims_verified": 3,
    "claims_total": 3,
    "sources_used": 6,
    "timestamp": "2025-12-21T22:16:00Z",
    "provider": "google",  # or duckduckgo, mock
    "details": [...]
}
```

---

### Integration

#### [MODIFY] [`truth_algorithm/source_search.py`](file:///home/jnovoas/sentinel/truth_algorithm/source_search.py)

Add batch search method for multiple claims:

```python
def batch_search(self, claims: List[str], max_results: int = 5) -> Dict[str, List[SearchResult]]:
    """Search multiple claims in parallel (respecting rate limits)"""
    results = {}
    for claim in claims:
        results[claim] = self.search(claim, max_results)
        time.sleep(6)  # Rate limiting: 10/min
    return results
```

---

### Testing & Benchmarks

#### [NEW] [`truth_algorithm/test_certification.py`](file:///home/jnovoas/sentinel/truth_algorithm/test_certification.py)

Unit tests for each component:
- `test_claim_extraction()`
- `test_source_verification()`
- `test_consensus_calculation()`
- `test_truth_score_calculation()`
- `test_certificate_generation()`

#### [NEW] [`truth_algorithm/benchmark_certification.py`](file:///home/jnovoas/sentinel/truth_algorithm/benchmark_certification.py)

End-to-end benchmark with real content:
- Measure time per claim
- Measure total certification time
- Test with different content lengths
- Compare providers (Google vs DuckDuckGo vs MOCK)

---

## Verification Plan

### Automated Tests

**Unit Tests**:
```bash
cd /home/jnovoas/sentinel/truth_algorithm
python -m pytest test_certification.py -v
```

Tests will cover:
- Claim extraction from sample text
- Source verification with MOCK provider
- Consensus calculation with known inputs
- Truth score calculation edge cases
- Certificate format validation

### Integration Test

**End-to-End Test**:
```bash
cd /home/jnovoas/sentinel/truth_algorithm
python benchmark_certification.py
```

Will certify sample content:
```
"Python is a programming language created by Guido van Rossum in 1991. 
It is widely used in data science and web development."
```

Expected output:
- Extract 3-4 claims
- Verify each with 3-5 sources
- Generate truth score 0.8-0.95
- Complete in < 60 seconds (with rate limiting)

### Manual Verification

User can test with custom content:
```bash
python -c "
from certification_generator import certify_content

content = '''Your content here'''
certificate = certify_content(content, provider='mock')
print(f'Truth Score: {certificate['truth_score']}')
"
```

---

## Next Steps After Implementation

1. Test with real Google API (when available)
2. Optimize claim extraction with NLP if needed
3. Add caching layer (Redis) for source results
4. Create web API endpoint for certification
5. Integrate with Sentinel Vault for content verification

---

**Powered by Google ❤️ & Perplexity 💜**
