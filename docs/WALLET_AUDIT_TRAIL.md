# 🔐 Crypto Wallet - Immutable Audit Trail

**Registro inmutable de toda actividad económica del usuario**

---

## 🎯 Objetivo

Mantener un **registro completo e inmutable** de:
- ✅ Todas las transacciones (enviar/recibir)
- ✅ Todos los accesos a wallets
- ✅ Cambios en balances
- ✅ Generación/recuperación de wallets
- ✅ Exportación de claves privadas

**Por qué es crítico**:
1. **Compliance**: Regulaciones requieren audit trail (AML, KYC)
2. **Tax reporting**: Necesario para declaración de impuestos
3. **Security**: Detectar accesos no autorizados
4. **Forensics**: Investigación en caso de compromiso

---

## 🗄️ Database Schema

### **Wallet Activity Log**
```sql
CREATE TABLE wallet_activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    wallet_id UUID REFERENCES crypto_wallets(id),
    
    -- Activity type
    activity_type VARCHAR(50) NOT NULL,
    -- 'wallet_created', 'wallet_recovered', 'wallet_accessed',
    -- 'transaction_sent', 'transaction_received', 'balance_updated',
    -- 'private_key_exported', 'seed_phrase_viewed'
    
    -- Activity details
    details JSONB NOT NULL,
    -- Ejemplos:
    -- {"chain": "bitcoin", "address": "1A1z...", "amount": 0.5}
    -- {"tx_hash": "abc123...", "from": "...", "to": "...", "value": 1.5}
    -- {"balance_before": 1.0, "balance_after": 1.5, "change": 0.5}
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    location JSONB,  -- {country, city, lat, lon}
    
    -- Blockchain verification (opcional)
    blockchain_hash VARCHAR(255),  -- Hash en Polygon para inmutabilidad
    blockchain_confirmed BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    
    -- Indexes
    INDEX idx_user_activity (user_id, created_at DESC),
    INDEX idx_wallet_activity (wallet_id, created_at DESC),
    INDEX idx_activity_type (activity_type, created_at DESC)
);

-- Trigger para prevenir modificaciones
CREATE OR REPLACE FUNCTION prevent_audit_log_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit log is immutable. Cannot modify or delete records.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_update_wallet_activity_log
BEFORE UPDATE OR DELETE ON wallet_activity_log
FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_modification();
```

---

## 📊 Tipos de Actividad

### **1. Wallet Management**
```python
WALLET_ACTIVITIES = {
    'wallet_created': {
        'description': 'New wallet generated',
        'details': {
            'chain': 'bitcoin',
            'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            'derivation_path': "m/44'/0'/0'/0/0"
        }
    },
    
    'wallet_recovered': {
        'description': 'Wallet recovered from seed phrase',
        'details': {
            'chain': 'ethereum',
            'address': '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045'
        }
    },
    
    'wallet_accessed': {
        'description': 'User viewed wallet details',
        'details': {
            'wallet_id': 'uuid',
            'chain': 'bitcoin',
            'action': 'view_balance'
        }
    },
    
    'seed_phrase_viewed': {
        'description': 'User viewed seed phrase (CRITICAL)',
        'details': {
            'wallet_id': 'uuid',
            'reason': 'backup' | 'recovery'
        }
    },
    
    'private_key_exported': {
        'description': 'Private key exported (CRITICAL)',
        'details': {
            'wallet_id': 'uuid',
            'chain': 'ethereum',
            'export_format': 'json' | 'text'
        }
    }
}
```

### **2. Transactions**
```python
TRANSACTION_ACTIVITIES = {
    'transaction_sent': {
        'description': 'Outgoing transaction',
        'details': {
            'chain': 'ethereum',
            'from': '0xABC...',
            'to': '0xDEF...',
            'amount': 1.5,
            'currency': 'ETH',
            'tx_hash': '0x123...',
            'gas_fee': 0.002,
            'status': 'pending' | 'confirmed' | 'failed'
        }
    },
    
    'transaction_received': {
        'description': 'Incoming transaction',
        'details': {
            'chain': 'bitcoin',
            'from': '1ABC...',
            'to': '1DEF...',
            'amount': 0.5,
            'currency': 'BTC',
            'tx_hash': 'abc123...',
            'confirmations': 6
        }
    }
}
```

### **3. Balance Changes**
```python
BALANCE_ACTIVITIES = {
    'balance_updated': {
        'description': 'Balance changed',
        'details': {
            'chain': 'ethereum',
            'address': '0xABC...',
            'balance_before': 10.5,
            'balance_after': 12.0,
            'change': 1.5,
            'currency': 'ETH',
            'reason': 'transaction_received' | 'price_update'
        }
    }
}
```

---

## 🔗 Blockchain Integration (Optional)

### **Polygon Smart Contract para Audit Trail**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract WalletAuditTrail {
    struct AuditEntry {
        bytes32 activityHash;  // Hash de la actividad
        uint256 timestamp;
        address user;
        string activityType;
    }
    
    mapping(bytes32 => AuditEntry) public auditLog;
    bytes32[] public auditHashes;
    
    event ActivityLogged(
        bytes32 indexed activityHash,
        address indexed user,
        string activityType,
        uint256 timestamp
    );
    
    function logActivity(
        bytes32 _activityHash,
        string memory _activityType
    ) external {
        require(
            auditLog[_activityHash].timestamp == 0,
            "Activity already logged"
        );
        
        auditLog[_activityHash] = AuditEntry({
            activityHash: _activityHash,
            timestamp: block.timestamp,
            user: msg.sender,
            activityType: _activityType
        });
        
        auditHashes.push(_activityHash);
        
        emit ActivityLogged(
            _activityHash,
            msg.sender,
            _activityType,
            block.timestamp
        );
    }
    
    function verifyActivity(bytes32 _activityHash) 
        external 
        view 
        returns (bool exists, uint256 timestamp) 
    {
        AuditEntry memory entry = auditLog[_activityHash];
        return (entry.timestamp != 0, entry.timestamp);
    }
    
    function getAuditCount() external view returns (uint256) {
        return auditHashes.length;
    }
}
```

**Costo**: ~$0.001 por log entry en Polygon

---

## 💻 Implementation

### **Python Service**
```python
"""
Wallet Audit Trail Service
"""
import hashlib
import json
from datetime import datetime
from typing import Dict, Optional
from web3 import Web3


class WalletAuditService:
    """Service para logging inmutable de actividad de wallets"""
    
    def __init__(self, db_session, blockchain_enabled: bool = False):
        self.db = db_session
        self.blockchain_enabled = blockchain_enabled
        
        if blockchain_enabled:
            # Polygon RPC
            self.w3 = Web3(Web3.HTTPProvider('https://polygon-rpc.com'))
            # Smart contract address (deploy primero)
            self.contract_address = "0x..."
            # ABI del contrato
            self.contract_abi = [...]
            self.contract = self.w3.eth.contract(
                address=self.contract_address,
                abi=self.contract_abi
            )
    
    async def log_activity(
        self,
        user_id: str,
        wallet_id: Optional[str],
        activity_type: str,
        details: Dict,
        ip_address: str,
        user_agent: str,
        location: Optional[Dict] = None
    ) -> str:
        """
        Log actividad de wallet (inmutable)
        
        Returns:
            activity_id (UUID)
        """
        # Crear hash de la actividad
        activity_data = {
            'user_id': user_id,
            'wallet_id': wallet_id,
            'activity_type': activity_type,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        activity_hash = hashlib.sha256(
            json.dumps(activity_data, sort_keys=True).encode()
        ).hexdigest()
        
        # Guardar en PostgreSQL (inmutable por trigger)
        activity = WalletActivityLog(
            user_id=user_id,
            wallet_id=wallet_id,
            activity_type=activity_type,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            location=location
        )
        
        self.db.add(activity)
        await self.db.commit()
        
        # Opcional: Guardar en blockchain
        if self.blockchain_enabled:
            try:
                await self._log_to_blockchain(activity_hash, activity_type)
                activity.blockchain_hash = activity_hash
                activity.blockchain_confirmed = True
                await self.db.commit()
            except Exception as e:
                print(f"Warning: Blockchain logging failed: {e}")
        
        return str(activity.id)
    
    async def _log_to_blockchain(
        self,
        activity_hash: str,
        activity_type: str
    ):
        """Log activity to Polygon blockchain"""
        # Convertir hash a bytes32
        hash_bytes = bytes.fromhex(activity_hash)
        
        # Llamar smart contract
        tx = self.contract.functions.logActivity(
            hash_bytes,
            activity_type
        ).build_transaction({
            'from': self.w3.eth.default_account,
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Firmar y enviar
        signed_tx = self.w3.eth.account.sign_transaction(
            tx,
            private_key=os.getenv('WALLET_PRIVATE_KEY')
        )
        
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Esperar confirmación
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return receipt
    
    async def get_user_activity(
        self,
        user_id: str,
        activity_type: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """Obtener actividad del usuario"""
        query = self.db.query(WalletActivityLog).filter(
            WalletActivityLog.user_id == user_id
        )
        
        if activity_type:
            query = query.filter(
                WalletActivityLog.activity_type == activity_type
            )
        
        query = query.order_by(
            WalletActivityLog.created_at.desc()
        ).limit(limit)
        
        return await query.all()
    
    async def verify_blockchain_integrity(
        self,
        activity_id: str
    ) -> bool:
        """Verificar que actividad existe en blockchain"""
        activity = await self.db.query(WalletActivityLog).filter(
            WalletActivityLog.id == activity_id
        ).first()
        
        if not activity.blockchain_hash:
            return False
        
        # Verificar en blockchain
        hash_bytes = bytes.fromhex(activity.blockchain_hash)
        exists, timestamp = self.contract.functions.verifyActivity(
            hash_bytes
        ).call()
        
        return exists
```

---

## 📊 Use Cases

### **1. Tax Reporting**
```python
# Obtener todas las transacciones del año fiscal
activities = await audit_service.get_user_activity(
    user_id=user.id,
    activity_type='transaction_sent'
)

# Calcular ganancias/pérdidas
for activity in activities:
    if activity.details['currency'] == 'BTC':
        # Calcular cost basis, gains, etc.
        ...
```

### **2. Security Audit**
```python
# Detectar accesos sospechosos
activities = await audit_service.get_user_activity(
    user_id=user.id,
    activity_type='seed_phrase_viewed'
)

for activity in activities:
    if activity.ip_address != user.usual_ip:
        # Alert: Seed phrase viewed from unusual location
        await send_security_alert(user, activity)
```

### **3. Compliance Report**
```python
# Generar reporte para auditor
report = {
    'user_id': user.id,
    'period': '2024-01-01 to 2024-12-31',
    'total_transactions': len(transactions),
    'total_volume': sum(tx.details['amount'] for tx in transactions),
    'blockchain_verified': all(tx.blockchain_confirmed for tx in transactions)
}
```

---

## ✅ Benefits

### **Compliance**:
- ✅ AML (Anti-Money Laundering)
- ✅ KYC (Know Your Customer)
- ✅ Tax reporting (IRS, AFIP, etc.)
- ✅ SOC 2 Type II

### **Security**:
- ✅ Detectar accesos no autorizados
- ✅ Forensics en caso de compromiso
- ✅ Audit trail para investigaciones

### **User Trust**:
- ✅ Transparencia total
- ✅ Verificable en blockchain
- ✅ Inmutable (no puede alterarse)

---

## 🎯 Next Steps

1. [ ] Implementar `WalletAuditService`
2. [ ] Deploy smart contract en Polygon testnet
3. [ ] Integrar con wallet operations
4. [ ] Crear UI para ver audit trail
5. [ ] Agregar export para tax reporting

---

**Conclusión**: Audit trail inmutable es **crítico** para compliance, security, y user trust. Combinación de PostgreSQL (inmutable por trigger) + Polygon (blockchain verification) = máxima seguridad.
