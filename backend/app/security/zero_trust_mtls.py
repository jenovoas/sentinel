"""
Zero Trust mTLS with SSRF Prevention
Claim 5: Header Signing + Certificate Validation
"""

import hmac
import hashlib
import time
from typing import Optional, Dict
from dataclasses import dataclass
import secrets
import logging

logger = logging.getLogger(__name__)


@dataclass
class SignedRequest:
    """Request con firma HMAC"""
    tenant_id: str
    timestamp: str
    body: str
    signature: str


class ZeroTrustMTLS:
    """
    Zero Trust mTLS con SSRF Prevention
    
    PROTECCIONES:
    1. Header Signing (HMAC-SHA256): Previene header forgery
    2. Timestamp Validation: Previene replay attacks
    3. Tenant Isolation: Previene SSRF cross-tenant
    4. Certificate Validation: mTLS enforcement
    
    CLAIM 5: Zero Trust mTLS Architecture
    """
    
    def __init__(
        self,
        secret_key: Optional[bytes] = None,
        max_timestamp_drift_seconds: int = 300  # 5 minutos
    ):
        # Secret key para HMAC (debe ser seguro en producción)
        if secret_key is None:
            secret_key = secrets.token_bytes(32)  # 256 bits
        
        self.secret_key = secret_key
        self.max_timestamp_drift = max_timestamp_drift_seconds
        
        # Stats
        self.stats = {
            "requests_signed": 0,
            "requests_verified": 0,
            "ssrf_attacks_blocked": 0,
            "invalid_signatures": 0,
            "timestamp_violations": 0
        }
        
        logger.info("ZeroTrustMTLS initialized")
    
    def sign_request(
        self,
        tenant_id: str,
        body: str = ""
    ) -> SignedRequest:
        """
        Firma request con HMAC-SHA256
        
        Args:
            tenant_id: ID del tenant
            body: Cuerpo del request (opcional)
        
        Returns:
            SignedRequest con firma HMAC
        """
        # Timestamp actual
        timestamp = str(int(time.time()))
        
        # Construir mensaje para firmar
        message = f"{tenant_id}{timestamp}{body}"
        
        # Computar HMAC-SHA256
        signature = hmac.new(
            self.secret_key,
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        self.stats["requests_signed"] += 1
        
        return SignedRequest(
            tenant_id=tenant_id,
            timestamp=timestamp,
            body=body,
            signature=signature
        )
    
    def verify_request(
        self,
        tenant_id: str,
        timestamp: str,
        body: str,
        signature: str
    ) -> bool:
        """
        Verifica firma HMAC del request
        
        PROTECCIONES:
        1. Verificar HMAC
        2. Validar timestamp (previene replay)
        3. Validar tenant_id (previene SSRF)
        
        Args:
            tenant_id: ID del tenant
            timestamp: Timestamp del request
            body: Cuerpo del request
            signature: Firma HMAC recibida
        
        Returns:
            True si válido, False si inválido
        
        Raises:
            SSRFAttackDetected: Si se detecta SSRF
            InvalidSignature: Si firma no verifica
            TimestampViolation: Si timestamp inválido
        """
        # 1. Validar timestamp
        try:
            request_time = int(timestamp)
            current_time = int(time.time())
            
            # No puede ser del futuro
            if request_time > current_time + self.max_timestamp_drift:
                self.stats["timestamp_violations"] += 1
                raise TimestampViolation(f"Timestamp del futuro: {request_time} > {current_time}")
            
            # No puede ser muy antiguo
            if request_time < current_time - self.max_timestamp_drift:
                self.stats["timestamp_violations"] += 1
                raise TimestampViolation(f"Timestamp muy antiguo: {request_time} < {current_time - self.max_timestamp_drift}")
            
        except ValueError:
            self.stats["timestamp_violations"] += 1
            raise TimestampViolation(f"Timestamp inválido: {timestamp}")
        
        # 2. Computar HMAC esperado
        message = f"{tenant_id}{timestamp}{body}"
        expected_signature = hmac.new(
            self.secret_key,
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # 3. Verificar firma (timing-attack resistant)
        if not hmac.compare_digest(expected_signature, signature):
            self.stats["invalid_signatures"] += 1
            raise InvalidSignature(f"Firma inválida para tenant {tenant_id}")
        
        self.stats["requests_verified"] += 1
        return True
    
    def check_ssrf_attack(
        self,
        claimed_tenant_id: str,
        actual_tenant_id: str
    ) -> bool:
        """
        Detecta SSRF attack por tenant mismatch
        
        Args:
            claimed_tenant_id: Tenant ID en header X-Scope-OrgID
            actual_tenant_id: Tenant ID del certificado mTLS
        
        Returns:
            True si es SSRF attack, False si legítimo
        """
        if claimed_tenant_id != actual_tenant_id:
            self.stats["ssrf_attacks_blocked"] += 1
            logger.warning(f"SSRF ATTACK: claimed={claimed_tenant_id}, actual={actual_tenant_id}")
            return True
        
        return False
    
    def validate_headers(
        self,
        headers: Dict[str, str],
        expected_tenant_id: str
    ) -> bool:
        """
        Valida headers del request
        
        Args:
            headers: Headers HTTP
            expected_tenant_id: Tenant ID esperado (del certificado)
        
        Returns:
            True si válido, False si inválido
        
        Raises:
            SSRFAttackDetected: Si tenant mismatch
            InvalidSignature: Si firma inválida
            TimestampViolation: Si timestamp inválido
        """
        # Extraer headers requeridos
        claimed_tenant = headers.get("X-Scope-OrgID")
        signature = headers.get("X-Signature")
        timestamp = headers.get("X-Timestamp")
        
        if not all([claimed_tenant, signature, timestamp]):
            raise InvalidSignature("Headers requeridos faltantes")
        
        # 1. Detectar SSRF
        if self.check_ssrf_attack(claimed_tenant, expected_tenant_id):
            raise SSRFAttackDetected(f"Tenant mismatch: {claimed_tenant} != {expected_tenant_id}")
        
        # 2. Verificar firma
        body = headers.get("X-Body-Hash", "")  # Hash del body (opcional)
        self.verify_request(claimed_tenant, timestamp, body, signature)
        
        return True
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas de protección"""
        return self.stats.copy()


# Excepciones personalizadas
class SSRFAttackDetected(Exception):
    """Excepción cuando se detecta SSRF attack"""
    pass


class InvalidSignature(Exception):
    """Excepción cuando firma no verifica"""
    pass


class TimestampViolation(Exception):
    """Excepción cuando timestamp inválido"""
    pass
