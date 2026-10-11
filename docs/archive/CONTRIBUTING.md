# Contributing to Sentinel Cortex

**Classification:** SENTINEL INTERNAL // DEFENSE GRADE  
**Standards Compliance:** ISO 27001, ISO 9001, ITIL v4

---

## 1. Introduction

Sentinel Cortex is a defense-grade security platform. As such, our development process is strictly governed by international standards for quality, security, and service management. We do not just "push code"; we **engineer reliability**.

All contributors must adhere to the protocols defined in this document. Failure to comply may result in revocation of access rights (ISO 27001: Access Control Policy).

---

## 2. Change Management (ITIL v4 / ISO 20000)

We follow a strict Change Management process to ensure stability and traceability.

### 2.1 The Request for Change (RFC)
Every code modification must be associated with an RFC (represented by a GitHub Issue or Jira Ticket). No "orphan" code is allowed.

**Branch Naming Convention:**
- `feat/RFC-123_brief_description` (New Features)
- `fix/INC-456_brief_description` (Incident Fixes)
- `refactor/RFC-789_brief_description` (Code Improvements)
- `hotfix/INC-999_brief_description` (Emergency Production Fixes)

### 2.2 The Change Advisory Board (CAB)
The "CAB" function is simulated via mandatory Code Reviews.
- **Master Branch Protection:** Direct pushes to `master` are blocked.
- **Review Requirements:** All PRs require at least 1 approval from a designated Code Owner.
- **Traceability (ISO 9001):** The PR description must link to the original RFC/Issue.

---

## 3. Incident Management (ITIL v4)

When bugs are discovered, they are classified as **Incidents**.

### 3.1 Severity Levels (SLA)
- **SEV-1 (Critical):** System Down or Data Loss. Response: < 15 mins.
    - Example: Kernel Panic in Guardian module.
- **SEV-2 (High):** Major functionality impaired. Response: < 1 hour.
    - Example: Dashboard not loading metrics.
- **SEV-3 (Medium):** Minor bug or annoyance. Response: < 24 hours.
    - Example: Typo in logs.
- **SEV-4 (Low):** Feature request or cosmetic issue.

### 3.2 Reporting Protocol
Create a GitHub Issue with the label `bug` and the appropriate `SEV-X` tag.
**Required Information:**
1. Steps to Reproduce
2. Expected vs Actual Behavior
3. Affected Component (Backend, Frontend, Kernel)
4. Evidence (Logs, Screenshots - **Sanitized**)

---

## 4. Security Standards (ISO 27001)

Security is everyone's responsibility.

### 4.1 Clean Desk Policy (Code)
- **NO SECRETS:** Never commit API keys, passwords, or certificates. Use `.env` files.
- **Sanitization:** Ensure logs do not leak PII (Personally Identifiable Information).
- **Least Privilege:** Request only the permissions necessary for your container/service.

### 4.2 Secure Coding Practices
- **Input Validation:** Never trust user input. Validate at the edge.
- **Dependency Management:** Regularly audit `package.json` and `requirements.txt` for vulnerabilities (CVEs).
- **Encryption:** Use TLS for data in transit and AES-256 for data at rest.

---

## 5. Quality Management (ISO 9001)

### 5.1 Definition of Done (DoD)
A feature is considered "Done" only when:
- [ ] Code compiles/runs without errors.
- [ ] Unit tests pass (where applicable).
- [ ] Documentation is updated (`README.md`, `ARCHITECTURE.md`).
- [ ] Resource usage is within defined limits (Docker specs).
- [ ] Code style checks pass (Linting).

### 5.2 Style Guides
- **Python:** PEP 8 (Enforced by `black`).
- **TypeScript/React:** Airbnb Style Guide (Enforced by `eslint`).
- **Commits:** Conventional Commits (e.g., `feat: add neural engine support`).

---

## 6. Onboarding Checklist

1. **Read** `CISO_EXECUTIVE_SUMMARY.md` to understand the mission.
2. **Review** `ARCHITECTURE.md` for system design.
3. **Configure** your local environment using `.env.example`.
4. **Sign** the Developer Certificate of Origin (DCO) via your first commit.

---
*Authorized by Sentinel Systems Command*
