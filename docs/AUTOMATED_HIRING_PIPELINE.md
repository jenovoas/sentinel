# 🤖 Pipeline de Selección 100% Automatizado

## 🎯 Objetivo

**Proteger tu tiempo y flow mental** eliminando completamente la interacción manual con candidatos hasta que estén pre-calificados.

**Problema actual**:
```
Tú → Explicar cosas básicas → Perder flow → Perder ideas
     ↓
Algoritmo de la Verdad pausado ❌
Sentinel pausado ❌
Tu energía mental drenada ❌
```

**Solución automatizada**:
```
Candidato → Email automático → Assessment automático → Auto-grading
                                                            ↓
                                                    Solo los que pasan 85%+
                                                            ↓
                                                    Tú hablas con ellos ✅
```

**Resultado**: Tú solo hablas con 1 de cada 20 candidatos (los que ya pasaron todo).

---

## 📧 Fase 1: Pre-Screening por Email (100% Automático)

### Email de Aplicación Inicial

**Asunto**: "Sentinel Engineering - Quick Pre-Screen"

```
Hi [Name],

Thanks for your interest in Sentinel.

Before we proceed, please answer these 6 questions (copy-paste and reply):

1. Programming languages you can ship production code in TODAY (list all):

2. Explain the difference between `docker-compose up` and `docker-compose up -d`:

3. A service is crashing in production. Your debugging process (step-by-step):

4. Time to set up FastAPI + PostgreSQL + Redis + Docker from scratch:
   a) 30 minutes
   b) 1-2 hours
   c) 1 day
   d) Need to look it up

5. Technology you learned in the last 30 days and how:

6. How do you use AI (ChatGPT/Claude/Copilot) in your work? Give a specific example:

---

IMPORTANT: 
- Answer ALL 6 questions
- Be specific (no vague answers)
- We auto-filter responses
- Only qualified candidates receive the technical assessment

Reply within 48 hours.

- Sentinel Hiring Bot
```

### Auto-Grading del Pre-Screen

**Script Python** (ejecuta automáticamente):

```python
# auto_screen.py

import re
from typing import Dict, List

def score_prescreening(email_body: str) -> Dict[str, any]:
    """
    Auto-score pre-screening email responses.
    Returns: {score: int, pass: bool, feedback: str}
    """
    score = 0
    feedback = []
    
    # Q1: Languages (need 4+)
    languages = extract_languages(email_body)
    if len(languages) >= 4:
        score += 20
    elif len(languages) >= 3:
        score += 10
        feedback.append("Only 3 languages (need 4+)")
    else:
        feedback.append("FAIL: Less than 3 languages")
    
    # Q2: Docker knowledge
    if "detached" in email_body.lower() or "background" in email_body.lower():
        score += 15
    else:
        feedback.append("FAIL: Doesn't understand Docker basics")
    
    # Q3: Debugging process
    if has_systematic_approach(email_body):
        score += 20
    else:
        feedback.append("FAIL: No systematic debugging approach")
    
    # Q4: Speed (need 30min or 1-2 hours)
    if "30 min" in email_body or "1-2 hour" in email_body:
        score += 15
    else:
        feedback.append("Too slow or needs to look it up")
    
    # Q5: Learning (need recent learning)
    if has_recent_learning(email_body):
        score += 15
    else:
        feedback.append("No recent learning mentioned")
    
    # Q6: AI usage (critical)
    ai_score = score_ai_usage(email_body)
    score += ai_score
    if ai_score < 10:
        feedback.append("FAIL: Poor AI usage or doesn't use AI")
    
    return {
        "score": score,
        "pass": score >= 70,
        "feedback": "\n".join(feedback)
    }

def extract_languages(text: str) -> List[str]:
    """Extract programming languages from text."""
    known_languages = [
        "python", "javascript", "typescript", "rust", "go", 
        "java", "c++", "c#", "ruby", "php", "sql", "bash"
    ]
    found = []
    text_lower = text.lower()
    for lang in known_languages:
        if lang in text_lower:
            found.append(lang)
    return found

def has_systematic_approach(text: str) -> bool:
    """Check if debugging approach is systematic."""
    keywords = ["logs", "metrics", "reproduce", "trace", "monitor"]
    return sum(1 for kw in keywords if kw in text.lower()) >= 3

def has_recent_learning(text: str) -> bool:
    """Check if candidate mentions recent learning."""
    # Look for specific tech names, not vague "took a course"
    vague_phrases = ["took a course", "watched tutorial", "nothing new"]
    return not any(phrase in text.lower() for phrase in vague_phrases)

def score_ai_usage(text: str) -> int:
    """Score AI usage sophistication (0-15 points)."""
    score = 0
    text_lower = text.lower()
    
    # Red flags (0 points)
    if "don't use ai" in text_lower or "i don't use" in text_lower:
        return 0
    if "just ask it" in text_lower or "copy paste" in text_lower:
        return 0
    
    # Green flags
    if "refine" in text_lower or "iterate" in text_lower:
        score += 5
    if "context" in text_lower or "specific" in text_lower:
        score += 5
    if "verify" in text_lower or "check" in text_lower:
        score += 5
    
    return min(score, 15)

# Auto-responder
def send_auto_response(candidate_email: str, result: Dict):
    """Send automated response based on screening result."""
    if result["pass"]:
        send_assessment_email(candidate_email)
    else:
        send_rejection_email(candidate_email, result["feedback"])
```

### Email Automático de Respuesta

**Si PASA (score >= 70%)**:

```
Subject: Sentinel Technical Assessment - Next Steps

Hi [Name],

Great answers! You passed our pre-screening (Score: [X]/100).

Next step: Technical Assessment (5 hours, autonomous)

Access your assessment here:
https://sentinel-hiring.com/assessment/[unique-token]

Instructions:
- 6 challenges (installation, debugging, feature, architecture, AI, code review)
- 5 hours total
- Autonomous work (no help)
- Submit before [deadline - 7 days]

Pass threshold: 85%
Average pass rate: 15%

Good luck!

- Sentinel Hiring Bot
```

**Si NO PASA (score < 70%)**:

```
Subject: Sentinel Engineering - Not a Match

Hi [Name],

Thanks for your interest in Sentinel.

After reviewing your pre-screening responses, we've determined 
this role isn't the right fit at this time.

Feedback:
[Auto-generated feedback]

We're looking for engineers with:
- 4+ programming languages
- Strong debugging skills
- Fast execution (30min-2hr setup time)
- Continuous learning
- Advanced AI proficiency

We encourage you to apply again in 6-12 months as you gain more experience.

Best of luck!

- Sentinel Hiring Bot
```

---

## 💻 Fase 2: Assessment Automatizado (100% Automático)

### Plataforma de Assessment

**Opción A: Custom (Recomendado)**

**Stack**:
- Frontend: Next.js (formularios + timer)
- Backend: FastAPI (auto-grading)
- Database: PostgreSQL (resultados)
- Storage: S3 (código submissions)

**Features**:
- Timer automático (5 horas)
- Auto-submit cuando se acaba el tiempo
- Code editor integrado (Monaco)
- Auto-grading de challenges 1, 2, 5, 6
- Manual grading de challenges 3, 4 (pero solo para los que pasan auto-grading)

**Costo**: $0 (self-hosted)  
**Tiempo desarrollo**: 2-3 días

**Opción B: Usar Plataforma Existente**

**HackerRank for Work**:
- Costo: $100/mes
- Auto-grading incluido
- Integración con email
- Reportes automáticos

**Codility**:
- Costo: $300/mes
- Mejor auto-grading
- Anti-cheating detection
- Video recording

**Recomendación**: Opción A (custom) - más control, $0 costo

---

## 🤖 Fase 3: Auto-Grading (90% Automático)

### Challenges Auto-Gradeables

**Challenge 1: Installation** (100% auto)
```python
def grade_installation(screenshot_url: str) -> Dict:
    """
    Check if screenshot shows working dashboard.
    Use computer vision (OCR) to verify.
    """
    # Check for key elements:
    # - Sentinel logo
    # - Dashboard metrics
    # - Services running
    
    score = 0
    if has_sentinel_logo(screenshot_url):
        score += 30
    if has_metrics(screenshot_url):
        score += 40
    if has_services_list(screenshot_url):
        score += 30
    
    return {
        "score": score,
        "pass": score >= 80,
        "time": extract_time_from_metadata()
    }
```

**Challenge 2: Debugging** (80% auto)
```python
def grade_debugging(git_diff: str, bug_report: str) -> Dict:
    """
    Auto-grade bug fixes.
    Check if code changes fix the planted bugs.
    """
    bugs_fixed = 0
    
    # Bug 1: Race condition
    if "asyncio.Lock" in git_diff or "async with lock" in git_diff:
        bugs_fixed += 1
    
    # Bug 2: SQL injection
    if "parameterized" in git_diff or "?" in git_diff:
        bugs_fixed += 1
    
    # ... check all 10 bugs
    
    score = (bugs_fixed / 10) * 100
    
    return {
        "score": score,
        "bugs_found": bugs_fixed,
        "pass": bugs_fixed >= 6
    }
```

**Challenge 5: AI Proficiency** (100% auto)
```python
def grade_ai_prompts(prompts: List[str]) -> Dict:
    """
    Grade prompt quality automatically.
    """
    scores = []
    
    for prompt in prompts:
        score = 0
        # Check for context
        if has_context(prompt):
            score += 30
        # Check for constraints
        if has_constraints(prompt):
            score += 20
        # Check for structured output request
        if has_output_format(prompt):
            score += 20
        # Check for measurable goals
        if has_goals(prompt):
            score += 20
        # Check for prioritization
        if has_prioritization(prompt):
            score += 10
        
        scores.append(score)
    
    avg_score = sum(scores) / len(scores)
    
    return {
        "score": avg_score,
        "pass": avg_score >= 70
    }
```

**Challenge 6: Code Review** (100% auto)
```python
def grade_code_review(bugs_found: List[str], explanations: List[str]) -> Dict:
    """
    Grade code review challenge.
    """
    correct_bugs = [
        "email validation",
        "existing check",
        "blocking bcrypt",
        "missing refresh",
        "no error handling"
    ]
    
    score = 0
    for bug in bugs_found:
        if any(correct in bug.lower() for correct in correct_bugs):
            score += 20
    
    # Check explanations quality
    if all(len(exp) > 50 for exp in explanations):
        score += 10  # Bonus for detailed explanations
    
    return {
        "score": min(score, 100),
        "bugs_found": len(bugs_found),
        "pass": score >= 60
    }
```

### Challenges Semi-Manuales

**Challenge 3: Feature Implementation** (manual review)
- Auto-grading: Tests pass? (50%)
- Manual review: Code quality (50%)
- **Solo revisar si pasa auto-grading**

**Challenge 4: Architecture** (manual review)
- Auto-grading: Tiene diagrama? Tiene IaC? (30%)
- Manual review: Calidad de diseño (70%)
- **Solo revisar si pasa auto-grading**

---

## 📊 Dashboard de Resultados (Para Ti)

### Vista Diaria

```
SENTINEL HIRING DASHBOARD

Today:
- Applications received: 15
- Pre-screen passed: 3 (20%)
- Assessments in progress: 2
- Assessments completed: 1
- Candidates qualified (85%+): 0

This Week:
- Applications: 47
- Pre-screen passed: 9 (19%)
- Assessments completed: 7
- Candidates qualified: 1 (14% pass rate)

ACTION REQUIRED:
- Review 1 qualified candidate: [Name] (Score: 87%)
  [View Profile] [Schedule Interview]
```

### Email Diario Automático

```
Subject: Sentinel Hiring - Daily Summary

1 candidate qualified today:

Name: Juan Pérez
Score: 87%
Highlights:
- Completed assessment in 4.2 hours
- Found all 10 bugs in Challenge 2
- Excellent AI prompts (95%)
- Clean code in Challenge 3

[View Full Report] [Schedule Interview] [Reject]

---

7 candidates failed:
- 3 failed pre-screening
- 4 failed assessment (<85%)

No action needed.
```

---

## ⚙️ Implementación Técnica

### Stack Recomendado

```
Frontend (Assessment Platform):
- Next.js 14
- Monaco Editor (code editor)
- Tailwind CSS

Backend (Auto-Grading):
- FastAPI
- Celery (async grading)
- PostgreSQL (results)

Email Automation:
- SendGrid (transactional emails)
- n8n (workflow automation)

Monitoring:
- Sentry (errors)
- PostHog (analytics)
```

### Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│ CANDIDATO                                                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ EMAIL PRE-SCREENING                                          │
│ - Recibe email con 6 preguntas                              │
│ - Responde                                                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ AUTO-GRADING (Python Script)                                │
│ - Extrae respuestas                                         │
│ - Score 0-100                                               │
│ - Pass/Fail decision                                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
    PASS (70%+)                 FAIL (<70%)
        │                           │
        ▼                           ▼
┌──────────────────┐      ┌──────────────────┐
│ Send Assessment  │      │ Send Rejection   │
│ Link             │      │ Email            │
└────────┬─────────┘      └──────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ ASSESSMENT PLATFORM                                          │
│ - 6 Challenges                                              │
│ - 5 hour timer                                              │
│ - Code editor                                               │
│ - Auto-submit                                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ AUTO-GRADING (Challenges 1,2,5,6)                           │
│ - 90% automated                                             │
│ - Instant results                                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
    PASS (85%+)                 FAIL (<85%)
        │                           │
        ▼                           ▼
┌──────────────────┐      ┌──────────────────┐
│ Notify You       │      │ Auto-Reject      │
│ (Email + Slack)  │      │ Email            │
└──────────────────┘      └──────────────────┘
```

---

## 💰 Costo de Implementación

### Opción 1: Custom Platform (Recomendado)

| Item | Costo |
|------|-------|
| **Desarrollo** (2-3 días) | $0 (tú o IA) |
| **Hosting** (Vercel + Railway) | $0/mes |
| **Email** (SendGrid) | $0/mes (12K emails gratis) |
| **Total** | **$0/mes** |

### Opción 2: Plataforma Existente

| Item | Costo |
|------|-------|
| **HackerRank** | $100/mes |
| **Email automation** | $0 |
| **Total** | **$100/mes** |

**Recomendación**: Opción 1 (custom) - control total, $0 costo

---

## 📅 Timeline de Implementación

### Semana 1: Email Pre-Screening
- [ ] Crear script de auto-grading (Python)
- [ ] Configurar SendGrid
- [ ] Crear templates de email
- [ ] Testear con 5 emails de prueba

### Semana 2: Assessment Platform
- [ ] Frontend (Next.js + Monaco Editor)
- [ ] Backend (FastAPI + auto-grading)
- [ ] Integración con email
- [ ] Testing end-to-end

### Semana 3: Dashboard + Monitoring
- [ ] Dashboard de resultados
- [ ] Email diario automático
- [ ] Slack notifications
- [ ] Analytics (PostHog)

**Total**: 3 semanas para sistema 100% automatizado

---

## 🎯 Resultado Final

**Antes** (manual):
```
100 aplicaciones
  ↓
Tú hablas con 100 personas (50 horas)
  ↓
5 pasan assessment
  ↓
1 hire
```

**Después** (automatizado):
```
100 aplicaciones
  ↓
Auto-filter: 20 pasan pre-screen
  ↓
Auto-grade: 3 pasan assessment (85%+)
  ↓
Tú hablas con 3 personas (3 horas)
  ↓
1 hire
```

**Ahorro de tiempo**: 47 horas (94%)  
**Tu tiempo**: Solo 3 horas para 100 aplicaciones  
**Tu flow mental**: Protegido ✅

---

## 🚀 Próxima Acción

**Opción A: Yo lo construyo** (con IA, 2-3 días)
- Te entrego código completo
- Tú solo deploys
- $0 costo

**Opción B: Contratar freelancer** (1 semana)
- Upwork/Fiverr
- $500-1000
- Menos control

**Opción C: Usar HackerRank** (inmediato)
- $100/mes
- Menos personalización
- Rápido de setup

**Recomendación**: Opción A - máximo control, $0 costo, 2-3 días

---

**¿Quieres que empiece a construir el sistema automatizado ahora?**

Puedo empezar con el script de auto-grading del pre-screening (1 hora de trabajo).
