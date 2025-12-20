# 🦅 Sentinel Vault Architecture

**Version**: 1.0 (Phase 6 Complete)
**Type**: Sovereign Personal OS (Local-First)

---

## 🏗️ High-Level Design

Sentinel Vault is designed as a **Local-First**, **Zero-Knowledge** application. It assumes the cloud is hostile and the network is compromised.

```mermaid
graph TD
    User[👤 Sovereign User] -->|Master Password| Auth[🔐 Argon2id Auth]
    
    subgraph "Local Secure Enclave (Memory)"
        Auth -->|Unlock Key| KeyManager[🔑 Key Manager]
        KeyManager -->|Decrypt| DB[(Encrypted SQLite)]
    end
    
    subgraph "Modules"
        DB -->|Notes/Docs| Vault[📄 Document Vault]
        DB -->|Secrets| Identity[🔐 Password Manager]
        DB -->|Assets| Finance[💰 Financial Dashboard]
    end
    
    subgraph "External Connectivity"
        Finance -->|Live Prices| CoinGecko[📉 CoinGecko API]
        Identity -->|Entropy| Ollama[🤖 Local AI (Ollama)]
        Browser[🦅 Triad Browser] -->|Routes| Internet[🌍 Internet]
    end
    
    subgraph "Triad Routing"
        Browser -->|Mode 1| Clear[Sanitized Direct]
        Browser -->|Mode 2| Proxy[Rotating Proxy]
        Browser -->|Mode 3| Ghost[Nym Mixnet]
        Browser -->|Mode 4| Deep[I2P Network]
    end
```

---

## 🧩 Core Modules

### 1. Identity & Secrets
- **Algorithm**: AES-256-GCM (Data) + Argon2id (Key Derivation).
- **Storage**: `secrets` table in `vault.db`.
- **AI Analysis**: Passwords analyzed locally by `phi3:mini` via Ollama for semantic weakness detection.

### 2. Sovereign Finance (New in Phase 6)
- **Concept**: Unified view of On-Chain + Off-Chain assets.
- **Crypto Engine**: `crypto_service.py` (derives keys from Master Seed).
    - Supports: BTC, ETH, SOL, MATIC.
- **Asset Engine**: `finance_service.py` (aggregates manual assets).
- **Privacy**: No external bank connections (Plaid/Yodlee) to prevent data leaks.

### 3. Triad Secure Browser (New in Phase 5)
- **Universal Switchboard**: `browser_service.py` acts as a local proxy.
- **Sanitization**: All HTML is stripped of `<script>`, `<iframe>`, `<object>` before rendering.
- **Routing Modes**:
    1.  **Clear**: Speed prioritized, trackers removed.
    2.  **Velocity**: IP masking via localized SOCKS5.
    3.  **Ghost**: Metadata protection via Nym Mixnet.
    4.  **Deep**: Hidden service access via I2P.

### 4. Document Vault
- **Storage**: Files stored physically on disk (`vault_storage/`) but encrypted with AES-256.
- **Filenames**: Obfuscated UUIDs. Metadata stored in DB.

---

## 🔒 Security Model

1.  **Zero-Knowledge**: The backend API has no access to data without the `master_password` sent per-session (cached in memory, never disk).
2.  **Air Gap UI**: The Frontend (React) never communicates directly with the internet. All requests go through the Backend Proxy.
3.  **Database Encryption**: SQLCipher (planned Phase 7) or Application-Level AES (Current).

---

## 📂 File Structure

```
backend/
├── poc/
│   ├── main.py             # FastAPI Entrypoint
│   ├── database.py         # SQLAlchemy Models (User, Secret, Asset)
│   ├── crypto_service.py   # Blockchain Logic
│   ├── finance_service.py  # Net Worth Logic
│   └── browser_service.py  # Triad Routing Logic
```

```
frontend/
├── poc/src/app/
│   └── page.tsx            # Unified Single-Page OS Interface
```

---

**Next Steps**:
- [ ] Phase 7: Docker Containerization
- [ ] Phase 8: Mobile App Sync (Encrypted P2P)
