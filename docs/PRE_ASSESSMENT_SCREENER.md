# ⚡ Sentinel - Pre-Assessment Screener (30 Seconds)

**Instant filter to save your time. Use BEFORE any conversation.**

---

## 🎯 Purpose

Filter out candidates who:
- ❌ Don't use proper development environments
- ❌ Lack basic command-line skills
- ❌ Haven't set up essential tools
- ❌ Are "Windows clickers" pretending to be engineers

**Time saved**: 3+ hours per bad candidate

---

## 📧 Email Template (Send This First)

```
Subject: Sentinel - Quick Technical Check

Hi [Name],

Before we proceed, please reply with the following (copy-paste from your terminal):

1. Your primary development OS:
2. `uname -a` (or `systeminfo` if Windows):
3. Clone our repo and show last 5 commits:
   `git clone https://github.com/jaime-novoa/sentinel.git && cd sentinel && git log --oneline -5`
4. `docker --version`:
5. `docker-compose --version`:
6. `git --version`:
7. `python3 --version`:
8. `node --version`:

Also answer:
9. Do you use WSL2? (if on Windows)
10. How many programming languages can you code in TODAY?
11. Link to your GitHub profile:

Reply within 24 hours.

Thanks,
Sentinel Team
```

---

## ✅ PASS Criteria (Proceed to Phone Screen)

### Acceptable Responses:

**Question 1 (OS)**:
- ✅ "Linux (Ubuntu 22.04)" or any Linux distro
- ✅ "macOS Monterey/Ventura/Sonoma"
- ✅ "Windows 11 with WSL2 (Ubuntu 22.04)"

**Question 3 (Git Basic Skills)**:
- ✅ Successfully cloned repo
- ✅ Showed last 5 commits with hashes
- ✅ Output is properly formatted

**Questions 4-8 (Tool Versions)**:
- ✅ All commands return valid versions
- ✅ Docker 20.0+
- ✅ Git 2.30+
- ✅ Python 3.9+
- ✅ Node 16+

**Question 9 (WSL2)**:
- ✅ "Yes, I use WSL2 with Ubuntu" (if Windows)
- ✅ N/A (if Linux/macOS)

**Question 9 (Languages)**:
- ✅ 4+ languages listed
- ✅ Includes Python AND TypeScript/JavaScript

**Question 11 (GitHub)**:
- ✅ Active profile with real projects
- ✅ Contributions in last 3 months
- ✅ Code quality looks good

---

## ❌ INSTANT REJECT (Don't Even Reply)

### Red Flag Responses:

**Question 1 (OS)**:
- ❌ "Windows 10/11" (without mentioning WSL2)
- ❌ "I use whatever the company provides"
- ❌ "Windows with Git Bash"
- ❌ "I have a Mac but don't use terminal much"

**Question 3 (Git Skills)**:
- ❌ "How do I clone a repo?"
- ❌ "What is git log?"
- ❌ "I don't know how to use terminal"
- ❌ Can't provide the output
- ❌ Provides screenshot instead of text (can't copy-paste)

**Questions 4-8 (Tools)**:
- ❌ "I don't have Docker installed"
- ❌ "What is docker-compose?"
- ❌ "I use Docker Desktop GUI"
- ❌ Any command returns error or "command not found"
- ❌ Old versions (Docker < 20, Python < 3.8, etc.)

**Question 9 (WSL2)**:
- ❌ "What is WSL2?"
- ❌ "No, I use Windows natively"
- ❌ "I tried WSL2 but it's complicated"

**Question 10 (Languages)**:
- ❌ Less than 3 languages
- ❌ Doesn't include Python or TypeScript
- ❌ "I'm learning Python"
- ❌ Lists only JavaScript/TypeScript (frontend-only)

**Question 11 (GitHub)**:
- ❌ No GitHub profile
- ❌ Empty profile or only forks
- ❌ Last commit > 6 months ago
- ❌ Only tutorial projects

---

## 🚨 Special Red Flags

**INSTANT REJECT if they say**:

- ❌ "I don't use the command line much"
- ❌ "I prefer GUI tools"
- ❌ "I'm more of a visual person"
- ❌ "I use Windows because it's easier"
- ❌ "I can learn Docker if needed"
- ❌ "I have X years of experience" (but can't answer basic questions)
- ❌ "I'm a fast learner" (instead of showing actual skills)
- ❌ "I mostly use VS Code extensions for everything"

---

## 📊 Scoring System

| Question | Points | Pass Threshold |
|----------|--------|----------------|
| 1. OS | 15 | Linux/macOS or Windows+WSL2 |
| 2. System Info | 5 | Valid output |
| 3. Git Skills | 20 | Clone + log works |
| 4-8. Tools | 30 | All installed, recent versions |
| 9. WSL2 | 10 | Yes (if Windows) |
| 10. Languages | 15 | 4+ including Python+TS |
| 11. GitHub | 5 | Active, quality code |

**Total**: 100 points  
**Pass**: 80+ points  
**Proceed to phone screen**: Yes  
**< 80 points**: Auto-reject

---

## 📧 Response Templates

### If They Pass (80+ points)

```
Subject: Re: Sentinel - Quick Technical Check

Hi [Name],

Thanks for the quick response! Your setup looks good.

Next step: 5-minute phone screen to discuss your experience.

Available times:
- [Time slot 1]
- [Time slot 2]
- [Time slot 3]

Let me know what works.

Best,
Sentinel Team
```

### If They Fail (< 80 points)

```
Subject: Re: Sentinel - Quick Technical Check

Hi [Name],

Thank you for your interest in Sentinel.

After reviewing your technical setup, we've decided not to move forward at this time.

We're looking for engineers with:
- Production-ready development environments (Linux/macOS/WSL2)
- Proficiency in Docker, Git, Python, TypeScript
- Active open source contributions

We encourage you to:
- Set up a proper development environment
- Contribute to open source projects
- Build a strong GitHub portfolio

Best of luck in your search.

Sentinel Team
```

### If They Don't Respond in 24 Hours

```
(Don't send anything. They're not interested or organized enough.)
```

---

## 🎯 Expected Results

**Before Pre-Screener**:
- 100 applicants → 20 phone screens → 5 technical assessments → 1 hire
- Time wasted: 60+ hours

**After Pre-Screener**:
- 100 applicants → 15 pass pre-screen → 10 phone screens → 5 assessments → 2 hires
- Time saved: 40+ hours
- Better hire quality: 2x

---

## 💡 Pro Tips

### 1. Be Ruthless
If they can't answer these basic questions, they're not engineers. Period.

### 2. Don't Make Exceptions
"But they have 10 years of experience!" → Doesn't matter if they use Windows without WSL2.

### 3. Trust the Data
GitHub activity doesn't lie. Empty profile = not a real engineer.

### 4. Move Fast
- Send pre-screener: 2 minutes
- Review response: 30 seconds
- Decision: Instant
- Total time per candidate: < 3 minutes

### 5. No Sympathy
"I'm learning Docker" → Great! Apply again when you know it.
"I can set up Linux if you hire me" → No. Set it up BEFORE applying.

---

## 🎓 What You're Really Testing

This pre-screener tests:

1. **Environment**: Do they use professional tools?
2. **Preparedness**: Are they ready to work TODAY?
3. **Honesty**: Can they actually do what their resume claims?
4. **Initiative**: Did they set up their dev environment without being told?
5. **Seriousness**: Are they serious about engineering or just job hunting?

---

## 📈 Calibration Examples

### Example 1: PASS (Strong Candidate)

```
1. OS: Ubuntu 22.04 LTS
2. uname -a: Linux dev-machine 5.15.0-91-generic x86_64 GNU/Linux
3. docker --version: Docker version 24.0.7, build afdd53b
4. docker-compose --version: Docker Compose version v2.23.3
5. git --version: git version 2.34.1
6. python3 --version: Python 3.11.6
7. node --version: v20.10.0
8. WSL2: N/A (native Linux)
9. Languages: Python, TypeScript, Rust, Go, SQL, Bash
10. GitHub: github.com/awesome-dev (250+ contributions last year)
```

**Score**: 100/100 → **PROCEED TO PHONE SCREEN**

### Example 2: FAIL (Your Current Applicants)

```
1. OS: Windows 11
2. systeminfo: [long Windows output]
3. docker --version: I don't have Docker installed yet
4. docker-compose --version: Same as above
5. git --version: git version 2.40.0.windows.1
6. python3 --version: 'python3' is not recognized as an internal or external command
7. node --version: v18.17.0
8. WSL2: No, I use Windows natively
9. Languages: JavaScript, HTML, CSS, learning Python
10. GitHub: github.com/newbie-dev (3 tutorial repos, last commit 8 months ago)
```

**Score**: 25/100 → **AUTO-REJECT**

---

## 🚀 Implementation

1. **Add to job posting**: "Before applying, ensure you have Docker, Git, Python, and Node installed."

2. **Auto-send pre-screener**: When someone applies, auto-send the email.

3. **Track results**: Keep a spreadsheet of pass/fail rates.

4. **Iterate**: Adjust questions based on what predicts good hires.

---

**Remember**: Your time is valuable. Don't waste it on people who aren't ready.

**Use this pre-screener religiously. No exceptions.**

---

**Last Updated**: December 2024  
**Time Saved Per Bad Candidate**: 3+ hours  
**Recommended Rejection Rate**: 70-85%
