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
    """Generar nuevo crypto wallet (Bitcoin + Ethereum + Polygon + Solana)"""
    try:
        from wallet_complete import CryptoWalletComplete
        
        wallet_service = CryptoWalletComplete()
        wallet = await wallet_service.create_wallet()
        await wallet_service.close()
        
        # ⚠️ En producción, seed phrase debe cifrarse con master password
        # y mostrarse SOLO UNA VEZ
        
        return wallet
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/crypto/recover")
async def recover_crypto_wallet(seed_phrase: str):
    """Recuperar wallet desde seed phrase"""
    try:
        from crypto_wallet import CryptoWallet
        
        crypto = CryptoWallet()
        wallet = crypto.recover_wallet(seed_phrase)
        
        return wallet
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/crypto/balance/{chain}/{address}")
async def get_crypto_balance(chain: str, address: str):
    """Obtener balance de una wallet específica"""
    try:
        from blockchain import BlockchainService
        
        blockchain = BlockchainService()
        balance = await blockchain.get_balance(chain, address)
        await blockchain.close()
        
        return balance
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/crypto/portfolio")
async def get_portfolio_value():
    """
    Obtener valor total del portfolio
    (En producción, esto vendría de la DB del usuario)
    """
    try:
        # Mock data para demo
        # En producción, obtener wallets del usuario desde DB
        mock_wallets = {
            "bitcoin": {
                "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
                "balance": 0,
                "balance_usd": 0
            },
            "ethereum": {
                "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
                "balance": 0,
                "balance_usd": 0
            }
        }
        
        from wallet_complete import CryptoWalletComplete
        
        wallet_service = CryptoWalletComplete()
        portfolio = await wallet_service.get_portfolio_value(mock_wallets)
        await wallet_service.close()
        
        return portfolio
    
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
# Endpoints - Documents
# ============================================================================

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile,
    category: str = "general",
    tags: str = ""  # Comma-separated
):
    """Upload encrypted document"""
    try:
        from document_service import DocumentService
        from database import SessionLocal, Document
        import secrets
        
        # Read file
        file_data = await file.read()
        
        # Generate encryption key (in production, use user's key)
        # For POC, we'll use a test key
        encryption_key = secrets.token_bytes(32)
        
        # Save document
        doc_service = DocumentService()
        metadata = doc_service.save_document(
            file_data=file_data,
            filename=file.filename,
            encryption_key=encryption_key,
            category=category,
            tags=tags.split(",") if tags else []
        )
        
        # Save metadata to database
        db = SessionLocal()
        db_doc = Document(
            id=metadata['id'],
            user_id='test-user',  # In production, get from auth
            filename=metadata['filename'],
            file_path=metadata['file_path'],
            file_hash=metadata['file_hash'],
            file_size=metadata['file_size'],
            category=metadata['category'],
            tags=metadata['tags'],
            nonce=metadata['nonce']
        )
        db.add(db_doc)
        db.commit()
        db.close()
        
        return {
            "success": True,
            "document": {
                "id": metadata['id'],
                "filename": metadata['filename'],
                "size": metadata['file_size'],
                "category": metadata['category'],
                "tags": metadata['tags']
            },
            "message": "Document uploaded and encrypted successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents/{doc_id}")
async def download_document(doc_id: str):
    """Download and decrypt document"""
    try:
        from document_service import DocumentService
        import secrets
        
        # In production, get user's encryption key
        # For POC, use test key
        encryption_key = secrets.token_bytes(32)
        
        # Load document
        doc_service = DocumentService()
        # Note: In production, get nonce from database
        # For POC, this will fail - need to implement database storage
        
        return {
            "success": False,
            "message": "Download endpoint needs database integration"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
async def list_documents():
    """List all documents (metadata only)"""
    try:
        from database import SessionLocal, Document
        
        db = SessionLocal()
        documents = db.query(Document).filter_by(user_id='test-user').all()
        db.close()
        
        return {
            "documents": [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "size": doc.file_size,
                    "category": doc.category,
                    "tags": doc.tags,
                    "created_at": doc.created_at.isoformat()
                }
                for doc in documents
            ],
            "count": len(documents)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Endpoints - Notes
# ============================================================================

@app.post("/notes")
async def create_note(
    title: str,
    content: str,
    tags: str = ""  # Comma-separated
):
    """Create encrypted note"""
    try:
        from notes_service import NotesService
        from database import SessionLocal, Note
        import secrets
        
        # Generate encryption key (in production, use user's key)
        encryption_key = secrets.token_bytes(32)
        
        # Create note
        notes_service = NotesService()
        note_data = notes_service.create_note(
            title=title,
            content=content,
            encryption_key=encryption_key,
            tags=tags.split(",") if tags else []
        )
        
        # Save to database
        db = SessionLocal()
        db_note = Note(
            id=note_data['id'],
            user_id='test-user',
            title=note_data['title'],
            encrypted_content=note_data['ciphertext'],
            nonce=note_data['nonce'],
            content_length=note_data['content_length'],
            links=note_data['links'],
            tags=note_data['tags']
        )
        db.add(db_note)
        db.commit()
        db.close()
        
        return {
            "success": True,
            "note": {
                "id": note_data['id'],
                "title": note_data['title'],
                "content_length": note_data['content_length'],
                "links": note_data['links'],
                "tags": note_data['tags']
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notes")
async def list_notes():
    """List all notes (metadata only)"""
    try:
        from database import SessionLocal, Note
        
        db = SessionLocal()
        notes = db.query(Note).filter_by(user_id='test-user').all()
        db.close()
        
        return {
            "notes": [
                {
                    "id": note.id,
                    "title": note.title,
                    "content_length": note.content_length,
                    "links": note.links,
                    "tags": note.tags,
                    "created_at": note.created_at.isoformat(),
                    "updated_at": note.updated_at.isoformat()
                }
                for note in notes
            ],
            "count": len(notes)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notes/{note_id}")
async def get_note(note_id: str):
    """Get note content (decrypted)"""
    try:
        from notes_service import NotesService
        from database import SessionLocal, Note
        import secrets
        
        # Get note from database
        db = SessionLocal()
        db_note = db.query(Note).filter_by(id=note_id, user_id='test-user').first()
        db.close()
        
        if not db_note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Decrypt content (in production, use user's key)
        encryption_key = secrets.token_bytes(32)
        notes_service = NotesService()
        
        # For now, return metadata (decryption needs same key as encryption)
        return {
            "id": db_note.id,
            "title": db_note.title,
            "content_length": db_note.content_length,
            "links": db_note.links,
            "tags": db_note.tags,
            "created_at": db_note.created_at.isoformat(),
            "message": "Decryption requires user's encryption key"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/notes/{note_id}")
async def update_note(note_id: str, content: str):
    """Update note content"""
    try:
        from notes_service import NotesService
        from database import SessionLocal, Note
        import secrets
        
        # Generate encryption key (in production, use user's key)
        encryption_key = secrets.token_bytes(32)
        
        # Update note
        notes_service = NotesService()
        updated_data = notes_service.update_note(note_id, content, encryption_key)
        
        # Update database
        db = SessionLocal()
        db_note = db.query(Note).filter_by(id=note_id, user_id='test-user').first()
        
        if not db_note:
            db.close()
            raise HTTPException(status_code=404, detail="Note not found")
        
        db_note.encrypted_content = updated_data['ciphertext']
        db_note.nonce = updated_data['nonce']
        db_note.content_length = updated_data['content_length']
        db_note.links = updated_data['links']
        db_note.tags = updated_data['tags']
        db_note.updated_at = datetime.utcnow()
        
        db.commit()
        db.close()
        
        return {
            "success": True,
            "note": {
                "id": note_id,
                "content_length": updated_data['content_length'],
                "links": updated_data['links'],
                "tags": updated_data['tags']
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    """Delete note"""
    try:
        from database import SessionLocal, Note
        
        db = SessionLocal()
        db_note = db.query(Note).filter_by(id=note_id, user_id='test-user').first()
        
        if not db_note:
            db.close()
            raise HTTPException(status_code=404, detail="Note not found")
        
        db.delete(db_note)
        db.commit()
        db.close()
        
        return {"success": True, "message": "Note deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Endpoints - Terminal
# ============================================================================

@app.post("/terminal/execute")
async def execute_terminal_command(command: str):
    """Execute vault command"""
    try:
        from terminal_service import TerminalService
        
        service = TerminalService()
        result = service.execute(command)
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health Check
# ============================================================================
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
