"""
Sentinel Vault - Document Storage Service
Encrypted file storage with categories and tags
"""
import os
import hashlib
from datetime import datetime
from typing import Optional, List
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives import hashes
import secrets


class DocumentService:
    """Service for encrypted document storage"""
    
    STORAGE_PATH = "storage/documents"
    
    def __init__(self):
        os.makedirs(self.STORAGE_PATH, exist_ok=True)
    
    def encrypt_file(self, file_data: bytes, encryption_key: bytes) -> dict:
        """
        Encrypt file data
        
        Args:
            file_data: Raw file bytes
            encryption_key: 256-bit encryption key
        
        Returns:
            Dict with nonce and ciphertext
        """
        # Generate nonce (96 bits for GCM)
        nonce = secrets.token_bytes(12)
        
        # Encrypt with AES-256-GCM
        aesgcm = AESGCM(encryption_key)
        ciphertext = aesgcm.encrypt(nonce, file_data, None)
        
        return {
            'nonce': nonce.hex(),
            'ciphertext': ciphertext.hex()
        }
    
    def decrypt_file(self, encrypted_data: dict, encryption_key: bytes) -> bytes:
        """
        Decrypt file data
        
        Args:
            encrypted_data: Dict with nonce and ciphertext
            encryption_key: 256-bit encryption key
        
        Returns:
            Decrypted file bytes
        """
        nonce = bytes.fromhex(encrypted_data['nonce'])
        ciphertext = bytes.fromhex(encrypted_data['ciphertext'])
        
        # Decrypt
        aesgcm = AESGCM(encryption_key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        return plaintext
    
    def save_document(
        self,
        file_data: bytes,
        filename: str,
        encryption_key: bytes,
        category: str = 'general',
        tags: List[str] = None
    ) -> dict:
        """
        Save encrypted document
        
        Args:
            file_data: Raw file bytes
            filename: Original filename
            encryption_key: User's encryption key
            category: Document category
            tags: List of tags
        
        Returns:
            Document metadata
        """
        # Generate document ID
        doc_id = secrets.token_hex(16)
        
        # Encrypt file
        encrypted = self.encrypt_file(file_data, encryption_key)
        
        # Calculate file hash (for integrity)
        file_hash = hashlib.sha256(file_data).hexdigest()
        
        # Save encrypted file to disk
        file_path = os.path.join(self.STORAGE_PATH, f"{doc_id}.enc")
        with open(file_path, 'wb') as f:
            # Store nonce + ciphertext
            f.write(bytes.fromhex(encrypted['nonce']))
            f.write(bytes.fromhex(encrypted['ciphertext']))
        
        # Return metadata (to be stored in database)
        return {
            'id': doc_id,
            'filename': filename,
            'file_path': file_path,
            'file_hash': file_hash,
            'file_size': len(file_data),
            'category': category,
            'tags': tags or [],
            'created_at': datetime.utcnow().isoformat(),
            'nonce': encrypted['nonce']  # Store nonce in DB
        }
    
    def load_document(
        self,
        doc_id: str,
        nonce: str,
        encryption_key: bytes
    ) -> bytes:
        """
        Load and decrypt document
        
        Args:
            doc_id: Document ID
            nonce: Nonce (from database)
            encryption_key: User's encryption key
        
        Returns:
            Decrypted file bytes
        """
        file_path = os.path.join(self.STORAGE_PATH, f"{doc_id}.enc")
        
        # Read encrypted file
        with open(file_path, 'rb') as f:
            stored_nonce = f.read(12)  # First 12 bytes
            ciphertext = f.read()      # Rest is ciphertext
        
        # Decrypt
        encrypted_data = {
            'nonce': stored_nonce.hex(),
            'ciphertext': ciphertext.hex()
        }
        
        return self.decrypt_file(encrypted_data, encryption_key)
    
    def delete_document(self, doc_id: str):
        """Delete document from storage"""
        file_path = os.path.join(self.STORAGE_PATH, f"{doc_id}.enc")
        if os.path.exists(file_path):
            os.remove(file_path)


# ============================================================================
# Testing
# ============================================================================

def test_document_service():
    print("📄 Document Service - Testing\n")
    
    service = DocumentService()
    
    # Generate test encryption key
    from encryption import VaultEncryption
    enc_service = VaultEncryption()
    master_password = "test_password_123"
    salt = secrets.token_bytes(32)
    encryption_key = enc_service.derive_key(master_password, salt)
    
    # Test 1: Save document
    print("Test 1: Save document")
    test_data = b"This is a secret document with sensitive information."
    doc_metadata = service.save_document(
        file_data=test_data,
        filename="secret.txt",
        encryption_key=encryption_key,
        category="confidential",
        tags=["important", "secret"]
    )
    print(f"✅ Document saved: {doc_metadata['id']}")
    print(f"   Filename: {doc_metadata['filename']}")
    print(f"   Size: {doc_metadata['file_size']} bytes")
    print(f"   Category: {doc_metadata['category']}")
    print(f"   Tags: {doc_metadata['tags']}\n")
    
    # Test 2: Load document
    print("Test 2: Load document")
    decrypted_data = service.load_document(
        doc_id=doc_metadata['id'],
        nonce=doc_metadata['nonce'],
        encryption_key=encryption_key
    )
    print(f"✅ Document loaded and decrypted")
    print(f"   Content: {decrypted_data.decode()}\n")
    
    # Test 3: Verify integrity
    print("Test 3: Verify integrity")
    assert decrypted_data == test_data, "❌ Data mismatch!"
    print("✅ Data integrity verified\n")
    
    # Test 4: Delete document
    print("Test 4: Delete document")
    service.delete_document(doc_metadata['id'])
    print("✅ Document deleted\n")
    
    print("🎉 All tests passed!")


if __name__ == "__main__":
    test_document_service()
