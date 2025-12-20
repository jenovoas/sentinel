"""
Sentinel Vault POC - FastAPI Backend
REST API para password manager + crypto wallets
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

from encryption import VaultEncryption
from ollama_analysis import PasswordAnalyzer
from crypto_wallet import CryptoWallet


# FastAPI app
app = FastAPI(
    title="Sentinel Vault POC",
    description="Password manager + crypto wallets con Ollama integration",
    version="0.1.0"
)

# CORS (para desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
vault = VaultEncryption()
analyzer = PasswordAnalyzer()
crypto = CryptoWallet()

# In-memory storage (POC only - en producción usar PostgreSQL)
vault_storage = {}


# ============================================================================
# Models
# ============================================================================

class UnlockRequest(BaseModel):
    master_password: str

class SavePasswordRequest(BaseModel):
    master_password: str
    service: str
    username: str
    password: str

class GetPasswordRequest(BaseModel):
    master_password: str
    service: str

class AnalyzePasswordRequest(BaseModel):
    password: str


# ============================================================================
# Endpoints - Vault
# ============================================================================

@app.post("/vault/unlock")
async def unlock_vault(req: UnlockRequest):
    """
    Unlock vault con master password
    Retorna success si password es correcto
    """
    try:
        # Obtener o crear salt
        salt = vault_storage.get("salt")
        if not salt:
            # Primera vez - generar salt
            salt = os.urandom(32)
            vault_storage["salt"] = salt.hex()
        else:
            salt = bytes.fromhex(salt)
        
        # Derivar key (esto valida el password)
        key = vault.derive_key(req.master_password, salt)
        
        # En producción, esto iría en session/JWT
        # Para POC, retornamos success
        
        return {
            "success": True,
            "message": "Vault unlocked successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vault/save")
async def save_password(req: SavePasswordRequest):
    """Guardar password cifrada en vault"""
    try:
        # Derivar key desde master password
        salt = bytes.fromhex(vault_storage["salt"])
        key = vault.derive_key(req.master_password, salt)
        
        # Encrypt password
        encrypted = vault.encrypt(req.password, key)
        
        # Guardar en storage
        if "passwords" not in vault_storage:
            vault_storage["passwords"] = {}
        
        vault_storage["passwords"][req.service] = {
            "username": req.username,
            "encrypted_password": encrypted
        }
        
        return {
            "success": True,
            "message": f"Password for {req.service} saved successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vault/get")
async def get_password(req: GetPasswordRequest):
    """Obtener password decrypted desde vault"""
    try:
        # Verificar que servicio existe
        if "passwords" not in vault_storage or req.service not in vault_storage["passwords"]:
            raise HTTPException(status_code=404, detail=f"Password for {req.service} not found")
        
        # Derivar key
        salt = bytes.fromhex(vault_storage["salt"])
        key = vault.derive_key(req.master_password, salt)
        
        # Decrypt password
        stored = vault_storage["passwords"][req.service]
        decrypted = vault.decrypt(stored["encrypted_password"], key)
        
        return {
            "success": True,
            "service": req.service,
            "username": stored["username"],
            "password": decrypted
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/vault/list")
async def list_passwords():
    """Lista todos los servicios guardados (sin passwords)"""
    if "passwords" not in vault_storage:
        return {"services": []}
    
    services = [
        {
            "service": service,
            "username": data["username"]
        }
        for service, data in vault_storage["passwords"].items()
    ]
    
    return {"services": services}


# ============================================================================
# Endpoints - Password Analysis (Ollama)
# ============================================================================

@app.post("/analyze/password")
async def analyze_password(req: AnalyzePasswordRequest):
    """Analizar fortaleza de password con Ollama"""
    try:
        result = await analyzer.analyze_strength(req.password)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Endpoints - Crypto Wallets
# ============================================================================

@app.post("/crypto/generate")
async def generate_crypto_wallet():
    """Generar nuevo crypto wallet (Bitcoin + Ethereum)"""
    try:
        wallet = crypto.generate_wallet()
        
        # ⚠️ En producción, seed phrase debe cifrarse con master password
        # y mostrarse SOLO UNA VEZ
        
        return wallet
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/crypto/recover")
async def recover_crypto_wallet(seed_phrase: str):
    """Recuperar wallet desde seed phrase"""
    try:
        wallet = crypto.recover_wallet(seed_phrase)
        return wallet
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Endpoints - Benchmarking
# ============================================================================

@app.get("/benchmark/encryption")
async def benchmark_encryption():
    """Benchmark de encryption performance"""
    try:
        kd_bench = vault.benchmark_key_derivation(10)
        enc_bench = vault.benchmark_encryption(100)
        
        return {
            "key_derivation": kd_bench,
            "encryption": enc_bench
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/benchmark/ollama")
async def benchmark_ollama():
    """Benchmark de Ollama analysis"""
    try:
        test_passwords = [
            "password123",
            "MyDog2024",
            "MyP@ssw0rd2024",
            "Xk9$mQ2#vL8@pR4&nT6"
        ]
        
        result = await analyzer.benchmark(test_passwords, iterations=3)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Sentinel Vault POC",
        "version": "0.1.0"
    }


@app.get("/")
async def root():
    """Root endpoint con info de API"""
    return {
        "message": "Sentinel Vault POC API",
        "version": "0.1.0",
        "endpoints": {
            "vault": [
                "POST /vault/unlock",
                "POST /vault/save",
                "POST /vault/get",
                "GET /vault/list"
            ],
            "analysis": [
                "POST /analyze/password"
            ],
            "crypto": [
                "POST /crypto/generate",
                "POST /crypto/recover"
            ],
            "benchmarks": [
                "GET /benchmark/encryption",
                "GET /benchmark/ollama"
            ]
        },
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Sentinel Vault POC API...")
    print("📚 API docs: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
