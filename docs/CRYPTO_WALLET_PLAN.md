# 🪙 Crypto Wallet - Implementation Plan

**Objetivo**: Implementar crypto wallet funcional con multi-chain support  
**Scope**: Solo crypto wallet (sin password manager por ahora)  
**Timeline**: 1 semana

---

## ✅ Features to Implement

### **Core Features**:
1. ✅ HD wallet generation (BIP39/BIP44)
2. ✅ Multi-chain support (Bitcoin, Ethereum, Solana, Polygon)
3. ✅ Seed phrase backup/recovery
4. ✅ Address generation
5. ✅ Balance tracking (read-only)
6. ✅ Transaction history (read-only)

### **Security**:
1. ✅ Seed phrase encryption (Argon2id + AES-256-GCM)
2. ✅ Master password protection
3. ✅ Never expose private keys in UI
4. ✅ Secure storage (PostgreSQL encrypted)

### **Out of Scope** (v1.1):
- ❌ Transaction signing (v1.1)
- ❌ Hardware wallet integration (v1.1)
- ❌ Multi-sig wallets (v1.1)
- ❌ DeFi integration (v1.1)

---

## 🗄️ Database Schema

```sql
-- Users table (simplified)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    salt BYTEA NOT NULL,  -- For Argon2id
    created_at TIMESTAMP DEFAULT NOW()
);

-- Crypto wallets table
CREATE TABLE crypto_wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Wallet metadata
    name VARCHAR(255) NOT NULL,
    chain VARCHAR(50) NOT NULL,  -- 'bitcoin', 'ethereum', 'solana', 'polygon'
    
    -- Encrypted seed phrase (cifrado con master password)
    encrypted_seed JSONB NOT NULL,  -- {nonce, ciphertext}
    
    -- Public data
    address VARCHAR(255) NOT NULL,
    derivation_path VARCHAR(100) NOT NULL,
    
    -- Balance cache (actualizado periódicamente)
    balance_cache JSONB,  -- {amount, usd_value, last_updated}
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_wallets (user_id),
    INDEX idx_chain (chain)
);
```

---

## 📁 Project Structure

```
sentinel-vault-crypto/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app
│   │   ├── config.py
│   │   ├── database.py
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── crypto_wallet.py
│   │   │
│   │   ├── services/
│   │   │   ├── crypto.py           # Wallet generation
│   │   │   ├── blockchain.py       # Balance/transactions
│   │   │   └── encryption.py       # Argon2id + AES-256-GCM
│   │   │
│   │   └── api/
│   │       ├── auth.py
│   │       └── crypto.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   │   └── login/
│   │   │   └── (dashboard)/
│   │   │       └── wallets/
│   │   │
│   │   ├── components/
│   │   │   └── wallet/
│   │   │       ├── WalletCard.tsx
│   │   │       ├── GenerateWallet.tsx
│   │   │       └── RecoverWallet.tsx
│   │   │
│   │   └── lib/
│   │       ├── api.ts
│   │       └── crypto.ts           # Client-side encryption
│   │
│   └── package.json
│
└── docker-compose.yml
```

---

## 🚀 Implementation Steps

### **Step 1: Backend - Crypto Service** ✅ (Ya tenemos POC)
Mejorar `backend/poc/crypto_wallet.py`:
- [x] Bitcoin support
- [x] Ethereum support
- [ ] Solana support
- [ ] Polygon support (usa mismo código que Ethereum)

### **Step 2: Backend - Blockchain Integration**
Crear `backend/app/services/blockchain.py`:
- [ ] Bitcoin balance (Blockchain.info API)
- [ ] Ethereum balance (Infura/Alchemy)
- [ ] Solana balance (Solana RPC)
- [ ] Transaction history

### **Step 3: Backend - Database Integration**
- [ ] Create SQLAlchemy models
- [ ] Add wallet CRUD endpoints
- [ ] Encrypt seed phrase before storing

### **Step 4: Frontend - Wallet UI**
- [ ] Wallet dashboard
- [ ] Generate wallet flow
- [ ] Recover wallet flow
- [ ] Display balances

### **Step 5: Testing**
- [ ] Test wallet generation
- [ ] Test recovery
- [ ] Test balance fetching
- [ ] Test encryption/decryption

---

## 🎯 MVP Deliverables

1. ✅ **Working wallet generation** (Bitcoin, Ethereum, Solana, Polygon)
2. ✅ **Seed phrase encryption** (Argon2id + AES-256-GCM)
3. ✅ **Balance tracking** (real-time from blockchain)
4. ✅ **Transaction history** (read-only)
5. ✅ **Beautiful UI** (Next.js + Tailwind)

---

## 📊 Chains to Support

| Chain | Derivation Path | Address Format | Balance API |
|-------|----------------|----------------|-------------|
| Bitcoin | m/44'/0'/0'/0/0 | P2PKH (1...) | Blockchain.info |
| Ethereum | m/44'/60'/0'/0/0 | 0x... (checksum) | Infura/Alchemy |
| Polygon | m/44'/60'/0'/0/0 | 0x... (same as ETH) | Polygon RPC |
| Solana | m/44'/501'/0'/0/0 | Base58 | Solana RPC |

---

**Next**: Empezar con Step 2 (Blockchain Integration) para tener balances reales
