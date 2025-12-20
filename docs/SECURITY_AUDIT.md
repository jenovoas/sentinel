# 🛡️ Sentinel Vault - Security Audit Checklist

**Objective**: Ensure Sentinel Vault is mathematically secure against financial deception and data theft.
**Version**: 1.0 (Pre-Production)

---

## 🔐 1. Cryptographic Integrity
- [ ] **Key Derivation**: Verify Argon2id parameters (Memory: 64MB+, Iterations: 3+, Parallelism: 4).
- [ ] **Zero-Knowledge**: Confirm `master_password` is NOT stored anywhere (disk, logs, database).
- [ ] **Encryption**: Verify AES-256-GCM is used for all `secrets`, `notes`, and `documents`.
- [ ] **Nonces**: Ensure a unique nonce is generated for EVERY encryption operation (never reused).

## 💰 2. Financial Sovereignty (Anti-Fraud)
- [ ] **Local-Only Processing**: Verify `finance_service.py` makes NO outbound connections except to valid price feeds (CoinGecko).
- [ ] **TruthSync Integration**: (Future) Verify claims against TruthSync Core before displaying "Verified".
- [ ] **Tamper Resistance**: Ensure `assets` table cannot be modified by non-authenticated processes (Audit: File permissions on `sentinel_vault.db`).

## 🦅 3. Triad Browser Isolation
- [ ] **Sanitization**: Test `BeautifulSoup` stripper against XSS vectors (e.g., `<img src=x onerror=alert(1)>`).
- [ ] **Air Gap**: Confirm frontend receives strictly `Request -> JSON -> HTML String` (No binary execution).
- [ ] **Leak Protection**: Verify DNS is resolved via the Proxy (Tor/Nym), NOT the local system DNS (DNS Leak Test).

## 🐳 4. Infrastructure & Deployment
- [ ] **Container User**: Ensure Docker containers run as non-root user (USER nextjs / USER python).
- [ ] **Volume Permissions**: Verify `vault_data` is readable ONLY by the container user.
- [ ] **Dependency Scan**: Run `pip-audit` or `safety` on `requirements.txt`.

## 🚨 5. Insider Threat / Physical Access
- [ ] **Cold Boot Attack**: (Mitigation) Recommend user to shutdown (not sleep) when carrying device.
- [ ] **Evil Maid**: (Mitigation) Recommend Full Disk Encryption (LUKS/BitLocker) on the host OS.

---

**Status**: 🟡 Pending Review
**Auditor**: [Your Name/Handle]
