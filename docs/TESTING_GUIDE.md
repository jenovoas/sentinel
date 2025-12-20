# 🦅 Sentinel Vault - Testing & Validation Guide

**Version**: 1.0
**Scope**: Manual & Automated Validation of Sovereign Features.

---

## 🤖 1. Automated Testing (Standard)

We use **Docker** to run tests in a clean, isolated environment.

### Prerequisites
- Docker & Docker Compose installed.

### Execute Tests
Run the automated verification script:
```bash
chmod +x run_tests.sh
./run_tests.sh
```

**What is tested?**
- **Crypto Wallet**: Key derivation, address generation (BTC/ETH).
- **Architecture**: Database models, API endpoints.
- **Finance**: Asset aggregation, net worth calculation.
- **Security**: Encryption/Decryption round-trip correctness.

---

## 👤 2. User Acceptance Testing (UAT) - Manual

Follow these steps to validate the "Sovereign OS" experience.

### A. 🔐 Identity Validation
1.  **Unlock**: Open `http://localhost:3000`. Enter Master Password.
2.  **Verify**: Dashboard decrypts.
3.  **Check AI**: Go to "Analysis". Enter `password123`. Confirm AI warns about weakness.

### B. 💰 Finance Validation
1.  **Add Asset**:
    - Go to "Financial Dashboard".
    - Click "Add Asset".
    - Type: `Gold Bar`, Category: `Gold`, Value: `2500`.
2.  **Verify Calculation**:
    - Check "Total Net Worth" card. It should increase by $2,500.
3.  **Persistence**:
    - Refresh the page.
    - Confirm "Gold Bar" is still listed (loaded from local DB).

### C. 🦅 Browser Validation (Triad)
1.  **Clear Mode**:
    - Select `Clear` mode. Enter `https://example.com`.
    - Result: Page loads fast. Inspect source -> No `<script>` tags found.
2.  **Velocity Mode** (Requires Tor):
    - Ensure Tor is running on port 9050.
    - Select `Velocity`. Enter `https://check.torproject.org`.
    - Result: Should say "Congratulations. This browser is configured to use Tor."

### D. 📄 Document Vault
1.  **Upload**: Drag & Drop a PDF into the "Documents" zone.
2.  **Verify**: Log shows "Encryption Complete (AES-256)". File appears in list.

---

## 🚨 3. Emergency / Recovery Testing

### Wallet Recovery
1.  Go to **Crypto Wallet**.
2.  Click **Recover**.
3.  Enter a known 12-word seed phrase.
4.  **Expectation**: The correct BTC/ETH addresses are regenerated instantly.

### Vault Lockout
1.  Click **Lock Vault**.
2.  Try to access API endpoints directly (`/vault/list`).
3.  **Expectation**: `403 Forbidden` (Token required).

---

**Tester Sign-off**: ____________________
**Date**: _______________
