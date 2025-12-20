# 🧪 Sentinel Vault POC - Quick Start

## Setup

```bash
# 1. Install dependencies
cd backend/poc
pip install -r requirements.txt

# 2. Asegúrate que Ollama esté corriendo
# Si no está corriendo:
# docker-compose up -d ollama
```

## Run Tests

### Test 1: Encryption
```bash
python encryption.py
```

**Expected output**:
- ✅ Key derivation: ~250ms
- ✅ Encryption: <2ms
- ✅ Decryption: <2ms

### Test 2: Ollama Analysis
```bash
python ollama_analysis.py
```

**Expected output**:
- ✅ Password analysis con scores
- ✅ Pattern detection (pet names, years, etc.)
- ✅ Latency <2s

### Test 3: Crypto Wallets
```bash
python crypto_wallet.py
```

**Expected output**:
- ✅ Seed phrase (24 palabras)
- ✅ Bitcoin address (empieza con '1')
- ✅ Ethereum address (checksum)
- ✅ Recovery works

## Next Steps

1. **FastAPI Backend** (día 6-7)
2. **Next.js Frontend** (día 8-9)
3. **Integration Testing** (día 10)

## Troubleshooting

### Ollama no responde
```bash
# Verificar que Ollama está corriendo
curl http://localhost:11434/api/tags

# Si no está, iniciar:
docker-compose up -d ollama
```

### Import errors
```bash
# Reinstalar dependencies
pip install -r requirements.txt --force-reinstall
```
