# Sentinel Vault V1.0 - Technical Context for AI Review

**Project**: Sentinel Vault (Sovereign Personal OS)
**Objective**: Privacy-first, local-only digital asset and identity management.
**Stack**: Python (FastAPI), React (Next.js), Docker, Nginx, Tor/I2P (Routing).

---

## 🏗️ System Architecture

### 1. Backend (`backend/poc/`)
- **Framework**: FastAPI (Python 3.11).
- **Database**: SQLite (`sentinel_vault.db`) with SQLAlchemy ORM.
- **Security**: 
    - `argon2-cffi` for Master Password hashing.
    - `cryptography` (Fernet/AES) for data encryption.
    - **Zero-Knowledge**: Master password never stored; derived key stays in RAM.
- **Key Modules**:
    - `browser_service.py`: "Universal Switchboard" proxy for routing traffic via Tor (9050), I2P (4444), or Direct. Sanitizes HTML (removes JS/IFrames).
    - `truthsync_service.py`: **[NEW]** Real-time AI content verification using local LLM (Ollama). Detects misinformation and logical fallacies.
    - `finance_service.py`: Aggregates crypto balances (Web3/BIP32) and manual assets. 
    - `terminal_service.py`: Command implementation for CLI-like control.

### 2. Frontend (`frontend/poc/`)
- **Framework**: Next.js 14 (React).
- **UI**: Tailwind CSS, Recharts (Finance).
- **Isolation**: "Virtual Air Gap" - Frontend never requests external URLs directly; all traffic goes through `browser_service` proxy.

### 3. Infrastructure (`docker-compose.yml`)
- **Services**: Backend, Frontend, Nginx.
- **Network**: Internal `sentinel-net`. Only Nginx exposes ports 80/443.
- **SSL**: Nginx terminates SSL with self-signed certs (Localhost).

---

## 🔍 Critical Areas for Review (Ask Perplexity to Check These)

1.  **Finance Logic (`finance_service.py`)**: 
    - Potential precision errors in `total_balance` calculation (Float vs Decimal).
    - Race conditions in `asset` creation? (SQLite concurrency).

2.  **Browser Sanitization (`browser_service.py`)**:
    - Is `BeautifulSoup` robust enough to strip all XSS vectors?
    - Are we leaking DNS requests in `velocity` mode?

3.  **Crypto Key Management (`crypto_wallet.py`)**:
    - Is the BIP32 derivation path standard?
    - Are private keys cleared from memory effectively?

4.  **TruthSync AI Verification**:
    - Can the prompt in `truthsync_service.py` be injected/jailbroken?
    - Is the JSON parsing robust against hallucinated formats?
    - Privacy: Are we sending sensitive URL data to the local LLM in a way that logs could leak?

5.  **Docker Security**:
    - Are we running containers as root? (Check `Dockerfile` user directives).
    - Are volume permissions too open?

---

## 📂 File Manifest
- `docs/VAULT_ARCHITECTURE.md`: Detailed module breakdown.
- `docs/SECURITY_AUDIT.md`: Self-assessment checklist.
- `nginx/nginx.conf`: Reverse proxy configuration.
- `run_tests.sh`: Automated verification script.

---

**Request to Perplexity**: 
"Analyze this architecture for security vulnerabilities, specifically focusing on data leaks in the proxy service and cryptographic weaknesses in the vault storage."
