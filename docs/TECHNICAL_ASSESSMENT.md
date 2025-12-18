# 🎯 Sentinel - Technical Assessment for Engineering Candidates

**Comprehensive evaluation framework for hiring engineers**

---

## 📋 Overview

This assessment evaluates candidates across multiple dimensions:
- **Technical Skills**: Docker, Linux, debugging, architecture
- **Problem-Solving**: Autonomy, resourcefulness, critical thinking
- **Communication**: Documentation reading, asking smart questions
- **Culture Fit**: Initiative, attention to detail, learning ability

---

## 🎓 Assessment Levels

### Level 1: Installation Challenge (Required - 1 hour)
**Filters**: Basic technical competence, ability to follow documentation

### Level 2: Debugging Challenge (Mid-Level - 2 hours)
**Filters**: Problem-solving, troubleshooting, system understanding

### Level 3: Architecture Challenge (Senior - 4 hours)
**Filters**: System design, scalability, best practices

### Level 4: Code Challenge (All Levels - 3 hours)
**Filters**: Coding skills, testing, code quality

---

## 🚀 Level 1: Installation Challenge

**Objective**: Install and run Sentinel successfully

**Time Limit**: 1 hour (strict)

**Instructions to Candidate**:

```
Welcome to Sentinel's technical assessment!

Your first task is to install and run Sentinel on your local machine.

Repository: https://github.com/jenovoas/sentinel
Documentation: See INSTALLATION_GUIDE.md (Linux) or INSTALLATION_GUIDE_WINDOWS.md (Windows)

Requirements:
1. Clone the repository
2. Install all dependencies
3. Start all services
4. Access the dashboard at http://localhost:3000
5. Take a screenshot showing:
   - Dashboard running
   - Terminal with `docker-compose ps` output
   - Your system info (OS, RAM, Docker version)

Time limit: 1 hour from now
Submit: Screenshot + brief description of any issues you encountered

Good luck!
```

### ✅ Passing Criteria

**PASS** if:
- ✅ Dashboard running within 1 hour
- ✅ All core services healthy (backend, frontend, postgres, redis)
- ✅ Screenshot shows correct setup
- ✅ Candidate worked autonomously (minimal questions)

**FAIL** if:
- ❌ Took more than 1 hour
- ❌ Services not running
- ❌ Asked for step-by-step guidance
- ❌ Couldn't troubleshoot basic errors

### 📊 Evaluation Rubric

| Criteria | Weight | Excellent (5) | Good (3) | Poor (1) |
|----------|--------|---------------|----------|----------|
| **Speed** | 30% | < 30 min | 30-60 min | > 60 min |
| **Autonomy** | 30% | Zero questions | 1-2 smart questions | Constant help needed |
| **Troubleshooting** | 20% | Solved all issues alone | Solved with hints | Couldn't solve |
| **Documentation** | 20% | Clear, detailed report | Basic report | No report |

**Minimum Score**: 3.0/5.0 to proceed to Level 2

---

## 🔧 Level 2: Debugging Challenge

**Objective**: Diagnose and fix intentional bugs in Sentinel

**Time Limit**: 2 hours

**Prerequisites**: Passed Level 1

**Setup**: We provide a broken version of Sentinel with 5 intentional bugs

### 🐛 Bugs Introduced

1. **Backend won't start** - Missing environment variable
2. **Database connection fails** - Wrong credentials in .env
3. **Frontend 404 error** - Nginx misconfiguration
4. **Prometheus not scraping** - Wrong port in config
5. **Redis connection timeout** - Service not started

### 📝 Instructions to Candidate

```
You've been given a Sentinel installation with several bugs.
Your task is to identify and fix all issues.

Repository: [broken-sentinel-branch]

Requirements:
1. Identify all bugs (there are 5)
2. Fix each bug
3. Document:
   - What was broken
   - How you found it
   - How you fixed it
   - Time spent on each bug

Submit:
- Fixed code (git diff or PR)
- Bug report document
- Working screenshot

Time limit: 2 hours
```

### ✅ Passing Criteria

**PASS** if:
- ✅ Found and fixed 4+ bugs
- ✅ Clear documentation of process
- ✅ Completed within 2 hours
- ✅ Used proper debugging techniques (logs, health checks, etc.)

**FAIL** if:
- ❌ Fixed less than 3 bugs
- ❌ Took more than 2 hours
- ❌ No documentation of process
- ❌ Random trial-and-error approach

### 📊 Evaluation Rubric

| Criteria | Weight | Excellent (5) | Good (3) | Poor (1) |
|----------|--------|---------------|----------|----------|
| **Bugs Found** | 40% | 5/5 bugs | 3-4/5 bugs | < 3/5 bugs |
| **Methodology** | 30% | Systematic debugging | Some structure | Random guessing |
| **Documentation** | 20% | Detailed, clear | Basic | Minimal/none |
| **Speed** | 10% | < 90 min | 90-120 min | > 120 min |

**Minimum Score**: 3.5/5.0 to proceed to Level 3

---

## 🏗️ Level 3: Architecture Challenge

**Objective**: Design a scalable, production-ready deployment

**Time Limit**: 4 hours

**Prerequisites**: Passed Level 2

### 📋 Scenario

```
Sentinel is being deployed to production for a client with:
- 100,000 daily active users
- 50 TB of logs per day
- 99.99% uptime SLA
- Multi-region deployment (US, EU, APAC)
- GDPR compliance required

Design the architecture for this deployment.
```

### 📝 Requirements

Candidate must provide:

1. **Architecture Diagram**
   - Infrastructure layout
   - Service topology
   - Data flow
   - Disaster recovery

2. **Technical Specification**
   - Hardware requirements
   - Scaling strategy
   - High availability setup
   - Backup and recovery

3. **Cost Analysis**
   - Infrastructure costs (AWS/GCP/Azure)
   - Estimated monthly spend
   - Cost optimization strategies

4. **Security Plan**
   - Authentication/Authorization
   - Data encryption
   - Network security
   - Compliance (GDPR, SOC2)

5. **Monitoring & Alerting**
   - Metrics to track
   - Alert thresholds
   - On-call procedures

### ✅ Passing Criteria

**PASS** if:
- ✅ Architecture is scalable and realistic
- ✅ Addresses all requirements
- ✅ Shows understanding of distributed systems
- ✅ Cost-effective solution
- ✅ Security and compliance considered

**FAIL** if:
- ❌ Architecture won't scale
- ❌ Ignores critical requirements
- ❌ Unrealistic or overly complex
- ❌ No cost consideration
- ❌ Security overlooked

### 📊 Evaluation Rubric

| Criteria | Weight | Excellent (5) | Good (3) | Poor (1) |
|----------|--------|---------------|----------|----------|
| **Scalability** | 25% | Handles 10x growth | Handles current load | Won't scale |
| **High Availability** | 25% | 99.99%+ achievable | 99.9% achievable | Single point of failure |
| **Cost Efficiency** | 20% | Optimized, justified | Reasonable | Wasteful/unrealistic |
| **Security** | 20% | Comprehensive | Basic coverage | Overlooked |
| **Documentation** | 10% | Clear, detailed | Adequate | Unclear |

**Minimum Score**: 4.0/5.0 to proceed to Level 4

---

## 💻 Level 4: Code Challenge

**Objective**: Implement a new feature in Sentinel

**Time Limit**: 3 hours

**Prerequisites**: Passed Level 3 (or can be done in parallel)

### 🎯 Feature Request

Choose ONE of the following features to implement:

#### Option A: API Rate Limiting (Backend)
```
Implement rate limiting for the Sentinel API:
- 100 requests per minute per user
- 1000 requests per minute per organization
- Return 429 Too Many Requests when exceeded
- Include rate limit headers in response
- Store limits in Redis
- Add tests
```

#### Option B: Dashboard Widget (Frontend)
```
Create a new dashboard widget that shows:
- Top 10 slowest API endpoints
- Average response time
- P95, P99 latency
- Real-time updates (WebSocket or polling)
- Responsive design
- Add tests
```

#### Option C: Alert Rule Engine (Backend)
```
Implement an alert rule engine:
- Define rules in YAML
- Evaluate metrics against rules
- Trigger alerts via webhook
- Support multiple conditions (AND/OR)
- Add tests
- Document the rule format
```

### 📝 Requirements

1. **Working Code**
   - Feature fully implemented
   - Follows project conventions
   - Clean, readable code

2. **Tests**
   - Unit tests
   - Integration tests (if applicable)
   - > 80% coverage

3. **Documentation**
   - README with usage examples
   - API documentation (if backend)
   - Code comments for complex logic

4. **Git Workflow**
   - Feature branch
   - Atomic commits
   - Clear commit messages

### ✅ Passing Criteria

**PASS** if:
- ✅ Feature works as specified
- ✅ Code quality is high
- ✅ Tests pass and coverage > 80%
- ✅ Documentation is clear
- ✅ Follows best practices

**FAIL** if:
- ❌ Feature doesn't work
- ❌ Poor code quality
- ❌ No tests or low coverage
- ❌ No documentation
- ❌ Took more than 3 hours

### 📊 Evaluation Rubric

| Criteria | Weight | Excellent (5) | Good (3) | Poor (1) |
|----------|--------|---------------|----------|----------|
| **Functionality** | 30% | Perfect, edge cases handled | Works, basic cases | Broken/incomplete |
| **Code Quality** | 25% | Clean, maintainable | Acceptable | Messy, hard to read |
| **Tests** | 25% | Comprehensive, >90% | Basic, >80% | Minimal, <80% |
| **Documentation** | 10% | Excellent | Adequate | Poor/missing |
| **Git Workflow** | 10% | Professional | Acceptable | Poor commits |

**Minimum Score**: 3.5/5.0 to pass

---

## 🎖️ Overall Assessment

### Scoring System

| Level | Weight | Pass Threshold |
|-------|--------|----------------|
| Level 1: Installation | 20% | 3.0/5.0 |
| Level 2: Debugging | 25% | 3.5/5.0 |
| Level 3: Architecture | 30% | 4.0/5.0 |
| Level 4: Code | 25% | 3.5/5.0 |

### Final Recommendation

**Overall Score** = Weighted average of all levels

| Score | Recommendation | Level |
|-------|----------------|-------|
| **4.5 - 5.0** | **STRONG HIRE** | Senior Engineer |
| **4.0 - 4.4** | **HIRE** | Mid-Level Engineer |
| **3.5 - 3.9** | **MAYBE** | Junior Engineer (with mentorship) |
| **< 3.5** | **NO HIRE** | Not ready |

---

## 🚨 Red Flags (Auto-Reject)

Regardless of score, **DO NOT HIRE** if candidate:

- ❌ **Plagiarizes** code (copy-paste from Stack Overflow without understanding)
- ❌ **Lies** about experience or skills
- ❌ **Gives up** easily when facing challenges
- ❌ **Blames tools** instead of solving problems
- ❌ **Asks for solutions** instead of hints
- ❌ **Ignores documentation** and asks answered questions
- ❌ **Misses deadlines** without communication
- ❌ **Poor communication** (unclear, defensive, arrogant)

---

## 💡 Green Flags (Bonus Points)

**STRONG POSITIVE SIGNALS**:

- ✅ **Finishes early** and asks for more challenges
- ✅ **Finds bugs** in the assessment itself
- ✅ **Suggests improvements** to Sentinel
- ✅ **Asks smart questions** that show deep thinking
- ✅ **Documents learnings** from the process
- ✅ **Helps other candidates** (if group assessment)
- ✅ **Shows genuine interest** in the product
- ✅ **Proactive communication** about progress

---

## 📧 Assessment Email Templates

### Initial Invitation

```
Subject: Sentinel Engineering Assessment - Next Steps

Hi [Name],

Thank you for your interest in joining the Sentinel team!

We'd like to invite you to our technical assessment. This is a hands-on evaluation
that will test your skills in:
- System installation and configuration
- Debugging and troubleshooting
- Architecture design
- Coding and testing

The assessment consists of 4 levels:
- Level 1: Installation (1 hour) - Required
- Level 2: Debugging (2 hours) - Required
- Level 3: Architecture (4 hours) - For senior roles
- Level 4: Code Challenge (3 hours) - Required

Total time commitment: 6-10 hours (can be done over multiple days)

Ready to start? Reply to this email and we'll send you Level 1.

Best regards,
Sentinel Team
```

### Level 1 Instructions

```
Subject: Sentinel Assessment - Level 1: Installation Challenge

Hi [Name],

Welcome to Level 1!

Your task: Install and run Sentinel on your local machine.

Repository: https://github.com/jenovoas/sentinel
Documentation: INSTALLATION_GUIDE.md

Time limit: 1 hour from when you start

Submit:
1. Screenshot of dashboard running
2. Output of `docker-compose ps`
3. Brief description of any issues encountered

Start when ready and email your submission within 1 hour.

Good luck!
```

### Pass Notification

```
Subject: Sentinel Assessment - Level 1 Passed! 🎉

Hi [Name],

Congratulations! You've passed Level 1.

Score: [X.X]/5.0
Time: [XX] minutes
Feedback: [Brief positive feedback]

Ready for Level 2? It's a debugging challenge (2 hours).

Reply when you're ready to start.

Best regards,
Sentinel Team
```

### Fail Notification

```
Subject: Sentinel Assessment - Level 1 Results

Hi [Name],

Thank you for completing Level 1 of our assessment.

Unfortunately, we won't be moving forward at this time.

Feedback:
- [Specific, constructive feedback]
- [Areas for improvement]

We encourage you to:
- Practice Docker and containerization
- Learn more about system administration
- Try the assessment again in 6 months

We appreciate your time and wish you the best in your job search.

Best regards,
Sentinel Team
```

---

## 🎯 Quick Reference for Interviewers

### Time Investment

| Candidate Quality | Time to Assess |
|-------------------|----------------|
| **Strong** | 30 min (passes L1 quickly, obvious hire) |
| **Good** | 2-3 hours (completes L1-L2, needs L3-L4) |
| **Weak** | 15 min (fails L1, obvious no-hire) |

### Decision Tree

```
L1 (1h) → FAIL → Reject (save 9 hours)
       → PASS → L2 (2h) → FAIL → Reject (save 7 hours)
                        → PASS → L3 (4h) → FAIL → Maybe Junior
                                         → PASS → L4 (3h) → FAIL → Maybe Mid
                                                          → PASS → Hire!
```

---

## 📊 Historical Data (Track This)

Keep track of candidate performance to improve the assessment:

```
Candidate: [Name]
Date: [Date]
Level 1: [Score] - [Time]
Level 2: [Score] - [Time]
Level 3: [Score] - [Time]
Level 4: [Score] - [Time]
Overall: [Score]
Decision: [Hire/No Hire]
Notes: [Observations]
```

---

**Last Updated**: December 2024  
**Version**: 1.0  
**Maintained by**: Sentinel Engineering Team
