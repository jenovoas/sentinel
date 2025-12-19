"""
Test Sentinel Fluido
Prueba rápida con métricas reales
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.sentinel_fluido import SentinelFluido


async def test_streaming():
    """Test con streaming (recomendado)"""
    print("🚀 Test Streaming - Sentinel Fluido")
    print("=" * 60)
    
    sentinel = SentinelFluido()
    
    mensaje = "Hola, ¿cómo optimizamos Sentinel?"
    print(f"\n📝 Mensaje: {mensaje}\n")
    print("💬 Respuesta:")
    print("-" * 60)
    
    ttfb_reportado = None
    
    async for chunk, ttfb in sentinel.responder("jaime", mensaje):
        print(chunk, end='', flush=True)
        if ttfb and not ttfb_reportado:
            ttfb_reportado = ttfb
    
    print("\n" + "=" * 60)
    if ttfb_reportado:
        print(f"\n⚡ TTFB: {ttfb_reportado:.0f}ms")
        print(f"   Target: <2000ms (GTX 1050)")
        print(f"   Estado: {'✅ EXCELENTE' if ttfb_reportado < 2000 else '⚠️ Revisar config'}")
    
    await sentinel.close()
    print("\n✅ Test completado\n")


async def test_simple():
    """Test simple sin streaming"""
    print("🧪 Test Simple - Sentinel Fluido")
    print("=" * 60)
    
    sentinel = SentinelFluido()
    
    mensaje = "Hola Sentinel"
    print(f"\n📝 Mensaje: {mensaje}\n")
    
    respuesta, ttfb = await sentinel.responder_simple("test", mensaje)
    
    print("💬 Respuesta:")
    print("-" * 60)
    print(respuesta[:200] + "..." if len(respuesta) > 200 else respuesta)
    print("=" * 60)
    print(f"\n⚡ TTFB: {ttfb:.0f}ms")
    print(f"   Target: <2000ms")
    print(f"   Estado: {'✅' if ttfb < 2000 else '⚠️'}")
    
    await sentinel.close()
    print("\n✅ Test completado\n")


async def benchmark(n: int = 5):
    """Benchmark rápido"""
    print(f"📊 Benchmark - {n} requests")
    print("=" * 60)
    
    sentinel = SentinelFluido()
    ttfbs = []
    
    for i in range(n):
        print(f"\n[{i+1}/{n}] ", end='', flush=True)
        _, ttfb = await sentinel.responder_simple(f"user_{i}", f"Test {i}")
        ttfbs.append(ttfb)
        print(f"TTFB: {ttfb:.0f}ms")
    
    print("\n" + "=" * 60)
    print(f"\n📈 Resultados:")
    print(f"   TTFB promedio: {sum(ttfbs)/len(ttfbs):.0f}ms")
    print(f"   TTFB mínimo: {min(ttfbs):.0f}ms")
    print(f"   TTFB máximo: {max(ttfbs):.0f}ms")
    print(f"   Target: <2000ms")
    
    await sentinel.close()
    print("\n✅ Benchmark completado\n")


async def main():
    """Menu"""
    print("\n" + "=" * 60)
    print("🛡️  SENTINEL FLUIDO - Tests")
    print("=" * 60)
    print("\nOpciones:")
    print("  1. Test streaming (recomendado)")
    print("  2. Test simple")
    print("  3. Benchmark (5 requests)")
    print()
    
    choice = input("Selecciona (1-3): ").strip()
    
    if choice == "1":
        await test_streaming()
    elif choice == "2":
        await test_simple()
    elif choice == "3":
        await benchmark()
    else:
        print("❌ Opción inválida")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
