# Truth Algorithm - Claim Extraction POC

## Requirements

```bash
pip install spacy transformers torch
python -m spacy download en_core_web_sm
```

## Quick Start

```python
from claim_extractor import ClaimExtractor

# Initialize extractor
extractor = ClaimExtractor()

# Extract claims from text
text = "Biden said unemployment is at 3.5% in December 2023."
claims = extractor.extract(text)

# Print results
for claim in claims:
    print(f"Claim: {claim.text}")
    print(f"Type: {claim.claim_type}")
    print(f"Entities: {claim.entities}")
```

## Run Tests

```bash
cd /home/jnovoas/sentinel/truth_algorithm
python claim_extractor.py
```

## Features

✅ **Claim Detection**: Identifies verifiable claims vs opinions  
✅ **Entity Extraction**: Extracts people, organizations, dates, numbers  
✅ **Claim Classification**: Categorizes as factual, statistical, causal, etc.  
✅ **Confidence Scoring**: 0-1 confidence for each classification  
✅ **Keyword Extraction**: Identifies important terms for search  

## Example Output

```json
{
  "text": "Biden said unemployment is at 3.5% in December 2023.",
  "claim_type": "statistical claim",
  "confidence": 0.92,
  "entities": [
    {"text": "Biden", "type": "PERSON"},
    {"text": "3.5%", "type": "PERCENT"},
    {"text": "December 2023", "type": "DATE"}
  ],
  "is_verifiable": true,
  "keywords": ["unemployment", "biden"]
}
```

## Architecture

```
Text Input
    ↓
┌─────────────────────────────────────┐
│ 1. CLAIM EXTRACTION                 │
│ - Detect verifiable claims          │
│ - Extract entities & keywords       │
│ - Classify claim types              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. SOURCE SEARCH                    │
│ - Optimize query                    │
│ - Select trusted sources            │
│ - Extract evidence                  │
│ - Rank by relevance + trust         │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. VERIFICATION (Coming Next)       │
│ - Consensus algorithm                │
│ - Confidence scoring                │
│ - Contradiction detection           │
└─────────────────────────────────────┘
```

## Components

### 1. Claim Extractor ✅

**File**: `claim_extractor.py`

Extracts verifiable claims from text using NLP.

**Features**:
- Factual vs opinion detection
- Entity extraction (people, orgs, dates, numbers)
- Claim type classification
- Confidence scoring

### 2. Source Search ✅

**File**: `source_search.py`

Searches trusted sources for verification evidence.

**Architecture** (4 Layers):
1. **Query Optimization** - Converts claims to optimal search queries
2. **Source Selection** - Chooses best sources by category
3. **Result Extraction** - Fetches evidence from sources
4. **Relevance Ranking** - Scores by trust + relevance

**Features**:
- Async/await for performance
- Redis caching (optional)
- Rate limiting
- Trust scoring per source
- Category-based source selection

**Configuration**:
```bash
# Copy example env file
cp .env.example .env

# Edit with your API keys
nano .env
```

**Usage**:
```python
from source_search import SourceSearchEngine

async with SourceSearchEngine() as engine:
    results = await engine.search(
        claim="Biden said unemployment is at 3.5%",
        entities=["Biden", "3.5%"],
        keywords=["unemployment"]
    )
    
    for result in results:
        print(f"{result.title} (trust: {result.trust_score})")
```

## Next Steps

1. ✅ Claim Extraction
2. ✅ Source Search
3. ⏳ Verification Algorithm (consensus scoring)
4. ⏳ API Integration (FastAPI endpoint)
5. ⏳ Frontend (browser extension)
