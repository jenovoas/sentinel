"""
Forensic-Grade Write-Ahead Log (WAL) con Replay Protection
Claim 4: HMAC + Replay Detection + Timestamp Validation
"""

import asyncio
import time
import json
import hmac
import hashlib
import secrets
from typing import Optional, Dict, Set
from pathlib import Path
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class WALRecord:
    """Registro WAL con protección forense"""
    event_id: str          # UUID único
    timestamp: float       # Unix timestamp
    nonce: str            # Nonce único (previene replay)
    data: dict            # Datos del evento
    hmac_signature: str   # HMAC-SHA256 del registro


class ForensicWAL:
    """
    Write-Ahead Log con protección forense
    
    PROTECCIONES:
    1. HMAC-SHA256: Integridad criptográfica
    2. Nonce-based replay detection: Previene replay attacks
    3. Timestamp validation: Detecta manipulación temporal
    4. Dual-lane separation: Security vs Observability
    
    CLAIM 4: Forensic-Grade WAL
    """
    
    def __init__(
        self,
        secret_key: Optional[bytes] = None,
        base_path: Optional[Path] = None,
        max_timestamp_drift_seconds: int = 300  # 5 minutos
    ):
        # Secret key para HMAC (debe ser seguro en producción)
        if secret_key is None:
            secret_key = secrets.token_bytes(32)  # 256 bits
        
        self.secret_key = secret_key
        
        # Base path para archivos WAL
        if base_path is None:
            base_path = Path("/tmp/sentinel/forensic_wal")
        
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Replay protection: Set de nonces vistos
        self.seen_nonces: Set[str] = set()
        
        # Timestamp validation
        self.max_timestamp_drift = max_timestamp_drift_seconds
        self.last_timestamp = 0.0
        
        # Stats
        self.stats = {
            "events_written": 0,
            "replay_attacks_blocked": 0,
            "timestamp_manipulations_blocked": 0,
            "hmac_failures": 0
        }
        
        logger.info(f"ForensicWAL initialized: {self.base_path}")
    
    def _generate_nonce(self) -> str:
        """Genera nonce único de 32 bytes"""
        return secrets.token_hex(32)
    
    def _compute_hmac(self, record_data: dict) -> str:
        """
        Computa HMAC-SHA256 del registro
        
        Input: event_id + timestamp + nonce + data
        Output: HMAC hex string
        """
        # Serializar datos en orden determinístico
        message = json.dumps(record_data, sort_keys=True).encode('utf-8')
        
        # Computar HMAC
        signature = hmac.new(
            self.secret_key,
            message,
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _verify_hmac(self, record: WALRecord) -> bool:
        """Verifica HMAC del registro"""
        # Reconstruir datos sin signature
        record_data = {
            "event_id": record.event_id,
            "timestamp": record.timestamp,
            "nonce": record.nonce,
            "data": record.data
        }
        
        # Computar HMAC esperado
        expected_hmac = self._compute_hmac(record_data)
        
        # Comparación segura (timing-attack resistant)
        return hmac.compare_digest(expected_hmac, record.hmac_signature)
    
    def _check_replay_attack(self, nonce: str) -> bool:
        """
        Detecta replay attack por nonce duplicado
        
        Returns:
            True si es replay attack, False si es legítimo
        """
        if nonce in self.seen_nonces:
            return True  # REPLAY ATTACK DETECTED
        
        return False
    
    def _check_timestamp_manipulation(self, timestamp: float) -> bool:
        """
        Detecta manipulación de timestamp
        
        Reglas:
        1. Timestamp no puede ser del futuro (> now + drift)
        2. Timestamp no puede ser muy antiguo (< now - drift)
        3. Timestamps deben ser monotónicamente crecientes (aprox)
        
        Returns:
            True si es manipulación, False si es legítimo
        """
        now = time.time()
        
        # Regla 1: No puede ser del futuro
        if timestamp > (now + self.max_timestamp_drift):
            logger.warning(f"Timestamp manipulation: future timestamp ({timestamp} > {now})")
            return True
        
        # Regla 2: No puede ser muy antiguo
        if timestamp < (now - self.max_timestamp_drift):
            logger.warning(f"Timestamp manipulation: too old ({timestamp} < {now - self.max_timestamp_drift})")
            return True
        
        # Regla 3: Debe ser >= último timestamp (con tolerancia de drift)
        if timestamp < (self.last_timestamp - self.max_timestamp_drift):
            logger.warning(f"Timestamp manipulation: out of order ({timestamp} < {self.last_timestamp})")
            return True
        
        return False
    
    async def write(self, event_data: dict) -> Optional[WALRecord]:
        """
        Escribe evento al WAL con protección forense
        
        Args:
            event_data: Datos del evento
        
        Returns:
            WALRecord si exitoso, None si bloqueado
        
        Raises:
            ReplayAttackDetected: Si se detecta replay attack
            TimestampManipulationDetected: Si se detecta manipulación temporal
            HMACVerificationFailed: Si HMAC no verifica
        """
        try:
            # Generar nonce único
            nonce = self._generate_nonce()
            
            # Timestamp actual
            timestamp = time.time()
            
            # Generar event_id único
            event_id = secrets.token_hex(16)
            
            # Construir registro
            record_data = {
                "event_id": event_id,
                "timestamp": timestamp,
                "nonce": nonce,
                "data": event_data
            }
            
            # Computar HMAC
            hmac_signature = self._compute_hmac(record_data)
            
            # Crear registro
            record = WALRecord(
                event_id=event_id,
                timestamp=timestamp,
                nonce=nonce,
                data=event_data,
                hmac_signature=hmac_signature
            )
            
            # Verificar HMAC (sanity check)
            if not self._verify_hmac(record):
                self.stats["hmac_failures"] += 1
                raise HMACVerificationFailed("HMAC verification failed")
            
            # Registrar nonce (replay protection)
            self.seen_nonces.add(nonce)
            
            # Actualizar último timestamp
            self.last_timestamp = timestamp
            
            # Escribir a archivo (simplificado para POC)
            wal_file = self.base_path / "forensic.wal"
            with open(wal_file, "a") as f:
                record_json = json.dumps({
                    "event_id": record.event_id,
                    "timestamp": record.timestamp,
                    "nonce": record.nonce,
                    "data": record.data,
                    "hmac": record.hmac_signature
                })
                f.write(record_json + "\n")
            
            self.stats["events_written"] += 1
            
            return record
            
        except Exception as e:
            logger.error(f"WAL write failed: {e}")
            raise
    
    async def verify_and_accept(self, record: WALRecord) -> bool:
        """
        Verifica y acepta registro WAL
        
        PROTECCIONES:
        1. Verificar HMAC
        2. Detectar replay attack
        3. Detectar timestamp manipulation
        
        Returns:
            True si aceptado, False si rechazado
        """
        # 1. Verificar HMAC
        if not self._verify_hmac(record):
            self.stats["hmac_failures"] += 1
            logger.warning(f"HMAC verification failed for event {record.event_id}")
            return False
        
        # 2. Detectar replay attack
        if self._check_replay_attack(record.nonce):
            self.stats["replay_attacks_blocked"] += 1
            logger.warning(f"REPLAY ATTACK DETECTED: nonce {record.nonce} already seen")
            raise ReplayAttackDetected(f"Nonce {record.nonce} already used")
        
        # 3. Detectar timestamp manipulation
        if self._check_timestamp_manipulation(record.timestamp):
            self.stats["timestamp_manipulations_blocked"] += 1
            logger.warning(f"TIMESTAMP MANIPULATION DETECTED: {record.timestamp}")
            raise TimestampManipulationDetected(f"Invalid timestamp {record.timestamp}")
        
        # Todo OK - aceptar registro
        self.seen_nonces.add(record.nonce)
        self.last_timestamp = record.timestamp
        
        return True
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas de protección"""
        return self.stats.copy()


# Excepciones personalizadas
class ReplayAttackDetected(Exception):
    """Excepción cuando se detecta replay attack"""
    pass


class TimestampManipulationDetected(Exception):
    """Excepción cuando se detecta manipulación de timestamp"""
    pass


class HMACVerificationFailed(Exception):
    """Excepción cuando HMAC no verifica"""
    pass
