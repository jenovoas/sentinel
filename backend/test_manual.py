"""
Test Comparativo Real - V1 vs V2
Prueba con diferentes tipos de queries para ver el beneficio real
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import asyncio
import time
from statistics import mean
from app.services.sentinel_fluido import SentinelFluido
from app.services.sentinel_fluido_v2 import SentinelFluidoV2


async def test_comparativo():
    """Test con queries de diferentes tamaños"""
    print("\n" + "="*60)
    print("🧪 TEST COMPARATIVO - V1 vs V2")
    print("="*60)
    
    # Queries de diferentes tamaños
    queries = {
        "short": [
            "Hola",
            "¿Qué hora es?",
            "Gracias"
        ],
        "medium": [
            "¿Cómo funciona Sentinel?",
            "Explica los buffers dinámicos",
            "¿Qué es AIOpsShield?"
        ],
        "long": [
            "Explica en detalle cómo funciona el sistema de buffers jerárquicos en Sentinel",
            "Describe la arquitectura completa de Sentinel Cortex incluyendo todos los componentes"
        ]
    }
    
    results = {"v1": {}, "v2": {}}
    
    # TEST V1
    print("\n📊 V1 (Buffers Estáticos):")
    print("-" * 60)
    sentinel_v1 = SentinelFluido()
    
    for qtype, qlist in queries.items():
        ttfbs = []
        print(f"\n{qtype.upper()}:")
        for i, query in enumerate(qlist):
            _, ttfb = await sentinel_v1.responder_simple(f"user_{i}", query)
            ttfbs.append(ttfb)
            print(f"  [{i+1}] TTFB: {ttfb:.0f}ms")
        
        results["v1"][qtype] = mean(ttfbs)
        print(f"  → Promedio: {results['v1'][qtype]:.0f}ms")
    
    await sentinel_v1.close()
    
    # TEST V2
    print("\n📊 V2 (Buffers Dinámicos):")
    print("-" * 60)
    sentinel_v2 = SentinelFluidoV2()
    
    for qtype, qlist in queries.items():
        ttfbs = []
        print(f"\n{qtype.upper()}:")
        for i, query in enumerate(qlist):
            _, ttfb = await sentinel_v2.responder_simple(f"user_{i}", query)
            ttfbs.append(ttfb)
            print(f"  [{i+1}] TTFB: {ttfb:.0f}ms")
        
        results["v2"][qtype] = mean(ttfbs)
        print(f"  → Promedio: {results['v2'][qtype]:.0f}ms")
    
    await sentinel_v2.close()
    
    # COMPARACIÓN
    print("\n" + "="*60)
    print("📊 COMPARACIÓN FINAL")
    print("="*60)
    
    for qtype in ["short", "medium", "long"]:
        v1_avg = results["v1"][qtype]
        v2_avg = results["v2"][qtype]
        diff = v1_avg - v2_avg
        pct = (diff / v1_avg * 100) if v1_avg > 0 else 0
        
        print(f"\n{qtype.upper()}:")
        print(f"  V1: {v1_avg:.0f}ms")
        print(f"  V2: {v2_avg:.0f}ms")
        if diff > 0:
            print(f"  ✅ V2 es {pct:.1f}% más rápido ({diff:.0f}ms menos)")
        else:
            print(f"  ⚠️ V2 es {abs(pct):.1f}% más lento ({abs(diff):.0f}ms más)")
    
    print("\n✅ Test completado\n")


if __name__ == "__main__":
    asyncio.run(test_comparativo())
