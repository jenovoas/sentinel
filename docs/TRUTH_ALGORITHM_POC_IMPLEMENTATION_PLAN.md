# 🎯 Truth Algorithm POC - Implementation Plan
## *Week 1-2: Minimal Viable Verification System*

**Created**: 2025-12-17  
**Goal**: Prove core concept with software version claims  
**Success Criteria**: >80% accuracy on 20 test claims

---

## 📋 Summary

### **What We're Building**:
A minimal verification system that can verify simple factual claims about software releases (e.g., "Rust 1.75 introduced async traits") by searching 2-3 official sources and applying a simple consensus algorithm.

### **What We're NOT Building** (Yet):
- Advanced NLP claim extraction
- Real-time TV monitoring
- Browser extensions
- Mobile apps
- Machine learning trust scoring
- Human expert review system
- Database persistence
- Caching layer

---

## 🏗️ Architecture Mapping: 5 Layers → POC Reality

### **Full Vision vs POC Implementation**:

| Layer | Full Vision | POC Implementation | Status |
|-------|-------------|-------------------|--------|
| **Layer 1: Input Guardian** | NLP extraction, adversarial detection | Simple string parsing, basic validation | ✅ POC |
| **Layer 2: Evidence Guardian** | Multi-source search, independence checking | 2-3 hardcoded sources, keyword matching | ✅ POC |
| **Layer 3: Trust Guardian** | ML-based reputation, historical tracking | Fixed trust scores (0.95, 0.90, 0.70) | ✅ POC |
| **Layer 4: Consensus Guardian** | Weighted algorithm, temporal/context validation | Simple majority voting | ✅ POC |
| **Layer 5: Human Expert** | Expert network, appeals process | Not in POC | ❌ Future |

### **POC Simplified Architecture**:

```
┌─────────────────────────────────────────┐
│ LAYER 1: Simple Parser                  │
│ - Extract keywords from claim            │
│ - Basic validation (not empty)           │
│ - No adversarial detection yet           │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ LAYER 2: Hardcoded Source Search        │
│ - 3 sources: Rust blog, Python.org, etc │
│ - Simple HTTP GET + keyword matching     │
│ - No independence checking yet           │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ LAYER 3: Fixed Trust Scores              │
│ - Official sources: 0.95                 │
│ - GitHub releases: 0.90                  │
│ - Wikipedia: 0.70                        │
│ - No learning/updating yet               │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ LAYER 4: Simple Majority Consensus       │
│ - If 2+ sources confirm → True           │
│ - If 2+ sources contradict → False       │
│ - Otherwise → Unverifiable               │
│ - No temporal/context validation yet     │
└─────────────────────────────────────────┘
```

---

## 📁 Proposed Code Changes

### **New Rust Project Structure**:

```
truth-algorithm-poc/
├── Cargo.toml
├── README.md
├── src/
│   ├── main.rs                 # API server (Axum)
│   ├── lib.rs                  # Library exports
│   ├── models/
│   │   ├── mod.rs
│   │   ├── claim.rs            # Claim struct
│   │   ├── verdict.rs          # Verdict enum (True/False/Unverifiable)
│   │   ├── source.rs           # Source struct
│   │   └── evidence.rs         # Evidence struct
│   ├── verification/
│   │   ├── mod.rs              # Verification orchestrator
│   │   ├── parser.rs           # Simple keyword extraction
│   │   ├── sources.rs          # Hardcoded source definitions
│   │   ├── search.rs           # HTTP search implementation
│   │   ├── consensus.rs        # Simple majority algorithm
│   │   └── explanation.rs      # Template-based explanations
│   └── api/
│       ├── mod.rs
│       └── routes.rs           # POST /api/verify endpoint
└── tests/
    ├── unit/
    │   ├── parser_tests.rs
    │   ├── consensus_tests.rs
    │   └── explanation_tests.rs
    └── integration/
        └── api_tests.rs
```

### **Key Files to Create**:

#### **1. `src/models/claim.rs`**:
```rust
pub struct Claim {
    pub text: String,
    pub software: Option<String>,  // e.g., "Rust"
    pub version: Option<String>,   // e.g., "1.75"
    pub feature: Option<String>,   // e.g., "async traits"
}
```

#### **2. `src/models/verdict.rs`**:
```rust
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum Verdict {
    True,
    False,
    Unverifiable,
}

pub struct VerificationResponse {
    pub claim: String,
    pub verdict: Verdict,
    pub confidence: f32,
    pub explanation: String,
    pub sources: Vec<Source>,
    pub timestamp: DateTime<Utc>,
}
```

#### **3. `src/verification/sources.rs`**:
```rust
pub struct Source {
    pub id: String,
    pub name: String,
    pub url: String,
    pub trust_score: f32,
    pub category: SourceCategory,
}

pub enum SourceCategory {
    Official,
    GitHub,
    Community,
}

// Hardcoded golden sources for POC
pub fn get_golden_sources() -> Vec<Source> {
    vec![
        Source {
            id: "rust-blog".to_string(),
            name: "Rust Blog".to_string(),
            url: "https://blog.rust-lang.org/".to_string(),
            trust_score: 0.95,
            category: SourceCategory::Official,
        },
        Source {
            id: "rust-releases".to_string(),
            name: "Rust GitHub Releases".to_string(),
            url: "https://github.com/rust-lang/rust/blob/master/RELEASES.md".to_string(),
            trust_score: 0.90,
            category: SourceCategory::GitHub,
        },
        // Add Python, Node.js sources...
    ]
}
```

#### **4. `src/verification/consensus.rs`**:
```rust
pub fn determine_verdict(evidence: &[Evidence]) -> VerificationResponse {
    let confirming = evidence.iter().filter(|e| e.confirms).count();
    let contradicting = evidence.iter().filter(|e| !e.confirms).count();
    let total = evidence.len();
    
    let verdict = if confirming >= 2 {
        Verdict::True
    } else if contradicting >= 2 {
        Verdict::False
    } else {
        Verdict::Unverifiable
    };
    
    let confidence = calculate_confidence(confirming, contradicting, total);
    
    VerificationResponse {
        verdict,
        confidence,
        // ... other fields
    }
}
```

#### **5. `src/api/routes.rs`**:
```rust
pub async fn verify_claim(
    Json(request): Json<VerificationRequest>,
) -> Result<Json<VerificationResponse>, StatusCode> {
    // 1. Parse claim
    let claim = parse_claim(&request.claim)?;
    
    // 2. Search sources
    let evidence = search_sources(&claim).await?;
    
    // 3. Determine verdict
    let response = determine_verdict(&evidence);
    
    // 4. Log decision
    log_verification(&response);
    
    Ok(Json(response))
}
```

---

## ✅ Verification Plan

### **Automated Tests**:

#### **1. Unit Tests** (Run: `cargo test --lib`):

**File**: `tests/unit/parser_tests.rs`
```rust
#[test]
fn test_parse_software_version_claim() {
    let claim = "Rust 1.75 introduced async traits";
    let parsed = parse_claim(claim).unwrap();
    
    assert_eq!(parsed.software, Some("Rust".to_string()));
    assert_eq!(parsed.version, Some("1.75".to_string()));
    assert_eq!(parsed.feature, Some("async traits".to_string()));
}
```

**File**: `tests/unit/consensus_tests.rs`
```rust
#[test]
fn test_consensus_with_majority_confirming() {
    let evidence = vec![
        Evidence { confirms: true, source_id: "rust-blog", trust_score: 0.95 },
        Evidence { confirms: true, source_id: "rust-releases", trust_score: 0.90 },
    ];
    
    let response = determine_verdict(&evidence);
    assert_eq!(response.verdict, Verdict::True);
    assert!(response.confidence >= 0.8);
}

#[test]
fn test_consensus_with_majority_contradicting() {
    let evidence = vec![
        Evidence { confirms: false, source_id: "source1", trust_score: 0.95 },
        Evidence { confirms: false, source_id: "source2", trust_score: 0.90 },
    ];
    
    let response = determine_verdict(&evidence);
    assert_eq!(response.verdict, Verdict::False);
}

#[test]
fn test_consensus_with_insufficient_evidence() {
    let evidence = vec![
        Evidence { confirms: true, source_id: "source1", trust_score: 0.95 },
    ];
    
    let response = determine_verdict(&evidence);
    assert_eq!(response.verdict, Verdict::Unverifiable);
}
```

#### **2. Integration Tests** (Run: `cargo test --test '*'`):

**File**: `tests/integration/api_tests.rs`
```rust
#[tokio::test]
async fn test_verify_true_claim() {
    let app = spawn_test_app().await;
    let client = reqwest::Client::new();
    
    let response = client
        .post(&format!("{}/api/verify", app.address))
        .json(&json!({
            "claim": "Rust 1.75 introduced async traits"
        }))
        .send()
        .await
        .unwrap();
    
    assert_eq!(response.status(), 200);
    
    let body: VerificationResponse = response.json().await.unwrap();
    assert_eq!(body.verdict, Verdict::True);
    assert!(body.confidence >= 0.8);
    assert!(body.sources.len() >= 2);
}

#[tokio::test]
async fn test_verify_false_claim() {
    let app = spawn_test_app().await;
    let client = reqwest::Client::new();
    
    let response = client
        .post(&format!("{}/api/verify", app.address))
        .json(&json!({
            "claim": "Python 4.0 was released in 2024"
        }))
        .send()
        .await
        .unwrap();
    
    let body: VerificationResponse = response.json().await.unwrap();
    assert_eq!(body.verdict, Verdict::False);
    assert!(body.confidence >= 0.8);
}
```

### **Manual Tests**:

#### **Test 1: Start the server**
```bash
# Terminal 1: Start server
cd truth-algorithm-poc
cargo run

# Expected output:
# Server listening on http://127.0.0.1:8000
```

#### **Test 2: Verify a true claim**
```bash
# Terminal 2: Send request
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"claim": "Rust 1.75 introduced async traits"}'

# Expected response:
# {
#   "claim": "Rust 1.75 introduced async traits",
#   "verdict": "True",
#   "confidence": 0.92,
#   "explanation": "Verified by 2 sources...",
#   "sources": [...]
# }
```

#### **Test 3: Verify a false claim**
```bash
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"claim": "Python 4.0 was released in 2024"}'

# Expected response:
# {
#   "verdict": "False",
#   "confidence": 0.95,
#   "explanation": "Contradicted by 2 sources. Latest Python is 3.12..."
# }
```

#### **Test 4: Accuracy evaluation**
```bash
# Run accuracy test with 20 ground truth claims
cargo test --test accuracy_evaluation -- --nocapture

# Expected output:
# Tested 20 claims
# Correct: 17
# Accuracy: 85%
# Target: >80% ✅
```

---

## 📊 Success Metrics

### **Must Achieve**:
- [ ] >80% accuracy on 20 test claims
- [ ] <5s response time per verification
- [ ] >70% code coverage
- [ ] All tests passing
- [ ] API endpoint working

### **Nice to Have**:
- [ ] >85% accuracy
- [ ] <3s response time
- [ ] >80% code coverage
- [ ] Detailed explanations
- [ ] Structured logging

---

## 🚫 Explicitly Out of Scope

The following are NOT in this POC:
- ❌ NLP-based claim extraction (use simple parsing)
- ❌ Dynamic source discovery (hardcode 2-3 sources)
- ❌ Machine learning (use fixed trust scores)
- ❌ Database persistence (in-memory only)
- ❌ Caching (Redis/etc)
- ❌ Authentication/authorization
- ❌ Rate limiting
- ❌ Real-time TV monitoring
- ❌ Browser extension
- ❌ Mobile app
- ❌ Human expert review
- ❌ Production deployment
- ❌ High availability
- ❌ Scalability optimizations

---

## 📅 Implementation Timeline

### **Day 1-2: Project Setup**
- [ ] Create Rust project (`cargo new truth-algorithm-poc`)
- [ ] Add dependencies (axum, tokio, serde, reqwest)
- [ ] Define data models
- [ ] Write basic unit tests for models

### **Day 3-4: Source Search**
- [ ] Implement hardcoded source definitions
- [ ] Build HTTP search functionality
- [ ] Test with real URLs (manual verification)
- [ ] Handle HTTP errors gracefully

### **Day 5-6: Consensus & Explanation**
- [ ] Implement simple majority consensus
- [ ] Calculate confidence scores
- [ ] Generate template-based explanations
- [ ] Unit tests for consensus logic

### **Day 7: API Integration**
- [ ] Build Axum API server
- [ ] Create `/api/verify` endpoint
- [ ] Integration tests
- [ ] Manual testing with curl

### **Day 8-9: Testing & Refinement**
- [ ] Create 20-claim test dataset
- [ ] Run accuracy evaluation
- [ ] Fix bugs and edge cases
- [ ] Improve explanations

### **Day 10-11: Documentation**
- [ ] API documentation
- [ ] README with examples
- [ ] Architecture diagram
- [ ] Lessons learned

### **Day 12-14: Demo & Review**
- [ ] Prepare demo
- [ ] Evaluate results
- [ ] Document what worked/didn't
- [ ] Plan next iteration

---

## 🔑 Key Decisions

### **Technology Stack**:
- **Language**: Rust (performance, safety)
- **Web Framework**: Axum (async, ergonomic)
- **HTTP Client**: reqwest (async HTTP)
- **Serialization**: serde (JSON)
- **Testing**: Built-in Rust testing

### **Simplifications for POC**:
1. **No NLP**: Use simple regex/string matching
2. **Hardcoded Sources**: 2-3 predefined URLs
3. **Fixed Trust Scores**: No learning/updating
4. **Simple Consensus**: Majority voting only
5. **No Persistence**: In-memory only

### **What We'll Learn**:
- Can simple keyword matching work?
- What's minimum accuracy achievable?
- What's the bottleneck (search, parsing, consensus)?
- What features are most valuable?
- Is this approach viable?

---

## ✅ Ready to Implement?

**Before proceeding to EXECUTION mode, confirm**:
1. ✅ Architecture is realistic for 1-2 weeks
2. ✅ Verification plan is clear and executable
3. ✅ Success criteria are measurable
4. ✅ Out-of-scope items are documented
5. ✅ User approves this plan

**If all ✅, proceed to EXECUTION mode and start coding.**

---

## 📞 Questions for User

Before starting implementation:

1. **Scope**: Does this POC scope feel realistic for 1-2 weeks?
2. **Sources**: Should we focus on Rust/Python/Node.js, or different languages?
3. **Testing**: Any specific test cases you want included?
4. **Success**: Is >80% accuracy a good target, or should we aim higher/lower?
5. **Next Steps**: After POC, what's the priority (more sources, better NLP, or different claim types)?

**Waiting for user approval before proceeding to implementation.** 🚀
