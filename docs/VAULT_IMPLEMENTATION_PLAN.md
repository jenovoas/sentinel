# 🏗 Sentinel Vault - Production Implementation Plan

**Objetivo**: Implementar Sentinel Vault como producto production-ready  
**Timeline**: 4-6 semanas  
**Status**: Planning → Execution

---

## 📋 Architecture Overview

### **Tech Stack**

**Backend**:
- FastAPI (Python 3.11+)
- PostgreSQL 16 (database)
- SQLAlchemy (ORM)
- Alembic (migrations)
- Redis (sessions + cache)
- Ollama (password analysis)

**Frontend**:
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Zustand (state management)
- React Query (API calls)

**Infrastructure**:
- Docker + Docker Compose
- Nginx (reverse proxy)
- Let's Encrypt (SSL)

---

## 🗄 Database Schema

### **Users Table**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    
    -- Master password (nunca almacenado en plaintext)
    salt BYTEA NOT NULL,  -- 32 bytes para Argon2id
    
    -- 2FA
    totp_secret VARCHAR(255),
    totp_enabled BOOLEAN DEFAULT FALSE,
    
    -- Recovery
    recovery_email VARCHAR(255),
    
    -- Metadata
    settings JSONB DEFAULT '{}'::jsonb
);
```

### **Vault Items Table**
```sql
CREATE TABLE vault_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Item type
    item_type VARCHAR(50) NOT NULL,  -- 'password', 'note', 'card', 'identity'
    
    -- Encrypted data
    encrypted_data JSONB NOT NULL,  -- {nonce, ciphertext, tag}
    
    -- Metadata (no cifrado)
    name VARCHAR(255) NOT NULL,
    folder VARCHAR(255),
    favorite BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP,
    
    -- Indexes
    INDEX idx_user_items (user_id, item_type),
    INDEX idx_user_folder (user_id, folder)
);
```

### **Crypto Wallets Table**
```sql
CREATE TABLE crypto_wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Wallet info
    name VARCHAR(255) NOT NULL,
    chain VARCHAR(50) NOT NULL,  -- 'bitcoin', 'ethereum', 'solana', etc.
    
    -- Encrypted seed phrase (cifrado con master password)
    encrypted_seed JSONB NOT NULL,  -- {nonce, ciphertext, tag}
    
    -- Public data
    address VARCHAR(255) NOT NULL,
    derivation_path VARCHAR(100),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_wallets (user_id)
);
```

### **Access Log Table** (Audit Trail)
```sql
CREATE TABLE access_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vault_item_id UUID REFERENCES vault_items(id) ON DELETE SET NULL,
    
    -- Action
    action VARCHAR(50) NOT NULL,  -- 'view', 'create', 'update', 'delete'
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    location JSONB,  -- {country, city, lat, lon}
    
    -- Anomaly detection
    anomaly_score FLOAT,
    flagged BOOLEAN DEFAULT FALSE,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_log (user_id, created_at DESC),
    INDEX idx_flagged (flagged, created_at DESC)
);
```

### **Sessions Table**
```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Session data
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    
    -- Device info
    device_name VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    last_activity TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_sessions (user_id),
    INDEX idx_token (token_hash)
);
```

---

## 🔐 Authentication Flow

### **1. Registration**
```
1. User enters email + master password
2. Backend:
   - Generate salt (32 bytes)
   - Derive key with Argon2id (NOT stored)
   - Store user + salt
   - Send verification email
3. User verifies email
```

### **2. Login**
```
1. User enters email + master password
2. Backend:
   - Fetch user + salt
   - Derive key with Argon2id
   - Validate (decrypt test item)
   - Generate JWT token
   - Create session
3. Frontend stores JWT in httpOnly cookie
```

### **3. Vault Unlock**
```
1. User already logged in (JWT valid)
2. User enters master password
3. Frontend:
   - Derive encryption key (client-side)
   - Store in memory (session)
   - Never send to backend
4. All encryption/decryption happens client-side
```

---

## 📁 Project Structure

```
sentinel-vault/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   ├── config.py               # Settings
│   │   ├── database.py             # DB connection
│   │   │
│   │   ├── models/                 # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── vault_item.py
│   │   │   ├── crypto_wallet.py
│   │   │   └── access_log.py
│   │   │
│   │   ├── schemas/                # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── vault.py
│   │   │   └── crypto.py
│   │   │
│   │   ├── services/               # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── vault.py
│   │   │   ├── crypto.py
│   │   │   └── ollama.py
│   │   │
│   │   ├── api/                    # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── vault.py
│   │   │   ├── crypto.py
│   │   │   └── analysis.py
│   │   │
│   │   └── utils/                  # Utilities
│   │       ├── __init__.py
│   │       ├── encryption.py
│   │       └── security.py
│   │
│   ├── alembic/                    # DB migrations
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   └── register/
│   │   │   ├── (dashboard)/
│   │   │   │   ├── vault/
│   │   │   │   ├── crypto/
│   │   │   │   └── settings/
│   │   │   └── layout.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                 # Shadcn components
│   │   │   ├── vault/
│   │   │   └── crypto/
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts              # API client
│   │   │   ├── encryption.ts       # Client-side crypto
│   │   │   └── utils.ts
│   │   │
│   │   └── store/                  # Zustand stores
│   │       ├── auth.ts
│   │       └── vault.ts
│   │
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── nginx/
│   └── nginx.conf
└── README.md
```

---

##  Implementation Phases

### **Phase 1: Backend Core** (Week 1-2)
- [ ] Setup FastAPI project
- [ ] Create database models
- [ ] Implement authentication (JWT)
- [ ] Add vault CRUD endpoints
- [ ] Add crypto wallet endpoints
- [ ] Integrate Ollama

### **Phase 2: Frontend Core** (Week 2-3)
- [ ] Setup Next.js project
- [ ] Create auth pages (login/register)
- [ ] Build vault dashboard
- [ ] Implement client-side encryption
- [ ] Add crypto wallet UI

### **Phase 3: Integration** (Week 3-4)
- [ ] Connect frontend to backend
- [ ] Add error handling
- [ ] Implement loading states
- [ ] Add notifications

### **Phase 4: Security & Testing** (Week 4-5)
- [ ] Security audit
- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance testing

### **Phase 5: Deployment** (Week 5-6)
- [ ] Docker setup
- [ ] CI/CD pipeline
- [ ] SSL certificates
- [ ] Monitoring

---

##  MVP Features (First Release)

### **Must Have**:
1. ✅ User registration + login
2. ✅ Password vault (save/retrieve)
3. ✅ Ollama password analysis
4. ✅ Crypto wallet generation (Bitcoin + Ethereum)
5. ✅ Client-side encryption (zero-knowledge)

### **Nice to Have** (v1.1):
- 2FA (TOTP)
- Password sharing
- Browser extension
- Mobile app
- Hardware wallet integration

---

## 📊 Success Metrics

### **Performance**:
- Login: <2s
- Vault unlock: <500ms
- Password decrypt: <100ms
- Ollama analysis: <2s

### **Security**:
- Zero-knowledge encryption ✅
- Argon2id + AES-256-GCM ✅
- JWT with httpOnly cookies ✅
- Audit trail for all actions ✅

### **UX**:
- Intuitive interface
- Fast response times
- Clear error messages
- Smooth animations

---

**Next Step**: Start implementing Phase 1 (Backend Core)
