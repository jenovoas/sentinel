"""
Tests para Forensic-Grade WAL (Claim 4)
Valida: HMAC, Replay Protection, Timestamp Validation
"""

import pytest
import asyncio
import time
from pathlib import Path
import tempfile
import shutil

from backend.app.core.forensic_wal import (
    ForensicWAL,
    WALRecord,
    ReplayAttackDetected,
    TimestampManipulationDetected,
    HMACVerificationFailed
)


@pytest.fixture
def temp_wal_dir():
    """Crea directorio temporal para tests"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def forensic_wal(temp_wal_dir):
    """Crea instancia de ForensicWAL para tests"""
    return ForensicWAL(base_path=temp_wal_dir)


@pytest.mark.asyncio
async def test_write_event_success(forensic_wal):
    """Test: Escritura exitosa de evento"""
    event_data = {"action": "user_login", "user_id": "123"}
    
    record = await forensic_wal.write(event_data)
    
    assert record is not None
    assert record.event_id is not None
    assert record.nonce is not None
    assert record.hmac_signature is not None
    assert record.data == event_data
    
    stats = forensic_wal.get_stats()
    assert stats["events_written"] == 1
    assert stats["replay_attacks_blocked"] == 0


@pytest.mark.asyncio
async def test_hmac_verification(forensic_wal):
    """Test: Verificación de HMAC"""
    event_data = {"action": "delete_user", "user_id": "456"}
    
    record = await forensic_wal.write(event_data)
    
    # HMAC debe verificar correctamente
    assert forensic_wal._verify_hmac(record) is True
    
    # Modificar datos debe invalidar HMAC
    record.data["user_id"] = "999"  # Modificación maliciosa
    assert forensic_wal._verify_hmac(record) is False


@pytest.mark.asyncio
async def test_replay_attack_detection(forensic_wal):
    """Test: Detección de replay attack"""
    event_data = {"action": "transfer_money", "amount": 1000}
    
    # Primer evento - debe pasar
    record1 = await forensic_wal.write(event_data)
    assert record1 is not None
    
    # Intentar replay del mismo nonce - debe fallar
    with pytest.raises(ReplayAttackDetected):
        await forensic_wal.verify_and_accept(record1)
    
    stats = forensic_wal.get_stats()
    assert stats["replay_attacks_blocked"] == 1
    
    print("✅ Replay attack detectado correctamente")


@pytest.mark.asyncio
async def test_timestamp_manipulation_future(forensic_wal):
    """Test: Detección de timestamp del futuro"""
    event_data = {"action": "admin_access", "user_id": "admin"}
    
    # Crear evento legítimo
    record = await forensic_wal.write(event_data)
    
    # Modificar timestamp al futuro (10 minutos)
    record.timestamp = time.time() + 600
    
    # Debe detectar manipulación
    with pytest.raises(TimestampManipulationDetected):
        await forensic_wal.verify_and_accept(record)
    
    stats = forensic_wal.get_stats()
    assert stats["timestamp_manipulations_blocked"] == 1
    
    print("✅ Timestamp manipulation (futuro) detectado")


@pytest.mark.asyncio
async def test_timestamp_manipulation_past(forensic_wal):
    """Test: Detección de timestamp muy antiguo"""
    event_data = {"action": "delete_logs", "target": "/var/log"}
    
    # Crear evento legítimo
    record = await forensic_wal.write(event_data)
    
    # Modificar timestamp al pasado (10 minutos)
    record.timestamp = time.time() - 600
    
    # Debe detectar manipulación
    with pytest.raises(TimestampManipulationDetected):
        await forensic_wal.verify_and_accept(record)
    
    stats = forensic_wal.get_stats()
    assert stats["timestamp_manipulations_blocked"] == 1
    
    print("✅ Timestamp manipulation (pasado) detectado")


@pytest.mark.asyncio
async def test_legitimate_events_accepted(forensic_wal):
    """Test: Eventos legítimos son aceptados"""
    events = [
        {"action": "user_login", "user_id": "user1"},
        {"action": "file_read", "file": "/etc/passwd"},
        {"action": "user_logout", "user_id": "user1"}
    ]
    
    for event_data in events:
        record = await forensic_wal.write(event_data)
        assert record is not None
    
    stats = forensic_wal.get_stats()
    assert stats["events_written"] == 3
    assert stats["replay_attacks_blocked"] == 0
    assert stats["timestamp_manipulations_blocked"] == 0
    
    print("✅ Eventos legítimos aceptados correctamente")


@pytest.mark.asyncio
async def test_nonce_uniqueness(forensic_wal):
    """Test: Nonces son únicos"""
    nonces = set()
    
    for i in range(100):
        event_data = {"action": f"event_{i}"}
        record = await forensic_wal.write(event_data)
        nonces.add(record.nonce)
    
    # Todos los nonces deben ser únicos
    assert len(nonces) == 100
    
    print("✅ Nonces únicos verificados (100 eventos)")


@pytest.mark.asyncio
async def test_hmac_tampering_detection(forensic_wal):
    """Test: Detección de tampering en HMAC"""
    event_data = {"action": "critical_operation", "level": "admin"}
    
    record = await forensic_wal.write(event_data)
    
    # Modificar HMAC (simulando tampering)
    record.hmac_signature = "0" * 64  # HMAC falso
    
    # Debe fallar verificación
    assert forensic_wal._verify_hmac(record) is False
    
    # Debe rechazar el registro
    result = await forensic_wal.verify_and_accept(record)
    assert result is False
    
    stats = forensic_wal.get_stats()
    assert stats["hmac_failures"] >= 1
    
    print("✅ Tampering de HMAC detectado")


@pytest.mark.asyncio
async def test_concurrent_writes(forensic_wal):
    """Test: Escrituras concurrentes"""
    async def write_event(i):
        event_data = {"action": f"concurrent_{i}"}
        return await forensic_wal.write(event_data)
    
    # Escribir 50 eventos concurrentemente
    tasks = [write_event(i) for i in range(50)]
    records = await asyncio.gather(*tasks)
    
    # Todos deben tener nonces únicos
    nonces = {r.nonce for r in records}
    assert len(nonces) == 50
    
    stats = forensic_wal.get_stats()
    assert stats["events_written"] == 50
    
    print("✅ Escrituras concurrentes manejadas correctamente")


@pytest.mark.asyncio
async def test_replay_attack_multiple_attempts(forensic_wal):
    """Test: Múltiples intentos de replay attack"""
    event_data = {"action": "withdraw_money", "amount": 10000}
    
    # Evento original
    record = await forensic_wal.write(event_data)
    
    # Intentar replay 10 veces
    replay_attempts = 0
    for _ in range(10):
        try:
            await forensic_wal.verify_and_accept(record)
        except ReplayAttackDetected:
            replay_attempts += 1
    
    assert replay_attempts == 10
    
    stats = forensic_wal.get_stats()
    assert stats["replay_attacks_blocked"] == 10
    
    print("✅ Múltiples replay attacks bloqueados (10/10)")


def test_stats_tracking(forensic_wal):
    """Test: Tracking de estadísticas"""
    stats = forensic_wal.get_stats()
    
    assert "events_written" in stats
    assert "replay_attacks_blocked" in stats
    assert "timestamp_manipulations_blocked" in stats
    assert "hmac_failures" in stats
    
    assert all(v >= 0 for v in stats.values())
    
    print("✅ Estadísticas tracked correctamente")


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v", "-s"])
