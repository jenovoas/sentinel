"""
Quick Test - Sentinel Optimized
Prueba rápida para validar funcionamiento básico
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.sentinel_optimized import SentinelOptimized


async def quick_test():
    """Prueba rápida de 1 request"""
    print("🧪 QUICK TEST - Sentinel Optimized")
    print("=" * 60)
    
    sentinel = SentinelOptimized()
    
    mensaje = "Hola, ¿cómo funciona Sentinel?"
    
    print(f"\n📝 Mensaje: {mensaje}\n")
    print("💬 Respuesta:")
    print("-" * 60)
    
    try:
        async for chunk, metrics in sentinel.generate_optimized("test_user", mensaje):
            print(chunk, end='', flush=True)
        
        print("\n" + "=" * 60)
        print("\n📊 Métricas:")
        metrics = sentinel.get_patent_metrics()
        
        if "error" not in metrics:
            print(f"  TTFB: {metrics['ttfb_mean_ms']:.0f}ms (target: <200ms)")
            print(f"  Token-rate: {metrics['token_rate_mean_ms']:.0f}ms (target: <250ms)")
            print(f"  Cumple TTFB: {'✅' if metrics['meets_ttfb_target'] else '❌'}")
            print(f"  Cumple Token-rate: {'✅' if metrics['meets_token_rate_target'] else '❌'}")
        else:
            print(f"  {metrics['error']}")
        
        await sentinel.close()
        print("\n✅ Test completado\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(quick_test())
