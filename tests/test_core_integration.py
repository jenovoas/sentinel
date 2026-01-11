#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -----------------------------------------------------------------------------
# TEST DE INTEGRACIÓN: CORE MEMORY
# -----------------------------------------------------------------------------
# Verifica que el adaptador LiquidMemory funcione correctamente
# como reemplazo del sistema legado.
# -----------------------------------------------------------------------------

import sys
import os
import json
sys.path.append(os.getcwd())

from quantum.liquid_memory_adapter import LiquidMemory

def run_integration_test():
    print("🔌 CORE INTEGRATION TEST: LIQUID MEMORY")
    print("-" * 60)
    
    # 1. Initialize System
    mem = LiquidMemory(size_scale=1) # Small/Fast
    
    # 2. Mock Configuration Data
    config = {
        "system_name": "SENTINEL_V2",
        "core_frequency": "153.4 MHz",
        "prime_directive": "PROTECT_YATRA",
        "modules": ["Cortex", "LiquidLattice", "VoidWalker"]
    }
    config_bytes = json.dumps(config).encode('utf-8')
    
    # 3. Store
    print(f"\n💾 Storing Configuration ({len(config_bytes)} bytes)...")
    success = mem.store("sys_config.json", config_bytes)
    
    if not success:
        print("❌ CRITICAL: Write Failed.")
        return
        
    print("✅ Write Confirmed.")
    
    # 4. Retrieve
    print(f"\n📂 Reading Configuration...")
    retrieved_bytes = mem.retrieve("sys_config.json")
    
    if retrieved_bytes is None:
         print("❌ CRITICAL: Read Failed (Not Found or Sig Mismatch).")
         return
         
    # 5. Validate Content
    try:
        retrieved_config = json.loads(retrieved_bytes.decode('utf-8'))
        print(f"   Contenido: {retrieved_config}")
        
        if retrieved_config == config:
            print("\n✅ ÉXITO: Integridad Perfecta de Objeto JSON.")
            print("   El sistema de memoria líquida está operativo para datos complejos.")
        else:
            print("\n❌ FALLO: Corrupción de Datos JSON.")
    except Exception as e:
        print(f"\n❌ FALLO FATAL: {e}")
        print(f"Raw Bytes: {retrieved_bytes}")

if __name__ == "__main__":
    run_integration_test()
