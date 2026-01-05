
import asyncio
import logging
import sys
import os

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'truth_algorithm')))

from app.services.truthsync import LocalTruthSyncEngine
from app.routers.health import biological_state

# Configurar logging para ver que REALMENTE sale a internet
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def demo_real_verification():
    print("🌍 1. INICIANDO MOTOR TRUTHSYNC (Modo Real)...")
    engine = LocalTruthSyncEngine()
    
    # Claim a verificar en internet real
    claim = "Guido van Rossum created the Python programming language"
    print(f"🔎 2. BUSCANDO EN INTERNET: '{claim}'")
    
    # 3. VERIFICACIÓN REAL
    # Esto activará DuckDuckGoSearch -> Leerá fuentes reales -> Aplicará penalización por disonancia
    result = await engine.verify(claim)
    
    print("\n📊 --- RESULTADOS DE VERIFICACIÓN EN VIVO ---")
    print(f"📝 Claim: {claim}")
    
    # Mostrar fuentes encontradas (Prueba de que no es emulado)
    print(f"🌐 Fuentes Reales Encontradas: {result.get('details', {}).get('sources_count', 0)}")
    
    # LEER PULSO REAL DIRECTAMENTE DE SHM (No estático)
    real_disonancia = 0.0
    try:
        import mmap
        import struct
        with open("/dev/shm/truthsync_shm", "r+b") as f:
            mm = mmap.mmap(f.fileno(), 1024 * 1024)
            # Leer primer double (8 bytes) = entropía
            entropy = struct.unpack("d", mm[:8])[0]
            real_disonancia = entropy * 100
            mm.close()
    except Exception as e:
        print(f"⚠️ Error leyendo SHM: {e}")

    print(f"💓 Disonancia del Sistema (Leída en Vivo de /dev/shm): {real_disonancia:.2f}")
    
    print("-" * 40)
    print(f"📢 STATUS FINAL: {result['status']}")
    print(f"📉 CONFIANZA FINAL: {result['confidence'] * 100:.1f}%")
    print(f"💡 EXPLICACIÓN: {result['explanation']}")
    print("-" * 40)

if __name__ == "__main__":
    asyncio.run(demo_real_verification())
