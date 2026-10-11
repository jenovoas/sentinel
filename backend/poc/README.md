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

## FastAPI Backend

### Start API Server
```bash
python main.py
```

**API will be available at**:
- 🌐 http://localhost:8000
- 📚 Docs: http://localhost:8000/docs
- 🔍 Health: http://localhost:8000/health

### Test API
```bash
# In another terminal
python test_api.py
```

**Tests**:
1. ✅ Health check
2. ✅ Vault flow (unlock → save → list → get)
3. ✅ Password analysis (Ollama)
4. ✅ Crypto wallet generation + recovery
5. ✅ Benchmarks

### API Endpoints

**Vault**:
- `POST /vault/unlock` - Unlock vault con master password
- `POST /vault/save` - Save encrypted password
- `POST /vault/get` - Get decrypted password
- `GET /vault/list` - List all services

**Analysis**:
- `POST /analyze/password` - Analyze password strength (Ollama)

**Crypto**:
- `POST /crypto/generate` - Generate new wallet
- `POST /crypto/recover` - Recover from seed phrase

**Benchmarks**:
- `GET /benchmark/encryption` - Encryption performance
- `GET /benchmark/ollama` - Ollama performance

## Next Steps

1. **Next.js Frontend** (día 8-9)
2. **Integration Testing** (día 10)
3. **Performance Validation** (benchmarks reales)

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

### Port 8000 already in use
```bash
# Cambiar puerto en main.py:
uvicorn.run(app, host="0.0.0.0", port=8001)
```

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
