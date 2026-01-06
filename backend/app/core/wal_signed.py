"""
WAL con Protección HMAC y Nonce
Write-Ahead Log con protección contra replay attacks

SEGURIDAD:
- Nonce monotónico (contador incremental)
- Timestamp monotónico del kernel
- HMAC-SHA256 por registro
- Detección de replay attacks
- Alertas de integrity gaps
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import hmac
import hashlib
import time
import json
import gzip
from pathlib import Path
from typing import AsyncGenerator, Optional, Dict
from dataclasses import dataclass, asdict
import asyncio

from app.core.data_lanes import DataLane, LaneEvent


@dataclass
class WALRecordSigned:
    """WAL record con nonce + HMAC"""
    nonce: int              # Monotonic counter
    timestamp: int          # Kernel monotonic time (nanoseconds)
    event: dict            # Lane event serializado
    hmac_signature: str    # HMAC-SHA256 hex


class WALSigned:
    """
    Write-Ahead Log con protección contra replay
    
    GARANTÍAS:
    - Nonce monotónico (detecta replay)
    - Timestamp monotónico (detecta clock manipulation)
    - HMAC por registro (detecta tampering)
    - Integrity gaps alertados
    """
    
    def __init__(
        self,
        base_path: Path = Path("/tmp/sentinel-wal"),
        secret_key: str = "sentinel_wal_secret_change_in_production"
    ):
        """
        Inicializa WAL firmado
        
        Args:
            base_path: Directorio base para WAL
            secret_key: Clave secreta para HMAC
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.secret_key = secret_key.encode('utf-8')
        
        # Nonce counters por lane
        self.nonce_counters: Dict[DataLane, int] = {
            DataLane.SECURITY: 0,
            DataLane.OBSERVABILITY: 0
        }
        
        # Last timestamps por lane
        self.last_timestamps: Dict[DataLane, int] = {
            DataLane.SECURITY: 0,
            DataLane.OBSERVABILITY: 0
        }
        
        # WAL files por lane
        self.wal_files: Dict[DataLane, Path] = {}
        for lane in DataLane:
            lane_dir = self.base_path / lane.value
            lane_dir.mkdir(exist_ok=True)
            self.wal_files[lane] = lane_dir / "current.wal"
        
        print(f"✅ WAL Signed inicializado: {self.base_path}")
    
    def _generate_hmac(
        self,
        nonce: int,
        timestamp: int,
        event_json: str
    ) -> str:
        """
        Genera HMAC-SHA256 para registro
        
        Args:
            nonce: Nonce monotónico
            timestamp: Timestamp monotónico
            event_json: Evento serializado
        
        Returns:
            HMAC en hexadecimal
        """
        # Mensaje: nonce + timestamp + event
        message = f"{nonce}{timestamp}{event_json}"
        
        # HMAC-SHA256
        signature = hmac.new(
            self.secret_key,
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    async def append(self, lane: DataLane, event: LaneEvent) -> bool:
        """
        Append evento con nonce + HMAC
        
        Args:
            lane: Lane del evento
            event: Evento a escribir
        
        Returns:
            True si exitoso
        """
        # 1. Incrementar nonce (monotónico)
        self.nonce_counters[lane] += 1
        nonce = self.nonce_counters[lane]
        
        # 2. Timestamp monotónico del kernel
        timestamp = time.clock_gettime_ns(time.CLOCK_MONOTONIC)
        
        # 3. Validar monotonía
        if timestamp <= self.last_timestamps[lane]:
            print(f"❌ WAL: Non-monotonic timestamp detected in {lane.value}")
            print(f"   Current: {timestamp}, Last: {self.last_timestamps[lane]}")
            await self._alert_integrity_violation(lane, nonce, "non_monotonic_timestamp")
            return False
        
        self.last_timestamps[lane] = timestamp
        
        # 4. Serializar evento
        event_dict = {
            'lane': event.lane.value,
            'source': event.source,
            'priority': event.priority.value,
            'timestamp': event.timestamp,
            'labels': event.labels,
            'data': event.data
        }
        event_json = json.dumps(event_dict, sort_keys=True)
        
        # 5. Generar HMAC
        hmac_sig = self._generate_hmac(nonce, timestamp, event_json)
        
        # 6. Crear record firmado
        record = WALRecordSigned(
            nonce=nonce,
            timestamp=timestamp,
            event=event_dict,
            hmac_signature=hmac_sig
        )
        
        # 7. Escribir a WAL
        wal_file = self.wal_files[lane]
        record_json = json.dumps(asdict(record))
        
        async with asyncio.Lock():
            with open(wal_file, 'a') as f:
                f.write(record_json + '\n')
        
        return True
    
    async def replay(self, lane: DataLane) -> AsyncGenerator[LaneEvent, None]:
        """
        Replay WAL con verificación de integridad
        
        Args:
            lane: Lane a replay
        
        Yields:
            Eventos válidos
        """
        wal_file = self.wal_files[lane]
        
        if not wal_file.exists():
            print(f"⚠️ WAL no existe: {wal_file}")
            return
        
        last_nonce = 0
        last_timestamp = 0
        valid_count = 0
        invalid_count = 0
        
        with open(wal_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    # Parse record
                    record_dict = json.loads(line.strip())
                    record = WALRecordSigned(**record_dict)
                    
                    # 1. Verificar HMAC
                    event_json = json.dumps(record.event, sort_keys=True)
                    expected_hmac = self._generate_hmac(
                        record.nonce,
                        record.timestamp,
                        event_json
                    )
                    
                    if record.hmac_signature != expected_hmac:
                        print(f"❌ WAL INTEGRITY VIOLATION: Invalid HMAC at line {line_num}")
                        await self._alert_integrity_violation(
                            lane, record.nonce, "invalid_hmac"
                        )
                        invalid_count += 1
                        continue
                    
                    # 2. Verificar monotonía de nonce
                    if record.nonce <= last_nonce:
                        print(f"❌ WAL REPLAY ATTACK: Non-monotonic nonce at line {line_num}")
                        print(f"   Current: {record.nonce}, Last: {last_nonce}")
                        await self._alert_replay_attack(lane, record)
                        invalid_count += 1
                        continue
                    
                    # 3. Verificar monotonía de timestamp
                    if record.timestamp <= last_timestamp:
                        print(f"❌ WAL REPLAY ATTACK: Non-monotonic timestamp at line {line_num}")
                        await self._alert_replay_attack(lane, record)
                        invalid_count += 1
                        continue
                    
                    last_nonce = record.nonce
                    last_timestamp = record.timestamp
                    
                    # 4. Evento válido
                    event = LaneEvent(
                        lane=DataLane(record.event['lane']),
                        source=record.event['source'],
                        priority=record.event['priority'],
                        timestamp=record.event['timestamp'],
                        labels=record.event['labels'],
                        data=record.event['data']
                    )
                    
                    valid_count += 1
                    yield event
                    
                except Exception as e:
                    print(f"❌ Error parsing line {line_num}: {e}")
                    invalid_count += 1
        
        print(f"✅ WAL Replay complete: {valid_count} valid, {invalid_count} invalid")
    
    async def _alert_integrity_violation(
        self,
        lane: DataLane,
        nonce: int,
        violation_type: str
    ):
        """Alerta de violación de integridad"""
        alert = {
            'alert_type': 'WAL_INTEGRITY_VIOLATION',
            'lane': lane.value,
            'nonce': nonce,
            'violation_type': violation_type,
            'timestamp': time.time()
        }
        
        # TODO: Enviar a sistema de alertas
        print(f"🚨 INTEGRITY VIOLATION: {json.dumps(alert)}")
    
    async def _alert_replay_attack(
        self,
        lane: DataLane,
        record: WALRecordSigned
    ):
        """Alerta de replay attack"""
        alert = {
            'alert_type': 'WAL_REPLAY_ATTACK',
            'lane': lane.value,
            'nonce': record.nonce,
            'timestamp': record.timestamp,
            'detected_at': time.time()
        }
        
        # TODO: Enviar a sistema de alertas
        print(f"🚨 REPLAY ATTACK: {json.dumps(alert)}")
    
    async def flush(self, lane: DataLane):
        """Flush WAL (fsync)"""
        wal_file = self.wal_files[lane]
        
        if wal_file.exists():
            # Force fsync
            with open(wal_file, 'a') as f:
                f.flush()
                import os
                os.fsync(f.fileno())


# Ejemplo de uso
if __name__ == "__main__":
    import asyncio
    from app.core.data_lanes import EventPriority
    
    async def test_wal_signed():
        print("🔒 WAL con Nonce + HMAC Protection\n")
        
        # 1. Crear WAL
        wal = WALSigned()
        
        print()
        
        # 2. Append eventos normales
        print("📝 Appending eventos...")
        for i in range(5):
            event = LaneEvent(
                lane=DataLane.SECURITY,
                source="auditd",
                priority=EventPriority.CRITICAL,
                timestamp=time.time(),
                labels={"lane": "security"},
                data={"event_id": i, "message": f"Security event {i}"}
            )
            
            success = await wal.append(DataLane.SECURITY, event)
            if success:
                print(f"   ✅ Event {i} appended (nonce={wal.nonce_counters[DataLane.SECURITY]})")
        
        print()
        
        # 3. Flush
        await wal.flush(DataLane.SECURITY)
        print("✅ WAL flushed\n")
        
        # 4. Replay
        print("🔄 Replaying WAL...")
        count = 0
        async for event in wal.replay(DataLane.SECURITY):
            count += 1
            print(f"   ✅ Event {count}: {event.data['message']}")
        
        print()
        
        # 5. Test replay attack (simulado)
        print("🧪 Testing replay attack detection...")
        
        # Intentar append con nonce antiguo (simulado manualmente)
        wal_file = wal.wal_files[DataLane.SECURITY]
        
        # Leer primer registro
        with open(wal_file, 'r') as f:
            first_line = f.readline()
        
        # Append de nuevo (replay)
        with open(wal_file, 'a') as f:
            f.write(first_line)
        
        print("   Registro antiguo agregado al final del WAL")
        print()
        
        # Replay debería detectar el ataque
        print("🔄 Replaying WAL (debería detectar replay)...")
        count = 0
        async for event in wal.replay(DataLane.SECURITY):
            count += 1
        
        print(f"\n✅ WAL Signed listo para producción")
    
    asyncio.run(test_wal_signed())
