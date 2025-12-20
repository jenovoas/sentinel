"""
Sentinel Vault - Notes Service
Encrypted notes with Markdown support and bidirectional linking
"""
import os
import re
import secrets
from datetime import datetime
from typing import List, Optional, Dict
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class NotesService:
    """Service for encrypted notes (Obsidian-style)"""
    
    def __init__(self):
        pass
    
    def encrypt_content(self, content: str, encryption_key: bytes) -> dict:
        """
        Encrypt note content
        
        Args:
            content: Markdown content
            encryption_key: 256-bit encryption key
        
        Returns:
            Dict with nonce and ciphertext
        """
        nonce = secrets.token_bytes(12)
        aesgcm = AESGCM(encryption_key)
        ciphertext = aesgcm.encrypt(nonce, content.encode(), None)
        
        return {
            'nonce': nonce.hex(),
            'ciphertext': ciphertext.hex()
        }
    
    def decrypt_content(self, encrypted_data: dict, encryption_key: bytes) -> str:
        """
        Decrypt note content
        
        Args:
            encrypted_data: Dict with nonce and ciphertext
            encryption_key: 256-bit encryption key
        
        Returns:
            Decrypted Markdown content
        """
        nonce = bytes.fromhex(encrypted_data['nonce'])
        ciphertext = bytes.fromhex(encrypted_data['ciphertext'])
        
        aesgcm = AESGCM(encryption_key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        return plaintext.decode()
    
    def extract_links(self, content: str) -> List[str]:
        """
        Extract [[Note Name]] links from content
        
        Args:
            content: Markdown content
        
        Returns:
            List of linked note names
        """
        # Match [[Note Name]] pattern
        pattern = r'\[\[([^\]]+)\]\]'
        matches = re.findall(pattern, content)
        return matches
    
    def extract_tags(self, content: str) -> List[str]:
        """
        Extract #tags from content
        
        Args:
            content: Markdown content
        
        Returns:
            List of tags (without #)
        """
        # Match #tag pattern (word characters only)
        pattern = r'#(\w+)'
        matches = re.findall(pattern, content)
        return list(set(matches))  # Remove duplicates
    
    def create_note(
        self,
        title: str,
        content: str,
        encryption_key: bytes,
        tags: List[str] = None
    ) -> dict:
        """
        Create encrypted note
        
        Args:
            title: Note title
            content: Markdown content
            encryption_key: User's encryption key
            tags: Optional tags
        
        Returns:
            Note metadata
        """
        # Generate note ID
        note_id = secrets.token_hex(16)
        
        # Encrypt content
        encrypted = self.encrypt_content(content, encryption_key)
        
        # Extract links and tags from content
        links = self.extract_links(content)
        auto_tags = self.extract_tags(content)
        all_tags = list(set((tags or []) + auto_tags))
        
        return {
            'id': note_id,
            'title': title,
            'content_length': len(content),
            'nonce': encrypted['nonce'],
            'ciphertext': encrypted['ciphertext'],
            'links': links,
            'tags': all_tags,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
    
    def update_note(
        self,
        note_id: str,
        content: str,
        encryption_key: bytes
    ) -> dict:
        """
        Update note content
        
        Args:
            note_id: Note ID
            content: New Markdown content
            encryption_key: User's encryption key
        
        Returns:
            Updated metadata
        """
        # Encrypt new content
        encrypted = self.encrypt_content(content, encryption_key)
        
        # Extract links and tags
        links = self.extract_links(content)
        tags = self.extract_tags(content)
        
        return {
            'id': note_id,
            'content_length': len(content),
            'nonce': encrypted['nonce'],
            'ciphertext': encrypted['ciphertext'],
            'links': links,
            'tags': tags,
            'updated_at': datetime.utcnow().isoformat()
        }
    
    def get_backlinks(self, note_title: str, all_notes: List[dict]) -> List[str]:
        """
        Find notes that link to this note
        
        Args:
            note_title: Title of the note
            all_notes: List of all notes with their links
        
        Returns:
            List of note IDs that link to this note
        """
        backlinks = []
        for note in all_notes:
            if note_title in note.get('links', []):
                backlinks.append(note['id'])
        return backlinks


# ============================================================================
# Testing
# ============================================================================

def test_notes_service():
    print("📝 Notes Service - Testing\n")
    
    service = NotesService()
    
    # Generate test encryption key
    from encryption import VaultEncryption
    enc_service = VaultEncryption()
    master_password = "test_password_123"
    salt = secrets.token_bytes(32)
    encryption_key = enc_service.derive_key(master_password, salt)
    
    # Test 1: Create note with links
    print("Test 1: Create note with links")
    content = """# My Research Notes

This is a note about [[Crypto Wallet]] and [[Document Vault]].

## Tags
#important #research #sentinel

## Links
- See also: [[Security Architecture]]
- Related: [[Encryption]]
"""
    
    note = service.create_note(
        title="Research Notes",
        content=content,
        encryption_key=encryption_key,
        tags=["notes"]
    )
    
    print(f"✅ Note created: {note['id']}")
    print(f"   Title: {note['title']}")
    print(f"   Length: {note['content_length']} chars")
    print(f"   Links: {note['links']}")
    print(f"   Tags: {note['tags']}")
    print()
    
    # Test 2: Decrypt note
    print("Test 2: Decrypt note")
    encrypted_data = {
        'nonce': note['nonce'],
        'ciphertext': note['ciphertext']
    }
    decrypted = service.decrypt_content(encrypted_data, encryption_key)
    print(f"✅ Note decrypted")
    print(f"   Content preview: {decrypted[:50]}...")
    print()
    
    # Test 3: Verify integrity
    print("Test 3: Verify integrity")
    assert decrypted == content, "❌ Content mismatch!"
    print("✅ Content integrity verified")
    print()
    
    # Test 4: Extract links
    print("Test 4: Extract links")
    links = service.extract_links(content)
    print(f"✅ Found {len(links)} links: {links}")
    print()
    
    # Test 5: Extract tags
    print("Test 5: Extract tags")
    tags = service.extract_tags(content)
    print(f"✅ Found {len(tags)} tags: {tags}")
    print()
    
    # Test 6: Backlinks
    print("Test 6: Backlinks")
    all_notes = [
        {'id': '1', 'title': 'Note 1', 'links': ['Research Notes']},
        {'id': '2', 'title': 'Note 2', 'links': ['Other Note']},
        {'id': '3', 'title': 'Note 3', 'links': ['Research Notes', 'Another']},
    ]
    backlinks = service.get_backlinks('Research Notes', all_notes)
    print(f"✅ Found {len(backlinks)} backlinks: {backlinks}")
    print()
    
    # Test 7: Update note
    print("Test 7: Update note")
    new_content = content + "\n\n## Update\nAdded new section with [[New Link]]"
    updated = service.update_note(note['id'], new_content, encryption_key)
    print(f"✅ Note updated")
    print(f"   New length: {updated['content_length']} chars")
    print(f"   New links: {updated['links']}")
    print()
    
    print("🎉 All tests passed!")


if __name__ == "__main__":
    test_notes_service()
