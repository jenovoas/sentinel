# 🔥 Sentinel - Elite Engineering Assessment

**Fast-paced technical evaluation for polyglot senior engineers**

> **Philosophy**: We move fast. We don't have time to train. You either know your stuff or you don't.

---

## 🎯 What We're Looking For

### Must-Have Skills (Non-Negotiable)

**Languages** (must know at least 4):
- ✅ Python (FastAPI, async/await, type hints)
- ✅ TypeScript/JavaScript (React, Next.js, Node.js)
- ✅ Bash/Shell scripting
- ✅ SQL (PostgreSQL, complex queries, optimization)
- ✅ Rust (bonus - we're migrating critical components)
- ✅ Go (bonus - for performance-critical services)

**Technologies** (must know most):
- ✅ Docker & Docker Compose (production-grade)
- ✅ Linux (Ubuntu/Debian, system administration)
- ✅ Git (advanced workflows, rebasing, cherry-picking)
- ✅ PostgreSQL (HA, replication, tuning)
- ✅ Redis (caching, pub/sub, Sentinel)
- ✅ Prometheus & Grafana (metrics, dashboards, alerts)
- ✅ CI/CD (GitHub Actions, GitLab CI, or similar)

**Architecture**:
- ✅ Microservices & distributed systems
- ✅ High availability & disaster recovery
- ✅ Observability (metrics, logs, traces)
- ✅ Security best practices
- ✅ Cloud infrastructure (AWS/GCP/Azure)

### Personality Traits

- 🚀 **Self-starter**: Figures things out independently
- ⚡ **Fast learner**: Picks up new tech in days, not months
- 🔍 **Detail-oriented**: Catches bugs before they ship
- 💬 **Clear communicator**: Writes docs, asks smart questions
- 🎯 **Results-driven**: Ships features, not excuses

---

## ⚡ The 4-Hour Gauntlet

**Total Time**: 4 hours (strict)  
**Format**: Timed, autonomous, no hand-holding  
**Passing Score**: 85%+ (we only hire the best)

### Challenge 1: Speed Installation (30 min)

```
Install Sentinel. Make it work. Screenshot the dashboard.

Time: 30 minutes MAX
Repo: github.com/jaime-novoa/sentinel
Docs: INSTALLATION_GUIDE.md

If you can't do this in 30 minutes, stop here. You're not ready.
```

**Auto-Fail if**:
- Takes more than 30 minutes
- Asks for help
- Can't troubleshoot basic Docker issues

---

### Challenge 2: Multi-Language Debugging (60 min)

```
We've introduced 10 bugs across the stack:
- 3 in Python (backend)
- 3 in TypeScript (frontend)
- 2 in Docker configs
- 1 in PostgreSQL schema
- 1 in Nginx config

Find and fix ALL 10 bugs. Document your process.

Time: 60 minutes
Branch: assessment-bugs-v1

Submit: Git diff + bug report
```

**Bugs Include**:
1. Python: Race condition in async code
2. Python: SQL injection vulnerability
3. Python: Memory leak in Celery worker
4. TypeScript: React hook dependency issue
5. TypeScript: Type error in API client
6. TypeScript: Performance issue (unnecessary re-renders)
7. Docker: Volume mount permission issue
8. Docker: Health check timeout too short
9. PostgreSQL: Missing index causing slow queries
10. Nginx: CORS misconfiguration

**Scoring**:
- 10/10 bugs: 100%
- 8-9/10 bugs: 80%
- 6-7/10 bugs: 60% (borderline)
- < 6/10 bugs: FAIL

---

### Challenge 3: Polyglot Feature Implementation (90 min)

```
Implement a new feature: "Real-time Anomaly Detection"

Requirements:
- Python backend: Anomaly detection algorithm (statistical or ML-based)
- TypeScript frontend: Real-time dashboard with charts
- PostgreSQL: Efficient schema for time-series data
- Redis: Caching layer for recent anomalies
- WebSocket: Real-time updates to frontend
- Tests: Unit + integration tests
- Docs: API documentation + usage guide

Time: 90 minutes
Submit: Working PR with all components
```

**Evaluation**:
- ✅ **Backend** (30%): Algorithm works, performant, tested
- ✅ **Frontend** (25%): Real-time updates, good UX, responsive
- ✅ **Database** (15%): Optimized schema, proper indexes
- ✅ **Integration** (20%): All components work together
- ✅ **Code Quality** (10%): Clean, maintainable, documented

**Auto-Fail if**:
- Feature doesn't work end-to-end
- No tests
- Code quality is poor
- Takes more than 90 minutes

---

### Challenge 4: Architecture Design (60 min)

```
Design a production deployment for:
- 1M daily active users
- 100TB logs/day
- 99.99% uptime SLA
- Multi-region (US, EU, APAC)
- Budget: $50K/month

Deliverables:
1. Architecture diagram (use draw.io, Excalidraw, or ASCII)
2. Infrastructure as Code (Terraform or Pulumi)
3. Cost breakdown
4. Scaling strategy
5. Disaster recovery plan

Time: 60 minutes
```

**Must Include**:
- Load balancing strategy
- Database replication topology
- Caching architecture
- Monitoring & alerting
- Security (WAF, DDoS protection, encryption)
- CI/CD pipeline
- Backup & recovery

**Scoring**:
- Architecture is scalable, realistic, and cost-effective: 100%
- Good but has some gaps: 70-90%
- Unrealistic or won't scale: FAIL

---

### Challenge 5: AI Proficiency & Prompt Engineering (30 min)

```
We work heavily with AI. You MUST know how to use it effectively.

This is NOT about using ChatGPT to write code for you.
This is about REFINING CONTEXT to get PRECISE answers.

Time: 30 minutes
```

**Part A: Prompt Refinement (10 min)**

```
Bad Prompt (Candidate receives this):
"How do I make my API faster?"

Your Task:
Refine this prompt to get a USEFUL answer from an AI.
Include:
- Specific context (tech stack, current performance, bottlenecks)
- Measurable goals
- Constraints
- Expected output format
```

**Example of Good Refinement**:
```
Context:
- FastAPI backend with PostgreSQL
- Current: 500ms P95 latency
- Bottleneck: Database queries (identified via profiling)
- Goal: Reduce to <100ms P95
- Constraints: Can't change database schema

Question:
"What are 5 specific techniques to reduce PostgreSQL query latency
in a FastAPI app, WITHOUT changing the schema? Rank by impact
(high/medium/low) and implementation difficulty (easy/medium/hard).
Provide code examples for top 2 techniques."
```

**Scoring Part A**:
- ✅ Includes specific context: 30%
- ✅ Defines measurable goal: 20%
- ✅ States constraints: 20%
- ✅ Requests structured output: 20%
- ✅ Asks for prioritization: 10%

---

**Part B: AI-Assisted Debugging (10 min)**

```
Error Message:
"RuntimeError: Event loop is closed"

Your Task:
Craft a prompt to diagnose this error. Include:
1. Full error context (stack trace, code snippet, environment)
2. What you've already tried
3. Specific question
```

**Example of Good Prompt**:
```
I'm getting "RuntimeError: Event loop is closed" in my FastAPI app.

Context:
- FastAPI 0.104.1, Python 3.11
- Using asyncio with Celery
- Error occurs after Celery task completes
- Stack trace: [paste full trace]
- Code snippet: [paste relevant code]

What I've tried:
- Checked event loop is running: Yes
- Verified async/await syntax: Correct
- Googled error: Found generic solutions, none worked

Question:
What are the 3 most common causes of this error in FastAPI + Celery
setups? For each cause, provide:
1. How to verify it's the issue
2. Exact code fix
3. Why it happens
```

**Scoring Part B**:
- ✅ Provides full context: 40%
- ✅ Lists what was tried: 30%
- ✅ Asks specific, answerable question: 30%

---

**Part C: Architecture Consultation (10 min)**

```
Scenario:
You need to design a caching layer for Sentinel.

Your Task:
Craft a prompt to get architectural guidance from AI.
```

**Example of Good Prompt**:
```
I need to design a caching layer for a multi-tenant observability platform.

Requirements:
- 1000+ organizations
- 10K requests/second
- Cache hit rate target: >80%
- Data: Metrics (time-series), logs (text), alerts (JSON)
- TTL: Metrics (5 min), Logs (1 min), Alerts (30 sec)
- Budget: $500/month

Current stack:
- FastAPI backend
- PostgreSQL (primary data)
- Redis available

Constraints:
- Must be self-hosted (no cloud services)
- Must support multi-tenancy (data isolation)
- Must handle cache invalidation on updates

Question:
Compare 3 caching strategies for this use case:
1. Redis with key namespacing
2. In-memory cache (Python dict) per worker
3. Hybrid (Redis + in-memory)

For each strategy, provide:
- Pros/cons
- Expected hit rate
- Memory usage estimate
- Code example (Python)
- When to use

Recommend the best option and explain why.
```

**Scoring Part C**:
- ✅ Clear requirements: 25%
- ✅ Specific constraints: 25%
- ✅ Requests comparison: 20%
- ✅ Asks for recommendation: 15%
- ✅ Requests code examples: 15%

---

**Overall Challenge 5 Scoring**:
- Part A (Prompt Refinement): 33%
- Part B (Debugging): 33%
- Part C (Architecture): 34%

**Pass Threshold**: 70%+

**Auto-Fail if**:
- Prompts are vague ("How do I fix this?")
- No context provided
- Doesn't refine based on AI's limitations
- Expects AI to read their mind

**Instant Hire Signal**:
- Prompts are better than the examples
- Includes edge cases and failure modes
- Asks for trade-offs and alternatives
- Structures output for easy implementation

---

### Challenge 6: AI-Generated Code Review (30 min)

```
CRITICAL: This challenge filters people who use AI as a crutch.

You will receive code "generated by AI" that has subtle bugs.
Your job: Find them WITHOUT using AI.

This tests if you can READ and THINK critically.

Time: 30 minutes
Tools allowed: Your brain, documentation, Google
Tools NOT allowed: ChatGPT, Claude, Copilot, any AI
```

**The Code** (candidate receives this):

```python
# AI-generated code for "Create user with validation"

async def create_user(
    email: str,
    password: str,
    organization_id: int,
    db: AsyncSession
) -> User:
    """
    Create a new user with validation.
    """
    # Validate email format
    if "@" not in email:
        raise ValueError("Invalid email")
    
    # Check if user exists
    existing = await db.execute(
        select(User).where(User.email == email)
    )
    if existing:
        raise ValueError("User already exists")
    
    # Hash password
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    
    # Create user
    user = User(
        email=email,
        password=hashed,
        organization_id=organization_id
    )
    db.add(user)
    await db.commit()
    
    return user
```

**Your Task**:
1. Find ALL bugs (there are 5)
2. Explain WHY each is a bug
3. Provide the fix
4. Explain how you found it (your thought process)

**The 5 Bugs** (for scoring):

1. **Bug 1: Email validation is too weak**
   - `"@" in email` accepts "@" or "user@"
   - Should use regex or email validator
   - Fix: `EmailStr` from Pydantic or proper regex

2. **Bug 2: `existing` check is wrong**
   - `existing` is a Result object, not User
   - Should be `existing.scalar_one_or_none()`
   - Will always be truthy (even if no user found)

3. **Bug 3: Password hashing is blocking**
   - `bcrypt.hashpw()` is synchronous (blocks event loop)
   - Should use `await run_in_executor()` or async bcrypt
   - Kills performance under load

4. **Bug 4: Missing `await` on commit**
   - `await db.commit()` is correct, but missing `await db.refresh(user)`
   - User object won't have `id` populated
   - Will cause errors if you try to use `user.id`

5. **Bug 5: No error handling**
   - If `db.commit()` fails, user is added but not committed
   - Should wrap in try/except and rollback on error
   - Can leave database in inconsistent state

**Scoring**:
- 5/5 bugs found: 100%
- 4/5 bugs found: 80%
- 3/5 bugs found: 60%
- <3/5 bugs found: FAIL

**Bonus Points** (+20%):
- Finds additional bugs we didn't plant
- Suggests architectural improvements
- Writes unit test that would catch these bugs

**Auto-Fail if**:
- Uses AI to find bugs (we can tell)
- Can't explain WHY it's a bug
- Suggests fixes that don't work
- Takes more than 30 minutes

**Instant Hire Signal**:
- Finds all 5 bugs in <15 minutes
- Explains bugs clearly and concisely
- Suggests better overall approach
- Writes test cases

---

## 🎖️ Scoring & Decision

### Overall Score Calculation

| Challenge | Weight | Time | Pass Threshold |
|-----------|--------|------|----------------|
| 1. Installation | 7% | 30 min | Must pass |
| 2. Debugging | 20% | 60 min | 60%+ |
| 3. Feature | 30% | 90 min | 70%+ |
| 4. Architecture | 15% | 60 min | 70%+ |
| 5. AI Proficiency | 13% | 30 min | 70%+ |
| 6. Code Review | 15% | 30 min | 60%+ |

**Total Time**: 5 hours (300 minutes)

### Hiring Decision

| Overall Score | Decision | Level |
|---------------|----------|-------|
| **90-100%** | **STRONG HIRE** | Senior/Lead Engineer |
| **85-89%** | **HIRE** | Senior Engineer |
| **75-84%** | **MAYBE** | Mid-Senior (needs interview) |
| **< 75%** | **NO HIRE** | Not ready for our pace |

---

## 🚨 Instant Rejection Criteria

**DO NOT HIRE** if candidate:

- ❌ **Can't install Sentinel in 30 min** (basic competence test)
- ❌ **Finds less than 6/10 bugs** (debugging skills too weak)
- ❌ **Can't code in multiple languages** (we need polyglots)
- ❌ **Asks for step-by-step help** (not autonomous enough)
- ❌ **Misses deadlines** (we move fast, no excuses)
- ❌ **Poor code quality** (we ship production code, not prototypes)
- ❌ **Doesn't read documentation** (wastes everyone's time)
- ❌ **Gives up when stuck** (we need problem solvers)
- ❌ **Can't use AI effectively** (wastes time with vague prompts)
- ❌ **Doesn't refine AI context** (gets generic, useless answers)
- ❌ **Blindly trusts AI code** (doesn't read or understand)
- ❌ **Can't review code critically** (misses obvious bugs)

---

## ✅ Instant Hire Signals

**HIRE IMMEDIATELY** if candidate:

- ✅ **Finishes all 4 challenges in < 3 hours** (exceptional speed)
- ✅ **Finds bugs we didn't plant** (attention to detail)
- ✅ **Suggests architecture improvements** (thinks beyond the task)
- ✅ **Writes production-quality code** (clean, tested, documented)
- ✅ **Knows 5+ programming languages** (true polyglot)
- ✅ **Has contributed to major open source projects** (proven track record)
- ✅ **Asks insightful questions** (deep technical understanding)
- ✅ **Masters AI prompt engineering** (gets precise answers in 1-2 tries)
- ✅ **Refines context like a pro** (AI becomes 10x more useful)
- ✅ **Reviews AI code critically** (catches bugs AI misses)
- ✅ **Uses AI as tool, not crutch** (can code without it)

---

## 📧 Assessment Email (No Fluff)

```
Subject: Sentinel Engineering Assessment

Hi [Name],

We're looking for elite engineers who can move fast and ship quality code.

Assessment: 4 challenges, 4 hours total, autonomous work.

Skills tested:
- Python, TypeScript, SQL, Bash, Docker
- Debugging, architecture, system design
- Speed, autonomy, code quality

Pass rate: ~15% (we only hire the best)

Interested? Reply and we'll send you the challenges.

- Sentinel Team
```

---

## 🎯 Quick Candidate Filter (5-Minute Phone Screen)

Before sending the assessment, ask these 5 questions:

### 1. Languages
**Q**: "What programming languages do you know well enough to ship production code today?"

**Red Flag**: Less than 3 languages  
**Green Flag**: 5+ languages, includes Python + TypeScript

### 2. Docker
**Q**: "Explain the difference between `docker-compose up` and `docker-compose up -d`. When would you use each?"

**Red Flag**: Doesn't know or gives vague answer  
**Green Flag**: Clear explanation with use cases

### 3. Debugging
**Q**: "A service is crashing in production. Walk me through your debugging process."

**Red Flag**: "I'd restart it" or "I'd ask someone"  
**Green Flag**: Systematic approach (logs, metrics, traces, reproduce)

### 4. Speed
**Q**: "How long would it take you to set up a new FastAPI project with PostgreSQL, Redis, and Docker?"

**Red Flag**: "A few days" or "I'd need to look it up"  
**Green Flag**: "30 minutes to an hour"

### 5. Learning
**Q**: "Tell me about a technology you learned in the last month. How did you learn it?"

**Red Flag**: "Nothing new" or "I took a course"  
**Green Flag**: "Built a project with X, read docs, shipped in a week"

### 6. AI Usage (CRITICAL)
**Q**: "How do you use AI tools (ChatGPT, Claude, Copilot) in your daily work? Give me a specific example of a complex problem you solved with AI."

**Red Flag**: 
- "I don't use AI" (living in the past)
- "I just ask it to write code" (doesn't understand AI limitations)
- "I copy-paste the first answer" (no critical thinking)
- Vague answer with no specifics

**Green Flag**:
- "I use AI for X, but I refine the prompt 3-4 times to get precise answers"
- "I give AI full context: tech stack, constraints, expected output"
- "I verify AI's answers, don't trust blindly"
- Specific example with before/after prompts

**Follow-up**: "Show me a prompt you used recently that got you a great answer."

**Red Flag**: Can't provide one or shows a vague prompt  
**Green Flag**: Shows a well-structured prompt with context, constraints, and specific ask

**Decision**: If they fail 2+ questions (including AI), don't send the assessment. Save everyone's time.

---

## 📊 Candidate Tracking Template

```
Name: [Name]
Date: [Date]
Source: [LinkedIn/Referral/etc]

Phone Screen (5 min):
- Languages: [Score/5]
- Docker: [Score/5]
- Debugging: [Score/5]
- Speed: [Score/5]
- Learning: [Score/5]
- Total: [Score/25]
- Decision: [Send Assessment / Reject]

Assessment (4 hours):
- Challenge 1 (Installation): [Score%] - [Time]
- Challenge 2 (Debugging): [Score%] - [Time]
- Challenge 3 (Feature): [Score%] - [Time]
- Challenge 4 (Architecture): [Score%] - [Time]
- Overall: [Score%]
- Decision: [Hire / No Hire]

Notes:
[Observations, red flags, green flags]
```

---

## 🎓 Calibration: What "Good" Looks Like

### Example: Strong Candidate

**Profile**:
- 5+ years experience
- Knows: Python, TypeScript, Rust, Go, SQL, Bash
- Has built distributed systems
- Open source contributor
- Fast learner, autonomous

**Assessment Results**:
- Challenge 1: 15 minutes (perfect)
- Challenge 2: 45 minutes, found 9/10 bugs
- Challenge 3: 75 minutes, fully working feature
- Challenge 4: 50 minutes, excellent architecture
- **Overall**: 92% → **STRONG HIRE**

### Example: Weak Candidate (Your Current Applicants)

**Profile**:
- 2-3 years experience
- Knows: Python (basic), JavaScript (basic)
- Has used Docker (following tutorials)
- Needs guidance, asks many questions

**Assessment Results**:
- Challenge 1: 180 minutes with help (FAIL)
- Challenge 2: Not attempted (gave up)
- Challenge 3: Not attempted
- Challenge 4: Not attempted
- **Overall**: 5% → **REJECT**

---

## 💡 Pro Tips for You

### 1. Be Ruthless
Don't lower the bar. One weak hire slows down the entire team.

### 2. Trust the Process
If they can't pass the assessment, they can't do the job. No exceptions.

### 3. Move Fast
- Phone screen: 5 minutes
- Assessment: 4 hours
- Decision: Same day
- Total time from application to offer: 1-2 days

### 4. Pay Well
Top engineers have options. Offer competitive compensation:
- Senior: $120K-180K (depending on location)
- Lead: $180K-250K
- Equity: 0.5%-2%

### 5. Sell the Vision
Elite engineers want to work on hard problems. Sell:
- Cutting-edge tech (Rust, eBPF, AI)
- Real impact (protecting infrastructure)
- Fast-paced environment (ship daily)
- Ownership (you build it, you own it)

---

## 🚀 Next Steps

1. **Use this assessment** for all engineering candidates
2. **Track results** to calibrate difficulty
3. **Iterate** based on hire quality
4. **Build a team** of elite engineers who move at your speed

---

**Remember**: It's better to have **no hire** than a **bad hire**.

**Good luck building your A-team!** 🔥

---

**Last Updated**: December 2024  
**Pass Rate**: ~15% (by design)  
**Average Hire Quality**: Senior+ only
