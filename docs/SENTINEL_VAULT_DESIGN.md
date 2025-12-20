# 🔐 Sentinel Vault - AI-Powered Password Manager

**Fecha**: 20-Dic-2024  
**Status**: 💡 Diseño inicial  
**Prioridad**: Alta (crítico para seguridad)

---

## 🎯 Visión

**Password manager integrado en Sentinel** con:
- ✅ Cifrado end-to-end (AES-256-GCM)
- ✅ Integración con IA (Ollama) para detección de passwords débiles
- ✅ Automatización con n8n para rotación automática
- ✅ Biometría + hardware keys (WebAuthn/FIDO2)
- ✅ Zero-knowledge architecture (ni admin puede ver passwords)
- ✅ **Crypto wallet management** (Bitcoin, Ethereum, etc.)
- ✅ **Blockchain-based audit trail** (immutable history)
- ✅ **Hardware wallet integration** (Ledger, Trezor)

---

## 🏗️ Arquitectura

### **Componentes**

```
┌─────────────────────────────────────────────────────────┐
│                    Sentinel Vault                        │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Frontend   │  │   Backend    │  │  Encryption  │  │
│  │   (Next.js)  │◄─┤   (FastAPI)  │◄─┤   (Rust)     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                  │                  │          │
│         ▼                  ▼                  ▼          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  WebAuthn    │  │  PostgreSQL  │  │    Redis     │  │
│  │  Biometrics  │  │  (Encrypted) │  │   (Cache)    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Ollama     │  │     n8n      │  │  TruthSync   │  │
│  │ (AI Audit)   │  │ (Auto-Rotate)│  │  (Verify)    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Blockchain  │  │ Crypto Wallet│  │ Hardware Key │  │
│  │ (Audit Log)  │  │  (BTC/ETH)   │  │ (Ledger/Trezor)│ │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🔒 Seguridad (Zero-Knowledge)

### **Encryption Flow**

```python
# 1. User Master Password (NUNCA se almacena)
master_password = input("Enter master password: ")

# 2. Derive encryption key (PBKDF2 + Argon2)
salt = os.urandom(32)
encryption_key = argon2.hash(
    password=master_password,
    salt=salt,
    iterations=100000,
    memory_cost=65536,  # 64MB
    parallelism=4
)

# 3. Encrypt vault data (AES-256-GCM)
cipher = AES.new(encryption_key, AES.MODE_GCM)
nonce = cipher.nonce
ciphertext, tag = cipher.encrypt_and_digest(vault_data)

# 4. Store SOLO datos cifrados
db.store({
    "user_id": user_id,
    "salt": base64.encode(salt),
    "nonce": base64.encode(nonce),
    "ciphertext": base64.encode(ciphertext),
    "tag": base64.encode(tag)
})

# ✅ Ni admin puede descifrar sin master password
```

---

## 🤖 Integración con IA (Ollama)

### **Feature 1: Password Strength Audit**

```python
# backend/app/services/vault_ai.py

async def audit_password_strength(password: str) -> dict:
    """
    Usa Ollama para analizar fortaleza de password
    """
    prompt = f"""
    Analyze this password strength:
    Password: {password}
    
    Evaluate:
    1. Length (min 20 chars)
    2. Complexity (uppercase, lowercase, numbers, symbols)
    3. Common patterns (dictionary words, sequences)
    4. Entropy (bits)
    
    Return JSON:
    {{
        "score": 0-100,
        "issues": ["list of issues"],
        "suggestions": ["how to improve"]
    }}
    """
    
    response = await ollama.generate(
        model="phi3:mini",
        prompt=prompt
    )
    
    return json.loads(response)
```

**UI Alert**:
```typescript
// frontend/src/components/PasswordStrengthMeter.tsx
if (audit.score < 70) {
  toast.error(`Weak password! ${audit.issues.join(', ')}`);
  toast.info(`Suggestion: ${audit.suggestions[0]}`);
}
```

---

### **Feature 2: Anomaly Detection**

```python
async def detect_anomalous_access(user_id: int, context: dict):
    """
    Detecta accesos sospechosos usando IA
    """
    # Obtener historial de accesos
    history = await db.get_access_history(user_id, limit=100)
    
    prompt = f"""
    Analyze if this access is anomalous:
    
    Current access:
    - Time: {context['timestamp']}
    - Location: {context['ip_location']}
    - Device: {context['device']}
    
    Historical pattern:
    {json.dumps(history)}
    
    Is this suspicious? Return JSON:
    {{
        "is_anomalous": true/false,
        "confidence": 0-100,
        "reason": "explanation"
    }}
    """
    
    response = await ollama.generate(model="phi3:mini", prompt=prompt)
    result = json.loads(response)
    
    if result['is_anomalous'] and result['confidence'] > 80:
        # Requiere MFA adicional
        await send_mfa_challenge(user_id)
        await alert_security_team(user_id, result['reason'])
```

---

## 🔄 Automatización con n8n

### **Workflow 1: Auto-Rotation de Passwords**

```javascript
// n8n workflow: Rotar passwords cada 90 días
{
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "cronExpression": "0 0 * * 0"  // Cada domingo
      }
    },
    {
      "name": "Get Expiring Passwords",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "query": "SELECT * FROM vault_items WHERE last_rotated < NOW() - INTERVAL '90 days'"
      }
    },
    {
      "name": "Generate New Password",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "code": `
          const crypto = require('crypto');
          return {
            new_password: crypto.randomBytes(32).toString('base64')
          };
        `
      }
    },
    {
      "name": "Update Service",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "{{$json.service_api}}/update-password",
        "method": "POST",
        "body": {
          "password": "{{$json.new_password}}"
        }
      }
    },
    {
      "name": "Update Vault",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "query": "UPDATE vault_items SET password = $1, last_rotated = NOW() WHERE id = $2",
        "values": ["{{$json.new_password}}", "{{$json.id}}"]
      }
    },
    {
      "name": "Notify User",
      "type": "n8n-nodes-base.sendEmail",
      "parameters": {
        "subject": "Password rotated for {{$json.service_name}}",
        "text": "Your password was automatically rotated for security."
      }
    }
  ]
}
```

---

### **Workflow 2: Breach Detection**

```javascript
// n8n workflow: Verificar si passwords están en breaches
{
  "nodes": [
    {
      "name": "Daily Check",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "cronExpression": "0 2 * * *"  // 2 AM diario
      }
    },
    {
      "name": "Get All Passwords",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "query": "SELECT id, password_hash FROM vault_items"
      }
    },
    {
      "name": "Check HaveIBeenPwned",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.pwnedpasswords.com/range/{{$json.hash_prefix}}",
        "method": "GET"
      }
    },
    {
      "name": "If Breached",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "boolean": [{
            "value1": "{{$json.is_breached}}",
            "value2": true
          }]
        }
      }
    },
    {
      "name": "Force Password Reset",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "query": "UPDATE vault_items SET force_reset = true WHERE id = $1"
      }
    },
    {
      "name": "Alert User",
      "type": "n8n-nodes-base.sendEmail",
      "parameters": {
        "subject": "⚠️ Password found in data breach!",
        "text": "Your password for {{$json.service}} was found in a breach. Please reset immediately."
      }
    }
  ]
}
```

---

## 🎨 UI/UX Features

### **1. Password Generator con IA**

```typescript
// frontend/src/components/PasswordGenerator.tsx
async function generatePassword(requirements: PasswordRequirements) {
  // Generar con crypto seguro
  const password = crypto.randomBytes(32).toString('base64');
  
  // Validar con IA
  const audit = await fetch('/api/vault/audit-password', {
    method: 'POST',
    body: JSON.stringify({ password })
  }).then(r => r.json());
  
  if (audit.score < 90) {
    // Regenerar si no es suficientemente fuerte
    return generatePassword(requirements);
  }
  
  return password;
}
```

---

### **2. Autofill Inteligente**

```typescript
// Browser extension integration
async function autofillPassword(domain: string) {
  // Buscar password para dominio
  const credentials = await fetch(`/api/vault/search?domain=${domain}`)
    .then(r => r.json());
  
  if (credentials.length === 0) {
    // Ofrecer crear nueva entrada
    return promptCreateEntry(domain);
  }
  
  if (credentials.length === 1) {
    // Auto-fill directo
    return fillForm(credentials[0]);
  }
  
  // Múltiples cuentas - mostrar selector
  return showAccountSelector(credentials);
}
```

---

### **3. Biometric Unlock**

```typescript
// WebAuthn integration
async function unlockWithBiometrics() {
  const credential = await navigator.credentials.get({
    publicKey: {
      challenge: new Uint8Array(32),
      rpId: "sentinel.com",
      userVerification: "required"
    }
  });
  
  // Verificar en backend
  const session = await fetch('/api/vault/unlock', {
    method: 'POST',
    body: JSON.stringify({ credential })
  }).then(r => r.json());
  
  // Descifrar vault en memoria (nunca en disco)
  const vault = await decryptVault(session.encryption_key);
  
  return vault;
}
```

---

## 📊 Database Schema

```sql
-- Vault items (encrypted)
CREATE TABLE vault_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- Encrypted data (AES-256-GCM)
    encrypted_data BYTEA NOT NULL,
    encryption_nonce BYTEA NOT NULL,
    encryption_tag BYTEA NOT NULL,
    
    -- Metadata (NOT encrypted)
    service_name VARCHAR(255) NOT NULL,
    service_url VARCHAR(500),
    username VARCHAR(255),
    category VARCHAR(50),  -- 'password', 'api_key', 'ssh_key', 'note'
    
    -- Security
    last_rotated TIMESTAMP DEFAULT NOW(),
    force_reset BOOLEAN DEFAULT FALSE,
    breach_detected BOOLEAN DEFAULT FALSE,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    accessed_at TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    
    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_service_name (service_name),
    INDEX idx_last_rotated (last_rotated)
);

-- Access history (for anomaly detection)
CREATE TABLE vault_access_history (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    vault_item_id UUID NOT NULL,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    device_fingerprint VARCHAR(255),
    location_country VARCHAR(2),
    location_city VARCHAR(100),
    
    -- Security
    mfa_used BOOLEAN DEFAULT FALSE,
    anomaly_score INTEGER,  -- 0-100
    
    -- Timestamp
    accessed_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_id (user_id),
    INDEX idx_accessed_at (accessed_at)
);

-- Master password metadata (NO password stored!)
CREATE TABLE vault_master_keys (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    
    -- For key derivation (PBKDF2 + Argon2)
    salt BYTEA NOT NULL,
    iterations INTEGER NOT NULL DEFAULT 100000,
    memory_cost INTEGER NOT NULL DEFAULT 65536,
    
    -- Biometric backup (WebAuthn)
    webauthn_credential_id BYTEA,
    webauthn_public_key BYTEA,
    
    -- Recovery
    recovery_key_hash BYTEA,  -- Hash of recovery key
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🚀 Roadmap de Implementación

### **Fase 1: Core Vault** (2-3 semanas)
- [ ] Backend API (FastAPI)
  - [ ] Encryption service (Rust)
  - [ ] CRUD operations
  - [ ] Zero-knowledge architecture
- [ ] Frontend UI (Next.js)
  - [ ] Vault dashboard
  - [ ] Password generator
  - [ ] Search & filter
- [ ] Database schema
- [ ] Tests (unit + integration)

### **Fase 2: AI Integration** (1-2 semanas)
- [ ] Ollama integration
  - [ ] Password strength audit
  - [ ] Anomaly detection
  - [ ] Breach prediction
- [ ] AI-powered suggestions
- [ ] Behavioral analysis

### **Fase 3: Automation** (1-2 semanas)
- [ ] n8n workflows
  - [ ] Auto-rotation
  - [ ] Breach detection
  - [ ] Compliance reports
- [ ] Scheduled tasks
- [ ] Email notifications

### **Fase 4: Advanced Features** (2-3 semanas)
- [ ] WebAuthn/FIDO2
  - [ ] Biometric unlock
  - [ ] Hardware key support
- [ ] Browser extension
  - [ ] Autofill
  - [ ] Password capture
- [ ] Mobile app (opcional)

### **Fase 5: Enterprise** (2-3 semanas)
- [ ] Team vaults (shared passwords)
- [ ] RBAC (role-based access)
- [ ] Audit logs
- [ ] Compliance reports (SOC 2, ISO 27001)

---

## 💰 Monetización

### **Pricing Tiers**

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0/mo | 50 passwords, basic encryption |
| **Pro** | $5/mo | Unlimited passwords, AI audit, biometrics |
| **Team** | $10/user/mo | Shared vaults, RBAC, n8n automation |
| **Enterprise** | Custom | SSO, compliance, dedicated support |

### **Revenue Potential**
- 1,000 Pro users = $5,000/mo
- 100 Team users (10 users/team) = $10,000/mo
- **Total**: $15,000/mo = $180,000/año

---

## 🎯 Diferenciadores vs Competencia

| Feature | 1Password | Bitwarden | **Sentinel Vault** |
|---------|-----------|-----------|---------------------|
| **AI Password Audit** | ❌ | ❌ | ✅ Ollama |
| **Auto-Rotation** | ⚠️ Manual | ⚠️ Manual | ✅ n8n automated |
| **Anomaly Detection** | ❌ | ❌ | ✅ AI-powered |
| **Zero-Knowledge** | ✅ | ✅ | ✅ |
| **Self-Hosted** | ❌ | ✅ | ✅ |
| **Integrated with AIOps** | ❌ | ❌ | ✅ Sentinel ecosystem |

**Unique Selling Point**: "El ÚNICO password manager con IA integrada y automatización completa"

---

## ✅ Próximos Pasos

1. **Validar idea** con equipo de seguridad
2. **Crear POC** (2 semanas)
3. **Beta testing** con equipo interno
4. **Launch** como feature de Sentinel

---

**Status**: 💡 Diseño completo, listo para implementación  
**Owner**: TBD  
**Timeline**: 8-12 semanas para MVP
