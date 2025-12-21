#!/usr/bin/env python3
"""
Test Runner Simple para Forensic WAL
Ejecuta tests sin necesidad de pytest
"""

import sys
import asyncio
from pathlib import Path

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.forensic_wal import (
    ForensicWAL,
    ReplayAttackDetected,
    TimestampManipulationDetected
)
import tempfile
import shutil
import time


async def test_replay_attack():
    """Test: Detección de replay attack"""
    print("\n🧪 Test 1: Replay Attack Detection")
    print("=" * 50)
    
    temp_dir = Path(tempfile.mkdtemp())
    wal = ForensicWAL(base_path=temp_dir)
    
    try:
        # Evento original
        event_data = {"action": "transfer_money", "amount": 1000}
        record = await wal.write(event_data)
        print(f"✅ Evento original escrito: {record.event_id}")
        
        # Intentar replay - debe fallar
        try:
            await wal.verify_and_accept(record)
            print("❌ FALLO: Replay attack NO detectado")
            return False
        except ReplayAttackDetected:
            print("✅ Replay attack DETECTADO correctamente")
        
        stats = wal.get_stats()
        print(f"📊 Stats: {stats['replay_attacks_blocked']} replay attacks bloqueados")
        
        return True
        
    finally:
        shutil.rmtree(temp_dir)


async def test_timestamp_manipulation():
    """Test: Detección de timestamp manipulation"""
    print("\n🧪 Test 2: Timestamp Manipulation Detection")
    print("=" * 50)
    
    temp_dir = Path(tempfile.mkdtemp())
    wal = ForensicWAL(base_path=temp_dir)
    
    try:
        # Escribir evento legítimo primero
        event_data = {"action": "delete_logs", "target": "/var/log"}
        record1 = await wal.write(event_data)
        print(f"✅ Evento original escrito: {record1.event_id}")
        
        # Crear segundo evento con timestamp manipulado
        # Esto debería fallar en _check_timestamp_manipulation
        event_data2 = {"action": "admin_access", "user_id": "admin"}
        record2 = await wal.write(event_data2)
        
        # Ahora intentar escribir evento con timestamp del futuro
        # Modificamos el método interno para simular timestamp manipulation
        original_check = wal._check_timestamp_manipulation
        
        def fake_timestamp_check(ts):
            # Simular timestamp del futuro
            return ts > time.time() + 600
        
        # Probar con timestamp del futuro
        future_timestamp = time.time() + 700
        if wal._check_timestamp_manipulation(future_timestamp):
            print(f"✅ Timestamp manipulation DETECTADO (futuro)")
        else:
            print("❌ FALLO: Timestamp del futuro NO detectado")
            return False
        
        # Probar con timestamp del pasado
        past_timestamp = time.time() - 700
        if wal._check_timestamp_manipulation(past_timestamp):
            print(f"✅ Timestamp manipulation DETECTADO (pasado)")
        else:
            print("❌ FALLO: Timestamp del pasado NO detectado")
            return False
        
        return True
        
    finally:
        shutil.rmtree(temp_dir)


async def test_hmac_verification():
    """Test: Verificación de HMAC"""
    print("\n🧪 Test 3: HMAC Verification")
    print("=" * 50)
    
    temp_dir = Path(tempfile.mkdtemp())
    wal = ForensicWAL(base_path=temp_dir)
    
    try:
        # Evento original
        event_data = {"action": "admin_access", "user_id": "admin"}
        record = await wal.write(event_data)
        print(f"✅ Evento original escrito: {record.event_id}")
        
        # HMAC debe verificar
        if wal._verify_hmac(record):
            print("✅ HMAC verificado correctamente")
        else:
            print("❌ FALLO: HMAC no verifica")
            return False
        
        # Modificar datos - HMAC debe fallar
        record.data["user_id"] = "hacker"
        if not wal._verify_hmac(record):
            print("✅ HMAC inválido detectado después de modificación")
        else:
            print("❌ FALLO: HMAC sigue verificando después de modificación")
            return False
        
        return True
        
    finally:
        shutil.rmtree(temp_dir)


async def test_legitimate_events():
    """Test: Eventos legítimos son aceptados"""
    print("\n🧪 Test 4: Legitimate Events Acceptance")
    print("=" * 50)
    
    temp_dir = Path(tempfile.mkdtemp())
    wal = ForensicWAL(base_path=temp_dir)
    
    try:
        events = [
            {"action": "user_login", "user_id": "user1"},
            {"action": "file_read", "file": "/etc/passwd"},
            {"action": "user_logout", "user_id": "user1"}
        ]
        
        for i, event_data in enumerate(events, 1):
            record = await wal.write(event_data)
            print(f"✅ Evento {i}/3 escrito: {record.event_id}")
        
        stats = wal.get_stats()
        print(f"\n📊 Stats finales:")
        print(f"   Eventos escritos: {stats['events_written']}")
        print(f"   Replay attacks bloqueados: {stats['replay_attacks_blocked']}")
        print(f"   Timestamp manipulations bloqueadas: {stats['timestamp_manipulations_blocked']}")
        
        if stats['events_written'] == 3 and stats['replay_attacks_blocked'] == 0:
            print("✅ Todos los eventos legítimos aceptados")
            return True
        else:
            print("❌ FALLO: Eventos legítimos rechazados incorrectamente")
            return False
        
    finally:
        shutil.rmtree(temp_dir)


async def test_multiple_replay_attempts():
    """Test: Múltiples intentos de replay"""
    print("\n🧪 Test 5: Multiple Replay Attempts")
    print("=" * 50)
    
    temp_dir = Path(tempfile.mkdtemp())
    wal = ForensicWAL(base_path=temp_dir)
    
    try:
        # Evento original
        event_data = {"action": "withdraw_money", "amount": 10000}
        record = await wal.write(event_data)
        print(f"✅ Evento original escrito: {record.event_id}")
        
        # Intentar replay 10 veces
        blocked = 0
        for i in range(10):
            try:
                await wal.verify_and_accept(record)
            except ReplayAttackDetected:
                blocked += 1
        
        print(f"✅ {blocked}/10 replay attacks bloqueados")
        
        stats = wal.get_stats()
        if stats['replay_attacks_blocked'] == 10:
            print("✅ Todos los replay attacks bloqueados")
            return True
        else:
            print(f"❌ FALLO: Solo {stats['replay_attacks_blocked']}/10 bloqueados")
            return False
        
    finally:
        shutil.rmtree(temp_dir)


async def main():
    """Ejecuta todos los tests"""
    print("\n" + "=" * 70)
    print("🔬 FORENSIC WAL - TEST SUITE")
    print("   Claim 4: HMAC + Replay Protection + Timestamp Validation")
    print("=" * 70)
    
    tests = [
        ("Replay Attack Detection", test_replay_attack),
        ("Timestamp Manipulation Detection", test_timestamp_manipulation),
        ("HMAC Verification", test_hmac_verification),
        ("Legitimate Events Acceptance", test_legitimate_events),
        ("Multiple Replay Attempts", test_multiple_replay_attempts)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' falló con excepción: {e}")
            results.append((test_name, False))
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE TESTS")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 70)
    print(f"Resultado: {passed}/{total} tests pasados ({passed/total*100:.0f}%)")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("\n✅ Claim 4 (Forensic-Grade WAL) VALIDADO")
        print("   - HMAC-SHA256: ✅ Funcionando")
        print("   - Replay Protection: ✅ Funcionando")
        print("   - Timestamp Validation: ✅ Funcionando")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests fallaron")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
