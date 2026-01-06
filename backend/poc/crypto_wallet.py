"""
Sentinel Vault POC - Crypto Wallet Generation
HD wallets con BIP39/BIP44 para Bitcoin y Ethereum
"""
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
from mnemonic import Mnemonic
from bip32 import BIP32
from web3 import Web3
import hashlib


class CryptoWallet:
    """Generación de crypto wallets multi-chain"""
    
    def __init__(self):
        self.mnemo = Mnemonic("english")
        self.w3 = Web3()
    
    def generate_wallet(self) -> dict:
        """
        Genera HD wallet con seed phrase de 24 palabras
        
        Returns:
            Dict con seed_phrase y wallets (Bitcoin, Ethereum)
        """
        # Generar seed phrase (BIP39)
        seed_phrase = self.mnemo.generate(strength=256)  # 24 palabras
        seed = self.mnemo.to_seed(seed_phrase)
        
        # Derivar master key (BIP32)
        bip32 = BIP32.from_seed(seed)
        
        # Bitcoin wallet (BIP44: m/44'/0'/0'/0/0)
        btc_wallet = self._derive_bitcoin_wallet(bip32)
        
        # Ethereum wallet (BIP44: m/44'/60'/0'/0/0)
        eth_wallet = self._derive_ethereum_wallet(bip32)
        
        return {
            "seed_phrase": seed_phrase,  # ⚠️ MOSTRAR SOLO UNA VEZ
            "bitcoin": btc_wallet,
            "ethereum": eth_wallet
        }
    
    def recover_wallet(self, seed_phrase: str) -> dict:
        """
        Recupera wallet desde seed phrase
        
        Args:
            seed_phrase: Seed phrase de 24 palabras
        
        Returns:
            Dict con wallets recuperadas
        """
        if not self.mnemo.check(seed_phrase):
            raise ValueError("Invalid seed phrase")
        
        seed = self.mnemo.to_seed(seed_phrase)
        bip32 = BIP32.from_seed(seed)
        
        return {
            "bitcoin": self._derive_bitcoin_wallet(bip32),
            "ethereum": self._derive_ethereum_wallet(bip32)
        }
    
    def _derive_bitcoin_wallet(self, bip32: BIP32) -> dict:
        """Deriva Bitcoin wallet (BIP44: m/44'/0'/0'/0/0)"""
        path = "m/44'/0'/0'/0/0"
        privkey = bip32.get_privkey_from_path(path)
        pubkey = bip32.get_pubkey_from_path(path)
        
        # P2PKH address (legacy, empieza con '1')
        address = self._btc_address_from_pubkey(pubkey)
        
        return {
            "chain": "bitcoin",
            "address": address,
            "derivation_path": path,
            "private_key": privkey.hex()  # ⚠️ NUNCA almacenar en plaintext
        }
    
    def _derive_ethereum_wallet(self, bip32: BIP32) -> dict:
        """Deriva Ethereum wallet (BIP44: m/44'/60'/0'/0/0)"""
        path = "m/44'/60'/0'/0/0"
        privkey = bip32.get_privkey_from_path(path)
        pubkey = bip32.get_pubkey_from_path(path)
        
        # Ethereum address (checksum)
        address = self._eth_address_from_pubkey(pubkey)
        
        return {
            "chain": "ethereum",
            "address": address,
            "derivation_path": path,
            "private_key": privkey.hex()  # ⚠️ NUNCA almacenar en plaintext
        }
    
    def _btc_address_from_pubkey(self, pubkey: bytes) -> str:
        """Convierte pubkey a Bitcoin address (P2PKH)"""
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
    
    def _eth_address_from_pubkey(self, pubkey: bytes) -> str:
        """Convierte pubkey a Ethereum address (checksum)"""
        # Keccak-256 hash (sin el primer byte 0x04)
        hash_bytes = self.w3.keccak(pubkey[1:])
        
        # Últimos 20 bytes
        address = hash_bytes[-20:].hex()
        
        # Checksum (EIP-55)
        return self.w3.to_checksum_address(address)
    
    def _base58_encode(self, data: bytes) -> str:
        """Base58 encoding para Bitcoin addresses"""
        alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        num = int.from_bytes(data, 'big')
        
        encoded = ""
        while num > 0:
            num, remainder = divmod(num, 58)
            encoded = alphabet[remainder] + encoded
        
        # Add leading '1' for each leading zero byte
        for byte in data:
            if byte == 0:
                encoded = '1' + encoded
            else:
                break
        
        return encoded

    async def get_wallet_status(self, user_id: str) -> dict:
        """Get wallet balances (mocked for now)"""
        # TODO: Implement real balance check using Web3/APIs
        # For POC, returns mocked data
        return {
            "wallets": {
                "bitcoin": {"balance": 0.05, "balance_usd": 2200.00},
                "ethereum": {"balance": 1.2, "balance_usd": 2800.00},
                "polygon": {"balance": 150.0, "balance_usd": 120.00},
                "solana": {"balance": 12.5, "balance_usd": 1250.00}
            }
        }

if __name__ == "__main__":
    print("🪙 Sentinel Vault - Crypto Wallet POC\n")
    
    wallet_gen = CryptoWallet()
    
    # Test 1: Generate new wallet
    print("Test 1: Generate New Wallet")
    wallet = wallet_gen.generate_wallet()
    
    print(f"\n⚠️  SAVE THIS SEED PHRASE (show only once):")
    print(f"   {wallet['seed_phrase']}\n")
    
    print(f"Bitcoin:")
    print(f"  Address: {wallet['bitcoin']['address']}")
    print(f"  Path: {wallet['bitcoin']['derivation_path']}")
    
    print(f"\nEthereum:")
    print(f"  Address: {wallet['ethereum']['address']}")
    print(f"  Path: {wallet['ethereum']['derivation_path']}")
    
    # Test 2: Recover wallet from seed phrase
    print("\n\nTest 2: Recover Wallet from Seed Phrase")
    recovered = wallet_gen.recover_wallet(wallet['seed_phrase'])
    
    # Validar que addresses coinciden
    assert recovered['bitcoin']['address'] == wallet['bitcoin']['address']
    assert recovered['ethereum']['address'] == wallet['ethereum']['address']
    
    print(f"✅ Bitcoin address matches: {recovered['bitcoin']['address']}")
    print(f"✅ Ethereum address matches: {recovered['ethereum']['address']}")
    
    print("\n✅ All tests passed!")
    print("\n⚠️  SECURITY REMINDER:")
    print("   - Seed phrase debe mostrarse SOLO UNA VEZ")
    print("   - Private keys NUNCA en plaintext en DB")
    print("   - Usar encryption (Argon2id + AES-256-GCM)")
