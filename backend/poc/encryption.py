"""
Sentinel Vault POC - Encryption Service
Argon2id + AES-256-GCM
"""
from argon2 import PasswordHasher
from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import time


class VaultEncryption:
    """Zero-knowledge encryption para Sentinel Vault"""
    
    def __init__(self):
        self.ph = PasswordHasher(
            time_cost=3,
            memory_cost=65536,  # 64MB
            parallelism=4
        )
    
    def derive_key(self, master_password: str, salt: bytes) -> bytes:
        """
        Deriva encryption key desde master password usando Argon2id
        
        Args:
            master_password: Master password del usuario (nunca se almacena)
            salt: Salt único por usuario (32 bytes)
        
        Returns:
            Encryption key de 32 bytes (256 bits)
        """
        key = hash_secret_raw(
            secret=master_password.encode(),
            salt=salt,
            time_cost=3,
            memory_cost=65536,  # 64MB (GPU-resistant)
            parallelism=4,
            hash_len=32,  # 256 bits
            type=Type.ID  # Argon2id (hybrid)
        )
        return key
    
    def encrypt(self, data: str, key: bytes) -> dict:
        """
        Encrypt data con AES-256-GCM
        
        Args:
            data: Plaintext a cifrar
            key: Encryption key (32 bytes)
        
        Returns:
            Dict con nonce y ciphertext (ambos en hex)
        """
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)  # 96 bits para GCM
        ciphertext = aesgcm.encrypt(nonce, data.encode(), None)
        
        return {
            "nonce": nonce.hex(),
            "ciphertext": ciphertext.hex()
        }
    
    def decrypt(self, encrypted: dict, key: bytes) -> str:
        """
        Decrypt data
        
        Args:
            encrypted: Dict con nonce y ciphertext
            key: Encryption key (32 bytes)
        
        Returns:
            Plaintext decrypted
        """
        aesgcm = AESGCM(key)
        nonce = bytes.fromhex(encrypted["nonce"])
        ciphertext = bytes.fromhex(encrypted["ciphertext"])
        
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode()
    
    def benchmark_key_derivation(self, iterations: int = 10) -> dict:
        """Benchmark de key derivation para validar performance"""
        master_password = "test-password-123"
        salt = os.urandom(32)
        
        times = []
        for _ in range(iterations):
            start = time.time()
            self.derive_key(master_password, salt)
            elapsed = time.time() - start
            times.append(elapsed * 1000)  # ms
        
        return {
            "average_ms": sum(times) / len(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "iterations": iterations
        }
    
    def benchmark_encryption(self, iterations: int = 100) -> dict:
        """Benchmark de encryption/decryption"""
        master_password = "test-password-123"
        salt = os.urandom(32)
        key = self.derive_key(master_password, salt)
        data = "my-super-secret-password-12345"
        
        # Encryption
        enc_times = []
        for _ in range(iterations):
            start = time.time()
            encrypted = self.encrypt(data, key)
            elapsed = time.time() - start
            enc_times.append(elapsed * 1000)
        
        # Decryption
        dec_times = []
        for _ in range(iterations):
            start = time.time()
            self.decrypt(encrypted, key)
            elapsed = time.time() - start
            dec_times.append(elapsed * 1000)
        
        return {
            "encryption": {
                "average_ms": sum(enc_times) / len(enc_times),
                "min_ms": min(enc_times),
                "max_ms": max(enc_times)
            },
            "decryption": {
                "average_ms": sum(dec_times) / len(dec_times),
                "min_ms": min(dec_times),
                "max_ms": max(dec_times)
            },
            "iterations": iterations
        }


if __name__ == "__main__":
    print("🔐 Sentinel Vault - Encryption POC\n")
    
    vault = VaultEncryption()
    
    # Test 1: Encryption roundtrip
    print("Test 1: Encryption Roundtrip")
    master_password = "super-secret-password-123"
    salt = os.urandom(32)
    
    key = vault.derive_key(master_password, salt)
    print(f"✅ Key derived: {key.hex()[:32]}...")
    
    # Encrypt
    original = "my-github-password"
    encrypted = vault.encrypt(original, key)
    print(f"✅ Encrypted: {encrypted['ciphertext'][:32]}...")
    
    # Decrypt
    decrypted = vault.decrypt(encrypted, key)
    assert decrypted == original
    print(f"✅ Decrypted: {decrypted}")
    print(f"✅ Roundtrip successful!\n")
    
    # Test 2: Performance benchmarks
    print("Test 2: Performance Benchmarks")
    
    print("\n📊 Key Derivation (Argon2id):")
    kd_bench = vault.benchmark_key_derivation(10)
    print(f"  Average: {kd_bench['average_ms']:.2f}ms")
    print(f"  Min: {kd_bench['min_ms']:.2f}ms")
    print(f"  Max: {kd_bench['max_ms']:.2f}ms")
    
    print("\n📊 Encryption/Decryption (AES-256-GCM):")
    enc_bench = vault.benchmark_encryption(100)
    print(f"  Encryption avg: {enc_bench['encryption']['average_ms']:.3f}ms")
    print(f"  Decryption avg: {enc_bench['decryption']['average_ms']:.3f}ms")
    
    print("\n✅ All tests passed!")
