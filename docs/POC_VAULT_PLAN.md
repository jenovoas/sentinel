# 🧪 POC: Sentinel Vault - Password Manager + Crypto Integration

**Objetivo**: Validar viabilidad técnica de la integración passwords + crypto + Ollama  
**Duración**: 2 semanas  
**Resultado esperado**: Demo funcional con métricas reales

---

## 🎯 Scope del POC

### ✅ **Incluido**
1. Password encryption/decryption (Argon2id + AES-256-GCM)
2. Ollama integration para password analysis
3. Crypto wallet generation (Bitcoin + Ethereum)
4. Basic UI (Next.js)
5. Performance benchmarking

### ❌ **Excluido** (para MVP posterior)
- Blockchain audit trail (Polygon)
- Hardware wallet integration (Ledger/Trezor)
- Multi-user support
- Production deployment

---

## 📅 Plan de 2 Semanas

### **Semana 1: Backend Core**

#### Día 1-2: Encryption Service (Python)
```python
# backend/poc/encryption.py
from argon2 import PasswordHasher
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

class VaultEncryption:
    def __init__(self):
        self.ph = PasswordHasher(
            time_cost=3,
            memory_cost=65536,  # 64MB
            parallelism=4
        )
    
    def derive_key(self, master_password: str, salt: bytes) -> bytes:
        """Deriva encryption key desde master password"""
        from argon2.low_level import hash_secret_raw, Type
        
        key = hash_secret_raw(
            secret=master_password.encode(),
            salt=salt,
            time_cost=3,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            type=Type.ID
        )
        return key
    
    def encrypt(self, data: str, key: bytes) -> dict:
        """Encrypt data con AES-256-GCM"""
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, data.encode(), None)
        
        return {
            "nonce": nonce.hex(),
            "ciphertext": ciphertext.hex()
        }
    
    def decrypt(self, encrypted: dict, key: bytes) -> str:
        """Decrypt data"""
        aesgcm = AESGCM(key)
        nonce = bytes.fromhex(encrypted["nonce"])
        ciphertext = bytes.fromhex(encrypted["ciphertext"])
        
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode()
```

**Testing**:
```python
# Test 1: Encryption roundtrip
master_password = "super-secret-password-123"
salt = os.urandom(32)

vault = VaultEncryption()
key = vault.derive_key(master_password, salt)

# Encrypt
encrypted = vault.encrypt("my-github-password", key)
print(f"Encrypted: {encrypted}")

# Decrypt
decrypted = vault.decrypt(encrypted, key)
assert decrypted == "my-github-password"
print("✅ Encryption works!")

# Test 2: Performance
import time
start = time.time()
for _ in range(100):
    key = vault.derive_key(master_password, salt)
elapsed = time.time() - start
print(f"Key derivation: {elapsed/100*1000:.2f}ms per operation")
```

**Métricas esperadas**:
- Key derivation: ~250ms (Argon2id con 64MB)
- Encryption: <2ms
- Decryption: <2ms

---

#### Día 3-4: Ollama Integration
```python
# backend/poc/ollama_analysis.py
import httpx
import json

class PasswordAnalyzer:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
    
    async def analyze_strength(self, password: str) -> dict:
        """Analiza fortaleza de password con Ollama"""
        prompt = f"""
Analyze this password strength and return ONLY valid JSON:

Password: {password}

Evaluate:
1. Length (minimum 20 characters recommended)
2. Complexity (uppercase, lowercase, numbers, symbols)
3. Common patterns (dictionary words, sequences like 123, abc)
4. Entropy estimation

Return JSON format:
{{
  "score": <0-100>,
  "length_ok": <true/false>,
  "has_uppercase": <true/false>,
  "has_lowercase": <true/false>,
  "has_numbers": <true/false>,
  "has_symbols": <true/false>,
  "has_patterns": <true/false>,
  "issues": ["list of issues"],
  "suggestions": ["how to improve"]
}}
"""
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                self.ollama_url,
                json={
                    "model": "phi3:mini",
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            result = response.json()
            # Extraer JSON del response
            text = result.get("response", "")
            
            # Parse JSON (puede venir con texto adicional)
            start = text.find("{")
            end = text.rfind("}") + 1
            json_str = text[start:end]
            
            return json.loads(json_str)
```

**Testing**:
```python
# Test con diferentes passwords
analyzer = PasswordAnalyzer()

passwords = [
    "password123",           # Débil
    "MyP@ssw0rd2024",       # Medio
    "Xk9$mQ2#vL8@pR4&nT6",  # Fuerte
]

for pwd in passwords:
    result = await analyzer.analyze_strength(pwd)
    print(f"\nPassword: {pwd}")
    print(f"Score: {result['score']}/100")
    print(f"Issues: {result['issues']}")
    print(f"Suggestions: {result['suggestions']}")
```

**Métricas esperadas**:
- Latencia: <1s (Ollama local)
- Accuracy: Validar manualmente con 20 passwords

---

#### Día 5: Crypto Wallet Generation
```python
# backend/poc/crypto_wallet.py
from mnemonic import Mnemonic
from bip32 import BIP32
from web3 import Web3

class CryptoWallet:
    def __init__(self):
        self.mnemo = Mnemonic("english")
    
    def generate_wallet(self) -> dict:
        """Genera HD wallet con seed phrase"""
        # Generar seed phrase (24 palabras)
        seed_phrase = self.mnemo.generate(strength=256)
        seed = self.mnemo.to_seed(seed_phrase)
        
        # Derivar master key
        bip32 = BIP32.from_seed(seed)
        
        # Bitcoin wallet (BIP44: m/44'/0'/0'/0/0)
        btc_key = bip32.get_privkey_from_path("m/44'/0'/0'/0/0")
        btc_pubkey = bip32.get_pubkey_from_path("m/44'/0'/0'/0/0")
        
        # Ethereum wallet (BIP44: m/44'/60'/0'/0/0)
        eth_key = bip32.get_privkey_from_path("m/44'/60'/0'/0/0")
        eth_pubkey = bip32.get_pubkey_from_path("m/44'/60'/0'/0/0")
        
        # Ethereum address
        w3 = Web3()
        eth_address = w3.to_checksum_address(
            w3.keccak(eth_pubkey[1:])[-20:].hex()
        )
        
        return {
            "seed_phrase": seed_phrase,  # MOSTRAR SOLO UNA VEZ
            "bitcoin": {
                "address": self._btc_address_from_pubkey(btc_pubkey),
                "path": "m/44'/0'/0'/0/0"
            },
            "ethereum": {
                "address": eth_address,
                "path": "m/44'/60'/0'/0/0"
            }
        }
    
    def _btc_address_from_pubkey(self, pubkey: bytes) -> str:
        """Convierte pubkey a Bitcoin address (P2PKH)"""
        import hashlib
        
        # SHA-256
        sha256 = hashlib.sha256(pubkey).digest()
        
        # RIPEMD-160
        ripemd160 = hashlib.new('ripemd160', sha256).digest()
        
        # Add version byte (0x00 for mainnet)
        versioned = b'\x00' + ripemd160
        
        # Double SHA-256 for checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
        
        # Base58 encode
        address_bytes = versioned + checksum
        return self._base58_encode(address_bytes)
    
    def _base58_encode(self, data: bytes) -> str:
        """Base58 encoding"""
        alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        num = int.from_bytes(data, 'big')
        
        encoded = ""
        while num > 0:
            num, remainder = divmod(num, 58)
            encoded = alphabet[remainder] + encoded
        
        # Add leading zeros
        for byte in data:
            if byte == 0:
                encoded = '1' + encoded
            else:
                break
        
        return encoded
```

**Testing**:
```python
# Test wallet generation
wallet = CryptoWallet()
result = wallet.generate_wallet()

print(f"Seed Phrase: {result['seed_phrase']}")
print(f"Bitcoin Address: {result['bitcoin']['address']}")
print(f"Ethereum Address: {result['ethereum']['address']}")

# Validar que seed phrase funciona
# Regenerar wallet con mismo seed
seed2 = wallet.mnemo.to_seed(result['seed_phrase'])
bip32_2 = BIP32.from_seed(seed2)
eth_key_2 = bip32_2.get_privkey_from_path("m/44'/60'/0'/0/0")

# Debe generar misma address
assert result['ethereum']['address'] == wallet._eth_address_from_key(eth_key_2)
print("✅ Seed phrase recovery works!")
```

---

### **Semana 2: Frontend + Integration**

#### Día 6-7: FastAPI Backend
```python
# backend/poc/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from encryption import VaultEncryption
from ollama_analysis import PasswordAnalyzer
from crypto_wallet import CryptoWallet
import os

app = FastAPI()

vault = VaultEncryption()
analyzer = PasswordAnalyzer()
crypto = CryptoWallet()

# In-memory storage (POC only)
vault_storage = {}

class UnlockRequest(BaseModel):
    master_password: str

class SavePasswordRequest(BaseModel):
    master_password: str
    service: str
    password: str

@app.post("/vault/unlock")
async def unlock_vault(req: UnlockRequest):
    """Unlock vault y retornar encryption key"""
    salt = vault_storage.get("salt")
    if not salt:
        # First time - generate salt
        salt = os.urandom(32)
        vault_storage["salt"] = salt.hex()
    else:
        salt = bytes.fromhex(salt)
    
    key = vault.derive_key(req.master_password, salt)
    
    return {
        "success": True,
        "key": key.hex()  # En producción, esto va en session
    }

@app.post("/vault/save")
async def save_password(req: SavePasswordRequest):
    """Guardar password cifrada"""
    salt = bytes.fromhex(vault_storage["salt"])
    key = vault.derive_key(req.master_password, salt)
    
    encrypted = vault.encrypt(req.password, key)
    
    # Guardar en storage
    if "passwords" not in vault_storage:
        vault_storage["passwords"] = {}
    
    vault_storage["passwords"][req.service] = encrypted
    
    return {"success": True}

@app.post("/vault/analyze")
async def analyze_password(password: str):
    """Analizar fortaleza con Ollama"""
    result = await analyzer.analyze_strength(password)
    return result

@app.post("/crypto/generate")
async def generate_crypto_wallet():
    """Generar crypto wallet"""
    wallet = crypto.generate_wallet()
    return wallet
```

---

#### Día 8-9: Next.js Frontend
```typescript
// frontend/poc/src/app/vault/page.tsx
'use client';

import { useState } from 'react';

export default function VaultPage() {
  const [masterPassword, setMasterPassword] = useState('');
  const [unlocked, setUnlocked] = useState(false);
  const [password, setPassword] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [wallet, setWallet] = useState(null);

  async function unlockVault() {
    const res = await fetch('http://localhost:8000/vault/unlock', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ master_password: masterPassword })
    });
    
    if (res.ok) {
      setUnlocked(true);
    }
  }

  async function analyzePassword() {
    const res = await fetch(`http://localhost:8000/vault/analyze?password=${password}`);
    const data = await res.json();
    setAnalysis(data);
  }

  async function generateWallet() {
    const res = await fetch('http://localhost:8000/crypto/generate', {
      method: 'POST'
    });
    const data = await res.json();
    setWallet(data);
  }

  if (!unlocked) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Unlock Vault</h1>
        <input
          type="password"
          value={masterPassword}
          onChange={(e) => setMasterPassword(e.target.value)}
          className="border p-2 rounded"
          placeholder="Master Password"
        />
        <button onClick={unlockVault} className="ml-2 bg-blue-500 text-white px-4 py-2 rounded">
          Unlock
        </button>
      </div>
    );
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Sentinel Vault POC</h1>
      
      {/* Password Analysis */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Password Analysis (Ollama)</h2>
        <input
          type="text"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="border p-2 rounded w-full"
          placeholder="Enter password to analyze"
        />
        <button onClick={analyzePassword} className="mt-2 bg-green-500 text-white px-4 py-2 rounded">
          Analyze
        </button>
        
        {analysis && (
          <div className="mt-4 p-4 bg-gray-100 rounded">
            <p>Score: {analysis.score}/100</p>
            <p>Issues: {analysis.issues.join(', ')}</p>
            <p>Suggestions: {analysis.suggestions.join(', ')}</p>
          </div>
        )}
      </div>
      
      {/* Crypto Wallet */}
      <div>
        <h2 className="text-xl font-semibold mb-2">Generate Crypto Wallet</h2>
        <button onClick={generateWallet} className="bg-purple-500 text-white px-4 py-2 rounded">
          Generate Wallet
        </button>
        
        {wallet && (
          <div className="mt-4 p-4 bg-gray-100 rounded">
            <p className="font-bold text-red-600">⚠️ Save this seed phrase (show only once):</p>
            <p className="font-mono text-sm">{wallet.seed_phrase}</p>
            <p className="mt-2">Bitcoin: {wallet.bitcoin.address}</p>
            <p>Ethereum: {wallet.ethereum.address}</p>
          </div>
        )}
      </div>
    </div>
  );
}
```

---

#### Día 10: Benchmarking
```python
# backend/poc/benchmark.py
import time
import asyncio
from encryption import VaultEncryption
from ollama_analysis import PasswordAnalyzer

async def benchmark():
    vault = VaultEncryption()
    analyzer = PasswordAnalyzer()
    
    # Test 1: Key Derivation
    print("=== Key Derivation Benchmark ===")
    master_password = "test-password-123"
    salt = os.urandom(32)
    
    times = []
    for _ in range(10):
        start = time.time()
        key = vault.derive_key(master_password, salt)
        elapsed = time.time() - start
        times.append(elapsed * 1000)  # ms
    
    print(f"Average: {sum(times)/len(times):.2f}ms")
    print(f"Min: {min(times):.2f}ms")
    print(f"Max: {max(times):.2f}ms")
    
    # Test 2: Encryption
    print("\n=== Encryption Benchmark ===")
    data = "my-super-secret-password"
    
    times = []
    for _ in range(100):
        start = time.time()
        encrypted = vault.encrypt(data, key)
        elapsed = time.time() - start
        times.append(elapsed * 1000)
    
    print(f"Average: {sum(times)/len(times):.2f}ms")
    
    # Test 3: Ollama Analysis
    print("\n=== Ollama Analysis Benchmark ===")
    
    times = []
    for _ in range(5):
        start = time.time()
        result = await analyzer.analyze_strength("MyP@ssw0rd2024")
        elapsed = time.time() - start
        times.append(elapsed * 1000)
    
    print(f"Average: {sum(times)/len(times):.2f}ms")

if __name__ == "__main__":
    asyncio.run(benchmark())
```

---

## 📊 Métricas a Validar

### Performance
- [ ] Key derivation: <300ms
- [ ] Encryption: <5ms
- [ ] Decryption: <5ms
- [ ] Ollama analysis: <2s
- [ ] Wallet generation: <100ms

### Functionality
- [ ] Password encrypt/decrypt roundtrip works
- [ ] Ollama analysis returns valid JSON
- [ ] Ollama detects weak passwords
- [ ] Crypto wallet generation works
- [ ] Seed phrase recovery works
- [ ] Bitcoin address is valid
- [ ] Ethereum address is valid

### Integration
- [ ] Frontend ↔ Backend communication works
- [ ] Master password unlock works
- [ ] UI is usable (basic)

---

## ✅ Entregables

1. **Working Demo** (video 2-3 min)
2. **Benchmark Results** (documento con métricas reales)
3. **Code** (GitHub repo o branch)
4. **Lessons Learned** (qué funcionó, qué no)

---

## 🚀 Siguiente Paso

**¿Empezamos con el POC?** Puedo ayudarte a:
1. Crear los archivos base
2. Setup del entorno
3. Debugging si algo falla
4. Análisis de resultados

¿Por dónde quieres empezar?
