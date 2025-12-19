# 🎯 Truth Algorithm POC - Scope Definition & Review
## *Validating the Plan Before Implementation*

**Created**: 2025-12-17  
**Purpose**: Define a realistic, achievable POC that proves core concepts  
**Timeline**: 1-2 weeks maximum

---

## 📋 Step 1: Problem Definition Review

### **Question 1: What EXACTLY are we solving?**

From the complete plan, the problem is:
> "Combat fake news and mass manipulation through TV, social media, and digital media"

**But for POC, we need to be MORE SPECIFIC:**

#### **POC Problem Statement (Narrowed)**:
> "Verify simple factual claims about technology releases and versions that can be checked against official documentation"

**Why this scope?**
- ✅ **Verifiable**: Official sources exist (release notes, docs)
- ✅ **Testable**: Clear ground truth (version X exists or doesn't)
- ✅ **Measurable**: Binary true/false with high confidence
- ✅ **Achievable**: No need for complex NLP or opinion analysis

**Examples of POC-scope claims**:
- ✅ "Rust 1.75 introduced async traits" (verifiable)
- ✅ "Python 3.12 was released in October 2023" (verifiable)
- ✅ "Node.js 20 includes native test runner" (verifiable)
- ❌ "Most developers prefer Rust" (opinion, not POC scope)
- ❌ "Biden won the 2020 election" (political, not POC scope)
- ❌ "Vaccines cause autism" (medical, too complex for POC)

---

## 📥 Step 2: Input/Output Contract

### **INPUT**:
```rust
struct VerificationRequest {
    claim: String,           // The claim to verify
    context: Option<String>, // Optional context (not used in POC)
}
```

**Example**:
```json
{
  "claim": "Rust 1.75 introduced async traits"
}
```

### **OUTPUT**:
```rust
struct VerificationResponse {
    claim: String,                    // Original claim
    verdict: Verdict,                 // true / false / unverifiable
    confidence: f32,                  // 0.0 - 1.0
    explanation: String,              // Human-readable explanation
    sources: Vec<Source>,             // Sources used
    timestamp: DateTime<Utc>,         // When verified
}

enum Verdict {
    True,          // Claim is verified as true
    False,         // Claim is verified as false
    Unverifiable,  // Cannot verify (no sources found)
}

struct Source {
    url: String,
    title: String,
    excerpt: String,
    trust_score: f32,
}
```

**Example**:
```json
{
  "claim": "Rust 1.75 introduced async traits",
  "verdict": "True",
  "confidence": 0.95,
  "explanation": "Verified by 3 official sources. Rust 1.75.0 was released on December 28, 2023, and included stabilization of async fn in traits (RFC 3185).",
  "sources": [
    {
      "url": "https://blog.rust-lang.org/2023/12/28/Rust-1.75.0.html",
      "title": "Announcing Rust 1.75.0",
      "excerpt": "async fn in traits is now stable",
      "trust_score": 0.95
    }
  ],
  "timestamp": "2025-12-17T21:22:30Z"
}
```

---

## 🏗️ Step 3: Architecture Review (5 Layers → POC Reality)

### **Full Vision (5 Layers)**:
1. Input Guardian (claim extraction, adversarial detection)
2. Evidence Guardian (multi-source search)
3. Trust Guardian (source reputation)
4. Consensus Guardian (weighted algorithm)
5. Human Expert (manual review)

### **POC Reality (Simplified)**:

```
┌─────────────────────────────────────────┐
│ POC LAYER 1: Claim Parser               │
│ - Simple string input (no NLP yet)      │
│ - Basic validation (not empty, etc.)    │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ POC LAYER 2: Source Search               │
│ - 2-3 hardcoded "golden" sources        │
│ - Simple keyword matching                │
│ - No complex search algorithms yet      │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ POC LAYER 3: Simple Consensus            │
│ - If 2+ sources confirm → True          │
│ - If 2+ sources contradict → False      │
│ - Otherwise → Unverifiable              │
│ - Fixed trust scores (no learning yet)  │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ POC OUTPUT: Verdict + Explanation        │
│ - Simple verdict enum                    │
│ - Template-based explanation             │
│ - Source citations                       │
└─────────────────────────────────────────┘
```

**What's NOT in POC**:
- ❌ NLP claim extraction (just parse simple strings)
- ❌ Adversarial input detection (trust input for now)
- ❌ Dynamic source discovery (hardcode 2-3 sources)
- ❌ Machine learning trust scoring (use fixed scores)
- ❌ Human expert review (automated only)
- ❌ Real-time TV monitoring (manual input only)
- ❌ Browser extension (API only)
- ❌ Mobile app (API only)

**What IS in POC**:
- ✅ Simple claim verification pipeline
- ✅ Multi-source checking (2-3 sources)
- ✅ Basic consensus algorithm
- ✅ Confidence scoring
- ✅ Explanation generation
- ✅ REST API endpoint
- ✅ Logging of all decisions
- ✅ Basic testing (unit + integration)

---

## 🎯 Step 4: POC Scope Definition

### **Claim Types (1-2 types)**:

#### **Type 1: Software Version Claims**
- Pattern: "[Software] [version] [action] [feature/date]"
- Examples:
  - "Rust 1.75 introduced async traits"
  - "Python 3.12 was released in October 2023"
  - "Node.js 20 includes native test runner"

**Why this type?**
- Clear ground truth (official release notes)
- Easy to verify (check version in official docs)
- Measurable success (binary true/false)

#### **Type 2: (Optional) Simple Date Claims**
- Pattern: "[Event] happened on [date]"
- Examples:
  - "Rust 1.75 was released on December 28, 2023"
  - "Python 3.12 was released on October 2, 2023"

**Why this type?**
- Even simpler than Type 1
- Perfect for testing date extraction
- Clear verification (check official announcements)

### **Golden Sources (2-3 sources)**:

#### **Source 1: Official Language Blogs**
- Rust: `https://blog.rust-lang.org/`
- Python: `https://www.python.org/downloads/`
- Node.js: `https://nodejs.org/en/blog/`

**Trust Score**: 0.95 (highest)

#### **Source 2: GitHub Release Notes**
- Rust: `https://github.com/rust-lang/rust/blob/master/RELEASES.md`
- Python: `https://github.com/python/cpython/blob/main/Misc/NEWS.d/`
- Node.js: `https://github.com/nodejs/node/blob/main/CHANGELOG.md`

**Trust Score**: 0.90

#### **Source 3: (Optional) Wikipedia**
- General tech history
- Good for dates and basic facts

**Trust Score**: 0.70

### **Verdict System**:

```rust
enum Verdict {
    True,          // 2+ sources confirm
    False,         // 2+ sources contradict
    Unverifiable,  // <2 sources found or conflicting
}
```

**Confidence Calculation**:
```rust
fn calculate_confidence(confirming: usize, contradicting: usize, total: usize) -> f32 {
    if total == 0 {
        return 0.0;
    }
    
    let agreement = confirming.max(contradicting) as f32 / total as f32;
    
    // Bonus for multiple sources
    let source_bonus = (total as f32 / 3.0).min(1.0) * 0.1;
    
    (agreement + source_bonus).min(1.0)
}
```

---

## 📐 Step 5: POC Architecture

### **Components**:

```
src/
├── main.rs                 # API server (Axum)
├── lib.rs                  # Library exports
├── verification/
│   ├── mod.rs              # Verification orchestrator
│   ├── parser.rs           # Simple claim parsing
│   ├── sources.rs          # Source definitions & search
│   ├── consensus.rs        # Consensus algorithm
│   └── explanation.rs      # Explanation generation
├── models/
│   ├── mod.rs
│   ├── claim.rs            # Claim struct
│   ├── verdict.rs          # Verdict enum
│   └── source.rs           # Source struct
└── api/
    ├── mod.rs
    └── routes.rs           # API endpoints

tests/
├── unit/
│   ├── parser_tests.rs
│   ├── consensus_tests.rs
│   └── explanation_tests.rs
└── integration/
    └── api_tests.rs
```

### **Data Flow**:

```
POST /api/verify
    ↓
[1] Parse claim (extract keywords)
    ↓
[2] Search golden sources (keyword match)
    ↓
[3] Extract evidence (title, excerpt, URL)
    ↓
[4] Apply consensus algorithm
    ↓
[5] Calculate confidence
    ↓
[6] Generate explanation
    ↓
[7] Log decision
    ↓
Return VerificationResponse
```

---

## ✅ Step 6: Success Criteria for POC

### **Functional Requirements**:
- [ ] Can verify 10+ test claims with >80% accuracy
- [ ] Returns verdict in <5 seconds (no optimization yet)
- [ ] Provides human-readable explanation
- [ ] Cites sources with URLs
- [ ] Logs all verification attempts

### **Technical Requirements**:
- [ ] REST API with `/api/verify` endpoint
- [ ] Unit tests for core functions (>70% coverage)
- [ ] Integration test for full pipeline
- [ ] Basic error handling (invalid input, source unavailable)
- [ ] Structured logging (JSON format)

### **Quality Requirements**:
- [ ] Code compiles without warnings
- [ ] All tests pass
- [ ] Documentation for API endpoint
- [ ] Example requests/responses

### **Non-Requirements (Out of Scope)**:
- ❌ Real-time performance (<2s)
- ❌ High availability / scaling
- ❌ Advanced NLP
- ❌ Machine learning
- ❌ User authentication
- ❌ Rate limiting
- ❌ Caching
- ❌ Database persistence

---

## 🗓️ Step 7: POC Timeline (1-2 Weeks)

### **Week 1: Core Implementation**

#### **Day 1-2: Setup & Models**
- [ ] Create Rust project structure
- [ ] Define data models (Claim, Verdict, Source)
- [ ] Write basic unit tests for models
- [ ] Set up logging

#### **Day 3-4: Source Search**
- [ ] Implement source definitions
- [ ] Build simple keyword search
- [ ] Test with real URLs (manual verification)
- [ ] Handle HTTP errors gracefully

#### **Day 5-6: Consensus Algorithm**
- [ ] Implement consensus logic
- [ ] Calculate confidence scores
- [ ] Generate explanations
- [ ] Unit tests for consensus

#### **Day 7: API & Integration**
- [ ] Build Axum API server
- [ ] Create `/api/verify` endpoint
- [ ] Integration test for full pipeline
- [ ] Manual testing with curl

### **Week 2: Testing & Refinement**

#### **Day 8-9: Testing**
- [ ] Create test dataset (20+ claims)
- [ ] Run accuracy evaluation
- [ ] Fix bugs and edge cases
- [ ] Improve explanations

#### **Day 10-11: Documentation**
- [ ] API documentation
- [ ] README with examples
- [ ] Architecture diagram
- [ ] Lessons learned document

#### **Day 12-14: Demo & Next Steps**
- [ ] Prepare demo
- [ ] Evaluate results
- [ ] Document what worked / didn't work
- [ ] Plan next iteration

---

## 🔬 Step 8: Testing Strategy for POC

### **Unit Tests** (50% of effort):
```rust
#[test]
fn test_parse_simple_claim() {
    let claim = "Rust 1.75 introduced async traits";
    let parsed = parse_claim(claim);
    
    assert_eq!(parsed.software, "Rust");
    assert_eq!(parsed.version, "1.75");
    assert_eq!(parsed.feature, "async traits");
}

#[test]
fn test_consensus_with_agreement() {
    let evidence = vec![
        Evidence { confirms: true, source: "rust-blog", trust: 0.95 },
        Evidence { confirms: true, source: "github", trust: 0.90 },
    ];
    
    let verdict = determine_verdict(&evidence);
    assert_eq!(verdict.status, Verdict::True);
    assert!(verdict.confidence >= 0.8);
}
```

### **Integration Tests** (30% of effort):
```rust
#[tokio::test]
async fn test_full_verification_pipeline() {
    let claim = "Rust 1.75 introduced async traits";
    let result = verify_claim(claim).await.unwrap();
    
    assert_eq!(result.verdict, Verdict::True);
    assert!(result.confidence >= 0.8);
    assert!(result.sources.len() >= 2);
    assert!(result.explanation.contains("Rust 1.75"));
}
```

### **Manual Tests** (20% of effort):
```bash
# Test 1: Verify true claim
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"claim": "Rust 1.75 introduced async traits"}'

# Expected: verdict=True, confidence>0.8

# Test 2: Verify false claim
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"claim": "Python 4.0 was released in 2024"}'

# Expected: verdict=False, confidence>0.8

# Test 3: Unverifiable claim
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"claim": "FooLang 99.0 was released yesterday"}'

# Expected: verdict=Unverifiable, confidence<0.5
```

---

## 💡 Step 9: What We'll Learn from POC

### **Technical Learnings**:
- How accurate can simple keyword matching be?
- What's the minimum number of sources needed?
- How to handle source unavailability?
- What's a good confidence threshold?

### **Product Learnings**:
- Is the explanation quality good enough?
- Do users trust the verdict?
- What edge cases did we miss?
- What features are most valuable?

### **Process Learnings**:
- How long does verification take?
- What's the bottleneck (search, parsing, consensus)?
- How to improve accuracy?
- What to build next?

---

## 🚀 Step 10: After POC - Next Iteration

### **If POC Succeeds (>80% accuracy)**:

#### **Iteration 2 Goals**:
- Expand to 5-10 claim types
- Add 5-10 more sources
- Implement basic NLP (spaCy)
- Add caching layer (Redis)
- Improve to <2s response time
- Add database persistence

#### **Iteration 3 Goals**:
- Real-time TV monitoring (closed captions)
- Browser extension
- Advanced NLP (claim extraction)
- Machine learning trust scoring
- A/B testing framework

### **If POC Fails (<80% accuracy)**:

#### **Diagnose**:
- Is keyword matching too simple?
- Are sources insufficient?
- Is consensus algorithm flawed?
- Are test claims too hard?

#### **Pivot Options**:
- Focus on even simpler claims (just dates)
- Add more sources
- Improve parsing logic
- Narrow scope further

---

## 📊 Step 11: POC Metrics Dashboard

### **Track During POC**:

```markdown
## POC Metrics (Update Daily)

### Accuracy
- Test claims: 20
- Correct verdicts: 16
- Accuracy: 80%
- Target: >80% ✅

### Performance
- Average response time: 3.2s
- Target: <5s ✅

### Coverage
- Claim types covered: 1 (software versions)
- Sources integrated: 3 (Rust, Python, Node.js)
- Test coverage: 75%
- Target: >70% ✅

### Quality
- Explanation quality: 4/5 (manual review)
- Source citation: 100%
- Error handling: Basic (needs improvement)
```

---

## 🎯 Step 12: Decision Points

### **Before Starting Implementation**:

**Question 1**: Is the POC scope realistic for 1-2 weeks?
- [ ] Yes → Proceed
- [ ] No → Narrow further

**Question 2**: Do we have access to the golden sources?
- [ ] Yes → Proceed
- [ ] No → Find alternatives

**Question 3**: Is the success criteria clear?
- [ ] Yes → Proceed
- [ ] No → Refine criteria

### **After Week 1**:

**Question 4**: Are we on track for >80% accuracy?
- [ ] Yes → Continue to Week 2
- [ ] No → Diagnose and pivot

**Question 5**: Is the architecture sound?
- [ ] Yes → Continue
- [ ] No → Refactor

### **After Week 2**:

**Question 6**: Did we achieve >80% accuracy?
- [ ] Yes → Plan Iteration 2
- [ ] No → Analyze failures and pivot

**Question 7**: Is this worth continuing?
- [ ] Yes → Full roadmap
- [ ] No → Document learnings and archive

---

## 🔑 Key Principles for POC

1. **Keep It Simple**: No fancy algorithms yet
2. **Prove Core Concept**: Can we verify claims at all?
3. **Measure Everything**: Track accuracy, performance, quality
4. **Fail Fast**: If it doesn't work, pivot quickly
5. **Document Learnings**: Every failure teaches something
6. **No Premature Optimization**: Make it work, then make it fast

---

## ✅ Ready to Start?

**Before writing ANY code, confirm**:
1. ✅ Problem is well-defined (software version claims)
2. ✅ Input/output contract is clear
3. ✅ Architecture is realistic for POC
4. ✅ Success criteria are measurable
5. ✅ Timeline is achievable (1-2 weeks)
6. ✅ Testing strategy is defined

**If all ✅, then proceed to implementation.**

**If any ❌, refine this document first.**

---

## 📞 Next Steps

1. **Review this document** - Does the POC scope make sense?
2. **Validate assumptions** - Can we access the golden sources?
3. **Confirm timeline** - Is 1-2 weeks realistic?
4. **Get approval** - User signs off on scope
5. **Start implementation** - Create Rust project and begin

**Only after approval, move to EXECUTION mode.** 🚀
