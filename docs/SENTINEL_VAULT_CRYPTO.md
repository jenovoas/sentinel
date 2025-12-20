# 🪙 Sentinel Vault - Crypto Wallet Integration

**Extensión del diseño principal para soporte de blockchain y criptomonedas**

---

## 🎯 Features de Crypto

### **1. Multi-Chain Wallet Management**

Soporte para múltiples blockchains:
- ✅ **Bitcoin** (BTC)
- ✅ **Ethereum** (ETH) + ERC-20 tokens
- ✅ **Binance Smart Chain** (BNB)
- ✅ **Polygon** (MATIC)
- ✅ **Solana** (SOL)
- ✅ **Cardano** (ADA)

---

## 🔐 Secure Key Storage

### **Hierarchical Deterministic (HD) Wallets**

```python
# backend/app/services/crypto_vault.py
from mnemonic import Mnemonic
from bip32 import BIP32

class CryptoVault:
    def generate_wallet(self, user_id: int) -> dict:
        """
        Genera wallet HD con seed phrase de 24 palabras
        """
        # Generar seed phrase (BIP39)
        mnemo = Mnemonic("english")
        seed_phrase = mnemo.generate(strength=256)  # 24 palabras
        
        # Derivar master key (BIP32)
        seed = mnemo.to_seed(seed_phrase)
        bip32 = BIP32.from_seed(seed)
        
        # Derivar keys para diferentes chains
        wallets = {
            "bitcoin": self._derive_bitcoin_wallet(bip32),
            "ethereum": self._derive_ethereum_wallet(bip32),
            "solana": self._derive_solana_wallet(bip32),
        }
        
        # Cifrar seed phrase con master password del usuario
        encrypted_seed = self.encrypt_with_master_password(
            user_id=user_id,
            data=seed_phrase
        )
        
        # Guardar en vault (NUNCA en plaintext)
        await db.store_crypto_wallet({
            "user_id": user_id,
            "encrypted_seed": encrypted_seed,
            "wallets": wallets,  # Solo public addresses
            "created_at": datetime.now()
        })
        
        return {
            "seed_phrase": seed_phrase,  # Mostrar UNA VEZ al usuario
            "wallets": wallets
        }
    
    def _derive_bitcoin_wallet(self, bip32: BIP32) -> dict:
        """BIP44: m/44'/0'/0'/0/0"""
        path = "m/44'/0'/0'/0/0"
        key = bip32.get_privkey_from_path(path)
        
        return {
            "chain": "bitcoin",
            "address": self._btc_address_from_key(key),
            "derivation_path": path
        }
    
    def _derive_ethereum_wallet(self, bip32: BIP32) -> dict:
        """BIP44: m/44'/60'/0'/0/0"""
        path = "m/44'/60'/0'/0/0"
        key = bip32.get_privkey_from_path(path)
        
        return {
            "chain": "ethereum",
            "address": self._eth_address_from_key(key),
            "derivation_path": path
        }
```

---

## 🔗 Blockchain Audit Trail

### **Immutable History con Smart Contract**

```solidity
// contracts/VaultAuditTrail.sol
pragma solidity ^0.8.0;

contract VaultAuditTrail {
    struct AuditEntry {
        address user;
        string action;  // "password_accessed", "password_rotated", etc.
        bytes32 itemHash;  // Hash del item (NO el password)
        uint256 timestamp;
        string ipAddress;
    }
    
    AuditEntry[] public auditLog;
    
    event AuditEntryAdded(
        address indexed user,
        string action,
        bytes32 itemHash,
        uint256 timestamp
    );
    
    function addAuditEntry(
        string memory action,
        bytes32 itemHash,
        string memory ipAddress
    ) public {
        AuditEntry memory entry = AuditEntry({
            user: msg.sender,
            action: action,
            itemHash: itemHash,
            timestamp: block.timestamp,
            ipAddress: ipAddress
        });
        
        auditLog.push(entry);
        
        emit AuditEntryAdded(
            msg.sender,
            action,
            itemHash,
            block.timestamp
        );
    }
    
    function getAuditHistory(address user) 
        public 
        view 
        returns (AuditEntry[] memory) 
    {
        uint256 count = 0;
        
        // Contar entradas del usuario
        for (uint256 i = 0; i < auditLog.length; i++) {
            if (auditLog[i].user == user) {
                count++;
            }
        }
        
        // Retornar entradas
        AuditEntry[] memory userEntries = new AuditEntry[](count);
        uint256 index = 0;
        
        for (uint256 i = 0; i < auditLog.length; i++) {
            if (auditLog[i].user == user) {
                userEntries[index] = auditLog[i];
                index++;
            }
        }
        
        return userEntries;
    }
}
```

**Integración con Backend**:
```python
# backend/app/services/blockchain_audit.py
from web3 import Web3

class BlockchainAudit:
    def __init__(self):
        # Conectar a Ethereum (o Polygon para fees bajos)
        self.w3 = Web3(Web3.HTTPProvider('https://polygon-rpc.com'))
        self.contract = self.w3.eth.contract(
            address="0x...",  # Contract address
            abi=AUDIT_TRAIL_ABI
        )
    
    async def log_access(self, user_id: int, action: str, item_id: str):
        """
        Registra acceso en blockchain (immutable)
        """
        # Hash del item (NO el password)
        item_hash = Web3.keccak(text=item_id)
        
        # Obtener wallet del usuario
        user_wallet = await self.get_user_wallet(user_id)
        
        # Crear transacción
        tx = self.contract.functions.addAuditEntry(
            action=action,
            itemHash=item_hash,
            ipAddress=get_client_ip()
        ).build_transaction({
            'from': user_wallet.address,
            'nonce': self.w3.eth.get_transaction_count(user_wallet.address),
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Firmar y enviar
        signed_tx = self.w3.eth.account.sign_transaction(
            tx, 
            private_key=user_wallet.private_key
        )
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Esperar confirmación
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            "tx_hash": tx_hash.hex(),
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed
        }
```

---

## 💰 Transaction Signing

### **Secure Transaction Flow**

```python
# backend/app/services/crypto_transactions.py

async def sign_transaction(
    user_id: int,
    chain: str,
    to_address: str,
    amount: float,
    master_password: str
) -> dict:
    """
    Firma transacción crypto de forma segura
    """
    # 1. Verificar master password
    if not await verify_master_password(user_id, master_password):
        raise UnauthorizedError("Invalid master password")
    
    # 2. Descifrar private key
    encrypted_wallet = await db.get_crypto_wallet(user_id, chain)
    private_key = await decrypt_with_master_password(
        user_id=user_id,
        encrypted_data=encrypted_wallet.encrypted_key,
        master_password=master_password
    )
    
    # 3. Crear transacción
    if chain == "ethereum":
        tx = {
            'nonce': w3.eth.get_transaction_count(encrypted_wallet.address),
            'to': to_address,
            'value': w3.to_wei(amount, 'ether'),
            'gas': 21000,
            'gasPrice': w3.eth.gas_price,
            'chainId': 1  # Mainnet
        }
        
        # Firmar
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        
        # Enviar
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
    elif chain == "bitcoin":
        # Bitcoin transaction signing
        tx_hash = await sign_bitcoin_transaction(
            private_key=private_key,
            to_address=to_address,
            amount=amount
        )
    
    # 4. Log en blockchain audit trail
    await blockchain_audit.log_access(
        user_id=user_id,
        action=f"transaction_sent_{chain}",
        item_id=tx_hash.hex()
    )
    
    # 5. Limpiar private key de memoria
    del private_key
    
    return {
        "tx_hash": tx_hash.hex(),
        "chain": chain,
        "amount": amount,
        "to": to_address
    }
```

---

## 🔌 Hardware Wallet Integration

### **Ledger & Trezor Support**

```typescript
// frontend/src/lib/hardwareWallet.ts
import TransportWebUSB from '@ledgerhq/hw-transport-webusb';
import Eth from '@ledgerhq/hw-app-eth';

export class HardwareWalletManager {
  async connectLedger(): Promise<string> {
    // Conectar a Ledger via USB
    const transport = await TransportWebUSB.create();
    const eth = new Eth(transport);
    
    // Obtener address (BIP44 path)
    const path = "44'/60'/0'/0/0";
    const result = await eth.getAddress(path);
    
    return result.address;
  }
  
  async signWithLedger(
    transaction: EthTransaction
  ): Promise<string> {
    const transport = await TransportWebUSB.create();
    const eth = new Eth(transport);
    
    // Firmar transacción en hardware
    const signature = await eth.signTransaction(
      "44'/60'/0'/0/0",
      transaction.serialize()
    );
    
    return signature;
  }
  
  async connectTrezor(): Promise<string> {
    // Similar para Trezor
    const TrezorConnect = await import('trezor-connect');
    
    const result = await TrezorConnect.ethereumGetAddress({
      path: "m/44'/60'/0'/0/0"
    });
    
    return result.payload.address;
  }
}
```

**UI Component**:
```typescript
// frontend/src/components/HardwareWalletConnect.tsx
export function HardwareWalletConnect() {
  const [connected, setConnected] = useState(false);
  const [address, setAddress] = useState('');
  
  async function connectHardwareWallet(type: 'ledger' | 'trezor') {
    const manager = new HardwareWalletManager();
    
    const addr = type === 'ledger' 
      ? await manager.connectLedger()
      : await manager.connectTrezor();
    
    setAddress(addr);
    setConnected(true);
    
    // Guardar en vault
    await fetch('/api/vault/crypto/add-hardware-wallet', {
      method: 'POST',
      body: JSON.stringify({
        type,
        address: addr
      })
    });
  }
  
  return (
    <div>
      <button onClick={() => connectHardwareWallet('ledger')}>
        Connect Ledger
      </button>
      <button onClick={() => connectHardwareWallet('trezor')}>
        Connect Trezor
      </button>
      
      {connected && (
        <div>
          ✅ Connected: {address}
        </div>
      )}
    </div>
  );
}
```

---

## 📊 Portfolio Tracking

### **Real-Time Balance & Price**

```python
# backend/app/services/crypto_portfolio.py

async def get_portfolio_value(user_id: int) -> dict:
    """
    Obtiene valor total del portfolio en USD
    """
    wallets = await db.get_user_crypto_wallets(user_id)
    total_usd = 0
    holdings = []
    
    for wallet in wallets:
        # Obtener balance on-chain
        balance = await get_balance(wallet.chain, wallet.address)
        
        # Obtener precio actual (CoinGecko API)
        price_usd = await get_crypto_price(wallet.chain)
        
        value_usd = balance * price_usd
        total_usd += value_usd
        
        holdings.append({
            "chain": wallet.chain,
            "balance": balance,
            "price_usd": price_usd,
            "value_usd": value_usd
        })
    
    return {
        "total_usd": total_usd,
        "holdings": holdings,
        "last_updated": datetime.now()
    }

async def get_balance(chain: str, address: str) -> float:
    """
    Obtiene balance on-chain
    """
    if chain == "ethereum":
        balance_wei = w3.eth.get_balance(address)
        return w3.from_wei(balance_wei, 'ether')
    
    elif chain == "bitcoin":
        # Usar blockchain.info API
        response = await httpx.get(
            f"https://blockchain.info/q/addressbalance/{address}"
        )
        satoshis = int(response.text)
        return satoshis / 100000000  # Convert to BTC
    
    # ... otros chains
```

---

## 🎨 UI Features

### **Crypto Dashboard**

```typescript
// frontend/src/app/vault/crypto/page.tsx
export default function CryptoDashboard() {
  const { data: portfolio } = useQuery('portfolio', getPortfolio);
  
  return (
    <div className="grid grid-cols-3 gap-4">
      {/* Total Value */}
      <Card>
        <h3>Total Portfolio Value</h3>
        <p className="text-4xl font-bold">
          ${portfolio?.total_usd.toLocaleString()}
        </p>
      </Card>
      
      {/* Holdings */}
      {portfolio?.holdings.map(holding => (
        <Card key={holding.chain}>
          <div className="flex items-center gap-2">
            <CryptoIcon chain={holding.chain} />
            <div>
              <h4>{holding.chain.toUpperCase()}</h4>
              <p>{holding.balance} {holding.chain}</p>
              <p className="text-sm text-gray-500">
                ${holding.value_usd.toLocaleString()}
              </p>
            </div>
          </div>
        </Card>
      ))}
      
      {/* Actions */}
      <Card>
        <button onClick={() => openSendModal()}>
          Send Crypto
        </button>
        <button onClick={() => openReceiveModal()}>
          Receive Crypto
        </button>
        <button onClick={() => connectHardwareWallet()}>
          Connect Hardware Wallet
        </button>
      </Card>
    </div>
  );
}
```

---

## 💎 Database Schema (Crypto Extension)

```sql
-- Crypto wallets
CREATE TABLE crypto_wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- Encrypted seed phrase (BIP39)
    encrypted_seed BYTEA NOT NULL,
    encryption_nonce BYTEA NOT NULL,
    encryption_tag BYTEA NOT NULL,
    
    -- Derived wallets (public info only)
    wallets JSONB NOT NULL,  -- {"bitcoin": {...}, "ethereum": {...}}
    
    -- Hardware wallet (if applicable)
    hardware_wallet_type VARCHAR(50),  -- 'ledger', 'trezor', null
    hardware_wallet_connected BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP,
    
    INDEX idx_user_id (user_id)
);

-- Crypto transactions
CREATE TABLE crypto_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    wallet_id UUID NOT NULL REFERENCES crypto_wallets(id),
    
    -- Transaction details
    chain VARCHAR(50) NOT NULL,
    tx_hash VARCHAR(255) NOT NULL UNIQUE,
    from_address VARCHAR(255) NOT NULL,
    to_address VARCHAR(255) NOT NULL,
    amount DECIMAL(36, 18) NOT NULL,
    
    -- Blockchain confirmation
    block_number BIGINT,
    confirmations INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'confirmed', 'failed'
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    confirmed_at TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_tx_hash (tx_hash),
    INDEX idx_status (status)
);

-- Blockchain audit log (reference to on-chain data)
CREATE TABLE blockchain_audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    
    -- On-chain reference
    chain VARCHAR(50) NOT NULL,  -- 'ethereum', 'polygon', etc.
    contract_address VARCHAR(255) NOT NULL,
    tx_hash VARCHAR(255) NOT NULL,
    block_number BIGINT NOT NULL,
    
    -- Action logged
    action VARCHAR(100) NOT NULL,
    item_hash VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_id (user_id),
    INDEX idx_tx_hash (tx_hash)
);
```

---

## 🚀 Monetización Crypto

### **Premium Features**

| Feature | Free | Pro | Enterprise |
|---------|------|-----|------------|
| **Wallets** | 3 chains | Unlimited | Unlimited |
| **Hardware Wallet** | ❌ | ✅ | ✅ |
| **Blockchain Audit** | ❌ | ✅ Polygon | ✅ Ethereum |
| **Portfolio Tracking** | Manual | Real-time | Real-time + Analytics |
| **Transaction Signing** | ✅ | ✅ | ✅ + Multi-sig |

---

## ✅ Roadmap Crypto

### **Fase 1: Basic Wallet** (2 semanas)
- [ ] HD wallet generation (BIP39/BIP44)
- [ ] Bitcoin + Ethereum support
- [ ] Secure key storage
- [ ] Basic send/receive

### **Fase 2: Blockchain Audit** (2 semanas)
- [ ] Smart contract deployment
- [ ] Audit trail integration
- [ ] Immutable history

### **Fase 3: Hardware Wallets** (2 semanas)
- [ ] Ledger integration
- [ ] Trezor integration
- [ ] Transaction signing

### **Fase 4: Advanced Features** (3 semanas)
- [ ] Multi-chain support (Solana, Cardano, etc.)
- [ ] Portfolio tracking
- [ ] Price alerts
- [ ] DeFi integration (opcional)

---

**Status**: 💡 Diseño completo con crypto support  
**Diferenciador**: Único password manager con crypto wallet integrado + blockchain audit trail
