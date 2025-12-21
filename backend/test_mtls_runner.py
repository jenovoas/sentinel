#!/usr/bin/env python3
"""
Test Runner para Zero Trust mTLS (Claim 5)
Valida: Header Signing, SSRF Prevention, Timestamp Validation
"""

import sys
import asyncio
from pathlib import Path

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.security.zero_trust_mtls import (
    ZeroTrustMTLS,
    SSRFAttackDetected,
    InvalidSignature,
    TimestampViolation
)
import time


async def test_header_signing():
    """Test: Firma y verificación de headers"""
    print("\n🧪 Test 1: Header Signing & Verification")
    print("=" * 50)
    
    mtls = ZeroTrustMTLS()
    
    # Firmar request
    tenant_id = "tenant-123"
    body = '{"action": "read", "resource": "/api/data"}'
    
    signed_req = mtls.sign_request(tenant_id, body)
    print(f"✅ Request firmado para tenant: {tenant_id}")
    print(f"   Timestamp: {signed_req.timestamp}")
    print(f"   Signature: {signed_req.signature[:16]}...")
    
    # Verificar request
    try:
        result = mtls.verify_request(
            signed_req.tenant_id,
            signed_req.timestamp,
            signed_req.body,
            signed_req.signature
        )
        print("✅ Firma verificada correctamente")
        return True
    except Exception as e:
        print(f"❌ FALLO: {e}")
        return False


async def test_ssrf_prevention():
    """Test: Prevención de SSRF attack"""
    print("\n🧪 Test 2: SSRF Attack Prevention")
    print("=" * 50)
    
    mtls = ZeroTrustMTLS()
    
    # Tenant legítimo
    actual_tenant = "tenant-123"
    
    # Atacante intenta forjar header para acceder a otro tenant
    forged_tenant = "tenant-admin"  # Intento de SSRF
    
    # Firmar con tenant legítimo
    signed_req = mtls.sign_request(actual_tenant, "")
    
    # Intentar verificar con tenant forjado
    headers = {
        "X-Scope-OrgID": forged_tenant,  # FORJADO
        "X-Signature": signed_req.signature,
        "X-Timestamp": signed_req.timestamp
    }
    
    try:
        mtls.validate_headers(headers, actual_tenant)
        print("❌ FALLO: SSRF attack NO detectado")
        return False
    except SSRFAttackDetected as e:
        print(f"✅ SSRF attack DETECTADO: {e}")
        stats = mtls.get_stats()
        print(f"📊 Stats: {stats['ssrf_attacks_blocked']} SSRF attacks bloqueados")
        return True


async def test_invalid_signature():
    """Test: Detección de firma inválida"""
    print("\n🧪 Test 3: Invalid Signature Detection")
    print("=" * 50)
    
    mtls = ZeroTrustMTLS()
    
    tenant_id = "tenant-456"
    signed_req = mtls.sign_request(tenant_id, "")
    
    # Modificar signature (simular tampering)
    forged_signature = "0" * 64
    
    try:
        mtls.verify_request(
            signed_req.tenant_id,
            signed_req.timestamp,
            signed_req.body,
            forged_signature  # FORJADA
        )
        print("❌ FALLO: Firma inválida NO detectada")
        return False
    except InvalidSignature as e:
        print(f"✅ Firma inválida DETECTADA: {e}")
        stats = mtls.get_stats()
        print(f"📊 Stats: {stats['invalid_signatures']} firmas inválidas detectadas")
        return True


async def test_timestamp_validation():
    """Test: Validación de timestamp"""
    print("\n🧪 Test 4: Timestamp Validation")
    print("=" * 50)
    
    mtls = ZeroTrustMTLS()
    
    tenant_id = "tenant-789"
    
    # Test 1: Timestamp del futuro
    future_timestamp = str(int(time.time()) + 600)  # 10 minutos futuro
    signature = "fake_signature"
    
    try:
        mtls.verify_request(tenant_id, future_timestamp, "", signature)
        print("❌ FALLO: Timestamp futuro NO detectado")
        return False
    except TimestampViolation:
        print("✅ Timestamp futuro DETECTADO")
    
    # Test 2: Timestamp muy antiguo
    old_timestamp = str(int(time.time()) - 600)  # 10 minutos pasado
    
    try:
        mtls.verify_request(tenant_id, old_timestamp, "", signature)
        print("❌ FALLO: Timestamp antiguo NO detectado")
        return False
    except TimestampViolation:
        print("✅ Timestamp antiguo DETECTADO")
    
    stats = mtls.get_stats()
    print(f"📊 Stats: {stats['timestamp_violations']} violaciones de timestamp")
    
    return True


async def test_legitimate_request():
    """Test: Request legítimo es aceptado"""
    print("\n🧪 Test 5: Legitimate Request Acceptance")
    print("=" * 50)
    
    mtls = ZeroTrustMTLS()
    
    tenant_id = "tenant-prod-001"
    body = '{"query": "SELECT * FROM users"}'
    
    # Firmar request
    signed_req = mtls.sign_request(tenant_id, body)
    
    # Crear headers
    headers = {
        "X-Scope-OrgID": signed_req.tenant_id,
        "X-Signature": signed_req.signature,
        "X-Timestamp": signed_req.timestamp,
        "X-Body-Hash": signed_req.body
    }
    
    # Validar headers
    try:
        result = mtls.validate_headers(headers, tenant_id)
        print("✅ Request legítimo ACEPTADO")
        
        stats = mtls.get_stats()
        print(f"\n📊 Stats finales:")
        print(f"   Requests firmados: {stats['requests_signed']}")
        print(f"   Requests verificados: {stats['requests_verified']}")
        print(f"   SSRF attacks bloqueados: {stats['ssrf_attacks_blocked']}")
        print(f"   Firmas inválidas: {stats['invalid_signatures']}")
        
        return True
    except Exception as e:
        print(f"❌ FALLO: Request legítimo rechazado: {e}")
        return False


async def test_multiple_ssrf_attempts():
    """Test: Múltiples intentos de SSRF"""
    print("\n🧪 Test 6: Multiple SSRF Attempts")
    print("=" * 50)
    
    mtls = ZeroTrustMTLS()
    
    actual_tenant = "tenant-user-123"
    target_tenants = [
        "tenant-admin",
        "tenant-root",
        "tenant-system",
        "tenant-billing",
        "tenant-analytics"
    ]
    
    blocked = 0
    
    for target in target_tenants:
        signed_req = mtls.sign_request(actual_tenant, "")
        
        headers = {
            "X-Scope-OrgID": target,  # Intento de SSRF
            "X-Signature": signed_req.signature,
            "X-Timestamp": signed_req.timestamp
        }
        
        try:
            mtls.validate_headers(headers, actual_tenant)
        except SSRFAttackDetected:
            blocked += 1
    
    print(f"✅ {blocked}/{len(target_tenants)} SSRF attempts bloqueados")
    
    stats = mtls.get_stats()
    if stats['ssrf_attacks_blocked'] == len(target_tenants):
        print("✅ Todos los SSRF attacks bloqueados")
        return True
    else:
        print(f"❌ FALLO: Solo {stats['ssrf_attacks_blocked']}/{len(target_tenants)} bloqueados")
        return False


async def main():
    """Ejecuta todos los tests"""
    print("\n" + "=" * 70)
    print("🔬 ZERO TRUST mTLS - TEST SUITE")
    print("   Claim 5: Header Signing + SSRF Prevention + Timestamp Validation")
    print("=" * 70)
    
    tests = [
        ("Header Signing & Verification", test_header_signing),
        ("SSRF Attack Prevention", test_ssrf_prevention),
        ("Invalid Signature Detection", test_invalid_signature),
        ("Timestamp Validation", test_timestamp_validation),
        ("Legitimate Request Acceptance", test_legitimate_request),
        ("Multiple SSRF Attempts", test_multiple_ssrf_attempts)
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
        print("\n✅ Claim 5 (Zero Trust mTLS) VALIDADO")
        print("   - Header Signing (HMAC-SHA256): ✅ Funcionando")
        print("   - SSRF Prevention: ✅ Funcionando")
        print("   - Timestamp Validation: ✅ Funcionando")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests fallaron")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
