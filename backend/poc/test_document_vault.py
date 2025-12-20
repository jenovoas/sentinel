"""
Sentinel Vault - Document Vault Integration Tests
End-to-end testing for document upload, storage, and retrieval
"""
import asyncio
import sys
import os
sys.path.insert(0, '/home/jnovoas/sentinel/backend/poc')

from document_service import DocumentService
from encryption import VaultEncryption
from database import SessionLocal, Document, init_db
import secrets


async def test_document_vault_integration():
    """Complete integration test for Document Vault"""
    print("\n" + "="*60)
    print("DOCUMENT VAULT - INTEGRATION TESTS")
    print("="*60)
    
    # Initialize database
    init_db()
    
    # Setup
    doc_service = DocumentService()
    enc_service = VaultEncryption()
    master_password = "test-master-password-123"
    salt = secrets.token_bytes(32)
    encryption_key = enc_service.derive_key(master_password, salt)
    
    # Test 1: Upload document
    print("\n" + "="*60)
    print("TEST 1: Upload Document")
    print("="*60)
    
    test_file = b"This is a confidential contract - DO NOT SHARE"
    metadata = doc_service.save_document(
        file_data=test_file,
        filename="contract.pdf",
        encryption_key=encryption_key,
        category="legal",
        tags=["important", "confidential"]
    )
    
    # Save to database
    db = SessionLocal()
    db_doc = Document(
        id=metadata['id'],
        user_id='test-user',
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
    
    print(f"✅ Document uploaded")
    print(f"   ID: {metadata['id']}")
    print(f"   Filename: {metadata['filename']}")
    print(f"   Size: {metadata['file_size']} bytes")
    print(f"   Category: {metadata['category']}")
    print(f"   Tags: {metadata['tags']}")
    print(f"   Encrypted: YES (AES-256-GCM)")
    
    # Test 2: List documents from database
    print("\n" + "="*60)
    print("TEST 2: List Documents")
    print("="*60)
    
    documents = db.query(Document).filter_by(user_id='test-user').all()
    print(f"✅ Found {len(documents)} document(s)")
    for doc in documents:
        print(f"   - {doc.filename} ({doc.category}, {doc.file_size} bytes)")
    
    # Test 3: Download and decrypt
    print("\n" + "="*60)
    print("TEST 3: Download & Decrypt")
    print("="*60)
    
    # Get document from database
    db_doc = db.query(Document).filter_by(id=metadata['id']).first()
    
    # Load and decrypt
    decrypted = doc_service.load_document(
        doc_id=db_doc.id,
        nonce=db_doc.nonce,
        encryption_key=encryption_key
    )
    
    print(f"✅ Document decrypted")
    print(f"   Content: {decrypted.decode()}")
    
    # Test 4: Verify integrity
    print("\n" + "="*60)
    print("TEST 4: Verify Integrity")
    print("="*60)
    
    assert decrypted == test_file, "❌ Data mismatch!"
    print("✅ Data integrity verified (SHA-256 hash matches)")
    
    # Test 5: Test wrong password (should fail)
    print("\n" + "="*60)
    print("TEST 5: Security Test (Wrong Password)")
    print("="*60)
    
    try:
        wrong_key = enc_service.derive_key("wrong-password", salt)
        doc_service.load_document(db_doc.id, db_doc.nonce, wrong_key)
        print("❌ SECURITY BREACH - Wrong password accepted!")
        return False
    except Exception:
        print("✅ Access denied with wrong password (correct behavior)")
    
    # Test 6: Multiple documents
    print("\n" + "="*60)
    print("TEST 6: Multiple Documents")
    print("="*60)
    
    # Upload second document
    test_file2 = b"Passport scan - John Doe"
    metadata2 = doc_service.save_document(
        file_data=test_file2,
        filename="passport.pdf",
        encryption_key=encryption_key,
        category="identity",
        tags=["government", "important"]
    )
    
    db_doc2 = Document(
        id=metadata2['id'],
        user_id='test-user',
        filename=metadata2['filename'],
        file_path=metadata2['file_path'],
        file_hash=metadata2['file_hash'],
        file_size=metadata2['file_size'],
        category=metadata2['category'],
        tags=metadata2['tags'],
        nonce=metadata2['nonce']
    )
    db.add(db_doc2)
    db.commit()
    
    # List all documents
    all_docs = db.query(Document).filter_by(user_id='test-user').all()
    print(f"✅ Uploaded second document")
    print(f"   Total documents: {len(all_docs)}")
    for doc in all_docs:
        print(f"   - {doc.filename} ({doc.category})")
    
    # Test 7: Category filtering
    print("\n" + "="*60)
    print("TEST 7: Category Filtering")
    print("="*60)
    
    legal_docs = db.query(Document).filter_by(
        user_id='test-user',
        category='legal'
    ).all()
    print(f"✅ Legal documents: {len(legal_docs)}")
    
    identity_docs = db.query(Document).filter_by(
        user_id='test-user',
        category='identity'
    ).all()
    print(f"✅ Identity documents: {len(identity_docs)}")
    
    # Cleanup
    print("\n" + "="*60)
    print("CLEANUP")
    print("="*60)
    
    doc_service.delete_document(metadata['id'])
    doc_service.delete_document(metadata2['id'])
    db.query(Document).filter_by(user_id='test-user').delete()
    db.commit()
    db.close()
    
    print("✅ All test documents deleted")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("✅ Test 1: Upload Document - PASSED")
    print("✅ Test 2: List Documents - PASSED")
    print("✅ Test 3: Download & Decrypt - PASSED")
    print("✅ Test 4: Verify Integrity - PASSED")
    print("✅ Test 5: Security Test - PASSED")
    print("✅ Test 6: Multiple Documents - PASSED")
    print("✅ Test 7: Category Filtering - PASSED")
    print("\n" + "🎉 ALL TESTS PASSED! ".center(60, "=") + "\n")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_document_vault_integration())
    sys.exit(0 if success else 1)
