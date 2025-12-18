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
Repo: github.com/jenovoas/sentinel
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

## 🎖️ Scoring & Decision

### Overall Score Calculation

| Challenge | Weight | Time | Pass Threshold |
|-----------|--------|------|----------------|
| 1. Installation | 10% | 30 min | Must pass |
| 2. Debugging | 30% | 60 min | 60%+ |
| 3. Feature | 40% | 90 min | 70%+ |
| 4. Architecture | 20% | 60 min | 70%+ |

**Total Time**: 4 hours (240 minutes)

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

**Decision**: If they fail 2+ questions, don't send the assessment. Save everyone's time.

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
